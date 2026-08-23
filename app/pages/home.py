import streamlit as st

def render():
    st.markdown("""
        <div style='text-align: center; padding: 3rem 0 2rem 0;'>
            <h1 style='font-size: 3.5rem; color: #1E3A8A; margin-bottom: 0.5rem;'>EMIPredict AI 🏦</h1>
            <h3 style='color: #4B5563; font-weight: normal; margin-top: 0;'>Intelligent Financial Risk & Affordability Assessment</h3>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("<h3 style='color: #2563EB;'>📊 Smart Assessment</h3>", unsafe_allow_html=True)
        st.write("Evaluate your financial profile using advanced machine learning to determine your EMI eligibility instantly and accurately.")
        
    with col2:
        st.markdown("<h3 style='color: #2563EB;'>🛡️ Risk Management</h3>", unsafe_allow_html=True)
        st.write("Understand your boundaries. We predict the maximum safe monthly EMI you can comfortably afford without financial strain.")
        
    with col3:
        st.markdown("<h3 style='color: #2563EB;'>⚡ Real-Time Insights</h3>", unsafe_allow_html=True)
        st.write("Get immediate feedback and transparent confidence scores on your assessment, empowering you to make better financial decisions.")
        
    st.markdown("---")
    
    st.markdown("""
        <div style='text-align: center; padding: 2rem 0;'>
            <h2>Ready to discover your financial potential?</h2>
            <p style='font-size: 1.1rem; color: #4B5563; margin-bottom: 2rem;'>Start your personalized EMI affordability assessment right now.</p>
        </div>
    """, unsafe_allow_html=True)
    
    col_empty1, col_btn, col_empty2 = st.columns([1, 1, 1])
    with col_btn:
        if st.button("🚀 Start EMI Assessment", use_container_width=True, type="primary"):
            st.session_state.current_page = "EMI Assessment"
            st.rerun()
