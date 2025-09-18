import streamlit as st
import pandas as pd
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Peerspace Liquidity Analyzer",
    page_icon="🏢",
    layout="wide"
)

# Title
st.title("🏢 Peerspace Marketplace Liquidity Analyzer")
st.write("Predict marketplace health and identify revenue opportunities")

# Sidebar for inputs
st.sidebar.header("Enter Marketplace Data")

# Get user inputs
metro = st.sidebar.selectbox(
    "Select Metro",
    ["San Francisco", "Los Angeles", "New York", "Chicago", "Austin", "Miami"]
)

active_venues = st.sidebar.number_input(
    "Number of Active Venues",
    min_value=10,
    max_value=500,
    value=100,
    help="How many venues are currently active in this metro"
)

monthly_searches = st.sidebar.number_input(
    "Monthly Searches",
    min_value=100,
    max_value=5000,
    value=1000,
    help="Number of searches in the past month"
)

avg_price = st.sidebar.slider(
    "Average Price per Hour ($)",
    min_value=50,
    max_value=300,
    value=150,
    help="Average venue rental price per hour"
)

# Add a button to run analysis
if st.sidebar.button("🔮 Run Analysis", type="primary"):
    
    # Show loading spinner
    with st.spinner("Analyzing marketplace..."):
        
        # Calculate simple metrics (replace with your actual model predictions)
        supply_demand_ratio = active_venues / monthly_searches
        
        # Simple liquidity score calculation
        if supply_demand_ratio < 0.05:
            liquidity_score = 30  # Low supply
            status = "Critical - Supply Shortage"
            color = "red"
        elif supply_demand_ratio > 0.3:
            liquidity_score = 40  # Oversupply
            status = "Warning - Oversupply"
            color = "orange"
        else:
            liquidity_score = 75  # Balanced
            status = "Healthy"
            color = "green"
        
        # Calculate conversion rate (simplified)
        conversion_rate = min(0.5, supply_demand_ratio * 2)
        
        # Calculate revenue opportunity
        unfulfilled_searches = monthly_searches * (1 - conversion_rate)
        revenue_opportunity = unfulfilled_searches * avg_price * 4
    
    # Display results in columns
    st.header("📊 Analysis Results")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="Liquidity Score",
            value=f"{liquidity_score:.0f}/100",
            delta=status
        )
    
    with col2:
        st.metric(
            label="Conversion Rate",
            value=f"{conversion_rate:.1%}",
            delta=f"{conversion_rate - 0.4:.1%} vs target"
        )
    
    with col3:
        st.metric(
            label="Revenue Opportunity",
            value=f"${revenue_opportunity:,.0f}",
            delta="Monthly"
        )
    
    # Recommendations section
    st.header("💡 Recommendations")
    
    if supply_demand_ratio < 0.05:
        st.error("🚨 **Critical: Supply Shortage Detected**")
        st.write(f"""
        **Problem**: Only {active_venues} venues for {monthly_searches} monthly searches
        
        **Recommended Actions**:
        1. Launch emergency host acquisition campaign
        2. Target: Add {int(monthly_searches * 0.1)} new venues
        3. Budget: ${int(monthly_searches * 0.1 * 2000):,}
        4. Expected ROI: {revenue_opportunity * 0.4 / (monthly_searches * 0.1 * 2000):.0%}
        """)
    elif supply_demand_ratio > 0.3:
        st.warning("📢 **Priority: Generate Demand**")
        st.write(f"""
        **Problem**: {active_venues} venues but only {monthly_searches} searches
        
        **Recommended Actions**:
        1. Launch targeted marketing campaign
        2. Budget: ${active_venues * 300:,}
        3. Target: Increase searches by 40%
        4. Channels: Google Ads, Instagram, Email
        """)
    else:
        st.success("✅ **Market is Balanced**")
        st.write("""
        **Recommended Actions**:
        1. Implement dynamic pricing
        2. A/B test on 10% of inventory
        3. Expected impact: 8-10% revenue increase
        """)
    
    # Add a chart
    st.header("📈 Supply vs Demand Visualization")
    
    chart_data = pd.DataFrame({
        'Metric': ['Current Supply', 'Current Demand', 'Optimal Supply', 'Optimal Demand'],
        'Value': [active_venues, monthly_searches/10, monthly_searches * 0.1, monthly_searches/10]
    })
    
    st.bar_chart(chart_data.set_index('Metric'))

# Add instructions if no analysis run yet
else:
    st.info("👈 Enter your marketplace data in the sidebar and click 'Run Analysis' to get started!")

# Footer
st.divider()
st.caption("Built with Streamlit • Peerspace Marketplace Analysis Project")