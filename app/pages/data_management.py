import streamlit as st
import pandas as pd
from src.database.database import get_database_url, get_engine, get_session_maker, Base
from src.database.crud import (
    create_assessment,
    get_assessments,
    get_assessment_by_id,
    update_assessment,
    delete_assessment,
    create_model_performance,
    get_model_performances,
    get_model_performance_by_id,
    update_model_performance,
    delete_model_performance
)

@st.cache_resource
def get_db_engine():
    url = get_database_url()
    # Safe local validation mechanism without touching a real Postgres instance
    if "postgresql://user:password@localhost/dbname" in url:
        # We only show this warning once per session due to caching
        url = "sqlite:///:memory:"
        
    engine = get_engine(url)
    from src.database.models import FinancialAssessment, ModelPerformance # Import to register the tables
    Base.metadata.create_all(bind=engine)
    return engine

@st.cache_resource
def get_session_factory(_engine):
    return get_session_maker(_engine)

def get_db_session():
    engine = get_db_engine()
    SessionLocal = get_session_factory(engine)
    return SessionLocal()

def render_25_field_form(defaults=None, key_suffix=""):
    """
    Renders the exact 25-field input structure and returns a dictionary of values.
    Accepts an optional defaults dictionary for pre-filling.
    """
    if defaults is None:
        defaults = {}
        
    def get_val(key, default):
        val = defaults.get(key, default)
        if val is None:
            return default
        return val
        
    data = {}
    
    st.subheader("Demographics & Personal Details")
    col1, col2, col3 = st.columns(3)
    with col1:
        data['age'] = st.number_input("Age", min_value=18.0, max_value=100.0, value=float(get_val('age', 30.0)), key=f"age_{key_suffix}")
        data['gender'] = st.selectbox("Gender", options=["M", "F"], index=["M", "F"].index(get_val('gender', "M")), key=f"gen_{key_suffix}")
    with col2:
        opts = ["Single", "Married"]
        data['marital_status'] = st.selectbox("Marital Status", options=opts, index=opts.index(get_val('marital_status', "Single")), key=f"ms_{key_suffix}")
        opts_edu = ['Graduate', 'High School', 'Post Graduate', 'Professional']
        # Fallback to Graduate if old bad data is loaded
        default_edu = get_val('education', 'Graduate')
        if default_edu not in opts_edu: default_edu = 'Graduate'
        data['education'] = st.selectbox("Education", options=opts_edu, index=opts_edu.index(default_edu), key=f"edu_{key_suffix}")
    with col3:
        data['family_size'] = st.number_input("Family Size", min_value=1.0, max_value=20.0, value=float(get_val('family_size', 2.0)), key=f"fs_{key_suffix}")
        data['dependents'] = st.number_input("Dependents", min_value=0.0, max_value=15.0, value=float(get_val('dependents', 0.0)), key=f"dep_{key_suffix}")
        
    st.subheader("Employment & Income")
    col4, col5, col6 = st.columns(3)
    with col4:
        opts_emp = ['Government', 'Private', 'Self-employed']
        default_emp = get_val('employment_type', 'Private')
        if default_emp not in opts_emp: default_emp = 'Private'
        data['employment_type'] = st.selectbox("Employment Type", options=opts_emp, index=opts_emp.index(default_emp), key=f"empt_{key_suffix}")
        data['monthly_salary'] = st.number_input("Monthly Salary (₹)", min_value=0.0, value=float(get_val('monthly_salary', 50000.0)), step=1000.0, key=f"msal_{key_suffix}")
    with col5:
        opts_comp = ['Large Indian', 'MNC', 'Mid-size', 'Small', 'Startup']
        default_comp = get_val('company_type', 'Mid-size')
        if default_comp not in opts_comp: default_comp = 'Mid-size'
        data['company_type'] = st.selectbox("Company Type", options=opts_comp, index=opts_comp.index(default_comp), key=f"comp_{key_suffix}")
        data['years_of_employment'] = st.number_input("Years of Employment", min_value=0.0, max_value=50.0, value=float(get_val('years_of_employment', 5.0)), step=1.0, key=f"yoe_{key_suffix}")
    with col6:
        opts_house = ['Family', 'Own', 'Rented']
        default_house = get_val('house_type', 'Rented')
        if default_house not in opts_house: default_house = 'Rented'
        data['house_type'] = st.selectbox("House Type", options=opts_house, index=opts_house.index(default_house), key=f"ht_{key_suffix}")
        
    st.subheader("Monthly Expenses & Obligations")
    col7, col8, col9 = st.columns(3)
    with col7:
        data['monthly_rent'] = st.number_input("Monthly Rent (₹)", min_value=0.0, value=float(get_val('monthly_rent', 10000.0)), step=1000.0, key=f"mrent_{key_suffix}")
        data['school_fees'] = st.number_input("School Fees (₹)", min_value=0.0, value=float(get_val('school_fees', 0.0)), step=1000.0, key=f"sf_{key_suffix}")
        data['college_fees'] = st.number_input("College Fees (₹)", min_value=0.0, value=float(get_val('college_fees', 0.0)), step=1000.0, key=f"cf_{key_suffix}")
    with col8:
        data['travel_expenses'] = st.number_input("Travel Expenses (₹)", min_value=0.0, value=float(get_val('travel_expenses', 3000.0)), step=500.0, key=f"te_{key_suffix}")
        data['groceries_utilities'] = st.number_input("Groceries & Utilities (₹)", min_value=0.0, value=float(get_val('groceries_utilities', 8000.0)), step=1000.0, key=f"gu_{key_suffix}")
        data['other_monthly_expenses'] = st.number_input("Other Monthly Expenses (₹)", min_value=0.0, value=float(get_val('other_monthly_expenses', 2000.0)), step=500.0, key=f"ome_{key_suffix}")
    with col9:
        opts_loan = ["No", "Yes"]
        data['existing_loans'] = st.selectbox("Existing Loans", options=opts_loan, index=opts_loan.index(get_val('existing_loans', 'No')), key=f"el_{key_suffix}")
        data['current_emi_amount'] = st.number_input("Current EMI Amount (₹)", min_value=0.0, value=float(get_val('current_emi_amount', 0.0)), step=1000.0, key=f"cea_{key_suffix}")
        
    st.subheader("Financial Assets & Credit Profile")
    col10, col11, col12 = st.columns(3)
    with col10:
        data['credit_score'] = st.number_input("Credit Score", min_value=300.0, max_value=900.0, value=float(get_val('credit_score', 750.0)), key=f"cs_{key_suffix}")
    with col11:
        data['bank_balance'] = st.number_input("Bank Balance (₹)", min_value=0.0, value=float(get_val('bank_balance', 100000.0)), step=10000.0, key=f"bb_{key_suffix}")
    with col12:
        data['emergency_fund'] = st.number_input("Emergency Fund (₹)", min_value=0.0, value=float(get_val('emergency_fund', 50000.0)), step=5000.0, key=f"ef_{key_suffix}")
        
    st.subheader("Requested Loan Scenario")
    col13, col14, col15 = st.columns(3)
    with col13:
        opts_emi = ['E-commerce Shopping EMI', 'Education EMI', 'Home Appliances EMI', 'Personal Loan EMI', 'Vehicle EMI']
        default_emi = get_val('emi_scenario', 'Personal Loan EMI')
        if default_emi not in opts_emi: default_emi = 'Personal Loan EMI'
        data['emi_scenario'] = st.selectbox("EMI Scenario", options=opts_emi, index=opts_emi.index(default_emi), key=f"esc_{key_suffix}")
    with col14:
        data['requested_amount'] = st.number_input("Requested Loan Amount (₹)", min_value=0.0, value=float(get_val('requested_amount', 50000.0)), step=5000.0, key=f"ra_{key_suffix}")
    with col15:
        data['requested_tenure'] = st.number_input("Requested Tenure (Months)", min_value=1.0, max_value=360.0, value=float(get_val('requested_tenure', 12.0)), step=1.0, key=f"rt_{key_suffix}")

    # Optional Predictions Data
    st.subheader("Predictions (Optional)")
    pcol1, pcol2 = st.columns(2)
    with pcol1:
        opts_pred = ["", "Eligible", "High_Risk", "Not_Eligible"]
        default_pred = get_val('predicted_eligibility', "")
        if default_pred not in opts_pred: default_pred = ""
        predicted_eligibility = st.selectbox("Predicted Eligibility", options=opts_pred, index=opts_pred.index(default_pred), key=f"pe_{key_suffix}")
        if predicted_eligibility:
            data['predicted_eligibility'] = predicted_eligibility
    with pcol2:
        predicted_max_emi = st.number_input("Predicted Max EMI (₹)", value=float(get_val('predicted_max_monthly_emi', 0.0)), step=1000.0, key=f"pme_{key_suffix}")
        if predicted_max_emi > 0:
            data['predicted_max_monthly_emi'] = predicted_max_emi
            
    return data


    return data


