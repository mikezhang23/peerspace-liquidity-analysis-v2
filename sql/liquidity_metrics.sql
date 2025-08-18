-- =====================================================
-- PEERSPACE MARKETPLACE LIQUIDITY ANALYSIS
-- =====================================================
-- This SQL script analyzes marketplace liquidity metrics
-- to identify supply-demand imbalances and growth opportunities

-- =====================================================
-- SECTION 1: SUPPLY METRICS
-- =====================================================

-- 1.1: Active Listings by Metro and Month
-- Business Purpose: Track supply growth and identify metros with limited inventory
WITH monthly_supply AS (
    SELECT 
        metro_area,
        DATE(created_date, 'start of month') as month,
        COUNT(DISTINCT venue_id) as total_venues,
        COUNT(DISTINCT CASE WHEN is_active = 1 THEN venue_id END) as active_venues,
        COUNT(DISTINCT host_id) as unique_hosts,
        AVG(price_per_hour) as avg_price,
        AVG(capacity) as avg_capacity
    FROM listings
    WHERE created_date <= DATE('2024-12-31')
    GROUP BY metro_area, DATE(created_date, 'start of month')
),
cumulative_supply AS (
    SELECT 
        metro_area,
        month,
        SUM(total_venues) OVER (PARTITION BY metro_area ORDER BY month) as cumulative_venues,
        SUM(active_venues) OVER (PARTITION BY metro_area ORDER BY month) as cumulative_active_venues
    FROM monthly_supply
)
SELECT 
    ms.*,
    cs.cumulative_venues,
    cs.cumulative_active_venues,
    ROUND(cs.cumulative_active_venues * 100.0 / cs.cumulative_venues, 2) as pct_active
FROM monthly_supply ms
JOIN cumulative_supply cs 
    ON ms.metro_area = cs.metro_area 
    AND ms.month = cs.month
ORDER BY ms.metro_area, ms.month;

-- 1.2: Venue Utilization Rate
-- Business Purpose: Identify underutilized venues and oversaturated venue types
WITH venue_bookings AS (
    SELECT 
        l.venue_id,
        l.metro_area,
        l.venue_type,
        l.price_per_hour,
        l.capacity,
        COUNT(DISTINCT b.booking_id) as total_bookings,
        COUNT(DISTINCT DATE(b.event_date)) as days_booked,
        SUM(b.hours_booked) as total_hours_booked,
        AVG(b.total_amount) as avg_booking_value
    FROM listings l
    LEFT JOIN bookings b 
        ON l.venue_id = b.venue_id 
        AND b.status = 'completed'
    GROUP BY l.venue_id, l.metro_area, l.venue_type, l.price_per_hour, l.capacity
),
utilization_stats AS (
    SELECT 
        venue_id,
        metro_area,
        venue_type,
        total_bookings,
        days_booked,
        total_hours_booked,
        -- Assuming venues are available 10 hours/day, 365 days
        ROUND(total_hours_booked * 100.0 / (10 * 365), 2) as utilization_rate,
        -- Bookings per month (12 months of data)
        ROUND(total_bookings / 12.0, 2) as bookings_per_month,
        avg_booking_value
    FROM venue_bookings
)
SELECT 
    metro_area,
    venue_type,
    COUNT(*) as venue_count,
    AVG(utilization_rate) as avg_utilization_rate,
    MIN(utilization_rate) as min_utilization_rate,
    MAX(utilization_rate) as max_utilization_rate,
    AVG(bookings_per_month) as avg_bookings_per_month,
    COUNT(CASE WHEN utilization_rate < 5 THEN 1 END) as low_utilization_venues,
    COUNT(CASE WHEN utilization_rate > 30 THEN 1 END) as high_utilization_venues
FROM utilization_stats
GROUP BY metro_area, venue_type
ORDER BY metro_area, avg_utilization_rate DESC;

