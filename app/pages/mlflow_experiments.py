import streamlit as st
import mlflow
import pandas as pd
import os
import json

def render():
    st.title("MLflow Experiments & Tracking")
    
    # Enforce RBAC
    if st.session_state.get('user_role') != 'admin':
        st.error("Unauthorized. Administrator access required.")
        return
        
    st.markdown("View all registered MLflow experiments, production runs, metrics, and parameters tracked by the backend.")
    st.markdown("---")
    
    # Fetch experiments
    try:
        experiments = mlflow.search_experiments()
    except Exception as e:
        st.error(f"Failed to connect to local MLflow tracking server: {e}")
        return
        
    if not experiments:
        st.info("No MLflow experiments found.")
        return
        
    # Build list of experiments
    exp_list = [exp for exp in experiments if exp.name != 'Default']
    
    if not exp_list:
        st.info("No custom MLflow experiments found (only Default).")
        return
        
    # Sidebar or top selectbox for experiment
    exp_names = {exp.name: exp for exp in exp_list}
    selected_exp_name = st.selectbox("Select Experiment", list(exp_names.keys()))
    
    selected_exp = exp_names[selected_exp_name]
    
    # Fetch runs for the selected experiment
    runs = mlflow.search_runs(experiment_ids=[selected_exp.experiment_id])
    
    if runs.empty:
        st.warning(f"No runs found in experiment '{selected_exp_name}'.")
        return
        
    st.subheader(f"Runs in {selected_exp_name}")
    
    # Prepare display dataframe
    display_cols = []
    
    if 'tags.mlflow.runName' in runs.columns:
        display_cols.append('tags.mlflow.runName')
    if 'tags.model_name' in runs.columns:
        display_cols.append('tags.model_name')
    if 'tags.task' in runs.columns:
        display_cols.append('tags.task')
    if 'tags.model_role' in runs.columns:
        display_cols.append('tags.model_role')
    if 'status' in runs.columns:
        display_cols.append('status')
    if 'start_time' in runs.columns:
        display_cols.append('start_time')
        
    # Add metric columns dynamically
    metric_cols = [c for c in runs.columns if c.startswith('metrics.')]
    display_cols.extend(metric_cols)
    
    display_df = runs[display_cols].copy()
    
    # Rename columns for cleaner display
    rename_map = {
        'tags.mlflow.runName': 'Run Name',
        'tags.model_name': 'Model',
        'tags.task': 'Task',
        'tags.model_role': 'Role',
        'status': 'Status',
        'start_time': 'Date'
    }
    
    for c in metric_cols:
        rename_map[c] = c.replace('metrics.', 'Metric: ').title()
        
    display_df = display_df.rename(columns=rename_map)
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    st.subheader("Run Details Inspector")
    
    # Select run to inspect
    run_names = runs['tags.mlflow.runName'].tolist() if 'tags.mlflow.runName' in runs.columns else runs['run_id'].tolist()
    run_ids = runs['run_id'].tolist()
    
    # Map friendly names to run_id
    run_options = {name: rid for name, rid in zip(run_names, run_ids)}
    
    selected_run_name = st.selectbox("Select a run to inspect details:", list(run_options.keys()))
    selected_run_id = run_options[selected_run_name]
    
    # Get specific run details
    run_details = mlflow.get_run(selected_run_id)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Logged Metrics")
        if run_details.data.metrics:
            metrics_df = pd.DataFrame(list(run_details.data.metrics.items()), columns=["Metric", "Value"])
            st.dataframe(metrics_df, hide_index=True, use_container_width=True)
        else:
            st.info("No metrics logged.")
            
        st.markdown("#### Artifacts")
        # List artifacts
        client = mlflow.tracking.MlflowClient()
        artifacts = client.list_artifacts(selected_run_id)
        if artifacts:
            for art in artifacts:
                st.write(f"- 📄 `{art.path}` (Directory: {art.is_dir})")
        else:
            st.info("No artifacts logged.")
            
    with col2:
        st.markdown("#### Logged Parameters")
        if run_details.data.params:
            params_df = pd.DataFrame(list(run_details.data.params.items()), columns=["Parameter", "Value"])
            st.dataframe(params_df, hide_index=True, use_container_width=True)
        else:
            st.info("No parameters logged.")
