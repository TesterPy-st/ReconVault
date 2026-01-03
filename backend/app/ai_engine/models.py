"""
ReconVault AI Anomaly Detection Models

This module implements ML models for detecting anomalies in OSINT data:
- Isolation Forest for outlier detection
- LSTM Autoencoder for behavioral anomalies
- Statistical models (Z-score, Benford's Law, CUSUM)
"""

import json
import os
import pickle
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import torch
import torch.nn as nn
from loguru import logger
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import RobustScaler, StandardScaler


class LSTMAutoencoder(nn.Module):
    """
    LSTM-based Autoencoder for detecting behavioral anomalies in time-series data.

    Architecture:
        Encoder: Input(50, 15) → LSTM(64) → LSTM(32) → Latent(16)
        Decoder: Latent(16) → LSTM(32) → LSTM(64) → Output(50, 15)
    """

    def __init__(
        self,
        sequence_length: int = 50,
        n_features: int = 15,
        encoding_dim: int = 16,
        hidden_dim_1: int = 64,
        hidden_dim_2: int = 32,
        dropout: float = 0.2,
    ):
        """
        Initialize LSTM Autoencoder.

        Args:
            sequence_length: Length of input sequences
            n_features: Number of features per timestep
            encoding_dim: Size of latent representation
            hidden_dim_1: Size of first LSTM layer
            hidden_dim_2: Size of second LSTM layer
            dropout: Dropout rate for regularization
        """
        super(LSTMAutoencoder, self).__init__()

        self.sequence_length = sequence_length
        self.n_features = n_features
        self.encoding_dim = encoding_dim

        # Encoder
        self.encoder_lstm1 = nn.LSTM(
            n_features, hidden_dim_1, batch_first=True, dropout=dropout
        )
        self.encoder_lstm2 = nn.LSTM(
            hidden_dim_1, hidden_dim_2, batch_first=True, dropout=dropout
        )
        self.encoder_fc = nn.Linear(hidden_dim_2, encoding_dim)

        # Decoder
        self.decoder_fc = nn.Linear(encoding_dim, hidden_dim_2)
        self.decoder_lstm1 = nn.LSTM(
            hidden_dim_2, hidden_dim_1, batch_first=True, dropout=dropout
        )
        self.decoder_lstm2 = nn.LSTM(
            hidden_dim_1, n_features, batch_first=True, dropout=dropout
        )

        self.dropout = nn.Dropout(dropout)

    def encode(self, x: torch.Tensor) -> torch.Tensor:
        """Encode input sequence to latent representation."""
        x, _ = self.encoder_lstm1(x)
        x, (hidden, cell) = self.encoder_lstm2(x)
        # Use last hidden state
        x = hidden[-1]
        x = self.dropout(x)
        x = self.encoder_fc(x)
        return x

    def decode(self, x: torch.Tensor) -> torch.Tensor:
        """Decode latent representation back to sequence."""
        batch_size = x.size(0)
        x = self.decoder_fc(x)
        x = self.dropout(x)
        # Repeat for sequence length
        x = x.unsqueeze(1).repeat(1, self.sequence_length, 1)
        x, _ = self.decoder_lstm1(x)
        x, _ = self.decoder_lstm2(x)
        return x

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass through autoencoder."""
        encoded = self.encode(x)
        decoded = self.decode(encoded)
        return decoded


class EntityAnomalyDetector:
    """Isolation Forest model for detecting entity anomalies."""

    def __init__(
        self,
        n_estimators: int = 100,
        max_samples: int = 256,
        contamination: float = 0.1,
        random_state: int = 42,
    ):
        """
        Initialize Entity Anomaly Detector.

        Args:
            n_estimators: Number of trees in the forest
            max_samples: Number of samples to draw from dataset
            contamination: Expected proportion of anomalies
            random_state: Random seed for reproducibility
        """
        self.model = IsolationForest(
            n_estimators=n_estimators,
            max_samples=max_samples,
            contamination=contamination,
            random_state=random_state,
            n_jobs=-1,
        )
        self.scaler = RobustScaler()
        self.is_fitted = False
        self.feature_names: List[str] = []
        self.threshold = -0.5

    def fit(self, X: np.ndarray, feature_names: List[str]) -> "EntityAnomalyDetector":
        """
        Train the Isolation Forest model.

        Args:
            X: Training data (n_samples, n_features)
            feature_names: Names of features

        Returns:
            Self for method chaining
        """
        logger.info(f"Training Entity Anomaly Detector on {X.shape[0]} samples")

        # Scale features
        X_scaled = self.scaler.fit_transform(X)

        # Train model
        self.model.fit(X_scaled)
        self.feature_names = feature_names
        self.is_fitted = True

        logger.info("Entity Anomaly Detector training complete")
        return self

    def predict(self, X: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Predict anomalies.

        Args:
            X: Input data (n_samples, n_features)

        Returns:
            Tuple of (predictions, anomaly_scores)
            predictions: 1 for normal, -1 for anomaly
            anomaly_scores: Raw anomaly scores
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted before prediction")

        X_scaled = self.scaler.transform(X)
        predictions = self.model.predict(X_scaled)
        scores = self.model.score_samples(X_scaled)

        return predictions, scores

    def predict_single(self, x: np.ndarray) -> Tuple[bool, float]:
        """
        Predict if single sample is anomalous.

        Args:
            x: Single sample (n_features,)

        Returns:
            Tuple of (is_anomaly, anomaly_score)
        """
        x = x.reshape(1, -1)
        predictions, scores = self.predict(x)

        is_anomaly = predictions[0] == -1 or scores[0] < self.threshold
        anomaly_score = self._normalize_score(scores[0])

        return is_anomaly, anomaly_score

    def _normalize_score(self, score: float) -> float:
        """
        Normalize anomaly score to 0-1 range.

        Args:
            score: Raw isolation forest score (typically -1 to 0)

        Returns:
            Normalized score (0=normal, 1=highly anomalous)
        """
        # Isolation Forest scores are typically between -1 and 0.5
        # More negative = more anomalous
        normalized = max(0.0, min(1.0, (self.threshold - score) / abs(self.threshold)))
        return normalized


class RelationshipAnomalyDetector:
    """Isolation Forest model for detecting relationship anomalies."""

    def __init__(
        self,
        n_estimators: int = 100,
        max_samples: int = 256,
        contamination: float = 0.1,
        random_state: int = 42,
    ):
        """Initialize Relationship Anomaly Detector."""
        self.model = IsolationForest(
            n_estimators=n_estimators,
            max_samples=max_samples,
            contamination=contamination,
            random_state=random_state,
            n_jobs=-1,
        )
        self.scaler = StandardScaler()
        self.is_fitted = False
        self.feature_names: List[str] = []
        self.threshold = -0.5

    def fit(
        self, X: np.ndarray, feature_names: List[str]
    ) -> "RelationshipAnomalyDetector":
        """Train the Relationship Anomaly Detector."""
        logger.info(f"Training Relationship Anomaly Detector on {X.shape[0]} samples")

        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled)
        self.feature_names = feature_names
        self.is_fitted = True

        logger.info("Relationship Anomaly Detector training complete")
        return self

    def predict_single(self, x: np.ndarray) -> Tuple[bool, float]:
        """Predict if single relationship is anomalous."""
        if not self.is_fitted:
            raise ValueError("Model must be fitted before prediction")

        x = x.reshape(1, -1)
        x_scaled = self.scaler.transform(x)

        prediction = self.model.predict(x_scaled)[0]
        score = self.model.score_samples(x_scaled)[0]

        is_anomaly = prediction == -1 or score < self.threshold
        anomaly_score = max(
            0.0, min(1.0, (self.threshold - score) / abs(self.threshold))
        )

        return is_anomaly, anomaly_score


class BehavioralAnomalyDetector:
    """LSTM Autoencoder for detecting behavioral anomalies."""

    def __init__(
        self,
        sequence_length: int = 50,
        n_features: int = 15,
        encoding_dim: int = 16,
        device: str = "cpu",
    ):
        """Initialize Behavioral Anomaly Detector."""
        self.sequence_length = sequence_length
        self.n_features = n_features
        self.device = torch.device(device)

        self.model = LSTMAutoencoder(
            sequence_length=sequence_length,
            n_features=n_features,
            encoding_dim=encoding_dim,
        ).to(self.device)

        self.scaler = StandardScaler()
        self.is_fitted = False
        self.threshold = None  # Will be set to 95th percentile during training

    def fit(
        self,
        X: np.ndarray,
        epochs: int = 50,
        batch_size: int = 32,
        learning_rate: float = 0.001,
    ) -> "BehavioralAnomalyDetector":
        """
        Train the LSTM Autoencoder.

        Args:
            X: Training sequences (n_samples, sequence_length, n_features)
            epochs: Number of training epochs
            batch_size: Batch size for training
            learning_rate: Learning rate for optimizer

        Returns:
            Self for method chaining
        """
        logger.info(f"Training Behavioral Anomaly Detector on {X.shape[0]} sequences")

        # Reshape for scaling: (n_samples * seq_length, n_features)
        n_samples = X.shape[0]
        X_reshaped = X.reshape(-1, self.n_features)
        X_scaled = self.scaler.fit_transform(X_reshaped)
        X_scaled = X_scaled.reshape(n_samples, self.sequence_length, self.n_features)

        # Convert to PyTorch tensor
        X_tensor = torch.FloatTensor(X_scaled).to(self.device)

        # Training setup
        self.model.train()
        optimizer = torch.optim.Adam(self.model.parameters(), lr=learning_rate)
        criterion = nn.MSELoss()

        # Training loop
        for epoch in range(epochs):
            total_loss = 0
            num_batches = 0

            for i in range(0, len(X_tensor), batch_size):
                batch = X_tensor[i : i + batch_size]

                optimizer.zero_grad()
                outputs = self.model(batch)
                loss = criterion(outputs, batch)

                # L1 regularization
                l1_lambda = 0.0001
                l1_norm = sum(p.abs().sum() for p in self.model.parameters())
                loss = loss + l1_lambda * l1_norm

                loss.backward()
                optimizer.step()

                total_loss += loss.item()
                num_batches += 1

            avg_loss = total_loss / num_batches
            if (epoch + 1) % 10 == 0:
                logger.info(f"Epoch [{epoch+1}/{epochs}], Loss: {avg_loss:.6f}")

        # Calculate threshold (95th percentile of reconstruction errors)
        self.model.eval()
        with torch.no_grad():
            outputs = self.model(X_tensor)
            errors = torch.mean((outputs - X_tensor) ** 2, dim=(1, 2)).cpu().numpy()
            self.threshold = np.percentile(errors, 95)

        self.is_fitted = True
        logger.info(f"Training complete. Threshold set to: {self.threshold:.6f}")

        return self

    def predict_single(self, x: np.ndarray) -> Tuple[bool, float]:
        """
        Predict if single sequence is anomalous.

        Args:
            x: Single sequence (sequence_length, n_features)

        Returns:
            Tuple of (is_anomaly, anomaly_score)
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted before prediction")

        # Scale
        x_reshaped = x.reshape(-1, self.n_features)
        x_scaled = self.scaler.transform(x_reshaped)
        x_scaled = x_scaled.reshape(1, self.sequence_length, self.n_features)

        # Predict
        self.model.eval()
        with torch.no_grad():
            x_tensor = torch.FloatTensor(x_scaled).to(self.device)
            output = self.model(x_tensor)
            error = torch.mean((output - x_tensor) ** 2).item()

        is_anomaly = error > self.threshold
        # Normalize score based on threshold
        anomaly_score = min(1.0, error / (self.threshold * 2))

        return is_anomaly, anomaly_score


