import os
import sys
import pandas as pd
import datetime
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from geopy.distance import geodesic

# Load data and initialize graph
def load_airports_and_edges():
    airports_df = pd.read_csv("dataset/airport_info.csv")
    trips_df = pd.read_csv("dataset/flights.csv")
    
    # Create directed graph from existing airport connections
    edges = list(zip(trips_df['ORIGIN_AIRPORT_ID'], trips_df['DEST_AIRPORT_ID']))
    G = nx.DiGraph()
    G.add_edges_from(edges)
    
    return G, airports_df


# outputs the network stats
def print_network_stats(G, label="Network"):
    print(f"\n{label} Stats:")
    num_reachable_pairs = sum(1 for node in G for _ in nx.single_source_shortest_path_length(G, node))
    total_possible_pairs = len(G) * (len(G) - 1)
    connectivity = num_reachable_pairs / total_possible_pairs if total_possible_pairs > 0 else 0
    print(f"Connectivity/Reachability: {connectivity:.6%}")
    
    betweenness_centrality = nx.betweenness_centrality(G)
    avg_betweenness = sum(betweenness_centrality.values()) / len(betweenness_centrality)
    print(f"Average Betweenness Centrality: {avg_betweenness:.6f}")

    clustering_coefficient = nx.average_clustering(G.to_undirected())
    print(f"Global Clustering Coefficient: {clustering_coefficient:.6f}")
    
    stats = {
        "Connectivity/Reachability": connectivity,
        "Average Betweenness Centrality": avg_betweenness,
        "Global Clustering Coefficient": clustering_coefficient
    }

    return stats

# This outputs a graph for each new airport into output/<time>
def plot_percent_change(city_name, original_stats, updated_stats, base_dir):
    percent_changes = {
        key: ((updated_stats[key] - original_stats[key]) / original_stats[key]) * 100
        for key in original_stats.keys()
        if key not in ["Number of Nodes", "Number of Edges"]
    }

    labels = list(percent_changes.keys())
    values = list(percent_changes.values())

    x = np.arange(len(labels))

    plt.figure(figsize=(15, 9))
    plt.bar(x, values, color="skyblue", alpha=0.8)
    plt.ylabel("Percent Change (%)")
    plt.title(f"Percent Change in Network Stats for {city_name}")
    plt.xticks(x, labels, rotation=45, ha="right")
    plt.axhline(0, color="black", linewidth=0.8, linestyle="--")

    for i, v in enumerate(values):
        plt.text(
            i, v + (0.1 if v > 0 else -0.1),
            f"{v:.3f}%",
            ha="center",
            va="bottom" if v > 0 else "top",
            fontsize=9
        )

    # Save the graph
    filename = os.path.join(base_dir, f"{city_name.replace(' ', '_')}_percent_change.png")
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()

    print(f"\nPercent change graph saved as {filename}")


# Returns the 10 'best' flights from the proposed new airports
def get_best_flights_for_city(city_data, G, airports_df, num_flights=10):
    candidate_coord = (city_data['LATITUDE'], city_data['LONGITUDE'])
    candidate_airport = city_data['AIRPORT_ID']

    if pd.isna(candidate_coord[0]) or pd.isna(candidate_coord[1]):
        return []

    airports_within_2000km = airports_df[
        airports_df.apply(
            lambda x: geodesic(candidate_coord, (x['LATITUDE'], x['LONGITUDE'])).km <= 2000
            if pd.notna(x['LATITUDE']) and pd.notna(x['LONGITUDE']) else False,
            axis=1
        )
    ]

    degree_centrality = nx.degree_centrality(G)

    airports_within_2000km = airports_within_2000km.copy()
    airports_within_2000km['centrality'] = airports_within_2000km['AIRPORT_ID'].map(degree_centrality)
    degree_dict = dict(G.degree())
    airports_within_2000km['num_connections'] = airports_within_2000km['AIRPORT_ID'].map(degree_dict)

    airports_within_2000km['score'] = (
        0.7 * airports_within_2000km['centrality'] +
        0.3 * airports_within_2000km['num_connections']
    )
    airports_within_2000km = airports_within_2000km.sort_values(by='score', ascending=False)

    airports_within_2000km = airports_within_2000km.groupby('AIRPORT_ID').agg({
        'LATITUDE': 'mean',
        'LONGITUDE': 'mean',
        'score': 'max'
    }).reset_index()

    top_airports = airports_within_2000km.head(num_flights)

    return top_airports[['AIRPORT_ID', 'LATITUDE', 'LONGITUDE']].to_dict('records')

# adds the 10 proposed flights to a copy of the graph
def add_city_and_flights(city_data, G, top_airports):
    candidate_airport = city_data['AIRPORT_ID']
    G = G.copy()
    G.add_node(candidate_airport)

    for airport in top_airports:
        airport_id = airport['AIRPORT_ID']
        G.add_edge(candidate_airport, airport_id)
        G.add_edge(airport_id, candidate_airport)
    
    return G

# takes the 10 proposed flights and gets the new stats and graph
def process_city(city_data, G, top_airports, base_dir, original_stats):
    city_name = city_data['DISPLAY_AIRPORT_NAME']

    updated_G = add_city_and_flights(city_data, G, top_airports)

    print(f"New proposed flights for {city_name}:\n")
    for flight in top_airports:
        print(flight)
    print()

    # print the updated stats and create the graph
    updated_stats = print_network_stats(updated_G, "Updated Network with New Airport and Flights")
    plot_percent_change(city_name, original_stats, updated_stats, base_dir)


# Loops through the csv and processes each city
def main(base_dir):
    G, airports_df = load_airports_and_edges()
    candidate_csv = "candidate_cities.csv"
    candidates_df = pd.read_csv(candidate_csv)

    original_stats = print_network_stats(G, "Original Network")

    # Process each city
    line = 0
    while line < len(candidates_df):
        if len(candidates_df.iloc[line]) > 2:
            try:
                print(f'\nCity {line + 1}: {candidates_df.iloc[line]["DISPLAY_AIRPORT_CITY_NAME_FULL"]} -----------------------------------------------------------------------\n')
                top_city = candidates_df.iloc[line]

                top_flights = get_best_flights_for_city(top_city, G, airports_df, num_flights=10)
                print("Top flights to add for the new airport:", top_flights)

                process_city(top_city, G, top_flights, base_dir, original_stats)
            except Exception as e:
                print(e)
        line += 1

    print("\nAll cities processed.")


# Starts the script

current_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
base_dir = 'output/' + current_time

# Create output directory
os.makedirs(base_dir, exist_ok=True)

# File for logging output
filename = os.path.join(base_dir, 'airport_analysis.txt')
print('running...')

with open(filename, 'w') as f:
    sys.stdout = f
    try:
        print('Analyzing the cities from candidate_cities.csv')
        main(base_dir)
    finally:
        sys.stdout = sys.__stdout__

print('finished.')
