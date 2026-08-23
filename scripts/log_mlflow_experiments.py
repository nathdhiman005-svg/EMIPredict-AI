import os
import joblib
import mlflow
import mlflow.xgboost
import mlflow.sklearn
import numpy as np

def get_or_create_experiment(experiment_name):
    """Get experiment ID if it exists, otherwise create it."""
    experiment = mlflow.get_experiment_by_name(experiment_name)
    if experiment is None:
        return mlflow.create_experiment(experiment_name)
    return experiment.experiment_id

def clean_params(params):
    """Remove None and NaN values from params dictionary to avoid MLflow logging errors."""
    clean = {}
    for k, v in params.items():
        if v is not None:
            if isinstance(v, float) and np.isnan(v):
                continue
            clean[k] = v
    return clean

def log_classification_model():
    exp_name = "EMIPredict_Classification"
    run_name = "Baseline_XGBoost_Production"
    
    experiment_id = get_or_create_experiment(exp_name)
    mlflow.set_experiment(experiment_id=experiment_id)
    
    # Check if run already exists to avoid duplicates
    runs = mlflow.search_runs(experiment_ids=[experiment_id], filter_string=f"tags.mlflow.runName = '{run_name}'")
    if len(runs) > 0:
        print(f"Run '{run_name}' already exists in experiment '{exp_name}'. Skipping to avoid duplicates.")
        return
        
    print(f"Logging run: {run_name}")
    with mlflow.start_run(run_name=run_name):
        # 1. Load Model
        model_path = os.path.join("models", "xgboost_classification_model.pkl")
        model = joblib.load(model_path)
        
        # 2. Log Params
        params = clean_params(model.get_params())
        mlflow.log_params(params)
        
        # 3. Log Metrics
        metrics = {
            "accuracy": 0.9293,
            "precision": 0.7861,
            "recall": 0.9228,
            "f1_score": 0.8144,
            "roc_auc": 0.9903
        }
        mlflow.log_metrics(metrics)
        
        # 4. Log Tags
        mlflow.set_tags({
            "model_role": "production",
            "task": "classification",
            "model_name": "Baseline XGBoost Classifier"
        })
        
        # 5. Log Model
        mlflow.xgboost.log_model(model, "model")
        
        # 6. Log Artifacts
        mlflow.log_artifact(os.path.join("models", "fitted_preprocessing_pipeline.pkl"), artifact_path="preprocessors")
        mlflow.log_artifact(os.path.join("models", "xgboost_classification_features.json"), artifact_path="configs")

def log_regression_model():
    exp_name = "EMIPredict_Regression"
    run_name = "Random_Forest_Config6_Production"
    
    experiment_id = get_or_create_experiment(exp_name)
    mlflow.set_experiment(experiment_id=experiment_id)
    
    # Check if run already exists
    runs = mlflow.search_runs(experiment_ids=[experiment_id], filter_string=f"tags.mlflow.runName = '{run_name}'")
    if len(runs) > 0:
        print(f"Run '{run_name}' already exists in experiment '{exp_name}'. Skipping to avoid duplicates.")
        return
        
    print(f"Logging run: {run_name}")
    with mlflow.start_run(run_name=run_name):
        # 1. Load Model
        model_path = os.path.join("models", "final_regression_model.pkl")
        model = joblib.load(model_path)
        
        # 2. Log Params
        params = clean_params(model.get_params())
        mlflow.log_params(params)
        
        # 3. Log Metrics
        metrics = {
            "r2_score": 0.9877,
            "mae": 237.89,
            "rmse": 854.63,
            "mape": 4.78
        }
        mlflow.log_metrics(metrics)
        
        # 4. Log Tags
        mlflow.set_tags({
            "model_role": "production",
            "task": "regression",
            "model_name": "Tuned Random Forest Regressor",
            "configuration": "Config 6"
        })
        
        # 5. Log Model
        mlflow.sklearn.log_model(model, "model")
        
        # 6. Log Artifacts
        mlflow.log_artifact(os.path.join("models", "fitted_preprocessing_pipeline.pkl"), artifact_path="preprocessors")
        mlflow.log_artifact(os.path.join("models", "final_regression_config.json"), artifact_path="configs")

if __name__ == "__main__":
    print("Starting MLflow experiment tracking...")
    log_classification_model()
    log_regression_model()
    print("MLflow tracking complete.")
