"""
Media OSINT Collector for ReconVault intelligence system.

This module provides media file intelligence gathering using OpenCV,
Pillow, ExifTool, and audio analysis libraries.
"""

import asyncio
import io
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import logging
import base64
from pathlib import Path
import tempfile
import hashlib

# Conditional imports for optional dependencies
try:
    import cv2
    import numpy as np
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False
    cv2 = None
    np = None

try:
    from PIL import Image, ExifTags
    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False
    Image = None
    ExifTags = None

try:
    import librosa
    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False
    librosa = None

try:
    from pydub import AudioSegment
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False
    AudioSegment = None

try:
    from transformers import pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    pipeline = None

from .base_collector import BaseCollector, CollectorConfig


class MediaCollector(BaseCollector):
    """Media OSINT collector for image and audio analysis"""
    
    def __init__(self, config: CollectorConfig):
        super().__init__(config)
        self.logger = logging.getLogger(__name__)
        
        # Initialize ML pipelines if available
        self.ocr_pipeline = None
        self.image_classifier = None
        self.sentiment_analyzer = None
        
        if TRANSFORMERS_AVAILABLE and pipeline:
            try:
                # Initialize OCR pipeline
                self.ocr_pipeline = pipeline("optical-character-recognition", model="microsoft/trocr-base-printed")
                
                # Initialize image classification
                self.image_classifier = pipeline("image-classification", model="google/vit-base-patch16-224")
                
                # Initialize sentiment analysis
                self.sentiment_analyzer = pipeline("sentiment-analysis")
                
            except Exception as e:
                self.logger.info(f"Could not initialize ML pipelines: {e}")
    
    async def collect(self) -> Dict[str, Any]:
        """Collect media intelligence data"""
        self.logger.info(f"Starting media collection for target: {self.config.target}")
        
        results = {
            "target": self.config.target,
            "entities": [],
            "relationships": [],
            "metadata": {}
        }
        
        try:
            # Determine media type
            media_type = self._detect_media_type(self.config.target)
            
            if media_type == "image":
                # Process image
                image_data = await self.process_image(self.config.target)
                if image_data:
                    results["entities"].extend(image_data.get("entities", []))
                    results["metadata"]["image_analysis"] = image_data.get("metadata", {})
            
            elif media_type == "audio":
                # Process audio
                audio_data = await self.process_audio(self.config.target)
                if audio_data:
                    results["entities"].extend(audio_data.get("entities", []))
                    results["metadata"]["audio_analysis"] = audio_data.get("metadata", {})
            
            elif media_type == "video":
                # Process video
                video_data = await self.process_video(self.config.target)
                if video_data:
                    results["entities"].extend(video_data.get("entities", []))
                    results["metadata"]["video_analysis"] = video_data.get("metadata", {})
            
            else:
                self.logger.warning(f"Unknown media type for target: {self.config.target}")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Media collection failed: {e}")
            raise
    
    def _detect_media_type(self, target: str) -> str:
        """Detect media type from target URL or path"""
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.svg']
        audio_extensions = ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a', '.wma']
        video_extensions = ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm']
        
        target_lower = target.lower()
        
        if any(target_lower.endswith(ext) for ext in image_extensions):
            return "image"
        elif any(target_lower.endswith(ext) for ext in audio_extensions):
            return "audio"
        elif any(target_lower.endswith(ext) for ext in video_extensions):
            return "video"
        
        # If no extension, try to download and detect
        return "unknown"
    
    async def process_image(self, image_source: str) -> Optional[Dict[str, Any]]:
        """Process image file or URL for OSINT data"""
        image_data = {
            "entities": [],
            "metadata": {}
        }
        
        try:
            self.logger.debug(f"Processing image: {image_source}")
            
            # Download or load image
            image_path = await self._download_media(image_source)
            if not image_path:
                return None
            
            # Extract basic metadata
            if PILLOW_AVAILABLE and Image:
                with Image.open(image_path) as img:
                    basic_info = {
                        "format": img.format,
                        "mode": img.mode,
                        "size": img.size,
                        "width": img.width,
                        "height": img.height,
                        "file_size": image_path.stat().st_size if hasattr(image_path, 'stat') else 0
                    }
                    
                    image_data["metadata"]["basic_info"] = basic_info
                    
                    # Extract EXIF data
                    exif_data = await self.extract_image_metadata(img, image_path)
                    if exif_data:
                        image_data["metadata"]["exif"] = exif_data
                        
                        # Create entities from EXIF
                        if "gps" in exif_data:
                            gps_entity = {
                                "value": f"GPS_{image_source}",
                                "type": "GPS_COORDINATES",
                                "metadata": {
                                    "latitude": exif_data["gps"].get("latitude"),
                                    "longitude": exif_data["gps"].get("longitude"),
                                    "source": "exif_data",
                                    "collected_at": datetime.utcnow().isoformat()
                                },
                                "source": "exif_extractor"
                            }
                            image_data["entities"].append(gps_entity)
                        
                        if "camera" in exif_data:
                            camera_entity = {
                                "value": exif_data["camera"].get("model", "unknown"),
                                "type": "DEVICE",
                                "sub_type": "CAMERA",
                                "metadata": {
                                    "make": exif_data["camera"].get("make"),
                                    "model": exif_data["camera"].get("model"),
                                    "software": exif_data["camera"].get("software"),
                                    "source": "exif_data"
                                },
                                "source": "exif_extractor"
                            }
                            image_data["entities"].append(camera_entity)
            
            # Extract text using OCR
            if self.ocr_pipeline or (OPENCV_AVAILABLE and cv2):
                text = await self.extract_text_from_image(image_path)
                if text:
                    image_data["metadata"]["extracted_text"] = text
                    
                    text_entity = {
                        "value": f"TEXT_{image_source[:30]}",
                        "type": "TEXT",
                        "metadata": {
                            "content": text[:1000],  # Limit text length
                            "length": len(text),
                            "source": "ocr_extraction",
                            "collected_at": datetime.utcnow().isoformat()
                        },
                        "source": "ocr_extractor"
                    }
                    
                    image_data["entities"].append(text_entity)
            
            # Detect faces
            if OPENCV_AVAILABLE and cv2:
                faces = await self.detect_faces(image_path)
                if faces:
                    image_data["metadata"]["faces"] = faces
                    
                    for i, face in enumerate(faces):
                        face_entity = {
                            "value": f"FACE_{i}_{image_source}",
                            "type": "FACE",
                            "metadata": {
                                "bounding_box": face.get("bbox"),
                                "confidence": face.get("confidence"),
                                "source_image": image_source,
                                "collected_at": datetime.utcnow().isoformat()
                            },
                            "source": "face_detector"
                        }
                        
                        image_data["entities"].append(face_entity)
            
            # Analyze image objects
            if TRANSFORMERS_AVAILABLE and self.image_classifier:
                objects = await self.analyze_image_objects(image_path)
                if objects:
                    image_data["metadata"]["detected_objects"] = objects
                    
                    for obj in objects:
                        obj_entity = {
                            "value": obj.get("label", "unknown"),
                            "type": "OBJECT",
                            "metadata": {
                                "confidence": obj.get("confidence"),
                                "source_image": image_source,
                                "collected_at": datetime.utcnow().isoformat()
                            },
                            "source": "object_detector"
                        }
                        
                        image_data["entities"].append(obj_entity)
            
            # Calculate hash for duplicate detection
            if image_path:
                file_hash = await self._calculate_file_hash(image_path)
                image_data["metadata"]["file_hash"] = file_hash
            
        except Exception as e:
            self.logger.error(f"Error processing image {image_source}: {e}")
        
        finally:
            # Cleanup temp file
            if 'image_path' in locals() and image_path and isinstance(image_path, Path):
                if image_path.exists() and 'temp' in str(image_path):
                    try:
                        image_path.unlink()
                    except:
                        pass
        
        return image_data
    
    async def extract_image_metadata(self, image: Any, image_path: Path) -> Optional[Dict[str, Any]]:
        """Extract EXIF and metadata from image"""
        metadata = {}
        
        try:
            if not (PILLOW_AVAILABLE and ExifTags):
                self.logger.debug("Pillow not available for EXIF extraction")
                return None
            
            self.logger.debug(f"Extracting metadata from image: {image_path}")
            
            # Get EXIF data
            exifdata = image.getexif()
            
            if exifdata:
                exif_info = {}
                
                for tag_id in exifdata:
                    tag = ExifTags.TAGS.get(tag_id, tag_id)
                    value = exifdata.get(tag_id)
                    
                    if isinstance(value, bytes):
                        try:
                            value = value.decode('utf-8')
                        except:
                            value = str(value)
                    
                    exif_info[tag] = value
                
                metadata["exif"] = exif_info
                
                # Extract GPS data
                gps_info = {}
                if "GPSInfo" in exif_info:
                    gps_data = exif_info["GPSInfo"]
                    
                    # Convert GPS coordinates to decimal
                    def convert_gps_to_decimal(gps_tuple, ref):
                        if gps_tuple and ref:
                            degrees = gps_tuple[0] if isinstance(gps_tuple[0], (int, float)) else gps_tuple[0][0] / gps_tuple[0][1]
                            minutes = gps_tuple[1] if isinstance(gps_tuple[1], (int, float)) else gps_tuple[1][0] / gps_tuple[1][1]
                            seconds = gps_tuple[2] if isinstance(gps_tuple[2], (int, float)) else gps_tuple[2][0] / gps_tuple[2][1]
                            
                            decimal = degrees + (minutes / 60.0) + (seconds / 3600.0)
                            if ref in ['S', 'W']:
                                decimal = -decimal
                            return decimal
                        return None
                    
                    gps_lat = convert_gps_to_decimal(gps_data.get(2), gps_data.get(1))
                    gps_lon = convert_gps_to_decimal(gps_data.get(4), gps_data.get(3))
                    
                    if gps_lat and gps_lon:
                        gps_info = {
                            "latitude": gps_lat,
                            "longitude": gps_lon,
                            "altitude": gps_data.get(6),
                            "timestamp": gps_data.get(29),
                            "satellites": gps_data.get(7)
                        }
                        
                        metadata["gps"] = gps_info
                
                # Extract camera info
                camera_info = {}
                if "Make" in exif_info:
                    camera_info["make"] = exif_info["Make"]
                if "Model" in exif_info:
                    camera_info["model"] = exif_info["Model"]
                if "Software" in exif_info:
                    camera_info["software"] = exif_info["Software"]
                if "DateTime" in exif_info:
                    camera_info["datetime"] = exif_info["DateTime"]
                if "DateTimeOriginal" in exif_info:
                    camera_info["datetime_original"] = exif_info["DateTimeOriginal"]
                
                if camera_info:
                    metadata["camera"] = camera_info
                
                # Extract location info
                if "GPSInfo" in exif_info:
                    metadata["has_gps"] = True
                
                if "LensModel" in exif_info:
                    metadata["lens_model"] = exif_info["LensModel"]
        
        except Exception as e:
            self.logger.error(f"Error extracting image metadata: {e}")
        
        return metadata
    
    async def extract_text_from_image(self, image_path: Path) -> Optional[str]:
        """Extract text from image using OCR"""
        try:
            if self.ocr_pipeline:
                # Use transformer-based OCR
                result = self.ocr_pipeline(str(image_path))
                return result[0].get("generated_text", "")
            
            elif OPENCV_AVAILABLE and cv2:
                # Use OpenCV + Tesseract if available
                import pytesseract
                
                image = cv2.imread(str(image_path))
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                
                # Preprocess image
                gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
                
                # Extract text
                text = pytesseract.image_to_string(gray)
                return text.strip()
            
        except Exception as e:
            self.logger.debug(f"OCR extraction error: {e}")
            self.logger.warning("OCR not available - install pytesseract for text extraction")
            
        return None
    
    async def detect_faces(self, image_path: Path) -> List[Dict[str, Any]]:
        """Detect faces in image using OpenCV"""
        faces = []
        
        try:
            if not (OPENCV_AVAILABLE and cv2):
                return faces
            
            # Load OpenCV face detector
            face_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            )
            
            if face_cascade.empty():
                return faces
            
            # Read and preprocess image
            image = cv2.imread(str(image_path))
            if image is None:
                return faces
            
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            detected_faces = face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30)
            )
            
            for i, (x, y, w, h) in enumerate(detected_faces):
                face_info = {
                    "face_id": i,
                    "bbox": {"x": int(x), "y": int(y), "width": int(w), "height": int(h)},
                    "center": {"x": int(x + w/2), "y": int(y + h/2)},
                    "confidence": 0.8  # OpenCV doesn't provide confidence
                }
                faces.append(face_info)
            
        except Exception as e:
            self.logger.error(f"Error detecting faces: {e}")
        
        return faces
    
    async def analyze_image_objects(self, image_path: Path) -> List[Dict[str, Any]]:
        """Analyze and classify objects in image"""
        objects = []
        
        try:
            if TRANSFORMERS_AVAILABLE and self.image_classifier:
                results = self.image_classifier(str(image_path))
                
                # Get top predictions
                for result in results[:5]:  # Top 5 predictions
                    object_info = {
                        "label": result["label"],
                        "confidence": result["score"]
                    }
                    objects.append(object_info)
            
        except Exception as e:
            self.logger.error(f"Error analyzing image objects: {e}")
        
        return objects
    
    async def process_audio(self, audio_source: str) -> Optional[Dict[str, Any]]:
        """Process audio file for OSINT data"""
        audio_data = {
            "entities": [],
            "metadata": {}
        }
        
        try:
            self.logger.debug(f"Processing audio: {audio_source}")
            
            # Download or load audio
            audio_path = await self._download_media(audio_source)
            if not audio_path:
                return None
            
            # Extract metadata
            metadata = await self.extract_audio_metadata(audio_path)
            if metadata:
                audio_data["metadata"]["audio_info"] = metadata
                
                # Check for speech and transcribe
                if TRANSFORMERS_AVAILABLE and metadata.get("duration", 0) < 300:  # Limit to 5 minutes
                    transcript = await self.extract_audio_transcript(audio_path)
                    if transcript:
                        audio_data["metadata"]["transcript"] = transcript
                        
                        transcript_entity = {
                            "value": f"TRANSCRIPT_{audio_source[:30]}",
                            "type": "TEXT",
                            "metadata": {
                                "content": transcript[:2000],  # Limit length
                                "source_audio": audio_source,
                                "collected_at": datetime.utcnow().isoformat()
                            },
                            "source": "audio_transcription"
                        }
                        
                        audio_data["entities"].append(transcript_entity)
                        
                        # Analyze sentiment
                        if self.sentiment_analyzer and len(transcript) > 10:
                            sentiment = await self.analyze_sentiment(transcript)
                            audio_data["metadata"]["sentiment"] = sentiment
                
                # Extract audio features for analysis
                if LIBROSA_AVAILABLE:
                    features = await self.extract_audio_features(audio_path)
                    if features:
                        audio_data["metadata"]["audio_features"] = features
            
        except Exception as e:
            self.logger.error(f"Error processing audio {audio_source}: {e}")
        
        finally:
            # Cleanup
            if 'audio_path' in locals() and audio_path and isinstance(audio_path, Path):
                if audio_path.exists() and 'temp' in str(audio_path):
                    try:
                        audio_path.unlink()
                    except:
                        pass
        
        return audio_data
    
    async def extract_audio_metadata(self, audio_path: Path) -> Optional[Dict[str, Any]]:
        """Extract metadata from audio file"""
        metadata = {}
        
        try:
            if LIBROSA_AVAILABLE:
                # Load audio with librosa
                y, sr = librosa.load(str(audio_path))
                duration = librosa.get_duration(y=y, sr=sr)
                
                metadata = {
                    "duration": duration,
                    "sample_rate": sr,
                    "samples": len(y),
                    "channels": 1 if y.ndim == 1 else y.shape[0]
                }
                
                # Extract audio features
                tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
                metadata["tempo"] = tempo
                
                # Check if likely contains speech
                # Simple heuristic: speech typically has consistent rhythm and pitch
                spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
                metadata["spectral_centroid_mean"] = float(spectral_centroids.mean())
                
                # Estimate if speech (spectral centroid typically 2000-5000 Hz for speech)
                metadata["likely_speech"] = 2000 <= metadata["spectral_centroid_mean"] <= 5000
                
            elif PYDUB_AVAILABLE:
                # Fallback to pydub
                audio = AudioSegment.from_file(str(audio_path))
                
                metadata = {
                    "duration": len(audio) / 1000.0,  # Convert to seconds
                    "sample_rate": audio.frame_rate,
                    "channels": audio.channels,
                    "sample_width": audio.sample_width,
                    "frame_rate": audio.frame_rate,
                    "frame_width": audio.frame_width,
                    "frame_count": len(audio.get_array_of_samples()) / (audio.channels * audio.sample_width)
                }
            
            # Get file info
            metadata["file_size"] = audio_path.stat().st_size
            metadata["file_name"] = audio_path.name
            
        except Exception as e:
            self.logger.error(f"Error extracting audio metadata: {e}")
        
        return metadata
    
    async def extract_audio_transcript(self, audio_path: Path) -> Optional[str]:
        """Extract text transcript from audio using speech-to-text"""
        try:
            if TRANSFORMERS_AVAILABLE:
                # Use transformer for speech recognition
                speech_pipeline = pipeline("automatic-speech-recognition")
                
                result = speech_pipeline(str(audio_path))
                return result["text"]
            
            else:
                self.logger.warning("Transformers not available for speech recognition")
                return None
        
        except Exception as e:
            self.logger.error(f"Error transcribing audio: {e}")
            return None
    
    async def extract_audio_features(self, audio_path: Path) -> Optional[Dict[str, Any]]:
        """Extract detailed audio features"""
        features = {}
        
        try:
            if LIBROSA_AVAILABLE:
                # Load audio
                y, sr = librosa.load(str(audio_path))
                
                # Extract features
                features["zero_crossing_rate"] = float(librosa.feature.zero_crossing_rate(y).mean())
                features["spectral_centroid"] = float(librosa.feature.spectral_centroid(y, sr=sr).mean())
                features["spectral_rolloff"] = float(librosa.feature.spectral_rolloff(y, sr=sr).mean())
                
                # MFCCs
                mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
                features["mfcc_means"] = [float(mfcc.mean()) for mfcc in mfccs]
                
                # Chroma features
                chroma = librosa.feature.chroma_stft(y=y, sr=sr)
                features["chroma_mean"] = float(chroma.mean())
                
                # Tempo and rhythm
                tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
                features["tempo"] = float(tempo)
                
        except Exception as e:
            self.logger.error(f"Error extracting audio features: {e}")
        
        return features
    
    async def process_video(self, video_source: str) -> Optional[Dict[str, Any]]:
        """Process video file for OSINT data"""
        video_data = {
            "entities": [],
            "metadata": {}
        }
        
        try:
            self.logger.debug(f"Processing video: {video_source}")
            
            # Download video
            video_path = await self._download_media(video_source)
            if not video_path:
                return None
            
            # Basic video processing would go here
            # For now, this is a placeholder
            self.logger.info("Video processing requires additional libraries (opencv-video)")
            
        except Exception as e:
            self.logger.error(f"Error processing video {video_source}: {e}")
        
        return video_data
    
    async def analyze_sentiment(self, text: str) -> Optional[Dict[str, Any]]:
        """Analyze sentiment of text using transformers"""
        try:
            if self.sentiment_analyzer:
                result = self.sentiment_analyzer(text[:512])[0]  # Limit length
                
                return {
                    "sentiment": result["label"],
                    "confidence": result["score"],
                    "text_length": len(text)
                }
        
        except Exception as e:
            self.logger.error(f"Error analyzing sentiment: {e}")
        
        return None
    
    async def _download_media(self, media_source: str) -> Optional[Path]:
        """Download media from URL or return local path"""
        try:
            # Check if it's a URL
            if media_source.startswith(('http://', 'https://')):
                import aiohttp
                
                # Create temp file
                temp_dir = Path(tempfile.gettempdir())
                temp_file = temp_dir / f"reconvault_media_{hashlib.md5(media_source.encode()).hexdigest()[:8]}"
                
                # Download file
                async with aiohttp.ClientSession() as session:
                    async with session.get(media_source, timeout=self.config.timeout) as response:
                        if response.status == 200:
                            content = await response.read()
                            with open(temp_file, 'wb') as f:
                                f.write(content)
                            return temp_file
                        else:
                            self.logger.error(f"Failed to download media: {response.status}")
                            return None
            
            else:
                # Treat as local path
                path = Path(media_source)
                if path.exists():
                    return path
                else:
                    self.logger.error(f"Media file not found: {media_source}")
                    return None
        
        except Exception as e:
            self.logger.error(f"Error downloading media: {e}")
            return None
    
    async def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of file"""
        try:
            sha256_hash = hashlib.sha256()
            
            with open(file_path, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            
            return sha256_hash.hexdigest()
        
        except Exception as e:
            self.logger.error(f"Error calculating file hash: {e}")
            return ""
    
    def normalize(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Normalize media collection results"""
        entities = []
        
        if isinstance(data, dict):
            if "entities" in data:
                # Already normalized format
                return data["entities"]
        
        return entities