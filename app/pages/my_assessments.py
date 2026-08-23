import streamlit as st
import json
from src.database.database import get_database_url, get_engine, get_session_maker
from src.database.crud import get_assessments_by_user

@st.cache_resource
def get_db_session():
    url = get_database_url()
    if "postgresql://user:password@localhost/dbname" in url:
        url = "sqlite:///:memory:"
    engine = get_engine(url)
    SessionLocal = get_session_maker(engine)
    return SessionLocal()

def render():
    st.title("My Assessments")
    st.markdown("View all your previously saved EMI risk assessments and predictions here.")
    st.markdown("---")

    user_id = st.session_state.get('user_id')
    if not user_id:
        st.warning("You must be logged in to view your assessments.")
        return

    with get_db_session() as db:
        assessments = get_assessments_by_user(db, user_id=user_id, limit=50)

    if not assessments:
        st.info("You haven't saved any assessments yet.")
        return

    for a in assessments:
        with st.expander(f"Assessment on {a.created_at.strftime('%Y-%m-%d %H:%M:%S')} - {a.emi_scenario}"):
            st.markdown(f"**Requested Loan:** ₹ {a.requested_amount:,.2f} for {a.requested_tenure} Months")
            
            # Show prediction results clearly
            st.markdown("### Prediction Results")
            res_col1, res_col2 = st.columns(2)
            with res_col1:
                if a.predicted_eligibility == "Eligible":
                    st.success(f"Eligibility: **{a.predicted_eligibility}**")
                elif a.predicted_eligibility == "High_Risk":
                    st.warning(f"Eligibility: **{a.predicted_eligibility}**")
                else:
                    st.error(f"Eligibility: **{a.predicted_eligibility}**")
                
                if a.prediction_probabilities:
                    try:
                        probs = json.loads(a.prediction_probabilities)
                        for cls_name, prob in probs.items():
                            st.progress(prob, text=f"{cls_name}: {prob:.1%}")
                    except Exception:
                        pass
                        
            with res_col2:
                if a.predicted_max_monthly_emi:
                    st.info(f"Predicted Max Safe EMI: **₹ {a.predicted_max_monthly_emi:,.2f}**")
                else:
                    st.write("Max Safe EMI: Not available")
            
            st.markdown("---")
            st.markdown("### Input Details")
            
            det1, det2, det3 = st.columns(3)
            with det1:
                st.write("**Personal**")
                st.write(f"- Age: {a.age}")
                st.write(f"- Gender: {a.gender}")
                st.write(f"- Marital Status: {a.marital_status}")
                st.write(f"- Dependents: {a.dependents}")
            with det2:
                st.write("**Employment**")
                st.write(f"- Type: {a.employment_type}")
                st.write(f"- Salary: ₹ {a.monthly_salary:,.2f}")
                st.write(f"- Years: {a.years_of_employment}")
            with det3:
                st.write("**Financials**")
                st.write(f"- Credit Score: {a.credit_score}")
                st.write(f"- Existing Loans: {a.existing_loans}")
                st.write(f"- Bank Balance: ₹ {a.bank_balance:,.2f}")
