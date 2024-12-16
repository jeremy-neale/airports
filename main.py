import pandas as pd
import networkx as nx

# Dometics airport details
airports_df = pd.read_csv('dataset/airport_info.csv')
print('Shape of airport_info:', airports_df.shape)
print('Example record:', airports_df[:1].T)

# Dometics airlines connections
flights_df = pd.read_csv('dataset/flights.csv')
print('\n=================')
print('Shape of flights:', flights_df.shape)
print('Example record:', flights_df[:1].T)

# convert connections to directed edges
edges = list(zip(flights_df['ORIGIN_AIRPORT_ID'], flights_df['DEST_AIRPORT_ID']))

# creating directed graphs based on airports and their connections
G = nx.DiGraph()
G.add_edges_from(edges)

# printing the total number of nodes and edges of directed graph
print('Total number of airports:', len(list(G.nodes)))
print('Total number of connections:', len(list(G.edges)))

# find network density
print('Network density:', nx.density(G))
