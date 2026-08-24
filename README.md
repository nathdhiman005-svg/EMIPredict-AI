# EMIPredict AI

EMIPredict AI is a full-stack, machine-learning-powered application designed to intelligently assess loan eligibility and recommend safe maximum Monthly Installment (EMI) limits for borrowers. 

By analyzing a user's demographics, income, financial obligations, and credit profile, EMIPredict AI helps mitigate default risks while offering transparent, data-driven financial recommendations.

---

## 1. Project Overview

**The Problem:** Traditional loan origination often relies on rigid, rule-based systems that fail to holistically analyze a borrower's complete financial burden (e.g., hidden expenses, emergency fund runway, real-time EMI-to-income ratios). 

**The Solution:** EMIPredict AI replaces static heuristics with predictive machine learning models. It features a complete pipeline from raw data ingestion to real-time interactive inference, packaged in a user-friendly web interface.

**Target Audience:** 
- **End Users (Borrowers):** Can input their financial details to receive instant, personalized EMI eligibility feedback and a calculated safe borrowing limit.
- **Administrators (Loan Officers/Data Scientists):** Can manage assessment records, monitor dataset distributions, and track model performance metrics through a secure administrative portal.

---

## 2. Key Features

### User-Facing Functionality
- **Secure Authentication:** User registration, login, and role-based access control (User vs. Admin).
- **Interactive EMI Assessment:** A comprehensive 25-field financial input form providing instant ML predictions for loan eligibility and maximum safe EMI.
- **My Assessments:** A personalized dashboard where users can review their historical financial assessments and predictions.

### Administrative Functionality
- **Data Management (CRUD):** Complete interface to view, create, update, and delete financial assessment records and model performance benchmarks.
- **Data Analysis Dashboard:** Live visualizations of the feature-engineered dataset, target distributions, and summary statistics.
- **Model Performance Tracking:** Monitor classification and regression metrics directly within the UI.
- **MLflow Integration:** Embedded MLflow tracking viewer to analyze experiment runs, model parameters, and training metrics (read-only production view).

---

## 3. System Architecture

EMIPredict AI utilizes a modular, decoupled architecture:

```mermaid
graph TD
    A[Streamlit Frontend] -->|User Input| B(Inference Pipeline)
    A -->|CRUD Operations| C(SQLAlchemy ORM)
    B -->|Load Artifacts| D[(Serialized Models & Preprocessors)]
    C -->|Read/Write| E[(PostgreSQL Database)]
    A -->|Read Tracking| F[(MLflow SQLite DB & mlruns)]
    
    subgraph "Backend Services (src/)"
    B
    C
    end
```

- **Frontend:** Streamlit (`app.py` and `app/pages/`) handles routing, session state, UI rendering, and form validation.
- **Backend/Business Logic:** `src/` modules manage database connections, authentication, and the inference pipeline.
- **Machine Learning Models:** Pre-trained and serialized using `joblib`, loaded dynamically at runtime for inference without requiring continuous retraining.
- **Database:** PostgreSQL (hosted via Neon) stores user credentials, historical assessments, and model performance metrics.
- **Tracking:** A local MLflow instance (`mlflow.db` and `mlruns/`) is deployed alongside the app to provide historical training metadata.

---

## 4. Machine Learning Pipeline

The ML pipeline is cleanly separated into offline development (Notebooks) and online runtime (Inference):

### Offline Development
1. **Data Preprocessing:** Handling missing values, outlier capping, and data type conversions.
2. **Feature Engineering:** Creating powerful derived indicators such as:
   - *Total Monthly Expenses* & *Total Financial Burden*
   - *Income After Expenses*
   - *EMI to Income Ratio*
   - *Emergency Fund Coverage (Months)*
3. **Encoding & Scaling:** Target encoding for high-cardinality categorical variables (e.g., Employment Type, Education) and standardization of numerical features.
4. **Training:** Evaluating multiple algorithms (Logistic Regression, Random Forest, XGBoost) and tuning hyperparameters.
5. **Serialization:** Exporting the final pipelines, encoders, and models to the `models/` directory using `joblib`.

### Online Inference
When a user submits an assessment, the application:
1. Instantiates the `EMIInferencePipeline`.
2. Loads the serialized `preprocessor.pkl`, `target_encoder.pkl`, and the prediction models.
3. Transforms the raw user input into the engineered feature space.
4. Generates and returns the predictions in real-time.

---

## 5. Models

The application relies on two primary production models:

