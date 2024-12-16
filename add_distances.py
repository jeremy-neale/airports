import pandas as pd
import numpy as np
from math import radians, sin, cos, sqrt, atan2

# Load the CSV files
airports_df = pd.read_csv("dataset/airport_info.csv")
trips_df = pd.read_csv("dataset/flights.csv")

# Warn if "Distance" has already been added
if 'DISTANCE' in trips_df.columns:
    print('Warning: flights.csv already has a "Distance" column')

# Create a dictionary of airport coordinates from airports_df
airport_coords = {
    row['AIRPORT_ID']: (row['LATITUDE'], row['LONGITUDE'])
    for _, row in airports_df.iterrows()
}

# Define Haversine formula to calculate distance
def haversine_distance(origin, destination):
    lat1, lon1 = origin
    lat2, lon2 = destination
    # Convert latitude and longitude from degrees to radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    radius = 6371  # Earth radius in kilometers
    return radius * c

# Calculate distances for each flight in trips_df
distances = []
for _, row in trips_df.iterrows():
    origin_id = row['ORIGIN_AIRPORT_ID']
    dest_id = row['DEST_AIRPORT_ID']
    if origin_id in airport_coords and dest_id in airport_coords:
        origin_coords = airport_coords[origin_id]
        dest_coords = airport_coords[dest_id]
        distance = haversine_distance(origin_coords, dest_coords)
        distances.append(distance)
    else:
        distances.append(np.nan)  # Use NaN for missing coordinates

# Add distances as a new column in trips_df
trips_df['DISTANCE'] = distances

# Save the updated DataFrame to the same CSV file
trips_df.to_csv("dataset/flights.csv", index=False)

print("Updated CSV file with DISTANCE column.")
