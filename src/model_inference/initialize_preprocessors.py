import os
import pickle
import pandas as pd
from src.ml_preparation.data_splitter import prepare_data_splits
from src.preprocessing.pipeline import DataPreprocessor
from src.feature_engineering.pipeline import FeatureEngineer
from src.ml_preparation.pipeline import MLPreparator

def initialize_and_save_preprocessors():
    print("--- Preprocessing State Initialization ---")
    
    # 1. Load the raw dataset
    raw_data_path = 'data/raw/financial_data.csv'
    if not os.path.exists(raw_data_path):
        raise FileNotFoundError(f"Cannot find {raw_data_path}. Ensure you are in the project root.")
    
    print("Loading raw dataset...")
    df_raw = pd.read_csv(raw_data_path)
    print(f"Loaded {len(df_raw)} raw rows.")

    # 2. Reproduce the exact Phase 5 training split logic
    print("Applying Phase 5 splitting logic to isolate training data...")
    splits = prepare_data_splits(df_raw)
    X_c_train, X_c_val, X_c_test, y_c_train, y_c_val, y_c_test = splits['classification']
    print(f"Isolated {len(X_c_train)} training rows.")

    # 3. Fit DataPreprocessor ONLY on the training data
    print("\nFitting DataPreprocessor on training data...")
    data_preprocessor = DataPreprocessor()
    data_preprocessor.fit(X_c_train)
    
    # Transform training data to feed into the next stage
    X_train_clean = data_preprocessor.transform(X_c_train)
    print("DataPreprocessor fit successfully.")

    # 4. Apply Feature Engineer (Stateless)
    print("\nApplying FeatureEngineer to training data...")
    feature_engineer = FeatureEngineer()
    X_train_eng = feature_engineer.transform(X_train_clean)
    print("Feature engineering applied successfully.")

    # 5. Fit MLPreparator ONLY on the appropriate training data
    print("\nFitting MLPreparator on feature-engineered training data...")
    ml_preparator = MLPreparator()
    ml_preparator.fit(X_train_eng)
    print("MLPreparator fit successfully.")

    # 6. Save only the fitted preprocessing state required for inference
    print("\nSaving fitted preprocessors...")
    model_dir = "models"
    os.makedirs(model_dir, exist_ok=True)
    
    pipeline_state = {
        'data_preprocessor': data_preprocessor,
        'feature_engineer': feature_engineer,  # Stateless, but saved for convenience
        'ml_preparator': ml_preparator
    }
    
    output_path = os.path.join(model_dir, "fitted_preprocessing_pipeline.pkl")
    with open(output_path, 'wb') as f:
        pickle.dump(pipeline_state, f)
        
    print(f"Successfully saved fitted preprocessing state to: {output_path}")
    print("Note: The training dataset was NOT stored in this pickle.")

if __name__ == "__main__":
    initialize_and_save_preprocessors()
