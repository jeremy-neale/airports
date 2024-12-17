import pandas as pd
import numpy as np
import geopandas as gp
from sklearn.preprocessing import MinMaxScaler, StandardScaler
import matplotlib.pyplot as plt
from shapely.geometry import Point

# load map of USA from shape file
SHAPEFILE_PATH = './shapefiles/tl_2024_us_state.shp'
usa_map = gp.read_file(SHAPEFILE_PATH)

# only include main 50 states
not_main_50 = ['VI','MP','GU','AS','PR']
for n in not_main_50:
    usa_map = usa_map[usa_map.STUSPS != n]

# cut off Alaska's western islands
cities_df = pd.read_csv('../dataset/uscities.csv')
east_cutoff = -48.378977
west_cutoff = -178.281323
cities_df = cities_df[cities_df['lng'] <= east_cutoff]
cities_df = cities_df[cities_df['lng'] >= west_cutoff]

# normalize and plot city population data
data_points = [Point(xy) for xy in zip(cities_df['lat'], cities_df['lng'])]
scaler = MinMaxScaler()
population_norm = scaler.fit_transform(cities_df[['population']])
population_norm = pd.Series(population_norm.flatten())
usa_map.plot(color='white', edgecolor='black', figsize=(15,9))

# create the heatmap
latitudes = cities_df['lat'].tolist()
longitudes = cities_df['lng'].tolist()
heatmap, xedges, yedges = np.histogram2d(latitudes, longitudes, bins=150, weights=population_norm)
plt.imshow(
    heatmap,
    cmap='rainbow',
    extent=[yedges[0], yedges[-1], xedges[-1], xedges[0]],
    zorder=2,
    alpha=0.8,
    interpolation='quadric',
    vmax=0.5
)

# format output
plt.gca().get_xaxis().set_visible(False)
plt.gca().get_yaxis().set_visible(False)
plt.title("Population Heatmap")
plt.gca().patch.set_facecolor("black")
plt.gca().invert_yaxis()
plt.colorbar()
plt.show()
