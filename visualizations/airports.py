import pandas as pd
import numpy as np
import geopandas as gp
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt
from shapely.geometry import Point

# load map of USA from shape file
SHAPEFILE_PATH = './shapefiles/tl_2024_us_state.shp'
usa_map = gp.read_file(SHAPEFILE_PATH)

# only include main 50 states
not_main_50 = ['VI','MP','GU','AS','PR']
for n in not_main_50:
    usa_map = usa_map[usa_map.STUSPS != n]

# remove missing values
airport_sizes_df = pd.read_csv('../dataset/airport_sizes.csv')
airport_sizes_df.dropna(subset=['LATITUDE', 'LONGITUDE'], inplace=True)
airport_sizes_df = airport_sizes_df[airport_sizes_df['AIRPORT_COUNTRY_CODE_ISO'] == 'US']

# cut off Alaska's western islands
east_cutoff = -48.378977
west_cutoff = -178.281323
airport_sizes_df = airport_sizes_df[airport_sizes_df['LONGITUDE'] <= east_cutoff]
airport_sizes_df = airport_sizes_df[airport_sizes_df['LONGITUDE'] >= west_cutoff]

# normalize airport size data
scaler = MinMaxScaler()
airport_sizes_norm = scaler.fit_transform(airport_sizes_df[['num_connections']])
airport_sizes_norm = pd.Series(airport_sizes_norm.flatten())

# plot airport size data
data_points = [Point(xy) for xy in zip(airport_sizes_df['LATITUDE'], airport_sizes_df['LONGITUDE'])]
usa_map.plot(color='white', edgecolor='black', figsize=(15,9))

# create the heatmap
latitudes = airport_sizes_df['LATITUDE'].tolist()
longitudes = airport_sizes_df['LONGITUDE'].tolist()
heatmap, xedges, yedges = np.histogram2d(latitudes, longitudes, bins=150, weights=airport_sizes_norm)
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
plt.title("Airport Heatmap")
plt.gca().patch.set_facecolor("black")
plt.gca().invert_yaxis()
plt.colorbar()
plt.show()
