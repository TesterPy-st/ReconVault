"""
Train Initial Risk Assessment Model

Script to train and save an initial XGBoost model using synthetic data.
This provides a baseline model that can be retrained with real data later.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from loguru import logger

from app.risk_engine.ml_models import RiskMLModel, generate_synthetic_training_data


def train_initial_model(n_samples: int = 1000):
    """
    Train initial risk model with synthetic data.
    
    Args:
        n_samples: Number of synthetic samples to generate
    """
    logger.info(f"Generating {n_samples} synthetic training samples...")
    
    # Generate synthetic training data
    entities, labels = generate_synthetic_training_data(n_samples)
    
    logger.info("Training XGBoost risk model...")
    
    # Initialize model
    model = RiskMLModel()
    
    # Train model
    results = model.train_model(entities, labels)
    
    logger.info("Training results:")
    logger.info(f"  - Accuracy: {results['accuracy']:.3f}")
    logger.info(f"  - F1 Score: {results['f1_score']:.3f}")
    logger.info(f"  - CV Mean: {results['cv_mean_score']:.3f} (+/- {results['cv_std_score']:.3f})")
    logger.info(f"  - Training samples: {results['training_samples']}")
    logger.info(f"  - Test samples: {results['test_samples']}")
    
    # Get feature importance
    importance = model.get_feature_importance()
    logger.info("\nTop 10 Feature Importances:")
    sorted_features = sorted(importance.items(), key=lambda x: x[1], reverse=True)[:10]
    for feature, score in sorted_features:
        logger.info(f"  - {feature}: {score:.4f}")
    
    # Save model
    logger.info("\nSaving model...")
    model_path = model.save_model()
    logger.info(f"Model saved to: {model_path}")
    
    # Test prediction
    logger.info("\nTesting prediction on sample entity...")
    test_entity = entities[0]
    prediction = model.predict_risk(test_entity)
    logger.info(f"  - Predicted risk level: {prediction['risk_level']}")
    logger.info(f"  - Confidence: {prediction['confidence']:.3f}")
    logger.info(f"  - Probabilities: {prediction['probabilities']}")
    
    logger.info("\n✅ Initial model training completed successfully!")
    
    return results


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Train initial risk assessment model")
    parser.add_argument(
        "--samples",
        type=int,
        default=1000,
        help="Number of synthetic samples to generate (default: 1000)"
    )
    
    args = parser.parse_args()
    
    train_initial_model(n_samples=args.samples)
