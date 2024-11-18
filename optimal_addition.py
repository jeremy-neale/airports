# including modules
import matplotlib.pyplot as plt
import pandas as pd
import datetime
import seaborn as sns
import operator
import numpy as np
import geopandas as gp
from utils import airtraffic_helpers
from geopy.distance import geodesic
import networkx as nx
# import community
import random
from shapely.geometry import Point

import pandas as pd
import networkx as nx

# Example of loading your existing graph data
def load_airports_and_edges():
    airports_df = pd.read_csv("dataset/288804893_T_MASTER_CORD.csv")
    trips_df = pd.read_csv("dataset/288798530_T_T100D_MARKET_ALL_CARRIER.csv")
    
    # Create directed graph from existing airport connections
    edges = list(zip(trips_df['ORIGIN_AIRPORT_ID'], trips_df['DEST_AIRPORT_ID']))
    G = nx.DiGraph()
    G.add_edges_from(edges)
    
    return G, airports_df



def haversine_distance(coord1, coord2):
    if pd.isna(coord1[0]) or pd.isna(coord1[1]) or pd.isna(coord2[0]) or pd.isna(coord2[1]):
        raise ValueError("Coordinates must not contain NaN values.")
    return geodesic(coord1, coord2).km


def get_score(city_data, G, airports_df):
    """
    Calculate centrality measures for a candidate city.
    Integrate the city realistically by connecting it to nearby high-degree airports.
    
    Parameters:
        city_data (pd.Series): Row containing candidate city data.
        G (nx.DiGraph): Original directed graph.
        airports_df (pd.DataFrame): DataFrame containing airport coordinates.
        
    Returns:
        dict: Centrality measures for the candidate city.
    """
    # Extract candidate coordinates
    candidate_coord = (city_data['LATITUDE'], city_data['LONGITUDE'])
    candidate_airport = city_data['AIRPORT_ID']
    
    # Skip candidate if coordinates are missing
    if pd.isna(candidate_coord[0]) or pd.isna(candidate_coord[1]):
        return {
            "city_id": candidate_airport,
            "in_degree_centrality": None,
            "out_degree_centrality": None,
            "betweenness_centrality": None,
        }

    # Find airports within 2000 km
    airports_within_2000km = airports_df[
        airports_df.apply(
            lambda x: haversine_distance(candidate_coord, (x['LATITUDE'], x['LONGITUDE'])) <= 2000
            if pd.notna(x['LATITUDE']) and pd.notna(x['LONGITUDE']) else False,
            axis=1
        )
    ]

    # Get top 4 airports by degree centrality within 2000 km
    degree_centrality = nx.degree_centrality(G)
    # Create a copy of the filtered DataFrame to avoid SettingWithCopyWarning
    airports_within_2000km = airports_df.loc[
        airports_df.apply(
            lambda x: haversine_distance(candidate_coord, (x['LATITUDE'], x['LONGITUDE'])) <= 2000
            if pd.notna(x['LATITUDE']) and pd.notna(x['LONGITUDE']) else False,
            axis=1
        )
    ].copy()  # Explicitly make a copy

    # Add a new column for centrality
    airports_within_2000km['centrality'] = airports_within_2000km['AIRPORT_ID'].map(degree_centrality)

    top_airports = airports_within_2000km.nlargest(4, 'centrality')['AIRPORT_ID']

    # Create a temporary graph to add the new city
    temp_G = G.copy()
    temp_G.add_node(candidate_airport)

    # Add connections to the top airports
    for airport_id in top_airports:
        temp_G.add_edge(candidate_airport, airport_id)
        temp_G.add_edge(airport_id, candidate_airport)

    # Calculate centrality measures
    in_degree_centrality = nx.in_degree_centrality(temp_G)
    out_degree_centrality = nx.out_degree_centrality(temp_G)
    betweenness_centrality = nx.betweenness_centrality(temp_G)

    # Get scores for the new city
    scores = {
        "city_id": candidate_airport,
        "in_degree_centrality": in_degree_centrality.get(candidate_airport, 0),
        "out_degree_centrality": out_degree_centrality.get(candidate_airport, 0),
        "betweenness_centrality": betweenness_centrality.get(candidate_airport, 0),
    }

    return scores



def calculate_centrality_for_candidates(candidate_csv, G, airports_df):
    """
    Calculate centrality measures for candidate cities in a CSV file.
    
    Parameters:
        candidate_csv (str): Path to the CSV file containing candidate city data.
        G (nx.DiGraph): Original directed graph representing the airport network.
    
    Returns:
        pd.DataFrame: DataFrame containing the centrality measures for each candidate city.
    """
    # Load candidate city data
    candidates_df = pd.read_csv(candidate_csv)
    
    # List to store centrality scores for each candidate city
    all_city_scores = []
    
    for _, city_data in candidates_df.iterrows():
        # Add candidate city to a temporary graph and calculate centrality scores
        scores = get_score(city_data, G, airports_df)
        all_city_scores.append(scores)
    
    # Convert results to a DataFrame
    scores_df = pd.DataFrame(all_city_scores)
    return scores_df




# Load existing airport network graph and dataset
G, airports_df = load_airports_and_edges()

# Clean the airports_df dataset
airports_df = airports_df.dropna(subset=['LATITUDE', 'LONGITUDE'])


# Assuming candidate_csv contains a column 'AIRPORT_ID' for city identifiers
candidate_csv = "candidate_cities.csv"
centrality_results = calculate_centrality_for_candidates(candidate_csv, G, airports_df)

# Save the results to a CSV file or display them
centrality_results.to_csv("candidate_centrality_scores.csv", index=False)
print(centrality_results)




# in_degree_avg = sum(nx.in_degree_centrality(G).values()) / len(G)
# out_degree_avg = sum(nx.out_degree_centrality(G).values()) / len(G)
# betweenness_avg = sum(nx.betweenness_centrality(G).values()) / len(G)

# print("Average in-degree centrality:", in_degree_avg)
# print("Average out-degree centrality:", out_degree_avg)
# print("Average betweenness centrality:", betweenness_avg)

# Average in-degree (incoming flights per airport): 15.391498881431767
# Median in-degree (incoming flights per airport): 4.0
# Average out-degree (outgoing flights per airport): 15.391498881431767
# Median out-degree (outgoing flights per airport): 4.0
# Average total degree (total connections per airport): 30.782997762863534
# Median total degree (total connections per airport): 8.0

# Average flight distance: 1244.53 km
# Median flight distance: 984.33 km