-- 1.3: Supply Diversity Index
-- Business Purpose: Measure variety of venue options (better liquidity with more options)
WITH supply_diversity AS (
    SELECT 
        metro_area,
        COUNT(DISTINCT venue_type) as venue_types_available,
        COUNT(DISTINCT venue_id) as total_venues,
        -- Calculate distribution entropy (higher = more diverse)
        SUM(-1.0 * (count_by_type * 1.0 / total_count) * 
            LOG(count_by_type * 1.0 / total_count)) as diversity_index
    FROM (
        SELECT 
            metro_area,
            venue_type,
            COUNT(*) as count_by_type,
            SUM(COUNT(*)) OVER (PARTITION BY metro_area) as total_count
        FROM listings
        WHERE is_active = 1
        GROUP BY metro_area, venue_type
    )
    GROUP BY metro_area
)
SELECT 
    metro_area,
    venue_types_available,
    total_venues,
    ROUND(diversity_index, 3) as diversity_score,
    ROUND(total_venues * 1.0 / venue_types_available, 2) as avg_venues_per_type
FROM supply_diversity
ORDER BY diversity_score DESC;

-- =====================================================
-- SECTION 2: DEMAND METRICS
-- =====================================================

-- 2.1: Search Volume and Patterns
-- Business Purpose: Understand demand trends and peak periods
WITH search_metrics AS (
    SELECT 
        metro_area,
        DATE(search_date, 'start of month') as month,
        COUNT(*) as total_searches,
        COUNT(DISTINCT user_id) as unique_searchers,
        AVG(capacity_needed) as avg_capacity_requested,
        AVG(max_price) as avg_max_price,
        -- Calculate lead time (days between search and intended event)
        AVG(JULIANDAY(event_date) - JULIANDAY(search_date)) as avg_lead_time_days
    FROM searches
    GROUP BY metro_area, DATE(search_date, 'start of month')
),
search_growth AS (
    SELECT 
        metro_area,
        month,
        total_searches,
        LAG(total_searches, 1) OVER (PARTITION BY metro_area ORDER BY month) as prev_month_searches,
        ROUND((total_searches - LAG(total_searches, 1) OVER (PARTITION BY metro_area ORDER BY month)) * 100.0 / 
              NULLIF(LAG(total_searches, 1) OVER (PARTITION BY metro_area ORDER BY month), 0), 2) as mom_growth_pct
    FROM search_metrics
)
SELECT 
    sm.*,
    sg.mom_growth_pct,
    CASE 
        WHEN sg.mom_growth_pct > 10 THEN 'High Growth'
        WHEN sg.mom_growth_pct > 0 THEN 'Moderate Growth'
        WHEN sg.mom_growth_pct > -10 THEN 'Stable'
        ELSE 'Declining'
    END as demand_trend
FROM search_metrics sm
JOIN search_growth sg 
    ON sm.metro_area = sg.metro_area 
    AND sm.month = sg.month
ORDER BY sm.metro_area, sm.month;

-- 2.2: Search-to-Booking Conversion Funnel
-- Business Purpose: Identify where users drop off in the booking process
WITH conversion_funnel AS (
    SELECT 
        s.metro_area,
        s.venue_type,
        COUNT(DISTINCT s.search_id) as total_searches,
        COUNT(DISTINCT CASE WHEN s.search_resulted_in_booking = 1 THEN s.search_id END) as converted_searches,
        COUNT(DISTINCT b.booking_id) as total_bookings,
        COUNT(DISTINCT CASE WHEN b.status = 'completed' THEN b.booking_id END) as completed_bookings,
        COUNT(DISTINCT CASE WHEN b.status = 'cancelled' THEN b.booking_id END) as cancelled_bookings
    FROM searches s
    LEFT JOIN bookings b ON s.search_id = b.search_id
    GROUP BY s.metro_area, s.venue_type
)
SELECT 
    metro_area,
    venue_type,
    total_searches,
    converted_searches,
    ROUND(converted_searches * 100.0 / NULLIF(total_searches, 0), 2) as search_to_booking_rate,
    completed_bookings,
    cancelled_bookings,
    ROUND(cancelled_bookings * 100.0 / NULLIF(total_bookings, 0), 2) as cancellation_rate,
    CASE 
        WHEN converted_searches * 100.0 / NULLIF(total_searches, 0) < 20 THEN 'Poor Liquidity'
        WHEN converted_searches * 100.0 / NULLIF(total_searches, 0) < 40 THEN 'Moderate Liquidity'
        ELSE 'Good Liquidity'
    END as liquidity_health
FROM conversion_funnel
ORDER BY metro_area, search_to_booking_rate DESC;