1. **Classification Model (EMI Eligibility)**
   - **Algorithm:** XGBoost Classifier (`models/xgboost_classification_model.pkl`)
   - **Purpose:** Predicts whether the borrower is `Eligible`, `High_Risk`, or `Not_Eligible`.
   
2. **Regression Model (Maximum Safe EMI)**
   - **Algorithm:** Random Forest Regressor (`models/final_regression_model.pkl`)
   - **Purpose:** Predicts the maximum monthly installment amount the borrower can safely afford based on their financial burden.

**Preprocessing Artifacts:**
- `models/preprocessor.pkl`: Handles numerical scaling and basic categorical encoding.
- `models/target_encoder.pkl`: Handles target-based encoding for categorical features.

---

## 6. MLflow Integration

EMIPredict AI utilizes **MLflow** for robust experiment tracking during the offline training phase.

- **Experiments Tracked:** `EMIPredict_Classification`, `EMIPredict_Regression`
- **Tracked Artifacts:** Hyperparameters, classification reports, R² scores, MAE/RMSE, and serialized model binaries.
- **Production Implementation:** The local `mlflow.db` SQLite database and the `mlruns/` artifact directory are bundled with the repository. 
- **UI Integration:** The Streamlit application features a dedicated `MLflow Experiments` page that queries this local tracking database to display historical training metrics and run comparisons to the administrators.

*(Note: The deployed application does not actively run an MLflow tracking server or Model Registry; it utilizes the tracked data in a read-only capacity for transparency).*

---

## 7. Data

The project utilizes data in three distinct phases:

1. **Raw Dataset** (`data/raw/` - *Ignored in Git*): The initial uncleaned financial records.
2. **Cleaned Dataset** (`data/processed/financial_data_cleaned.csv` - *Ignored in Git*): Data post-imputation and outlier handling.
3. **Feature Engineered Dataset** (`data/processed/financial_data_feature_engineered.csv` - *Tracked in Git*): The final dataset containing derived financial indicators. **This specific file is required by the deployed Streamlit application** to render the administrative Data Analysis dashboard.

---

## 8. Database

**Technology:** PostgreSQL (SQLAlchemy ORM)

### Key Entities:
- `users`: Manages authentication credentials (`email`, `password_hash`) and authorization (`role`).
- `financial_assessments`: Stores the complete 25-field financial profile of a borrower along with the ML predictions generated at the time of submission. Enforces a strict `user_id` foreign key constraint.
- `model_performance_records`: Administrative table used to log and track production model metrics (Accuracy, F1, R², RMSE) over time.

---

## 9. Streamlit Application Pages

| Page | Access Level | Purpose |
|------|--------------|---------|
| **Home** | Public | Project landing page and overview. |
| **Auth** | Public | User registration and authentication login. |
| **EMI Assessment** | User | The core ML prediction form for EMI eligibility. |
| **My Assessments** | User | Personal history of saved financial assessments. |
| **Model Performance** | Admin | Track and log production model metrics. |
| **Data Analysis** | Admin | View dataset distributions and summary statistics. |
| **Data Management** | Admin | Full CRUD interface for database records and user assignments. |
| **MLflow Experiments**| Admin | Read-only viewer for MLflow training experiments and metrics. |

---

## 10. Repository Structure

```text
EMIPredict-AI/
├── app.py                      # Streamlit application entry point
├── app/
│   └── pages/                  # Streamlit application pages (auth, analysis, etc.)
├── src/                        # Backend business logic and inference code
│   ├── database/               # SQLAlchemy models, CRUD, and connection logic
│   ├── feature_engineering/    # Feature creation pipelines
│   ├── ml_preparation/         # Data splitting and class weighting
│   ├── model_inference/        # Runtime ML inference pipeline
│   └── preprocessing/          # Data cleaning and imputation
├── models/                     # Serialized production ML models (.pkl)
├── data/
│   └── processed/              # Required data artifacts (feature_engineered.csv)
├── notebooks/                  # Jupyter notebooks for offline ML development
├── mlruns/                     # MLflow experiment tracking artifacts
├── mlflow.db                   # MLflow tracking SQLite database
├── requirements.txt            # Python dependencies
└── .gitignore                  # Git tracking rules
```

---

## 11. Notebooks (ML Lifecycle)

The `notebooks/` directory documents the complete end-to-end Machine Learning lifecycle. These are used strictly for offline development and are not executed by the live application:

