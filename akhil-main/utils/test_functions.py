# Generate 10 cities you want to add

# Average connections -> airports

# factor in nearest hub airports / distance to other cities to that have other airports


import pandas as pd
import math



import pandas as pd
from geopy.distance import geodesic

# Find dictionary about the states and neighboring states

# Draw some visualizations of the data -> 


"""
Create a function that determines the size of the airports based on the number of incoming/outgoing carriers it has

Parameters:
    airports_df
    trips_df

Returns:
    pd.Dataframe (airports_df) with added column determining the rank of the airport based on size

"""

def determine_airport_size(airports_df, trips_df):

    airports_df["num_connections"] = 0

    for index, airport in airports_df.iterrows():

        num_connections = len(trips_df.loc[trips_df['ORIGIN'] == airport['AIRPORT']]) + len(trips_df.loc[trips_df['DEST'] == airport['AIRPORT']])
        airports_df.at[index, 'num_connections'] = num_connections        

    return airports_df


"""
Rank US cities for potential new airport locations based on population and proximity to existing airports.

Parameters:
    cities_df (pd.DataFrame): DataFrame containing US cities with 'city', 'state', 'population', 'latitude', 'longitude'.
    airports_df (pd.DataFrame): DataFrame containing existing airports with 'airport_name', 'latitude', 'longitude'.
    population_threshold (int): Minimum population for a city to be considered.
    distance_threshold (float): Minimum distance (in miles) from existing airports to consider a city underserved.

Returns:
    pd.DataFrame: Ranked list of cities for potential new airport locations.
"""
def rank_cities_for_new_airports(cities_df, airports_df, population_threshold, distance_threshold):
    
    def find_nearest_airport(city_lat, city_lon):
        """
        Find the distance to the nearest airport for a given city location.
        """
        min_distance = float('inf')
        for _, airport in airports_df.iterrows():
            airport_location = (airport['LATITUDE'], airport['LONGITUDE'])
            city_location = (city_lat, city_lon)
            if(not math.isnan(airport_location[0]) and not math.isnan(airport_location[1])):
                distance = geodesic(city_location, airport_location).miles
                if distance < min_distance:
                    min_distance = distance
        return min_distance

    # Filter cities based on the population threshold
    filtered_cities = cities_df[cities_df['population'] >= population_threshold]

    # Calculate the nearest airport distance for each city
    filtered_cities['nearest_airport_distance'] = filtered_cities.apply(
        lambda row: find_nearest_airport(row['lat'], row['lng']), axis=1
    )

    # Filter cities that are farther away from existing airports than the distance threshold
    underserved_cities = filtered_cities[filtered_cities['nearest_airport_distance'] >= distance_threshold]

    # Rank cities based on population and distance from the nearest airport
    underserved_cities['rank_score'] = underserved_cities['population'] * underserved_cities['nearest_airport_distance']
    ranked_cities = underserved_cities.sort_values(by='rank_score', ascending=False)

    # Select relevant columns for the output
    ranked_cities = ranked_cities[['city', 'state_name', 'population', 'nearest_airport_distance', 'rank_score']]

    return ranked_cities.reset_index(drop=True)

# Example usage:
# cities_df = pd.read_csv('us_cities.csv')
# airports_df = pd.read_csv('us_airports.csv')
# result = rank_cities_for_new_airports(cities_df, airports_df)
# print(result)