def render_model_performance_form(defaults=None, key_suffix=""):
    """
    Renders the form for ModelPerformance records.
    """
    if defaults is None:
        defaults = {}
        
    def get_val(key, default):
        val = defaults.get(key, default)
        if val is None:
            return default
        return val
        
    data = {}
    
    st.subheader("Model Information")
    col1, col2 = st.columns(2)
    with col1:
        data['model_name'] = st.text_input("Model Name", value=get_val('model_name', ""), key=f"mp_name_{key_suffix}")
        opts_pt = ["Classification", "Regression"]
        data['problem_type'] = st.selectbox("Problem Type", options=opts_pt, index=opts_pt.index(get_val('problem_type', "Classification")), key=f"mp_pt_{key_suffix}")
    with col2:
        data['purpose'] = st.text_input("Purpose", value=get_val('purpose', ""), key=f"mp_purp_{key_suffix}")
        opts_status = ["Active", "Development", "Archived"]
        data['status'] = st.selectbox("Status", options=opts_status, index=opts_status.index(get_val('status', "Active")), key=f"mp_stat_{key_suffix}")
        
    if data['problem_type'] == "Classification":
        st.subheader("Classification Metrics")
        ccol1, ccol2, ccol3 = st.columns(3)
        with ccol1:
            data['accuracy'] = st.number_input("Accuracy", min_value=0.0, max_value=1.0, value=float(get_val('accuracy', 0.0) or 0.0), step=0.01, format="%.4f", key=f"mp_acc_{key_suffix}")
            data['precision'] = st.number_input("Macro Precision", min_value=0.0, max_value=1.0, value=float(get_val('precision', 0.0) or 0.0), step=0.01, format="%.4f", key=f"mp_pre_{key_suffix}")
        with ccol2:
            data['recall'] = st.number_input("Macro Recall", min_value=0.0, max_value=1.0, value=float(get_val('recall', 0.0) or 0.0), step=0.01, format="%.4f", key=f"mp_rec_{key_suffix}")
            data['f1_score'] = st.number_input("Macro F1", min_value=0.0, max_value=1.0, value=float(get_val('f1_score', 0.0) or 0.0), step=0.01, format="%.4f", key=f"mp_f1_{key_suffix}")
        with ccol3:
            data['roc_auc'] = st.number_input("Macro ROC-AUC", min_value=0.0, max_value=1.0, value=float(get_val('roc_auc', 0.0) or 0.0), step=0.01, format="%.4f", key=f"mp_roc_{key_suffix}")
            
    else:
        st.subheader("Regression Metrics")
        rcol1, rcol2 = st.columns(2)
        with rcol1:
            data['r2_score'] = st.number_input("R² Score", value=float(get_val('r2_score', 0.0) or 0.0), step=0.01, format="%.4f", key=f"mp_r2_{key_suffix}")
            data['mae'] = st.number_input("MAE", min_value=0.0, value=float(get_val('mae', 0.0) or 0.0), step=1.0, format="%.2f", key=f"mp_mae_{key_suffix}")
        with rcol2:
            data['rmse'] = st.number_input("RMSE", min_value=0.0, value=float(get_val('rmse', 0.0) or 0.0), step=1.0, format="%.2f", key=f"mp_rmse_{key_suffix}")
            data['mape'] = st.number_input("MAPE", min_value=0.0, value=float(get_val('mape', 0.0) or 0.0), step=0.1, format="%.2f", key=f"mp_mape_{key_suffix}")
            
    return data


