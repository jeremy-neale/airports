# including modules
import matplotlib.pyplot as plt
import pandas as pd
import datetime
import seaborn as sns
import operator
import numpy as np
# import geopandas as gp
from utils import airtraffic_helpers
import networkx as nx
# import community
import random
from shapely.geometry import Point

# Dometics airport details
airports_df = pd.read_csv("{}/dataset/288804893_T_MASTER_CORD.csv".format(dir_path))
print('Shape of the dataframe:',airports_df.shape,'\n')
print('Printing one record:',airports_df[:1].T)

# Dometics airlines connections
trips_df = pd.read_csv("{}/dataset/288798530_T_T100D_MARKET_ALL_CARRIER.csv".format(dir_path))
print('Shape of the dataframe:',trips_df.shape,'\n')
print('Printing one record:',trips_df[:1].T)

# Extracting edges - we consider a connection from one airport to another as an edge.
# Note: these edges will be directed.
edges = list(zip(trips_df['ORIGIN_AIRPORT_ID'],trips_df['DEST_AIRPORT_ID']))

# creating directed and undirected graphs based on airports and their connections
G = nx.DiGraph()
G.add_edges_from(edges)
G_undirected = nx.Graph()
G_undirected.add_edges_from(edges)

# printing the total number of nodes and edges of directed graph
print('Total number of airports:',len(list(G.nodes)))
print('Total number of connections:',len(list(G.edges)))

# creating a GeoDataframe for plotting airports on a map
airport_ids = list(G.nodes)
edgelist = list(G.edges)
geo_stations = airtraffic_helpers.get_geodataframe_airports(airports_df,airport_ids)

airtraffic_helpers.plot_network(G,title="",edgealpha=0.08,node_dist=1,nodesize=20,savefig=False,figsize=(15,15))