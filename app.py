from flask import Flask, request, jsonify
import pandas as pd
from flask_cors import CORS
from sklearn.neighbors import NearestNeighbors
import numpy as np

app = Flask(__name__)

CORS(app)
# Load and prepare the data
file_path = 'location.xlsx'  # Update this with the path to your Excel file
location_data = pd.read_excel(file_path)
location_data.columns = location_data.columns.str.strip()  # Remove extra spaces in column names

# Extract coordinates and names
coordinates = location_data[['Latitude', 'Lognitude']].values
names = location_data['Admin'].values

# Initialize KNN model
knn = NearestNeighbors(n_neighbors=1, metric='haversine')
knn.fit(np.radians(coordinates))  # Convert coordinates to radians for haversine distance

# Function to find the nearest location
def find_nearest_location(lat, lon):
    input_coords = np.radians([[lat, lon]])  # Convert input to radians
    distance, index = knn.kneighbors(input_coords, return_distance=True)
    distance_km = distance[0][0] * 6371  # Convert from radians to kilometers
    nearest_name = names[index[0][0]]
    return nearest_name, distance_km

# Define the API endpoint
@app.route('/nearest_location', methods=['POST'])
def nearest_location():
    data = request.get_json()  # Expect JSON input with 'latitude' and 'longitude'
    
    # Extract latitude and longitude from request
    lat = data.get('latitude')
    lon = data.get('longitude')
    
    if lat is None or lon is None:
        return jsonify({"error": "Please provide both latitude and longitude"}), 400
    
    # Find the nearest location
    nearest_name, min_distance = find_nearest_location(lat, lon)
    
    # Return result as JSON
    return jsonify({
        "nearest_location": nearest_name,
        "minimum_distance_km": round(min_distance, 2)
    })
