import pandas as pd
import numpy as np
from faker import Faker
import random
from datetime import datetime, timedelta
import sqlite3
import os

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)
fake = Faker()
Faker.seed(42)

# Configuration
START_DATE = datetime(2024, 1, 1)
END_DATE = datetime(2024, 12, 31)
DB_PATH = 'data/peerspace_marketplace.db'

# Metro areas with their characteristics
METROS = {
    'San Francisco': {'supply_level': 'high', 'demand_level': 'high', 'avg_price': 150},
    'Los Angeles': {'supply_level': 'high', 'demand_level': 'medium', 'avg_price': 120},
    'New York': {'supply_level': 'medium', 'demand_level': 'high', 'avg_price': 200},
    'Chicago': {'supply_level': 'medium', 'demand_level': 'medium', 'avg_price': 90},
    'Austin': {'supply_level': 'low', 'demand_level': 'high', 'avg_price': 100},
    'Miami': {'supply_level': 'low', 'demand_level': 'medium', 'avg_price': 110}
}

# Venue types and their characteristics
VENUE_TYPES = {
    'meeting_room': {'base_capacity': 10, 'price_multiplier': 1.0, 'popularity': 0.3},
    'event_space': {'base_capacity': 50, 'price_multiplier': 1.5, 'popularity': 0.25},
    'photo_studio': {'base_capacity': 15, 'price_multiplier': 1.8, 'popularity': 0.2},
    'workshop_space': {'base_capacity': 30, 'price_multiplier': 1.2, 'popularity': 0.15},
    'rooftop': {'base_capacity': 75, 'price_multiplier': 2.0, 'popularity': 0.1}
}

def generate_listings():
    """Generate venue listings with realistic distribution across metros"""
    print("Generating listings...")
    
    listings = []
    venue_id = 1
    host_id = 1
    
    for metro, characteristics in METROS.items():
        # Determine number of venues based on supply level
        if characteristics['supply_level'] == 'high':
            num_venues = random.randint(150, 200)
        elif characteristics['supply_level'] == 'medium':
            num_venues = random.randint(80, 120)
        else:  # low
            num_venues = random.randint(30, 60)
        
        for _ in range(num_venues):
            venue_type = random.choices(
                list(VENUE_TYPES.keys()),
                weights=[v['popularity'] for v in VENUE_TYPES.values()]
            )[0]
            
            # Calculate price with some variance
            base_price = characteristics['avg_price']
            type_multiplier = VENUE_TYPES[venue_type]['price_multiplier']
            price_variance = random.uniform(0.7, 1.3)
            price_per_hour = round(base_price * type_multiplier * price_variance, 0)
            
            # Calculate capacity with variance
            base_capacity = VENUE_TYPES[venue_type]['base_capacity']
            capacity = int(base_capacity * random.uniform(0.5, 2.0))
            
            # Random creation date in the past 2 years
            days_ago = random.randint(0, 730)
            created_date = END_DATE - timedelta(days=days_ago)
            
            listings.append({
                'venue_id': venue_id,
                'host_id': host_id,
                'metro_area': metro,
                'venue_type': venue_type,
                'price_per_hour': price_per_hour,
                'capacity': capacity,
                'created_date': created_date,
                'listing_title': f"{venue_type.replace('_', ' ').title()} in {metro}",
                'is_active': random.random() > 0.1  # 90% active
            })
            
            venue_id += 1
            # Some hosts have multiple venues
            if random.random() > 0.7:
                host_id += 1
    
    return pd.DataFrame(listings)

def generate_users(num_listings):
    """Generate users (both hosts and guests)"""
    print("Generating users...")
    
    users = []
    
    # Generate hosts (from listings)
    num_hosts = num_listings // 2  # Assume some hosts have multiple venues
    for host_id in range(1, num_hosts + 1):
        metro = random.choice(list(METROS.keys()))
        signup_date = START_DATE + timedelta(days=random.randint(0, 365))
        
        users.append({
            'user_id': host_id,
            'user_type': 'host',
            'metro_area': metro,
            'signup_date': signup_date,
            'total_bookings': 0  # Will update later
        })
    
    # Generate guests (more guests than hosts)
    num_guests = num_hosts * 5
    for i in range(num_guests):
        guest_id = num_hosts + i + 1
        metro = random.choice(list(METROS.keys()))
        signup_date = START_DATE + timedelta(days=random.randint(0, 365))
        
        users.append({
            'user_id': guest_id,
            'user_type': 'guest',
            'metro_area': metro,
            'signup_date': signup_date,
            'total_bookings': 0  # Will update later
        })
    
    return pd.DataFrame(users)

