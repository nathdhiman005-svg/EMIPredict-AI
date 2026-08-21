import pandas as pd
from sklearn.utils.class_weight import compute_class_weight
import numpy as np

def compute_class_weights(y_train: pd.Series) -> dict:
    """
    Computes class weights for a given training set to handle class imbalance
    during classification model training.
    
    Returns:
        dict: A dictionary mapping class labels to their computed weights.
    """
    classes = np.unique(y_train)
    weights = compute_class_weight('balanced', classes=classes, y=y_train)
    return dict(zip(classes, weights))