def render():
    st.title("Data Management")
    st.markdown("Manage persistent financial assessment records safely via PostgreSQL.")
    
    url = get_database_url()
    if "postgresql://user:password@localhost/dbname" in url:
        st.warning("⚠️ Warning: Using safe in-memory SQLite configuration for local validation since no PostgreSQL connection was provided.")
        
    management_type = st.radio("Select Domain to Manage", ["Financial Assessments", "Model Performance Records"], horizontal=True)
    st.markdown("---")

    if management_type == "Financial Assessments":
        tabs = st.tabs(["View All Records", "Create New Record", "Update / Delete"])
        
        # ---------------------------
        # Tab 1: View All Records
        # ---------------------------
        with tabs[0]:
            st.subheader("Saved Records")
            with get_db_session() as db:
                assessments = get_assessments(db, limit=1000)
                if assessments:
                    data_list = []
                    for a in assessments:
                        a_dict = {c.name: getattr(a, c.name) for c in a.__table__.columns}
                        data_list.append(a_dict)
                    df = pd.DataFrame(data_list)
                    # Reorder to show important columns first
                    cols = ['id', 'created_at', 'predicted_eligibility', 'predicted_max_monthly_emi'] + [c for c in df.columns if c not in ['id', 'created_at', 'predicted_eligibility', 'predicted_max_monthly_emi', 'updated_at']]
                    df = df[cols]
                    st.dataframe(df, use_container_width=True)
                else:
                    st.info("No records found in the database.")
                    
        # ---------------------------
        # Tab 2: Create New Record
        # ---------------------------
        with tabs[1]:
            st.subheader("Create a New Financial Assessment Record")
            
            # Fetch users to allow assignment
            with get_db_session() as db:
                from src.database.models import User
                users = db.query(User).all()
                
            if users:
                user_options = {u.email: u.id for u in users}
                with st.form("create_record_form"):
                    selected_email = st.selectbox("Assign to User (Email)", options=list(user_options.keys()))
                    new_data = render_25_field_form(key_suffix="create")
                    submit_create = st.form_submit_button("Save Record")
                    
                if submit_create:
                    new_data['user_id'] = user_options[selected_email]
                    with get_db_session() as db:
                        try:
                            created = create_assessment(db, new_data)
                            st.success(f"Successfully created record with ID {created.id}.")
                        except Exception as e:
                            st.error(f"Error creating record: {e}")
            else:
                st.warning("No users available in the system. Please register a user first to assign an assessment.")

        # ---------------------------
        # Tab 3: Update / Delete
        # ---------------------------
        with tabs[2]:
            st.subheader("Manage Existing Records")
            search_id = st.number_input("Enter Record ID to Manage", min_value=1, step=1, key="search_id")
            search_btn = st.button("Load Record")
            
            if search_btn or 'loaded_record' in st.session_state:
                if search_btn:
                    with get_db_session() as db:
                        record = get_assessment_by_id(db, search_id)
                        if record:
                            st.session_state.loaded_record = {c.name: getattr(record, c.name) for c in record.__table__.columns}
                        else:
                            if 'loaded_record' in st.session_state:
                                del st.session_state.loaded_record
                            st.error(f"Record with ID {search_id} not found.")
                
                if 'loaded_record' in st.session_state:
                    record_data = st.session_state.loaded_record
                    st.write(f"**Editing Record ID:** {record_data['id']}")
                    st.write(f"**Created At:** {record_data['created_at']}")
                    
                    with st.form("update_record_form"):
                        updated_data = render_25_field_form(defaults=record_data, key_suffix="update")
                        
                        update_col, delete_col = st.columns(2)
                        with update_col:
                            submit_update = st.form_submit_button("Update Record", type="primary")
                        with delete_col:
                            submit_delete = st.form_submit_button("Delete Record")
                            
                    if submit_update:
                        with get_db_session() as db:
                            try:
                                update_assessment(db, record_data['id'], updated_data)
                                st.success(f"Record {record_data['id']} updated successfully.")
                                # Clear state so it triggers reload next time
                                del st.session_state.loaded_record
                            except Exception as e:
                                st.error(f"Error updating record: {e}")
                                
                    if submit_delete:
                        with get_db_session() as db:
                            try:
                                delete_assessment(db, record_data['id'])
                                st.success(f"Record {record_data['id']} deleted successfully.")
                                del st.session_state.loaded_record
                            except Exception as e:
                                st.error(f"Error deleting record: {e}")

    else:
        # Model Performance Records Management
        mp_tabs = st.tabs(["View All Models", "Add Model Performance", "Update / Delete Model"])

        with mp_tabs[0]:
            st.subheader("Model Performance Records")
            with get_db_session() as db:
                performances = get_model_performances(db, limit=100)
                if performances:
                    data_list = []
                    for p in performances:
                        p_dict = {c.name: getattr(p, c.name) for c in p.__table__.columns}
                        data_list.append(p_dict)
                    df = pd.DataFrame(data_list)
                    cols = ['id', 'model_name', 'problem_type', 'status', 'created_at'] + [c for c in df.columns if c not in ['id', 'model_name', 'problem_type', 'status', 'created_at']]
                    df = df[cols]
                    st.dataframe(df, use_container_width=True)
                else:
                    st.info("No model performance records found.")

        with mp_tabs[1]:
            st.subheader("Add Model Performance Record")
            with st.form("create_mp_form"):
                new_mp_data = render_model_performance_form(key_suffix="create_mp")
                submit_mp_create = st.form_submit_button("Save Record")

            if submit_mp_create:
                if not new_mp_data['model_name'] or not new_mp_data['purpose']:
                    st.error("Model Name and Purpose are required.")
                else:
                    with get_db_session() as db:
                        try:
                            created = create_model_performance(db, new_mp_data)
                            st.success(f"Successfully created record with ID {created.id}.")
                        except Exception as e:
                            st.error(f"Error creating record: {e}")

        with mp_tabs[2]:
            st.subheader("Manage Existing Model Records")
            search_mp_id = st.number_input("Enter Model Record ID to Manage", min_value=1, step=1, key="search_mp_id")
            search_mp_btn = st.button("Load Model Record")

            if search_mp_btn or 'loaded_mp_record' in st.session_state:
                if search_mp_btn:
                    with get_db_session() as db:
                        record = get_model_performance_by_id(db, search_mp_id)
                        if record:
                            st.session_state.loaded_mp_record = {c.name: getattr(record, c.name) for c in record.__table__.columns}
                        else:
                            if 'loaded_mp_record' in st.session_state:
                                del st.session_state.loaded_mp_record
                            st.error(f"Record with ID {search_mp_id} not found.")

                if 'loaded_mp_record' in st.session_state:
                    mp_data = st.session_state.loaded_mp_record
                    st.write(f"**Editing Record ID:** {mp_data['id']} ({mp_data['model_name']})")

                    with st.form("update_mp_form"):
                        updated_mp_data = render_model_performance_form(defaults=mp_data, key_suffix="update_mp")

                        update_mp_col, delete_mp_col = st.columns(2)
                        with update_mp_col:
                            submit_mp_update = st.form_submit_button("Update Record", type="primary")
                        with delete_mp_col:
                            submit_mp_delete = st.form_submit_button("Delete Record")

                    if submit_mp_update:
                        with get_db_session() as db:
                            try:
                                update_model_performance(db, mp_data['id'], updated_mp_data)
                                st.success(f"Record {mp_data['id']} updated successfully.")
                                del st.session_state.loaded_mp_record
                            except Exception as e:
                                st.error(f"Error updating record: {e}")

                    if submit_mp_delete:
                        with get_db_session() as db:
                            try:
                                delete_model_performance(db, mp_data['id'])
                                st.success(f"Record {mp_data['id']} deleted successfully.")
                                del st.session_state.loaded_mp_record
                            except Exception as e:
                                st.error(f"Error deleting record: {e}")