def generate_searches(users_df):
    """Generate search data with realistic patterns"""
    print("Generating searches...")
    
    searches = []
    search_id = 1
    
    guests = users_df[users_df['user_type'] == 'guest']
    
    # Generate searches for each day
    current_date = START_DATE
    while current_date <= END_DATE:
        # More searches on weekdays, spike on Tuesdays/Thursdays
        if current_date.weekday() in [1, 3]:  # Tuesday, Thursday
            daily_searches = random.randint(80, 120)
        elif current_date.weekday() in [5, 6]:  # Weekend
            daily_searches = random.randint(30, 50)
        else:
            daily_searches = random.randint(50, 80)
        
        # Seasonal adjustment (more in spring/fall)
        month = current_date.month
        if month in [3, 4, 5, 9, 10, 11]:  # Peak seasons
            daily_searches = int(daily_searches * 1.3)
        elif month in [12, 1, 2]:  # Winter slowdown
            daily_searches = int(daily_searches * 0.7)
        
        for _ in range(daily_searches):
            user = guests.sample(1).iloc[0]
            
            # Users often search in their metro (70%) or popular metros (30%)
            if random.random() < 0.7:
                search_metro = user['metro_area']
            else:
                # Weight by demand level
                metro_weights = []
                for metro, chars in METROS.items():
                    if chars['demand_level'] == 'high':
                        metro_weights.append(3)
                    elif chars['demand_level'] == 'medium':
                        metro_weights.append(2)
                    else:
                        metro_weights.append(1)
                search_metro = random.choices(list(METROS.keys()), weights=metro_weights)[0]
            
            venue_type = random.choices(
                list(VENUE_TYPES.keys()),
                weights=[v['popularity'] for v in VENUE_TYPES.values()]
            )[0]
            
            base_capacity = VENUE_TYPES[venue_type]['base_capacity']
            capacity_needed = int(base_capacity * random.uniform(0.5, 1.5))
            
            # Price expectations based on metro
            metro_price = METROS[search_metro]['avg_price']
            max_price = metro_price * random.uniform(0.8, 2.0)
            
            # Event date is typically 1-30 days in future
            event_date = current_date + timedelta(days=random.randint(1, 30))
            
            searches.append({
                'search_id': search_id,
                'user_id': user['user_id'],
                'metro_area': search_metro,
                'search_date': current_date,
                'event_date': event_date,
                'venue_type': venue_type,
                'capacity_needed': capacity_needed,
                'max_price': max_price,
                'search_resulted_in_booking': False  # Will update later
            })
            
            search_id += 1
        
        current_date += timedelta(days=1)
    
    return pd.DataFrame(searches)

def generate_bookings(listings_df, searches_df, users_df):
    """Generate bookings based on searches and liquidity"""
    print("Generating bookings...")
    
    bookings = []
    booking_id = 1
    
    # For each search, determine if it converts to a booking
    for _, search in searches_df.iterrows():
        # Get matching venues
        matching_venues = listings_df[
            (listings_df['metro_area'] == search['metro_area']) &
            (listings_df['venue_type'] == search['venue_type']) &
            (listings_df['capacity'] >= search['capacity_needed'] * 0.8) &
            (listings_df['price_per_hour'] <= search['max_price']) &
            (listings_df['is_active'] == True)
        ]
        
        if len(matching_venues) == 0:
            continue  # No matching venues - unfulfilled demand
        
        # Conversion probability based on liquidity
        metro_demand = METROS[search['metro_area']]['demand_level']
        metro_supply = METROS[search['metro_area']]['supply_level']
        
        # Calculate conversion probability
        if metro_supply == 'low' and metro_demand == 'high':
            conversion_prob = 0.3  # Low liquidity - hard to book
        elif metro_supply == 'high' and metro_demand == 'low':
            conversion_prob = 0.7  # High liquidity - easy to book
        else:
            conversion_prob = 0.5  # Balanced
        
        # Add some randomness for day of week
        if search['event_date'].weekday() in [4, 5]:  # Friday/Saturday
            conversion_prob *= 0.8  # Harder to book on popular days
        
        if random.random() < conversion_prob:
            # Select a venue (prefer lower prices)
            venue = matching_venues.sample(1, weights=1/matching_venues['price_per_hour']).iloc[0]
            
            # Determine booking duration
            if venue['venue_type'] == 'meeting_room':
                hours_booked = random.choice([2, 3, 4])
            elif venue['venue_type'] == 'photo_studio':
                hours_booked = random.choice([4, 6, 8])
            else:
                hours_booked = random.choice([3, 4, 5, 6])
            
            total_amount = venue['price_per_hour'] * hours_booked
            
            # Booking typically happens 1-3 days after search
            booking_date = search['search_date'] + timedelta(days=random.randint(1, 3))
            
            # Determine status (most are completed)
            status_choices = ['completed', 'completed', 'completed', 'cancelled', 'pending']
            status = random.choice(status_choices)
            
            bookings.append({
                'booking_id': booking_id,
                'venue_id': venue['venue_id'],
                'guest_id': search['user_id'],
                'search_id': search['search_id'],
                'booking_date': booking_date,
                'event_date': search['event_date'],
                'hours_booked': hours_booked,
                'total_amount': total_amount,
                'status': status
            })
            
            booking_id += 1
            
            # Mark search as converted
            searches_df.loc[searches_df['search_id'] == search['search_id'], 'search_resulted_in_booking'] = True
    
    return pd.DataFrame(bookings)

