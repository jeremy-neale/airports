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

# Function to print network stats
def print_network_stats(G, label="Original Network"):
    print("printing " + label + " stats...")
    num_nodes = len(G.nodes())
    num_edges = len(G.edges())
    in_degree_avg = sum(nx.in_degree_centrality(G).values()) / len(G)
    out_degree_avg = sum(nx.out_degree_centrality(G).values()) / len(G)
    betweenness_avg = sum(nx.betweenness_centrality(G).values()) / len(G)
    
    print(f"{label} Stats:")
    print(f"Number of nodes: {num_nodes}")
    print(f"Number of edges: {num_edges}")
    print(f"Average in-degree centrality: {in_degree_avg}")
    print(f"Average out-degree centrality: {out_degree_avg}")
    print(f"Average betweenness centrality: {betweenness_avg}")
    print()

def get_best_flights_for_city(city_data, G, airports_df, num_flights=10):
    """
    Determine the best flights to add for a new airport in a candidate city.
    """
    candidate_coord = (city_data['LATITUDE'], city_data['LONGITUDE'])
    candidate_airport = city_data['AIRPORT_ID']

    # Skip if coordinates are missing
    if pd.isna(candidate_coord[0]) or pd.isna(candidate_coord[1]):
        return []

    # Find nearby airports (within 2000 km)
    airports_within_2000km = airports_df[
        airports_df.apply(
            lambda x: geodesic(candidate_coord, (x['LATITUDE'], x['LONGITUDE'])).km <= 2000
            if pd.notna(x['LATITUDE']) and pd.notna(x['LONGITUDE']) else False,
            axis=1
        )
    ]

    # Compute centrality and connections
    degree_centrality = nx.degree_centrality(G)
    airports_within_2000km.loc[:, 'centrality'] = airports_within_2000km['AIRPORT_ID'].map(degree_centrality)

    # Compute num_connections based on graph degree
    degree_dict = dict(G.degree())  # Total degree (in + out)
    airports_within_2000km.loc[:, 'num_connections'] = airports_within_2000km['AIRPORT_ID'].map(degree_dict)

    # Sort airports by centrality and num_connections
    airports_within_2000km = airports_within_2000km.sort_values(
        by=['centrality', 'num_connections'], ascending=False
    )

    # Select top N airports for connections
    top_airports = airports_within_2000km.head(num_flights)

    return top_airports[['AIRPORT_ID', 'LATITUDE', 'LONGITUDE']].to_dict('records')

# Function to add the city and print the updated stats
def add_city_and_print_stats(city_data, G, top_airports):
    # Print original network stats
    print_network_stats(G, "Original Network")
    
    # Add the city and flights to the graph
    updated_G = add_city_and_flights(city_data, G, top_airports)
    
    # Print the new proposed flights
    print(f"New proposed flights for {city_data['DISPLAY_AIRPORT_NAME']}:")
    for flight in top_airports:
        print(flight)
    print()
    
    # Print updated network stats
    print_network_stats(updated_G, "Updated Network with New Airport and Flights")
    
    return updated_G


def add_city_and_flights(city_data, G, top_airports):
    """
    Add a candidate city to the network with the proposed flights.
    
    Parameters:
        city_data (pd.Series): Data for the candidate city.
        G (nx.DiGraph): Flight network graph.
        top_airports (list): Best airports to connect the city to.
    
    Returns:
        nx.DiGraph: Updated flight network graph.
    """
    candidate_airport = city_data['AIRPORT_ID']
    G = G.copy()
    G.add_node(candidate_airport)

    # Add connections to top airports
    for airport in top_airports:
        airport_id = airport['AIRPORT_ID']
        G.add_edge(candidate_airport, airport_id)
        G.add_edge(airport_id, candidate_airport)
    
    return G


# Load existing flight network and data
G, airports_df = load_airports_and_edges()

# Load the candidate cities CSV
candidate_csv = "candidate_cities.csv"
candidates_df = pd.read_csv(candidate_csv)

# Select the top city (assuming the CSV is already sorted by rank)
top_city = candidates_df.iloc[0]

# Get the best flights to add for the top city
top_flights = get_best_flights_for_city(top_city, G, airports_df, num_flights=10)
print("Top flights to add for the new airport:", top_flights)

# Add the city and its proposed flights to the network
updated_G = add_city_and_print_stats(top_city, G, top_flights)



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
