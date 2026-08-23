import streamlit as st
import importlib.util
import sys
import os

# Dynamically load pages to avoid namespace collision between app.py and app/ directory
def load_page(module_name, file_name):
    spec = importlib.util.spec_from_file_location(module_name, os.path.join("app", "pages", file_name))
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

auth = load_page("auth", "auth.py")
emi_assessment = load_page("emi_assessment", "emi_assessment.py")
home = load_page("home", "home.py")
my_assessments = load_page("my_assessments", "my_assessments.py")
model_performance = load_page("model_performance", "model_performance.py")
data_analysis = load_page("data_analysis", "data_analysis.py")
data_management = load_page("data_management", "data_management.py")

def main():
    st.set_page_config(page_title="EMIPredict AI", page_icon="🏦", layout="wide")
    
    if 'is_authenticated' not in st.session_state:
        st.session_state.is_authenticated = False
        
    if not st.session_state.is_authenticated:
        # Full page auth gate
        auth.render()
        return
    
    user_role = st.session_state.get('user_role', 'user')
    public_pages = ["Home", "EMI Assessment", "My Assessments"]
    admin_pages = ["Data Analysis", "Model Performance", "MLflow Experiments", "Data Management"]

    # Enforce routing security
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "Home" if user_role == "user" else "Data Analysis"
    else:
        if user_role == "user" and st.session_state.current_page not in public_pages:
            st.session_state.current_page = "Home"
        elif user_role == "admin" and st.session_state.current_page not in admin_pages:
            st.session_state.current_page = "Data Analysis"

    # Custom Sidebar Navigation
    st.sidebar.title("Navigation")
    
    # Show authenticated user
    st.sidebar.markdown(f"**Logged in as:**<br>{st.session_state.user_email}", unsafe_allow_html=True)
    if st.sidebar.button("Logout", use_container_width=True):
        st.session_state.is_authenticated = False
        st.rerun()
    st.sidebar.markdown("---")
    if user_role == "user":
        st.sidebar.markdown("### Customer Portal")
        for page in public_pages:
            if st.sidebar.button(page, use_container_width=True, type="primary" if st.session_state.current_page == page else "secondary"):
                st.session_state.current_page = page
                st.rerun()

    elif user_role == "admin":
        st.sidebar.markdown("### Administrative Management")
        for page in admin_pages:
            if st.sidebar.button(page, use_container_width=True, type="primary" if st.session_state.current_page == page else "secondary"):
                st.session_state.current_page = page
                st.rerun()

    selection = st.session_state.current_page

    # Render selected page
    if selection == "Home":
        home.render()
    elif selection == "EMI Assessment":
        emi_assessment.render()
    elif selection == "My Assessments":
        my_assessments.render()
    elif selection == "Data Analysis":
        data_analysis.render()
    elif selection == "Model Performance":
        model_performance.render()
    elif selection == "MLflow Experiments":
        st.info("MLflow Experiments section placeholder. MLflow tracking details will be integrated here.")
    elif selection == "Data Management":
        data_management.render()

if __name__ == "__main__":
    main()
