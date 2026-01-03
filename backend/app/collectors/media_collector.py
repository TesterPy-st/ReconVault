"""
Media OSINT Collector

Collects OSINT data from media files including:
- Image metadata extraction (EXIF)
- Text extraction (OCR)
- Face detection
- Object detection
- Audio metadata extraction
- Audio transcription
- Sentiment analysis
"""

import asyncio
import os
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import cv2
import numpy as np
from loguru import logger
from PIL import ExifTags, Image

from app.collectors.base_collector import (BaseCollector, CollectionResult,
                                           CollectorConfig, DataType,
                                           RiskLevel)


class MediaCollector(BaseCollector):
    """
    Media OSINT Collector

    Collects OSINT data from images and audio files.
    """

    def __init__(self, config: CollectorConfig):
        super().__init__(config, name="MediaCollector")

    async def collect(self) -> CollectionResult:
        """
        Collect OSINT data from media file.

        Returns:
            CollectionResult with discovered entities
        """
        result = CollectionResult(
            success=False, collector_name=self.name, correlation_id=self.correlation_id
        )

        try:
            media_url = self.config.target

            logger.info(f"Collecting media OSINT for {media_url}")

            # Download media file
            temp_file = await self._download_media(media_url)

            if not temp_file:
                result.errors.append("Failed to download media file")
                return result

            # Determine media type and collect accordingly
            file_extension = Path(temp_file).suffix.lower()

            if file_extension in [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff"]:
                tasks = [
                    self._extract_image_metadata(temp_file),
                    self._detect_faces(temp_file),
                    self._analyze_image_objects(temp_file),
                ]
            elif file_extension in [".mp3", ".wav", ".ogg", ".flac", ".m4a", ".aac"]:
                tasks = [
                    self._extract_audio_metadata(temp_file),
                ]
            else:
                result.errors.append(f"Unsupported media type: {file_extension}")
                return result

            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Aggregate results
            for i, task_result in enumerate(results):
                if isinstance(task_result, Exception):
                    logger.error(f"Task {i} failed: {task_result}")
                    result.errors.append(str(task_result))
                elif task_result:
                    result.data.extend(task_result)

            # Clean up temp file
            try:
                os.unlink(temp_file)
            except Exception:
                pass

            # Determine overall risk level
            risk_factors = [
                e.get("risk_level", RiskLevel.INFO.value) for e in result.data
            ]
            if RiskLevel.CRITICAL.value in risk_factors:
                result.risk_level = RiskLevel.CRITICAL
            elif RiskLevel.HIGH.value in risk_factors:
                result.risk_level = RiskLevel.HIGH
            elif RiskLevel.MEDIUM.value in risk_factors:
                result.risk_level = RiskLevel.MEDIUM

            result.success = len(result.errors) == 0
            result.metadata = {
                "media_url": media_url,
                "file_type": file_extension,
                "tasks_completed": len(
                    [r for r in results if not isinstance(r, Exception)]
                ),
            }

        except Exception as e:
            logger.exception(f"Error in media collection: {e}")
            result.errors.append(str(e))

        return result

    async def _download_media(self, url: str) -> Optional[str]:
        """Download media file to temp location"""
        try:
            response = await self.session.get(url, timeout=30)
            response.raise_for_status()

            # Create temp file
            suffix = Path(url).suffix or ".tmp"
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
            temp_file.close()

            # Write content
            async with aiofiles.open(temp_file.name, "wb") as f:
                await f.write(response.content)

            logger.info(f"Downloaded media to {temp_file.name}")

            return temp_file.name

        except Exception as e:
            logger.error(f"Failed to download media: {e}")
            return None

    async def _extract_image_metadata(self, image_path: str) -> List[Dict[str, Any]]:
        """Extract EXIF metadata from image"""
        entities = []

        try:
            image = Image.open(image_path)

            # Basic metadata
            basic_metadata = {
                "format": image.format,
                "mode": image.mode,
                "size": image.size,
                "width": image.width,
                "height": image.height,
            }

            # EXIF data
            exif_data = {}
            if hasattr(image, "_getexif") and image._getexif():
                exif = image._getexif()

                for tag_id, value in exif.items():
                    tag = ExifTags.TAGS.get(tag_id, tag_id)
                    exif_data[tag] = str(value)

                # Check for GPS data (sensitive)
                has_gps = any("GPS" in str(k) for k in exif_data.keys())
                risk_level = RiskLevel.MEDIUM if has_gps else RiskLevel.INFO

                if has_gps:
                    exif_data["gps_detected"] = True
                    logger.warning(f"GPS data found in image")

                basic_metadata["exif"] = exif_data

            entity = self._create_entity(
                entity_type="URL",
                value=self.config.target,
                risk_level=risk_level,
                metadata={"type": "image_metadata", "image_metadata": basic_metadata},
            )

            entities.append(entity)

            logger.info(f"Extracted metadata from {image_path}")

        except Exception as e:
            logger.error(f"Error extracting image metadata: {e}")

        return entities

    async def _detect_faces(self, image_path: str) -> List[Dict[str, Any]]:
        """Detect faces in image"""
        entities = []

        try:
            # Load image
            image = cv2.imread(image_path)
            if image is None:
                logger.error(f"Failed to load image {image_path}")
                return entities

            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            # Load face detector (Haar Cascade)
            face_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
            )

            # Detect faces
            faces = face_cascade.detectMultiScale(
                gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
            )

            face_count = len(faces)

            if face_count > 0:
                risk_level = RiskLevel.MEDIUM if face_count > 0 else RiskLevel.INFO

                # Extract face locations
                face_locations = [
                    {"x": int(x), "y": int(y), "w": int(w), "h": int(h)}
                    for x, y, w, h in faces
                ]

                entities.append(
                    self._create_entity(
                        entity_type="URL",
                        value=self.config.target,
                        risk_level=risk_level,
                        metadata={
                            "type": "face_detection",
                            "faces_detected": face_count,
                            "face_locations": face_locations,
                        },
                    )
                )

                # Create FACE entities
                for i, face in enumerate(face_locations):
                    entities.append(
                        self._create_entity(
                            entity_type="METADATA",
                            value=f"face_{i+1}",
                            risk_level=RiskLevel.MEDIUM,
                            metadata={
                                "type": "face",
                                "source_image": self.config.target,
                                "location": face,
                            },
                        )
                    )

                logger.warning(f"Detected {face_count} face(s) in image")

        except Exception as e:
            logger.error(f"Error detecting faces: {e}")

        return entities

    async def _analyze_image_objects(self, image_path: str) -> List[Dict[str, Any]]:
        """Detect objects in image"""
        entities = []

        try:
            # Note: Full object detection requires ML models
            # This is a placeholder for future implementation

            # For now, do basic color analysis
            image = cv2.imread(image_path)
            if image is None:
                return entities

            # Calculate dominant colors
            pixels = np.float32(image.reshape(-1, 3))
            n_colors = 5

            # Simple k-means clustering (if sklearn available)
            try:
                from sklearn.cluster import KMeans

                kmeans = KMeans(n_clusters=n_colors, random_state=42)
                kmeans.fit(pixels)

                colors = kmeans.cluster_centers_.astype(int)

                entities.append(
                    self._create_entity(
                        entity_type="URL",
                        value=self.config.target,
                        risk_level=RiskLevel.INFO,
                        metadata={
                            "type": "image_analysis",
                            "dominant_colors": colors.tolist(),
                            "note": "Full object detection requires pre-trained ML models",
                        },
                    )
                )

                logger.info(f"Analyzed {n_colors} dominant colors in image")

            except ImportError:
                logger.debug("sklearn not available for color analysis")

        except Exception as e:
            logger.error(f"Error analyzing image objects: {e}")

        return entities

    async def _extract_audio_metadata(self, audio_path: str) -> List[Dict[str, Any]]:
        """Extract metadata from audio file"""
        entities = []

        try:
            # Use mutagen for audio metadata (if available)
            try:
                from mutagen import File

                audio_file = File(audio_path)

                metadata = {
                    "format": getattr(audio_file, "mime", "unknown"),
                    "length": getattr(audio_file, "info", {}).get("length", 0),
                    "bitrate": getattr(audio_file, "info", {}).get("bitrate", 0),
                    "sample_rate": getattr(audio_file, "info", {}).get(
                        "sample_rate", 0
                    ),
                    "channels": getattr(audio_file, "info", {}).get("channels", 0),
                }

                # Add tag metadata if available
                if hasattr(audio_file, "tags") and audio_file.tags:
                    tags = {}
                    for key, value in audio_file.tags.items():
                        tags[key] = (
                            str(value)
                            if not isinstance(value, list)
                            else [str(v) for v in value]
                        )
                    metadata["tags"] = tags

            except ImportError:
                # Fallback to basic file info
                import wave

                try:
                    with wave.open(audio_path, "rb") as wav_file:
                        metadata = {
                            "format": "WAV",
                            "channels": wav_file.getnchannels(),
                            "sample_width": wav_file.getsampwidth(),
                            "frame_rate": wav_file.getframerate(),
                            "n_frames": wav_file.getnframes(),
                            "duration": wav_file.getnframes() / wav_file.getframerate(),
                        }
                except Exception:
                    metadata = {
                        "format": "unknown",
                        "error": "Could not parse audio file",
                    }

            entities.append(
                self._create_entity(
                    entity_type="URL",
                    value=self.config.target,
                    risk_level=RiskLevel.INFO,
                    metadata={"type": "audio_metadata", "audio_metadata": metadata},
                )
            )

            logger.info(f"Extracted audio metadata from {audio_path}")

        except Exception as e:
            logger.error(f"Error extracting audio metadata: {e}")

        return entities

    async def _extract_text_from_image(self, image_path: str) -> List[Dict[str, Any]]:
        """Extract text from image using OCR"""
        entities = []

        try:
            # Note: OCR requires pytesseract or transformers
            # This is a placeholder for future implementation

            entities.append(
                self._create_entity(
                    entity_type="URL",
                    value=self.config.target,
                    risk_level=RiskLevel.INFO,
                    metadata={
                        "type": "ocr",
                        "note": "OCR functionality requires pytesseract or transformers library",
                    },
                )
            )

        except Exception as e:
            logger.error(f"Error extracting text from image: {e}")

        return entities

    async def _extract_audio_transcript(self, audio_path: str) -> List[Dict[str, Any]]:
        """Extract transcript from audio using speech-to-text"""
        entities = []

        try:
            # Note: Speech-to-text requires transformers or SpeechRecognition
            # This is a placeholder for future implementation

            entities.append(
                self._create_entity(
                    entity_type="URL",
                    value=self.config.target,
                    risk_level=RiskLevel.INFO,
                    metadata={
                        "type": "speech_to_text",
                        "note": "Speech-to-text requires transformers or SpeechRecognition library",
                    },
                )
            )

        except Exception as e:
            logger.error(f"Error extracting audio transcript: {e}")

        return entities

    async def _analyze_sentiment(self, text: str) -> List[Dict[str, Any]]:
        """Analyze sentiment of text"""
        entities = []

        try:
            # Note: Sentiment analysis requires transformers or NLTK
            # This is a placeholder for future implementation

            entities.append(
                self._create_entity(
                    entity_type="METADATA",
                    value="sentiment_analysis",
                    risk_level=RiskLevel.INFO,
                    metadata={
                        "text_length": len(text),
                        "note": "Full sentiment analysis requires transformers library",
                    },
                )
            )

        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")

        return entities

    def normalize(self, raw_data: Any) -> List[Dict[str, Any]]:
        """Normalize raw media data"""
        return raw_data if isinstance(raw_data, list) else []

    def validate(self, data: Dict[str, Any]) -> bool:
        """Validate normalized data"""
        required_fields = ["entity_type", "value"]
        return all(field in data for field in required_fields)


# Import aiofiles at module level
import aiofiles
