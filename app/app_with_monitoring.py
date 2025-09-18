import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import json
import os

# Create or load usage log
LOG_FILE = 'logs/usage_log.json'

def log_usage(metro, venues, searches, score, opportunity):
    """Log each analysis run"""
    
    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # Load existing log or create new
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'r') as f:
            logs = json.load(f)
    else:
        logs = []
    
    # Add new entry
    logs.append({
        'timestamp': datetime.now().isoformat(),
        'metro': metro,
        'venues': venues,
        'searches': searches,
        'liquidity_score': score,
        'revenue_opportunity': opportunity
    })
    
    # Save log
    with open(LOG_FILE, 'w') as f:
        json.dump(logs, f, indent=2)
    
    return len(logs)  # Return total number of analyses

# Add to your analysis button:
if st.sidebar.button("Run Analysis"):
    # ... your analysis code ...
    
    # Log the usage
    total_runs = log_usage(metro, active_venues, monthly_searches, 
                          liquidity_score, revenue_opportunity)
    
    # Show usage stats
    st.sidebar.metric("Total Analyses Run", total_runs)