-- 2.3: Unfulfilled Demand Analysis
-- Business Purpose: Identify gaps in supply that prevent bookings
WITH unfulfilled_searches AS (
    SELECT 
        s.metro_area,
        s.venue_type,
        s.search_date,
        s.capacity_needed,
        s.max_price,
        s.search_resulted_in_booking,
        -- Check if matching supply exists
        CASE 
            WHEN EXISTS (
                SELECT 1 FROM listings l 
                WHERE l.metro_area = s.metro_area 
                AND l.venue_type = s.venue_type 
                AND l.capacity >= s.capacity_needed * 0.8
                AND l.price_per_hour <= s.max_price
                AND l.is_active = 1
            ) THEN 1 ELSE 0 
        END as matching_supply_exists
    FROM searches s
    WHERE s.search_resulted_in_booking = 0
)
SELECT 
    metro_area,
    venue_type,
    COUNT(*) as unfulfilled_searches,
    COUNT(CASE WHEN matching_supply_exists = 0 THEN 1 END) as no_matching_supply,
    COUNT(CASE WHEN matching_supply_exists = 1 THEN 1 END) as had_supply_but_no_booking,
    AVG(capacity_needed) as avg_capacity_gap,
    AVG(max_price) as avg_price_expectation,
    ROUND(COUNT(CASE WHEN matching_supply_exists = 0 THEN 1 END) * 100.0 / COUNT(*), 2) as pct_true_supply_gap
FROM unfulfilled_searches
GROUP BY metro_area, venue_type
HAVING COUNT(*) > 10  -- Filter out noise
ORDER BY unfulfilled_searches DESC;

-- =====================================================
-- SECTION 3: LIQUIDITY SCORE CALCULATION
-- =====================================================

-- 3.1: Comprehensive Liquidity Score
-- Business Purpose: Create a single metric to assess market health
WITH liquidity_components AS (
    SELECT 
        l.metro_area,
        -- Supply metrics
        COUNT(DISTINCT l.venue_id) as supply_count,
        COUNT(DISTINCT CASE WHEN l.is_active = 1 THEN l.venue_id END) as active_supply,
        COUNT(DISTINCT l.venue_type) as supply_diversity,
        
        -- Demand metrics
        COUNT(DISTINCT s.search_id) as demand_count,
        COUNT(DISTINCT s.user_id) as unique_searchers,
        
        -- Conversion metrics
        COUNT(DISTINCT b.booking_id) as booking_count,
        COUNT(DISTINCT CASE WHEN s.search_resulted_in_booking = 1 THEN s.search_id END) as converted_searches,
        
        -- Calculate ratios
        COUNT(DISTINCT b.booking_id) * 1.0 / NULLIF(COUNT(DISTINCT l.venue_id), 0) as bookings_per_venue,
        COUNT(DISTINCT s.search_id) * 1.0 / NULLIF(COUNT(DISTINCT l.venue_id), 0) as searches_per_venue
        
    FROM listings l
    LEFT JOIN searches s ON l.metro_area = s.metro_area
    LEFT JOIN bookings b ON b.venue_id = l.venue_id AND b.status = 'completed'
    GROUP BY l.metro_area
),
liquidity_scores AS (
    SELECT 
        metro_area,
        supply_count,
        demand_count,
        booking_count,
        
        -- Component scores (each normalized to 0-100 scale)
        -- Conversion rate score
        ROUND(converted_searches * 100.0 / NULLIF(demand_count, 0), 2) as conversion_score,
        
        -- Utilization score (bookings per venue, capped at 100)
        ROUND(MIN(bookings_per_venue * 10, 100), 2) as utilization_score,
        
        -- Balance score (ideal is 1:10 venue to search ratio)
        ROUND(100 - ABS(searches_per_venue - 10) * 5, 2) as balance_score,
        
        -- Diversity bonus (more venue types = better)
        ROUND(supply_diversity * 20, 2) as diversity_score
        
    FROM liquidity_components
)
SELECT 
    metro_area,
    supply_count,
    demand_count,
    booking_count,
    conversion_score,
    utilization_score,
    balance_score,
    diversity_score,
    -- Weighted composite score
    ROUND(
        conversion_score * 0.35 +  -- 35% weight on conversion
        utilization_score * 0.25 +  -- 25% weight on utilization
        balance_score * 0.25 +      -- 25% weight on supply/demand balance
        diversity_score * 0.15,      -- 15% weight on diversity
    2) as liquidity_score,
    -- Classification
    CASE 
        WHEN (conversion_score * 0.35 + utilization_score * 0.25 + balance_score * 0.25 + diversity_score * 0.15) >= 70 THEN 'Healthy'
        WHEN (conversion_score * 0.35 + utilization_score * 0.25 + balance_score * 0.25 + diversity_score * 0.15) >= 50 THEN 'Moderate'
        ELSE 'Needs Attention'
    END as market_health
