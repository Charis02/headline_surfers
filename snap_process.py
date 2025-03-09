import pandas as pd
import numpy as np
from sklearn.cluster import DBSCAN
from geopy.distance import great_circle
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
import time

# Load the location data
file_path = "location_data.csv"  # Replace with your actual file path
df = pd.read_csv(file_path)
df['timestamp'] = pd.to_datetime(df['Time'])
df = df[df['timestamp'].dt.strftime('%m/%d') == '01/29']

# Extract latitude and longitude
coordinates = df["Latitude_Longitude"].str.extract(r'([-\d\.]+),\s*([-\d\.]+)')
coordinates.columns = ["Latitude", "Longitude"]
df["Latitude"] = coordinates["Latitude"].astype(float)
df["Longitude"] = coordinates["Longitude"].astype(float)

# Convert to numpy array
coords = df[["Latitude", "Longitude"]].to_numpy()
# Define the clustering model (DBSCAN) with a radius of ~50m
kms_per_radian = 6371.0088  # Earth's radius in km
epsilon = 0.005 / kms_per_radian  # 50 m radius in radians

# Apply DBSCAN
clustering = DBSCAN(eps=epsilon, min_samples=2, metric="haversine").fit(np.radians(coords))
df["Cluster"] = clustering.labels_

# After DBSCAN clustering, select representative points from each cluster
cluster_representatives = []

# Include noise points (cluster -1)
noise_points = df[df['Cluster'] == -1]
cluster_representatives.append(noise_points)

# Get one representative from each valid cluster
for cluster_id in df[df['Cluster'] != -1]['Cluster'].unique():
    cluster_points = df[df['Cluster'] == cluster_id]
    # Take the point closest to cluster centroid as representative
    centroid = cluster_points[['Latitude', 'Longitude']].mean()
    closest_point = cluster_points.iloc[((cluster_points['Latitude'] - centroid['Latitude'])**2 + 
                                       (cluster_points['Longitude'] - centroid['Longitude'])**2).argmin()]
    cluster_representatives.append(pd.DataFrame([closest_point]))

# Combine all representatives into a new DataFrame
df_representatives = pd.concat(cluster_representatives, ignore_index=True)

# After DBSCAN clustering and before saving, add reverse geocoding
def get_detailed_location(lat, lon):
    geolocator = Nominatim(user_agent="my_app")
    try:
        location = geolocator.reverse((lat, lon), language='en')
        if location and location.raw.get('address'):
            address = location.raw['address']
            # Get detailed address components
            street = address.get('road', '')
            house_number = address.get('house_number', '')
            suburb = address.get('suburb', '')
            city = address.get('city', address.get('town', address.get('village', '')))
            state = address.get('state', '')
            postcode = address.get('postcode', '')
            country = address.get('country', '')
            
            # Construct full address
            full_address = ', '.join(filter(None, [
                f"{house_number} {street}".strip(),
                suburb,
                city,
                state,
                postcode,
                country
            ]))
            
            return {
                'full_address': full_address,
                'street': f"{house_number} {street}".strip(),
                'suburb': suburb,
                'city': city,
                'state': state,
                'postcode': postcode,
                'country': country
            }
        return {
            'full_address': 'N/A',
            'street': 'N/A',
            'suburb': 'N/A',
            'city': 'N/A',
            'state': 'N/A',
            'postcode': 'N/A',
            'country': 'N/A'
        }
    except (GeocoderTimedOut, Exception) as e:
        print(f"Error geocoding {lat}, {lon}: {str(e)}")
        return {
            'full_address': f"Error: {str(e)}",
            'street': 'N/A',
            'suburb': 'N/A',
            'city': 'N/A',
            'state': 'N/A',
            'postcode': 'N/A',
            'country': 'N/A'
        }

# Add location information to the representative points
print("Adding detailed location information...")
location_details = [get_detailed_location(lat, lon) 
                   for lat, lon in zip(df_representatives['Latitude'], 
                                     df_representatives['Longitude'])]

# Add new columns to df_representatives DataFrame
for key in location_details[0].keys():
    df_representatives[key] = [d[key] for d in location_details]
    time.sleep(1)  # Respect rate limits

# Save results with detailed addresses
df_representatives.to_csv('clustered_location_data_detailed.csv', index=False)

print("Clustering and geocoding complete. Results saved to 'clustered_location_data_detailed.csv'.")
