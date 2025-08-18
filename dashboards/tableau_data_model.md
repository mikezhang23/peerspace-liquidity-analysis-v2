# Tableau Dashboard Design Document

## Dashboard Overview
**Title**: Peerspace Marketplace Liquidity Intelligence Dashboard  
**Purpose**: Monitor and predict marketplace health to drive strategic interventions  
**Audience**: Executive team, Operations managers, Growth team

## Data Sources & Relationships

### Primary Data Sources
1. **liquidity_scores.csv** - Current liquidity metrics by metro
2. **liquidity_predictions.csv** - ML predictions and historical trends
3. **priority_matrix.csv** - Action priorities and revenue opportunities
4. **metro_segments.csv** - Market segmentation from clustering
5. **price_elasticity.csv** - Pricing sensitivity analysis
6. **demand_forecast.csv** - 30-day demand predictions
7. **recommendations.csv** - Prioritized action items

### Data Model in Tableau
```
liquidity_scores (Metro Area) ←→ priority_matrix (Metro Area)
                              ←→ metro_segments (Metro Area)
                              ←→ liquidity_predictions (Metro Area, Month)
                              
price_elasticity (Venue Type) ←→ recommendations (if venue-specific)

demand_forecast (Date) - Standalone for time series
```

## Dashboard Pages

### Page 1: Executive Summary
**Purpose**: High-level health metrics and alerts

**Layout**:
```
┌─────────────────────────────────────────────────────────┐
│                    MARKETPLACE HEALTH                    │
├──────────┬──────────┬──────────┬──────────┬────────────┤
│  Overall │ At Risk  │ Revenue  │ Forecast │ Conversion │
│  Score   │ Metros   │ at Risk  │ Accuracy │    Rate    │
│   72.3   │    2     │  $487K   │   85%    │   41.2%    │
├──────────┴──────────┴──────────┴──────────┴────────────┤
│                                                          │
│              Liquidity Score by Metro (Map)             │
│                                                          │
├──────────────────────────┬───────────────────────────────┤
│   Action Priority Matrix │   30-Day Demand Forecast     │
│   (Scatter Plot)         │   (Line Chart)                │
└──────────────────────────┴───────────────────────────────┘
```

### Page 2: Metro Deep Dive
**Purpose**: Detailed analysis per metro with drill-down

**Layout**:
```
┌─────────────────────────────────────────────────────────┐
│ [Metro Selector Dropdown]        [Date Range Filter]    │
├─────────────────────────────────────────────────────────┤
│ Metro KPIs:                                             │
│ Supply | Demand | Conversion | Utilization | Revenue   │
├──────────────────────────┬───────────────────────────────┤
│ Liquidity Score Trend    │ Supply vs Demand Balance     │
│ (Time Series)             │ (Dual Axis)                  │
├──────────────────────────┼───────────────────────────────┤
│ Venue Type Performance   │ Unfulfilled Demand Analysis  │
│ (Heatmap)                │ (Waterfall Chart)            │
└──────────────────────────┴───────────────────────────────┘
```

### Page 3: Predictive Analytics
**Purpose**: ML model outputs and forecasts

**Layout**:
```
┌─────────────────────────────────────────────────────────┐
│            PREDICTIVE INTELLIGENCE DASHBOARD            │
├──────────────────────────┬───────────────────────────────┤
│ Liquidity Score Forecast │ Model Accuracy Metrics       │
│ (Actual vs Predicted)    │ (KPI Cards)                  │
├──────────────────────────┼───────────────────────────────┤
│ Market Segmentation      │ Price Elasticity by Type     │
│ (Cluster Visualization)  │ (Bar Chart with Reference)   │
├──────────────────────────┴───────────────────────────────┤
│              Demand Forecast with Confidence Bands       │
│                    (Area Chart)                          │
└───────────────────────────────────────────────────────────┘
```

### Page 4: Action Center
**Purpose**: Prioritized recommendations and implementation tracking

**Layout**:
```
┌─────────────────────────────────────────────────────────┐
│                    ACTION CENTER                        │
├─────────────────────────────────────────────────────────┤
│ Priority Actions Table:                                 │
│ Metro | Issue | Action | Impact | Priority | Status    │
├─────────────────────────────────────────────────────────┤
│                 Revenue Opportunity Treemap              │
├──────────────────────────┬───────────────────────────────┤
│ Implementation Timeline  │ Expected Impact by Action    │
│ (Gantt Chart)           │ (Horizontal Bar)             │
└──────────────────────────┴───────────────────────────────┘
```

## Key Visualizations to Build

### 1. Liquidity Score Map
- **Type**: Filled Map
- **Data**: liquidity_scores.csv
- **Color**: Diverging palette (Red-Yellow-Green)
- **Threshold**: <50 Red, 50-70 Yellow, >70 Green
- **Tooltip**: Score, Supply, Demand, Conversion Rate

### 2. Priority Matrix Scatter
- **Type**: Scatter Plot
- **X-Axis**: Total Venues (Supply)
- **Y-Axis**: Total Searches (Demand)
- **Size**: Revenue Opportunity
- **Color**: Action Required
- **Reference Lines**: Optimal balance zones