- `01_dataset_understanding_and_data_quality.ipynb`: Initial data inspection and profiling.
- `02_data_preprocessing.ipynb`: Handling missing values, outliers, and data types.
- `03_eda.ipynb`: Exploratory Data Analysis and visual feature distributions.
- `04_feature_engineering.ipynb`: Creation of derived financial indicators and encoding.
- `05_ml_preparation_and__model_training.ipynb`: Train/test splitting, hyperparameter tuning, model evaluation, MLflow logging, and final serialization.

---

## 12. Scripts

The `scripts/` directory contains automation and utility scripts that streamline local development and repository management. *(Note: Development scripts are not executed in the deployed runtime environment).*

---

## 13. Technology Stack

| Technology | Purpose |
|------------|---------|
| **Python 3.11** | Core programming language |
| **Streamlit** | Web application framework and UI |
| **PostgreSQL** | Relational database (hosted on Neon) |
| **SQLAlchemy** | Database Object-Relational Mapping (ORM) |
| **Scikit-Learn** | Preprocessing, pipelines, and Regression modeling |
| **XGBoost** | Gradient boosting Classification modeling |
| **MLflow** | Experiment tracking and metric logging |
| **Pandas / NumPy** | Data manipulation and numerical operations |
| **Joblib** | Model serialization and deserialization |

---

## 14. Installation and Local Setup

### Prerequisites
- Python 3.11
- Git (with Git LFS installed)
- A PostgreSQL database instance

### Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone https://github.com/nathdhiman005-svg/EMIPredict-AI.git
   cd EMIPredict-AI
   ```

2. **Pull Large Files (Git LFS):**
   ```bash
   git lfs pull
   ```

3. **Create and activate a virtual environment:**
   ```bash
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # Linux/Mac:
   source .venv/bin/activate
   ```

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Configure Secrets:**
   Create a `.streamlit/secrets.toml` file in the root directory and add your PostgreSQL connection string:
   ```toml
   POSTGRES_URI = "postgresql://user:password@host/dbname"
   ```
   *(Note: Never commit `secrets.toml` to version control).*

6. **Run the application:**
   ```bash
   streamlit run app.py
   ```

---

## 15. Deployment

EMIPredict AI is configured for seamless deployment on **Streamlit Cloud**.

- **Repository:** Connected directly to the GitHub `main` branch.
- **Entry Point:** The "Main file path" must be configured to `app.py`.
- **Environment:** Streamlit Cloud Linux environment running Python 3.11.
- **Secrets:** The `POSTGRES_URI` must be added to the Streamlit Cloud "Secrets" configuration panel.
- **Git LFS:** Streamlit Cloud natively supports Git LFS, which is required to download the serialized `.pkl` models from the `models/` directory during deployment.

---

## 16. Git LFS

This repository utilizes Git Large File Storage (LFS) to manage large binary files that exceed GitHub's standard tracking limits.

The following artifacts require Git LFS:
- Serialized machine learning models (`.pkl`)
- Preprocessing and encoding artifacts
- Historical MLflow model artifacts (`.skops`, `.pkl`)

Ensure Git LFS is installed locally before pulling the repository to prevent downloading pointer files instead of actual binaries.

---

## 17. Current Project Status

EMIPredict AI is a complete, fully functional deployment. 

**Currently Working:**
- End-to-end user authentication and role-based dashboards.
- Real-time loan eligibility and Max EMI predictions.
- Administrative CRUD operations for database records.
- Live dataset monitoring and MLflow tracking visualizations.

### Future Improvements
While EMIPredict AI is fully functional, potential future extensions could include:
- **Active Model Registry:** Transitioning from static `.pkl` files to a live MLflow Model Registry for automated model versioning and seamless A/B testing.
- **Automated Retraining Pipeline:** Implementing Apache Airflow or GitHub Actions to automatically retrain the models when data drift is detected in the `model_performance_records` table.
- **Explainable AI (XAI):** Integrating SHAP (SHapley Additive exPlanations) into the UI to show users exactly *why* their specific loan was approved or denied.

---

## 18. Limitations

- **Stateless MLflow:** The deployed application relies on a bundled SQLite `mlflow.db`. It cannot log *new* training runs from the cloud without a dedicated remote MLflow tracking server.
- **In-Memory Fallback:** If the `POSTGRES_URI` is omitted or invalid, the application defaults to an in-memory SQLite database (`sqlite:///:memory:`). In this mode, user accounts and financial assessments will be lost whenever the server restarts.