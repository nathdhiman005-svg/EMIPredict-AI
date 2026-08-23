import os
import json
import pickle
import pandas as pd
import numpy as np

from src.model_inference.validation import validate_raw_input, validate_final_features

class EMIInferencePipeline:
    def __init__(self, models_dir: str = 'models'):
        self.models_dir = models_dir
        
        # 1. Load Preprocessing Pipeline
        pipeline_path = os.path.join(models_dir, 'fitted_preprocessing_pipeline.pkl')
        if not os.path.exists(pipeline_path):
            raise FileNotFoundError(f"Preprocessing pipeline not found at {pipeline_path}. Please run initialize_preprocessors.py first.")
            
        with open(pipeline_path, 'rb') as f:
            pipeline_state = pickle.load(f)
            self.data_preprocessor = pipeline_state['data_preprocessor']
            self.feature_engineer = pipeline_state['feature_engineer']
            self.ml_preparator = pipeline_state['ml_preparator']

        # 2. Load Models
        import joblib
        
        xgb_model_path = os.path.join(models_dir, 'xgboost_classification_model.pkl')
        rf_model_path = os.path.join(models_dir, 'final_regression_model.pkl')
        
        self.classifier = joblib.load(xgb_model_path)
        self.regressor = joblib.load(rf_model_path)
            
        # 3. Load Metadata
        xgb_meta_path = os.path.join(models_dir, 'xgboost_classification_features.json')
        rf_meta_path = os.path.join(models_dir, 'final_regression_config.json')
        
        with open(xgb_meta_path, 'r') as f:
            self.classification_meta = json.load(f)
            
        with open(rf_meta_path, 'r') as f:
            self.regression_meta = json.load(f)
            
        # The exact 49 feature order required by the classification model
        self.expected_feature_order = self.classification_meta['ordered_feature_names']
        
        # Ensure that regression expects the same number of features (49)
        assert self.regression_meta['n_features'] == 49
        
    def predict(self, raw_data: dict) -> dict:
        """
        Executes the full end-to-end inference pipeline for a single record.
        """
        # 1. Validate raw input
        validate_raw_input(raw_data)
        
        # 2. Convert to DataFrame
        # pd.DataFrame([raw_data]) handles a single dict naturally.
        df_raw = pd.DataFrame([raw_data])
        
        # 3. Preprocessing Flow
        # Phase 2: Data Cleaning and Imputation
        df_clean = self.data_preprocessor.transform(df_raw)
        
        # Phase 4: Feature Engineering
        df_eng = self.feature_engineer.transform(df_clean)
        
        # Phase 5: ML Preparation (Scaling and OHE)
        df_ml = self.ml_preparator.transform(df_eng)
        
        # 4. Feature Ordering & Validation
        # Re-order the DataFrame to match the exact training feature order
        # Missing columns will cause a KeyError, ensuring structural integrity
        try:
            df_final = df_ml[self.expected_feature_order]
        except KeyError as e:
            raise ValueError(f"MLPreparator failed to produce the required columns. Missing: {e}")
            
        # Validate final 49 features
        validate_final_features(df_final.columns.tolist(), self.expected_feature_order)
        
        # 5. Model Inference
        # Classification (XGBoost)
        # XGBoost expects the exact column order, which we've enforced.
        class_pred_encoded = self.classifier.predict(df_final)[0]
        class_proba = self.classifier.predict_proba(df_final)[0]
        
        # Decode the class string based on the metadata class names
        class_names = self.classification_meta['class_names']
        predicted_class_str = class_names[class_pred_encoded]
        
        # Map probabilities to class names
        probabilities = {class_names[i]: float(class_proba[i]) for i in range(len(class_names))}
        
        # Regression (Random Forest Config 6)
        # Return the exact, raw numerical prediction without inventing business rules.
        regression_pred = float(self.regressor.predict(df_final)[0])
        
        # 6. Response Construction
        return {
            "classification": {
                "predicted_class": predicted_class_str,
                "probabilities": probabilities
            },
            "regression": {
                "max_monthly_emi": regression_pred
            }
        }