class StatisticalAnomalyDetector:
    """Statistical models for anomaly detection."""

    @staticmethod
    def z_score_detection(
        values: np.ndarray, threshold: float = 3.0
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Detect anomalies using Z-score method.

        Args:
            values: Array of values
            threshold: Z-score threshold (default: 3.0)

        Returns:
            Tuple of (is_anomaly, z_scores)
        """
        mean = np.mean(values)
        std = np.std(values)

        if std == 0:
            return np.zeros(len(values), dtype=bool), np.zeros(len(values))

        z_scores = np.abs((values - mean) / std)
        is_anomaly = z_scores > threshold

        return is_anomaly, z_scores

    @staticmethod
    def benfords_law_detection(
        values: np.ndarray, significance_level: float = 0.05
    ) -> Dict[str, Any]:
        """
        Detect anomalies using Benford's Law.

        Benford's Law states that in many natural datasets, the first digit
        follows a logarithmic distribution.

        Args:
            values: Array of positive numeric values
            significance_level: Chi-square test significance level

        Returns:
            Dictionary with test results
        """
        from scipy.stats import chisquare

        # Extract first digits
        first_digits = []
        for val in values:
            if val > 0:
                first_digit = int(str(abs(int(val)))[0])
                if first_digit != 0:
                    first_digits.append(first_digit)

        if len(first_digits) < 10:
            return {
                "is_anomalous": False,
                "reason": "Insufficient data for Benford's Law test",
                "chi_square": None,
                "p_value": None,
            }

        # Expected frequencies according to Benford's Law
        expected_freq = np.array([np.log10(1 + 1 / d) for d in range(1, 10)]) * len(
            first_digits
        )

        # Observed frequencies
        observed_freq = np.array([first_digits.count(d) for d in range(1, 10)])

        # Chi-square test
        chi_square, p_value = chisquare(observed_freq, expected_freq)

        is_anomalous = p_value < significance_level

        return {
            "is_anomalous": is_anomalous,
            "chi_square": float(chi_square),
            "p_value": float(p_value),
            "observed_freq": observed_freq.tolist(),
            "expected_freq": expected_freq.tolist(),
        }

    @staticmethod
    def cusum_detection(
        values: np.ndarray, threshold: float = 5.0, drift: float = 0.0
    ) -> Tuple[List[int], np.ndarray]:
        """
        Detect change points using CUSUM algorithm.

        Args:
            values: Time series values
            threshold: Detection threshold
            drift: Allowable drift

        Returns:
            Tuple of (change_points, cusum_values)
        """
        n = len(values)
        mean = np.mean(values)

        cusum_pos = np.zeros(n)
        cusum_neg = np.zeros(n)
        change_points = []

        for i in range(1, n):
            cusum_pos[i] = max(0, cusum_pos[i - 1] + values[i] - mean - drift)
            cusum_neg[i] = max(0, cusum_neg[i - 1] - values[i] + mean - drift)

            if cusum_pos[i] > threshold or cusum_neg[i] > threshold:
                change_points.append(i)
                cusum_pos[i] = 0
                cusum_neg[i] = 0

        return change_points, cusum_pos + cusum_neg


class ModelPersistence:
    """Utilities for saving and loading models."""

    @staticmethod
    def save_sklearn_model(
        model: Any, scaler: Any, filepath: Path, metadata: Dict[str, Any]
    ) -> None:
        """Save scikit-learn model with metadata."""
        save_dict = {
            "model": model,
            "scaler": scaler,
            "metadata": metadata,
            "saved_at": datetime.utcnow().isoformat(),
        }

        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "wb") as f:
            pickle.dump(save_dict, f)

        logger.info(f"Model saved to {filepath}")

    @staticmethod
    def load_sklearn_model(filepath: Path) -> Tuple[Any, Any, Dict[str, Any]]:
        """Load scikit-learn model with metadata."""
        with open(filepath, "rb") as f:
            save_dict = pickle.load(f)

        logger.info(f"Model loaded from {filepath}")
        return save_dict["model"], save_dict["scaler"], save_dict["metadata"]

    @staticmethod
    def save_pytorch_model(
        model: nn.Module, scaler: Any, filepath: Path, metadata: Dict[str, Any]
    ) -> None:
        """Save PyTorch model with metadata."""
        filepath.parent.mkdir(parents=True, exist_ok=True)

        save_dict = {
            "model_state_dict": model.state_dict(),
            "model_config": {
                "sequence_length": model.sequence_length,
                "n_features": model.n_features,
                "encoding_dim": model.encoding_dim,
            },
            "scaler": scaler,
            "metadata": metadata,
            "saved_at": datetime.utcnow().isoformat(),
        }

        torch.save(save_dict, filepath)
        logger.info(f"PyTorch model saved to {filepath}")

    @staticmethod
    def load_pytorch_model(
        filepath: Path, device: str = "cpu"
    ) -> Tuple[LSTMAutoencoder, Any, Dict[str, Any]]:
        """Load PyTorch model with metadata."""
        save_dict = torch.load(filepath, map_location=device)

        config = save_dict["model_config"]
        model = LSTMAutoencoder(
            sequence_length=config["sequence_length"],
            n_features=config["n_features"],
            encoding_dim=config["encoding_dim"],
        )
        model.load_state_dict(save_dict["model_state_dict"])
        model.to(device)
        model.eval()

        logger.info(f"PyTorch model loaded from {filepath}")
        return model, save_dict["scaler"], save_dict["metadata"]
