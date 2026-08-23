import streamlit as st
import pandas as pd
import os

@st.cache_data
def load_data():
    file_path = os.path.join("data", "processed", "financial_data_feature_engineered.csv")
    if os.path.exists(file_path):
        return pd.read_csv(file_path)
    return None

def render():
    st.title("Data Analysis")
    st.markdown("Overview of the EMIPredict AI dataset and feature engineering results.")
    
    with st.spinner("Loading dataset..."):
        df = load_data()
        
    if df is None:
        st.error("Processed dataset not found. Please ensure data pipeline has been run.")
        return
        
    # General Dataset Stats
    st.header("Dataset Overview")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Records", f"{len(df):,}")
    with col2:
        st.metric("Total Features (After Engineering)", f"{len(df.columns)}")
        
    st.markdown("### Sample Data")
    st.dataframe(df.head(10), use_container_width=True)
    
    st.markdown("---")
    
    # Target Distributions
    st.header("Target Variables Analysis")
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.subheader("Classification: EMI Eligibility")
        class_counts = df['emi_eligibility'].value_counts().reset_index()
        class_counts.columns = ['Eligibility Class', 'Count']
        
        st.dataframe(class_counts, hide_index=True, use_container_width=True)
        
        # Simple Bar Chart
        st.bar_chart(class_counts.set_index('Eligibility Class'))

    with col4:
        st.subheader("Regression: Maximum Monthly EMI")
        
        # Summary Statistics
        desc = df['max_monthly_emi'].describe().reset_index()
        desc.columns = ['Statistic', 'Value']
        # Format the values
        desc['Value'] = desc['Value'].apply(lambda x: f"₹ {x:,.2f}")
        
        st.dataframe(desc, hide_index=True, use_container_width=True)
        
    st.markdown("---")
    st.header("Feature Information")
    st.write(
        "The feature-engineered dataset includes the original 25 raw inputs, along with "
        "derived financial indicators such as:"
    )
    st.markdown(
        """
        - **Total Monthly Expenses**: Aggregation of rent, fees, travel, utilities, etc.
        - **Total Financial Burden**: Total expenses + current EMI.
        - **Income After Expenses**: Monthly salary minus total financial burden.
        - **EMI to Income Ratio**: Proportion of income dedicated to the current EMI.
        - **Emergency Fund Coverage**: Months of expenses covered by emergency savings.
        """
    )