FROM liquidity_scores
ORDER BY liquidity_score DESC;

-- 3.2: Time-Series Liquidity Trend
-- Business Purpose: Track how liquidity evolves over time
WITH monthly_liquidity AS (
    SELECT 
        DATE(s.search_date, 'start of month') as month,
        s.metro_area,
        COUNT(DISTINCT s.search_id) as searches,
        COUNT(DISTINCT CASE WHEN s.search_resulted_in_booking = 1 THEN s.search_id END) as conversions,
        COUNT(DISTINCT b.booking_id) as bookings,
        COUNT(DISTINCT l.venue_id) as active_venues
    FROM searches s
    LEFT JOIN bookings b 
        ON s.search_id = b.search_id 
        AND b.status = 'completed'
    LEFT JOIN listings l 
        ON s.metro_area = l.metro_area 
        AND l.is_active = 1
        AND l.created_date <= s.search_date
    GROUP BY DATE(s.search_date, 'start of month'), s.metro_area
)
SELECT 
    month,
    metro_area,
    searches,
    conversions,
    bookings,
    active_venues,
    ROUND(conversions * 100.0 / NULLIF(searches, 0), 2) as conversion_rate,
    ROUND(bookings * 1.0 / NULLIF(active_venues, 0), 2) as bookings_per_venue,
    ROUND(searches * 1.0 / NULLIF(active_venues, 0), 2) as demand_supply_ratio
FROM monthly_liquidity
ORDER BY metro_area, month;

-- =====================================================
-- SECTION 4: ACTIONABLE INSIGHTS
-- =====================================================

-- 4.1: Metro Priority Matrix
-- Business Purpose: Identify which metros need immediate intervention
WITH metro_summary AS (
    SELECT 
        l.metro_area,
        COUNT(DISTINCT l.venue_id) as total_venues,
        COUNT(DISTINCT s.search_id) as total_searches,
        COUNT(DISTINCT b.booking_id) as total_bookings,
        COUNT(DISTINCT CASE WHEN s.search_resulted_in_booking = 0 THEN s.search_id END) as unfulfilled_searches,
        ROUND(AVG(l.price_per_hour), 2) as avg_price,
        ROUND(AVG(b.total_amount), 2) as avg_booking_value
    FROM listings l
    LEFT JOIN searches s ON l.metro_area = s.metro_area
    LEFT JOIN bookings b ON b.venue_id = l.venue_id
    GROUP BY l.metro_area
)
SELECT 
    metro_area,
    total_venues,
    total_searches,
    total_bookings,
    unfulfilled_searches,
    ROUND(total_bookings * 100.0 / NULLIF(total_searches, 0), 2) as conversion_rate,
    ROUND(unfulfilled_searches * avg_booking_value, 2) as potential_revenue_loss,
    CASE 
        WHEN total_venues < 50 AND total_searches > 500 THEN 'URGENT: Add Supply'
        WHEN total_venues > 100 AND total_bookings < 100 THEN 'URGENT: Generate Demand'
        WHEN total_bookings * 100.0 / NULLIF(total_searches, 0) < 30 THEN 'MONITOR: Poor Conversion'
        ELSE 'STABLE: Maintain'
    END as action_required,
    CASE 
        WHEN total_venues < 50 AND total_searches > 500 THEN 1
        WHEN total_venues > 100 AND total_bookings < 100 THEN 2
        WHEN total_bookings * 100.0 / NULLIF(total_searches, 0) < 30 THEN 3
        ELSE 4
    END as priority_rank
FROM metro_summary
ORDER BY priority_rank, potential_revenue_loss DESC;