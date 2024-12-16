import pandas as pd
from geopy.distance import geodesic

def determine_airport_size(airports_df, trips_df):
    """
    Create a function that determines the size of the airports based on the number of incoming/outgoing carriers it has

    Parameters:
        airports_df
        trips_df

    Returns:
        pd.Dataframe (airports_df) with added column determining the rank of the airport based on size

    """

    airports_df["num_connections"] = 0
    for index, airport in airports_df.iterrows():
        num_origin = len(trips_df.loc[trips_df['ORIGIN'] == airport['AIRPORT']])
        num_dest = len(trips_df.loc[trips_df['DEST'] == airport['AIRPORT']])
        airports_df.at[index, 'num_connections'] = num_origin + num_dest        

    return airports_df

def rank_cities_for_new_airports(cities_df, airports_df, population_threshold, distance_threshold):
    """
    Ranks cities for potential new airport locations based on population and distance to the nearest airport.

    Parameters:
    - cities_df (pd.DataFrame): DataFrame containing city data with columns ['city', 'state_name', 'population', 'lat', 'lng'].
    - airports_df (pd.DataFrame): DataFrame containing airport data with columns ['LATITUDE', 'LONGITUDE'].
    - population_threshold (int): Minimum population for cities to be considered.
    - distance_threshold (float): Minimum distance (in miles) to classify a city as underserved.

    Returns:
    - pd.DataFrame: Ranked cities for potential new airports with relevant columns.
    """

    def find_nearest_airport(city_lat, city_lon):
        """
        Find the distance to the nearest airport for a given city location.
        """
        min_distance = float('inf')
        
        # Loop through each airport and calculate distance
        for _, airport in airports_df.iterrows():

            airport_lat, airport_lon = airport['LATITUDE'], airport['LONGITUDE']
            
            # Skip if airport coordinates are missing or invalid
            if pd.notna(airport_lat) and pd.notna(airport_lon):
                airport_location = (airport_lat, airport_lon)
                city_location = (city_lat, city_lon)
                
                try:
                    distance = geodesic(city_location, airport_location).miles
                    if distance < min_distance:
                        min_distance = distance
                except ValueError as e:
                    print(f"Error calculating distance for city {city_lat, city_lon} and airport {airport_lat, airport_lon}: {e}")
                    continue

        return min_distance

    
    # Filter cities based on the population threshold
    filtered_cities = cities_df[cities_df['population'] >= population_threshold]

    if filtered_cities.empty:
        print("No cities meet the population threshold.")
        return pd.DataFrame()  # Return an empty DataFrame if no cities meet the criteria

    # Calculate the nearest airport distance for each city
    filtered_cities['nearest_airport_distance'] = filtered_cities.apply(
        lambda row: find_nearest_airport(row['lat'], row['lng']), axis=1
    )

    # Filter cities that are underserved based on the distance threshold
    underserved_cities = filtered_cities.loc[filtered_cities['nearest_airport_distance'] >= distance_threshold]

    if underserved_cities.empty:
        print("No cities meet the distance threshold.")
        return pd.DataFrame()  # Return an empty DataFrame if no cities meet the criteria

    print(f"Number of underserved cities: {len(underserved_cities)}")

    # Rank cities based on population and distance from the nearest airport
    underserved_cities['rank_score'] = underserved_cities['population'] * underserved_cities['nearest_airport_distance']
    ranked_cities = underserved_cities.sort_values(by='rank_score', ascending=False)

      # Generate the required output format
    ranked_cities['AIRPORT_ID'] = range(20000, 20000 + len(ranked_cities))
    ranked_cities['AIRPORT'] = ranked_cities['city'] + " Municipal Airport"
    ranked_cities['DISPLAY_AIRPORT_NAME'] = ranked_cities['city'] + " Municipal Airport"
    ranked_cities['DISPLAY_AIRPORT_CITY_NAME_FULL'] = ranked_cities['city'] + ", " + ranked_cities['state_name']
    ranked_cities['AIRPORT_WAC'] = 67  # Assuming constant for this example
    ranked_cities['AIRPORT_COUNTRY_NAME'] = "United States"
    ranked_cities['AIRPORT_COUNTRY_CODE_ISO'] = "US"
    ranked_cities['AIRPORT_STATE_NAME'] = ranked_cities['state_name']
    ranked_cities['AIRPORT_STATE_CODE'] = ranked_cities['state_name'].apply(lambda x: x[:2].upper())  # Simplified
    ranked_cities['AIRPORT_STATE_FIPS'] = "06"  # Placeholder
    ranked_cities['CITY_MARKET_ID'] = range(40000, 40000 + len(ranked_cities))
    ranked_cities['DISPLAY_CITY_MARKET_NAME_FULL'] = ranked_cities['city'] + ", " + ranked_cities['state_name']
    ranked_cities['CITY_MARKET_WAC'] = 67
    ranked_cities['LAT_DEGREES'] = ranked_cities['lat'].astype(int)
    ranked_cities['LAT_HEMISPHERE'] = ranked_cities['lat'].apply(lambda x: "N" if x >= 0 else "S")
    ranked_cities['LAT_MINUTES'] = 0  # Placeholder
    ranked_cities['LAT_SECONDS'] = 0  # Placeholder
    ranked_cities['LATITUDE'] = ranked_cities['lat']
    ranked_cities['LON_DEGREES'] = ranked_cities['lng'].astype(int)
    ranked_cities['LON_HEMISPHERE'] = ranked_cities['lng'].apply(lambda x: "E" if x >= 0 else "W")
    ranked_cities['LON_MINUTES'] = 0  # Placeholder
    ranked_cities['LON_SECONDS'] = 0  # Placeholder
    ranked_cities['LONGITUDE'] = ranked_cities['lng']
    ranked_cities['AIRPORT_START_DATE'] = "2024-01-01"  # Example start date
    ranked_cities['AIRPORT_THRU_DATE'] = None  # Assuming it's open-ended
    ranked_cities['AIRPORT_IS_CLOSED'] = 0  # Not closed
    ranked_cities['AIRPORT_IS_LATEST'] = 1  # Assuming latest data

    # Select relevant columns for the output
    ranked_cities = ranked_cities[[
        "AIRPORT_ID", "AIRPORT", "DISPLAY_AIRPORT_NAME", "DISPLAY_AIRPORT_CITY_NAME_FULL",
        "AIRPORT_WAC", "AIRPORT_COUNTRY_NAME", "AIRPORT_COUNTRY_CODE_ISO", "AIRPORT_STATE_NAME",
        "AIRPORT_STATE_CODE", "AIRPORT_STATE_FIPS", "CITY_MARKET_ID", "DISPLAY_CITY_MARKET_NAME_FULL",
        "CITY_MARKET_WAC", "LAT_DEGREES", "LAT_HEMISPHERE", "LAT_MINUTES", "LAT_SECONDS",
        "LATITUDE", "LON_DEGREES", "LON_HEMISPHERE", "LON_MINUTES", "LON_SECONDS",
        "LONGITUDE", "AIRPORT_START_DATE", "AIRPORT_THRU_DATE", "AIRPORT_IS_CLOSED", "AIRPORT_IS_LATEST"
    ]]

    print("Ranking and formatting completed.")
    return ranked_cities.reset_index(drop=True)
