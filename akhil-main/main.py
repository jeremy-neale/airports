# including modules
import matplotlib.pyplot as plt
import pandas as pd
import datetime
import seaborn as sns
import operator
import numpy as np
# import geopandas as gp
from utils import test_functions_inside
import random

import os


# Dometics airport details
airports_df = pd.read_csv("../dataset/airport_info.csv")
airports_df = airports_df.drop_duplicates(subset='AIRPORT_ID', keep='first')
airports_df = airports_df.set_index('AIRPORT_ID')
# print(airports_df.loc[10508].to_frame(), '\n')


# Dometics airlines connections
trips_df = pd.read_csv("../dataset/flights.csv")
# print('Shape of the dataframe:',trips_df.shape,'\n')
# print('Printing trips record:',trips_df[:1].T)

cities_df = pd.read_csv("../dataset/uscities.csv")
# print('Printing cities record:',cities_df[:1], '\n')

airports_df = test_functions_inside.determine_airport_size(airports_df, trips_df)

airports_df = airports_df.sort_values(by='num_connections', ascending=False).reset_index(drop=True)

airports_df = airports_df.loc[airports_df['num_connections'] > 100]

print(len(airports_df))

cities = test_functions_inside.rank_cities_for_new_airports(cities_df, airports_df, 100000, 100)

cities.to_csv("candidate_cities.csv", index=False)