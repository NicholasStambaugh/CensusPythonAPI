import matplotlib.pyplot as plt
import pandas as pd
import geopandas as gpd
from census import Census
from us import states

# Key
c = Census("Your Key Here")

mi_census = c.acs5.state_county_tract(fields=('NAME', 'C17002_001E', 'C17002_002E', 'C17002_003E', 'B01003_001E'),
                                      state_fips=states.MI.fips,
                                      county_fips="*",
                                      tract="*",
                                      year=2017,
                                      key=c
                                      )

# Create a dataframe from the census data
mi_df = pd.DataFrame(mi_census)

# Show the dataframe
print(mi_df.head(2))
print('Shape: ', mi_df.shape)

# Access shapefile of Michigan census tracts
mi_tract = gpd.read_file("https://www2.census.gov/geo/tiger/TIGER2019/TRACT/tl_2019_26_tract.zip")

# Reproject shapefile to UTM Zone 17N
mi_tract = mi_tract.to_crs(epsg = 32617)

# Print GeoDataFrame of shapefile
print(mi_tract.head(2))
print('Shape: ', mi_tract.shape)

# Check shapefile projection
print("\nThe shapefile projection is: {}".format(mi_tract.crs))

# Combine state, county, and tract columns together to create a new string and assign to new column
mi_df["GEOID"] = mi_df["state"] + mi_df["county"] + mi_df["tract"]

# Print head of dataframe
mi_df.head()

# Remove columns
mi_df = mi_df.drop(columns = ["state", "county", "tract"])

# Show updated dataframe
mi_df.head(2)

# Check column data types for census data
print("Column data types for census data:\n{}".format(mi_df.dtypes))

# Check column data types for census shapefile
print("\nColumn data types for census shapefile:\n{}".format(mi_tract.dtypes))


# Join the dataframes together
mi_merge = mi_tract.merge(mi_df, on = "GEOID")

# Show result
print(mi_merge.head(2))
print('Shape: ', mi_merge.shape)

# Create new dataframe from select columns
mi_poverty_tract = mi_merge[["STATEFP", "COUNTYFP", "TRACTCE", "GEOID", "geometry", "C17002_001E", "C17002_002E", "C17002_003E", "B01003_001E"]]

# Show dataframe
print(mi_poverty_tract.head(2))
print('Shape: ', mi_poverty_tract.shape)

# Dissolve and group the census tracts within each county and aggregate all the values together
mi_poverty_county = mi_poverty_tract.dissolve(by = 'COUNTYFP', aggfunc = 'sum')

# Show dataframe
print(mi_poverty_county.head(2))
print('Shape: ', mi_poverty_county.shape)

# Get poverty rate and store values in new column
mi_poverty_county["Poverty_Rate"] = (mi_poverty_county["C17002_002E"] + mi_poverty_county["C17002_003E"]) / mi_poverty_county["B01003_001E"] * 100

# Show dataframe
mi_poverty_county.head(2)

# Create subplots
fig, ax = plt.subplots(1, 1, figsize = (20, 20))

# Plot data
mi_poverty_county.plot(column = "Poverty_Rate",
                       ax = ax,
                       cmap = "RdPu",
                       legend = True)

# Stylize plots
plt.style.use('classic')

# Set title
ax.set_title('Poverty Rates (%) in Michigan', fontdict = {'fontsize': '25', 'fontweight' : '3'})

plt.show()