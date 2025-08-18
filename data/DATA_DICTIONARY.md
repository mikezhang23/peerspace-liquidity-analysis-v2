# Peerspace Marketplace Data Dictionary

## Overview
This synthetic dataset simulates a two-sided marketplace for venue rentals, modeled after Peerspace's business model. The data represents 12 months of marketplace activity across 6 major US metros.

## Business Context
The dataset captures the key dynamics of marketplace liquidity:
- **Supply**: Venue listings available for booking
- **Demand**: User searches for venues
- **Liquidity**: The balance between supply and demand that enables successful transactions

## Tables

### 1. listings
Represents venues available for rent on the platform.

| Column | Type | Description | Business Significance |
|--------|------|-------------|----------------------|
| venue_id | INTEGER | Unique venue identifier | Primary key for tracking individual venues |
| host_id | INTEGER | Host/owner identifier | Links to users table; some hosts have multiple venues |
| metro_area | TEXT | City location | Key dimension for geographic analysis |
| venue_type | TEXT | Category of space | Affects pricing, demand patterns, and use cases |
| price_per_hour | FLOAT | Hourly rental rate | Core economic metric; varies by location and type |
| capacity | INTEGER | Maximum occupancy | Matching criterion for search fulfillment |
| created_date | DATE | Listing creation date | Indicates supply growth over time |
| listing_title | TEXT | Venue name/description | For identification purposes |
| is_active | BOOLEAN | Listing status | Active venues are bookable; inactive are paused |

**Venue Types**:
- `meeting_room`: Professional spaces for business meetings
- `event_space`: Larger venues for parties, conferences
- `photo_studio`: Specialized spaces for photo/video shoots
- `workshop_space`: Venues for classes, workshops
- `rooftop`: Premium outdoor spaces for events

### 2. users
Represents all platform users (hosts and guests).

| Column | Type | Description | Business Significance |
|--------|------|-------------|----------------------|
| user_id | INTEGER | Unique user identifier | Primary key for user tracking |
| user_type | TEXT | 'host' or 'guest' | Determines marketplace role |
| metro_area | TEXT | User's primary location | Influences search and booking patterns |
| signup_date | DATE | Registration date | For cohort analysis and growth tracking |
| total_bookings | INTEGER | Lifetime bookings completed | Engagement metric |

### 3. searches
Captures all venue searches performed by users.

| Column | Type | Description | Business Significance |
|--------|------|-------------|----------------------|
| search_id | INTEGER | Unique search identifier | Primary key for search tracking |
| user_id | INTEGER | Searching user | Links to users table |
| metro_area | TEXT | Search location | Demand indicator by geography |
| search_date | DATE | When search occurred | Temporal demand patterns |
| event_date | DATE | Intended event date | Lead time analysis |
| venue_type | TEXT | Type of venue sought | Demand by category |
| capacity_needed | INTEGER | Required capacity | Size requirement |
| max_price | FLOAT | Budget limit | Price sensitivity indicator |
| search_resulted_in_booking | BOOLEAN | Conversion flag | Key liquidity metric |

### 4. bookings
Represents completed venue reservations.

| Column | Type | Description | Business Significance |
|--------|------|-------------|----------------------|
| booking_id | INTEGER | Unique booking identifier | Primary key for transaction tracking |
| venue_id | INTEGER | Booked venue | Links to listings table |
| guest_id | INTEGER | Booking user | Links to users table |
| search_id | INTEGER |