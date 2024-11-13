# including modules
import matplotlib.pyplot as plt
import pandas as pd
import datetime
import seaborn as sns
import operator
import numpy as np
import geopandas as gp
from utils import airtraffic_helpers
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

# Helper function to get centrality score for a candidate city
def get_score(city_data, G):
    # Create a temporary graph to add the new city
    temp_G = G.copy()
    
    # Add the new city as a node, along with its potential connections
    # Here, example connections are added from city_data['ORIGIN_AIRPORT_ID'] to other cities
    temp_G.add_node(city_data['AIRPORT_ID'])
    
    # Example: connect to high centrality nodes (customize as needed)
    # temp_G.add_edge(city_data['AIRPORT_ID'], high_centrality_airport) # Add relevant edges
    
    # Calculate centrality measures
    in_degree_centrality = nx.in_degree_centrality(temp_G)
    out_degree_centrality = nx.out_degree_centrality(temp_G)
    betweenness_centrality = nx.betweenness_centrality(temp_G)
    
    # Get scores for the new city
    scores = {
        "city_id": city_data['AIRPORT_ID'],
        "in_degree_centrality": in_degree_centrality[city_data['AIRPORT_ID']],
        "out_degree_centrality": out_degree_centrality[city_data['AIRPORT_ID']],
        "betweenness_centrality": betweenness_centrality[city_data['AIRPORT_ID']],
    }
    
    return scores

# Main function to get scores for all candidate cities
def get_all_city_scores(candidate_csv, G):
    candidate_df = pd.read_csv(candidate_csv)
    all_scores = []
    
    for _, city_data in candidate_df.iterrows():
        # Get centrality scores for each city independently
        city_score = get_score(city_data, G)
        all_scores.append(city_score)
    
    return all_scores



# Load existing airport network graph and dataset
G, airports_df = load_airports_and_edges()

# Evaluate each candidate city in the new cities CSV file
candidate_csv = "candidate_cities.csv"
#all_city_scores = get_all_city_scores(candidate_csv, G)


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