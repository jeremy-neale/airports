# including modules
import matplotlib.pyplot as plt
import pandas as pd
from utils import candidate_helper_functions

# Dometics airport details
print('Loading in datasets...')
airports_df = pd.read_csv("dataset/airport_info.csv")
airports_df = airports_df.drop_duplicates(subset='AIRPORT_ID', keep='first')
airports_df = airports_df.set_index('AIRPORT_ID')

# Dometics airlines connections
trips_df = pd.read_csv("dataset/flights.csv")
cities_df = pd.read_csv("dataset/uscities.csv")

# Calculate airport size based on number of connections
print('Calculating airport sizes...')
airports_df = candidate_helper_functions.determine_airport_size(airports_df, trips_df)

# Sort and filter results
print('Sorting and filtering...')
airports_df = airports_df.sort_values(by='num_connections', ascending=False).reset_index(drop=True)
airports_df = airports_df.loc[airports_df['num_connections'] > 100]

# Rank cities
print('Final length:', len(airports_df))
print('Ranking cities for new airports...')
cities = candidate_helper_functions.rank_cities_for_new_airports(cities_df, airports_df, 100000, 100)

# Export
print('Exporting to candidate_cities.csv')
cities.to_csv("candidate_cities.csv", index=False)