### 3. Demand Forecast
- **Type**: Dual-Axis Line Chart
- **Primary**: Historical Daily Searches
- **Secondary**: Forecasted Searches
- **Confidence**: Add reference bands at ±20%
- **Annotation**: Mark anomalies and holidays

### 4. Market Segmentation
- **Type**: Bubble Chart on Map
- **Position**: Metro coordinates
- **Color**: Cluster/Segment
- **Size**: Market size (total searches)
- **Border**: Highlight if action needed

### 5. Price Elasticity Visualization
- **Type**: Diverging Bar Chart
- **Center Line**: Elasticity = 1 (unit elastic)
- **Color**: Red for elastic (>1), Blue for inelastic (<1)
- **Sort**: By absolute elasticity value

### 6. Conversion Funnel
- **Type**: Funnel Chart or Waterfall
- **Stages**: Searches → Matched → Converted → Completed
- **Breakdown**: By Metro or Venue Type
- **Color**: Performance vs benchmark

## Calculated Fields to Create

### 1. Liquidity Health Status
```tableau
IF [Liquidity Score] >= 70 THEN "Healthy"
ELSEIF [Liquidity Score] >= 50 THEN "Moderate"
ELSE "Needs Attention"
END
```

### 2. Supply-Demand Balance
```tableau
[Total Searches] / [Total Venues]
```

### 3. Revenue at Risk
```tableau
[Unfulfilled Searches] * [Average Booking Value]
```

### 4. Conversion Rate
```tableau
[Bookings] / [Searches] * 100
```

### 5. Forecast Accuracy
```tableau
1 - (ABS([Actual] - [Predicted]) / [Actual])
```

### 6. Days Until Action
```tableau
CASE [Priority]
  WHEN "High" THEN 7
  WHEN "Medium" THEN 30
  WHEN "Low" THEN 90
END
```

### 7. YoY Growth
```tableau
(([Current Period] - [Previous Period]) / [Previous Period]) * 100
```

## Dashboard Interactivity

### Filters to Add
1. **Global Filters** (apply to all sheets):
   - Date Range
   - Metro Area (multi-select)
   - Market Segment

2. **Page-Specific Filters**:
   - Venue Type
   - Price Range
   - Minimum Liquidity Score

### Actions to Configure
1. **Filter Action**: Click metro on map → filter all sheets
2. **Highlight Action**: Hover on segment → highlight related metros
3. **URL Action**: Click recommendation → open detailed plan
4. **Parameter Action**: Select forecast period → update predictions

### Parameters to Create
1. **Forecast Horizon**: 7, 14, 30, 60 days
2. **Liquidity Threshold**: Slider 0-100
3. **Price Sensitivity**: Toggle elastic/inelastic
4. **Metric Selection**: Revenue/Conversion/Utilization

## Color Schemes

### Liquidity Score
- Red (#DC3545): 0-40
- Orange (#FD7E14): 40-50  
- Yellow (#FFC107): 50-70
- Green (#28A745): 70-100

### Segments
- Segment 1 (High-Performance): #007BFF (Blue)
- Segment 2 (Oversupplied): #6C757D (Gray)
- Segment 3 (Growth): #20C997 (Teal)

### Priority
- High: #DC3545 (Red)
- Medium: #FFC107 (Yellow)
- Low: #28A745 (Green)

## Performance Optimization

### Data Extract
- Create Tableau Extract (.hyper) for better performance
- Schedule daily refresh at 2 AM
- Aggregate detailed data to daily level

### Level of Detail (LOD) Calculations
```tableau
// Metro-level conversion regardless of filters
{ FIXED [Metro Area] : AVG([Conversion Rate]) }

// Overall liquidity score
{ FIXED : AVG([Liquidity Score]) }
```

### Dashboard Performance Tips
1. Limit marks to <5000 per view
2. Use data source filters for date ranges
3. Optimize extracts with aggregation
4. Hide unused fields
5. Use "Assume Referential Integrity" for joins

## Publishing & Sharing

### Tableau Server/Online Setup
1. **Project**: Marketplace Analytics
2. **Workbook Name**: Liquidity_Dashboard_v1
3. **Permissions**: 
   - Executive Team: View & Interact
   - Analysts: Edit & Publish
4. **Refresh Schedule**: Daily at 6 AM
5. **Alerts**: 
   - Email if liquidity < 50 for any metro
   - Slack notification for new recommendations

### Mobile Optimization
- Create phone-specific layout
- Limit to 3 key metrics per screen
- Use device preview before publishing
- Enable offline mode for executive travel

## Success Metrics for Dashboard

1. **Adoption**: 80% of stakeholders accessing weekly
2. **Action Rate**: 60% of recommendations implemented
3. **Decision Speed**: 50% reduction in analysis time
4. **Accuracy**: 85% forecast accuracy maintained
5. **ROI**: $100K+ monthly revenue impact tracked

---
*Dashboard designed for Tableau Desktop 2023.3+*
*Optimized for 1920x1080 resolution*