def calculate_metrics_summary(listings_df, bookings_df, searches_df):
    """Calculate and print summary metrics"""
    print("\n" + "="*50)
    print("DATA GENERATION SUMMARY")
    print("="*50)
    
    print(f"\nTotal listings: {len(listings_df)}")
    print(f"Total users: {len(users_df)}")
    print(f"Total searches: {len(searches_df)}")
    print(f"Total bookings: {len(bookings_df)}")
    
    print("\nMetro Distribution:")
    for metro in METROS.keys():
        metro_listings = len(listings_df[listings_df['metro_area'] == metro])
        metro_bookings = len(bookings_df[bookings_df['venue_id'].isin(
            listings_df[listings_df['metro_area'] == metro]['venue_id']
        )])
        metro_searches = len(searches_df[searches_df['metro_area'] == metro])
        conversion_rate = (metro_bookings / metro_searches * 100) if metro_searches > 0 else 0
        
        print(f"  {metro}:")
        print(f"    Listings: {metro_listings}")
        print(f"    Searches: {metro_searches}")
        print(f"    Bookings: {metro_bookings}")
        print(f"    Conversion Rate: {conversion_rate:.1f}%")
    
    print("\nVenue Type Distribution:")
    for venue_type in VENUE_TYPES.keys():
        type_count = len(listings_df[listings_df['venue_type'] == venue_type])
        print(f"  {venue_type}: {type_count} venues")
    
    # Calculate overall conversion rate
    overall_conversion = (len(searches_df[searches_df['search_resulted_in_booking'] == True]) / 
                         len(searches_df) * 100)
    print(f"\nOverall Search-to-Booking Conversion Rate: {overall_conversion:.1f}%")

def save_to_database(listings_df, users_df, searches_df, bookings_df):
    """Save all dataframes to SQLite database"""
    print("\nSaving to database...")
    
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    # Connect to database
    conn = sqlite3.connect(DB_PATH)
    
    # Save each dataframe
    listings_df.to_sql('listings', conn, if_exists='replace', index=False)
    users_df.to_sql('users', conn, if_exists='replace', index=False)
    searches_df.to_sql('searches', conn, if_exists='replace', index=False)
    bookings_df.to_sql('bookings', conn, if_exists='replace', index=False)
    
    # Create indexes for better query performance
    cursor = conn.cursor()
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_listings_metro ON listings(metro_area)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_bookings_venue ON bookings(venue_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_bookings_date ON bookings(event_date)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_searches_metro ON searches(metro_area)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_searches_date ON searches(search_date)")
    
    conn.commit()
    conn.close()
    
    print(f"Database saved to: {DB_PATH}")

def save_to_csv(listings_df, users_df, searches_df, bookings_df):
    """Also save as CSV files for easy inspection"""
    print("Saving CSV files...")
    
    listings_df.to_csv('data/listings.csv', index=False)
    users_df.to_csv('data/users.csv', index=False)
    searches_df.to_csv('data/searches.csv', index=False)
    bookings_df.to_csv('data/bookings.csv', index=False)
    
    print("CSV files saved to data/ directory")

# Main execution
if __name__ == "__main__":
    print("Starting Peerspace marketplace data generation...")
    print(f"Generating data from {START_DATE.date()} to {END_DATE.date()}")
    
    # Generate all datasets
    listings_df = generate_listings()
    users_df = generate_users(len(listings_df))
    searches_df = generate_searches(users_df)
    bookings_df = generate_bookings(listings_df, searches_df, users_df)
    
    # Update user total bookings
    guest_bookings = bookings_df[bookings_df['status'] == 'completed'].groupby('guest_id').size()
    for guest_id, count in guest_bookings.items():
        users_df.loc[users_df['user_id'] == guest_id, 'total_bookings'] = count
    
    # Calculate and display metrics
    calculate_metrics_summary(listings_df, bookings_df, searches_df)
    
    # Save to database and CSV
    save_to_database(listings_df, users_df, searches_df, bookings_df)
    save_to_csv(listings_df, users_df, searches_df, bookings_df)
    
    print("\n✅ Data generation complete!")
    print("Next steps:")
    print("1. Check the data/ directory for generated files")
    print("2. Open the SQLite database to verify tables")
    print("3. Proceed to Step 2: SQL Analysis")