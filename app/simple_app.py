import streamlit as st
import pandas as pd
import numpy as np
# Comment out any other imports for now
# import plotly  # COMMENT THIS OUT
# import scikit-learn  # COMMENT THIS OUT

st.title("🏢 Peerspace Liquidity Analyzer")
st.write("Basic deployment test")

# Simple test
metro = st.selectbox("Metro", ["Austin", "LA", "SF"])
venues = st.number_input("Venues", value=100)

if st.button("Calculate"):
    st.write(f"Metro: {metro}, Venues: {venues}")
    st.success("App is working!")