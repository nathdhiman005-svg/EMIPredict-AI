import streamlit as st
from src.model_inference.inference import EMIInferencePipeline
import json
from src.database.database import get_database_url, get_engine, get_session_maker
from src.database.crud import create_assessment

@st.cache_resource
def get_db_session():
    url = get_database_url()
    if "postgresql://user:password@localhost/dbname" in url:
        url = "sqlite:///:memory:"
    engine = get_engine(url)
    SessionLocal = get_session_maker(engine)
    return SessionLocal()

def render():
    st.title("EMI Assessment")
    st.markdown("Enter the customer's financial and demographic details to assess EMI eligibility and predict the maximum safe monthly EMI.")
    
    # Initialize pipeline in session state to avoid reloading on every rerun
    if 'pipeline' not in st.session_state:
        try:
            with st.spinner("Loading ML models and pipelines..."):
                st.session_state.pipeline = EMIInferencePipeline(models_dir='models')
        except Exception as e:
            st.error(f"Failed to load the inference pipeline: {e}")
            return
            
    pipeline = st.session_state.pipeline
    
    # Form for the 25 input fields
    with st.form("prediction_form"):
        st.subheader("Demographics & Personal Details")
        col1, col2, col3 = st.columns(3)
        with col1:
            age = st.number_input("Age", min_value=18, max_value=100, value=30)
            gender = st.selectbox("Gender", options=["M", "F"])
        with col2:
            marital_status = st.selectbox("Marital Status", options=["Single", "Married"])
            education = st.selectbox("Education", options=['Graduate', 'High School', 'Post Graduate', 'Professional'])
        with col3:
            family_size = st.number_input("Family Size", min_value=1, max_value=20, value=2)
            dependents = st.number_input("Dependents", min_value=0, max_value=15, value=0)
            
        st.subheader("Employment & Income")
        col4, col5, col6 = st.columns(3)
        with col4:
            employment_type = st.selectbox("Employment Type", options=['Government', 'Private', 'Self-employed'])
            monthly_salary = st.number_input("Monthly Salary (₹)", min_value=0.0, value=50000.0, step=1000.0)
        with col5:
            company_type = st.selectbox("Company Type", options=['Large Indian', 'MNC', 'Mid-size', 'Small', 'Startup'])
            years_of_employment = st.number_input("Years of Employment", min_value=0.0, max_value=50.0, value=5.0, step=1.0)
        with col6:
            house_type = st.selectbox("House Type", options=['Family', 'Own', 'Rented'])
            
        st.subheader("Monthly Expenses & Obligations")
        col7, col8, col9 = st.columns(3)
        with col7:
            monthly_rent = st.number_input("Monthly Rent (₹)", min_value=0.0, value=10000.0, step=1000.0)
            school_fees = st.number_input("School Fees (₹)", min_value=0.0, value=0.0, step=1000.0)
            college_fees = st.number_input("College Fees (₹)", min_value=0.0, value=0.0, step=1000.0)
        with col8:
            travel_expenses = st.number_input("Travel Expenses (₹)", min_value=0.0, value=3000.0, step=500.0)
            groceries_utilities = st.number_input("Groceries & Utilities (₹)", min_value=0.0, value=8000.0, step=1000.0)
            other_monthly_expenses = st.number_input("Other Monthly Expenses (₹)", min_value=0.0, value=2000.0, step=500.0)
        with col9:
            existing_loans = st.selectbox("Existing Loans", options=["No", "Yes"])
            current_emi_amount = st.number_input("Current EMI Amount (₹)", min_value=0.0, value=0.0, step=1000.0)
            
        st.subheader("Financial Assets & Credit Profile")
        col10, col11, col12 = st.columns(3)
        with col10:
            credit_score = st.number_input("Credit Score", min_value=300, max_value=900, value=750)
        with col11:
            bank_balance = st.number_input("Bank Balance (₹)", min_value=0.0, value=100000.0, step=10000.0)
        with col12:
            emergency_fund = st.number_input("Emergency Fund (₹)", min_value=0.0, value=50000.0, step=5000.0)
            
        st.subheader("Requested Loan Scenario")
        col13, col14, col15 = st.columns(3)
        with col13:
            emi_scenario = st.selectbox("EMI Scenario", options=['E-commerce Shopping EMI', 'Education EMI', 'Home Appliances EMI', 'Personal Loan EMI', 'Vehicle EMI'])
        with col14:
            requested_amount = st.number_input("Requested Loan Amount (₹)", min_value=0.0, value=50000.0, step=5000.0)
        with col15:
            requested_tenure = st.number_input("Requested Tenure (Months)", min_value=1, max_value=360, value=12, step=1)
            
        submit_button = st.form_submit_button("Assess Risk & Predict Maximum EMI")

    if submit_button:
        # Build the raw input dictionary
        raw_data = {
            'age': float(age),
            'gender': gender,
            'marital_status': marital_status,
            'education': education,
            'monthly_salary': float(monthly_salary),
            'employment_type': employment_type,
            'years_of_employment': float(years_of_employment),
            'company_type': company_type,
            'house_type': house_type,
            'monthly_rent': float(monthly_rent),
            'family_size': float(family_size),
            'dependents': float(dependents),
            'school_fees': float(school_fees),
            'college_fees': float(college_fees),
            'travel_expenses': float(travel_expenses),
            'groceries_utilities': float(groceries_utilities),
            'other_monthly_expenses': float(other_monthly_expenses),
            'existing_loans': existing_loans,
            'current_emi_amount': float(current_emi_amount),
            'credit_score': float(credit_score),
            'bank_balance': float(bank_balance),
            'emergency_fund': float(emergency_fund),
            'emi_scenario': emi_scenario,
            'requested_amount': float(requested_amount),
            'requested_tenure': float(requested_tenure)
        }
        
        with st.spinner("Processing prediction..."):
            try:
                result = pipeline.predict(raw_data)
                
                # Clearly separate classification and regression
                st.markdown("---")
                st.header("Prediction Results")
                
                res_col1, res_col2 = st.columns(2)
                
                with res_col1:
                    st.subheader("Classification: EMI Eligibility")
                    predicted_class = result["classification"]["predicted_class"]
                    
                    if predicted_class == "Eligible":
                        st.success(f"**{predicted_class}**")
                    elif predicted_class == "High_Risk":
                        st.warning(f"**{predicted_class}**")
                    else:
                        st.error(f"**{predicted_class}**")
                        
                    st.write("Confidence/Probabilities:")
                    for cls_name, prob in result["classification"]["probabilities"].items():
                        st.progress(prob, text=f"{cls_name}: {prob:.1%}")
                
                with res_col2:
                    st.subheader("Regression: Max Monthly EMI")
                    max_emi = result["regression"]["max_monthly_emi"]
                    st.info(f"**Predicted Maximum Safe EMI:** ₹ {max_emi:,.2f}")
                    
                # Save to session state for the Save Assessment button
                st.session_state.pending_assessment = {
                    **raw_data,
                    "predicted_eligibility": predicted_class,
                    "prediction_probabilities": json.dumps(result["classification"]["probabilities"]),
                    "predicted_max_monthly_emi": float(max_emi)
                }
                
            except Exception as e:
                st.error(f"An error occurred during prediction:\n\n{str(e)}")

    if 'pending_assessment' in st.session_state:
        st.markdown("---")
        st.subheader("Save Assessment")
        st.write("You can save this prediction securely to your account.")
        if st.button("Save Assessment", type="primary"):
            user_id = st.session_state.get('user_id')
            if not user_id:
                st.error("You must be logged in to save an assessment.")
            else:
                data_to_save = st.session_state.pending_assessment
                data_to_save['user_id'] = user_id
                with get_db_session() as db:
                    try:
                        create_assessment(db, data_to_save)
                        st.success("Assessment saved successfully! View it in 'My Assessments'.")
                        del st.session_state.pending_assessment
                    except Exception as e:
                        st.error(f"Error saving assessment: {e}")
