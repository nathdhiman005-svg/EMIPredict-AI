import streamlit as st
import pandas as pd
from src.database.database import get_database_url, get_engine, get_session_maker
from src.database.crud import get_model_performances

@st.cache_resource
def get_db_session():
    url = get_database_url()
    if "postgresql://user:password@localhost/dbname" in url:
        url = "sqlite:///:memory:"
    engine = get_engine(url)
    SessionLocal = get_session_maker(engine)
    return SessionLocal()

def render():
    st.title("Model Performance & Metrics")
    st.markdown("Overview of the models for EMIPredict AI based on validation and testing.")
    st.markdown("---")

    with get_db_session() as db:
        performances = get_model_performances(db, limit=50)

    if not performances:
        st.info("No model performance records available.")
        return

    # Split models by problem type
    classification_models = [p for p in performances if p.problem_type == "Classification" and p.status != "Archived"]
    regression_models = [p for p in performances if p.problem_type == "Regression" and p.status != "Archived"]

    col1, col2 = st.columns(2)

    with col1:
        st.header("Classification")
        if not classification_models:
            st.info("No active classification models found.")
        for p in classification_models:
            with st.container(border=True):
                st.subheader(f"{p.model_name}")
                st.markdown(f"**Purpose:** {p.purpose}")
                st.markdown(f"**Status:** `{p.status}`")
                
                st.markdown("**Test Metrics:**")
                if p.accuracy is not None:
                    st.metric(label="Accuracy", value=f"{p.accuracy:.4f}")
                
                m_col1, m_col2 = st.columns(2)
                with m_col1:
                    if p.precision is not None:
                        st.metric(label="Macro Precision", value=f"{p.precision:.4f}")
                    if p.recall is not None:
                        st.metric(label="Macro Recall", value=f"{p.recall:.4f}")
                with m_col2:
                    if p.f1_score is not None:
                        st.metric(label="Macro F1", value=f"{p.f1_score:.4f}")
                    if p.roc_auc is not None:
                        st.metric(label="Macro ROC-AUC", value=f"{p.roc_auc:.4f}")


    with col2:
        st.header("Regression")
        if not regression_models:
            st.info("No active regression models found.")
        for p in regression_models:
            with st.container(border=True):
                st.subheader(f"{p.model_name}")
                st.markdown(f"**Purpose:** {p.purpose}")
                st.markdown(f"**Status:** `{p.status}`")
                
                st.markdown("**Test Metrics:**")
                if p.r2_score is not None:
                    st.metric(label="R² Score", value=f"{p.r2_score:.4f}")
                
                m_col3, m_col4 = st.columns(2)
                with m_col3:
                    if p.mae is not None:
                        st.metric(label="MAE", value=f"{p.mae:.2f}")
                    if p.rmse is not None:
                        st.metric(label="RMSE", value=f"{p.rmse:.2f}")
                with m_col4:
                    if p.mape is not None:
                        st.metric(label="MAPE", value=f"{p.mape:.2f}%")

