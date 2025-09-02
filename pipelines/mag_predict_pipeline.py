import pandas as pd
import numpy as np
from math import sqrt
from sklearn.cluster import DBSCAN
from sklearn.metrics.pairwise import haversine_distances
import joblib
import pickle

# ------------------ Load Models & Data ------------------ #
coord_model = joblib.load("models/rf_multioutput_model_lat_lon_zone.pkl")
with open("models/zone_time_map.pkl", "rb") as f:
    time_model = pickle.load(f)
mag_model = joblib.load("models/rf_magnitude_predictor.pkl")

df2 = pd.read_csv("models/earthquake_final_dataset_full_2.csv")
df_fault_reference = df2[['latitude_fault', 'longitude_fault', 'area_fault']].copy()

# ------------------ Pre-compute DBSCAN clusters ------------------ #
coord_array = df2[['latitude_eq', 'longitude_eq']].dropna().to_numpy()
dbscan = DBSCAN(eps=0.3, min_samples=5).fit(coord_array)
df2 = df2[~df2[['latitude_eq', 'longitude_eq']].isnull().any(axis=1)].copy()
df2['fault_cluster'] = dbscan.labels_
cluster_centroids = df2.groupby('fault_cluster')[['latitude_eq', 'longitude_eq']].mean().reset_index()

# ------------------ Helper Function ------------------ #
def format_direction(coord, is_lat=True):
    return f"{abs(coord):.4f}° {'N' if is_lat and coord >= 0 else 'S' if is_lat else 'E' if coord >= 0 else 'W'}"

# ------------------ Pipeline Function ------------------ #
def predict_earthquake(latitude_input, longitude_input, zone_input):
    lat_dir = format_direction(latitude_input, True)
    lon_dir = format_direction(longitude_input, False)

    # ------------------ Nearest Fault Line ------------------ #
    df_fault_reference['distance'] = df_fault_reference.apply(
        lambda row: sqrt((row['latitude_fault'] - latitude_input)**2 +
                         (row['longitude_fault'] - longitude_input)**2),
        axis=1
    )
    nearest_fault_area = df_fault_reference.loc[df_fault_reference['distance'].idxmin(), 'area_fault']

    # ------------------ Assign Fault Cluster ------------------ #
    pred_point_rad = np.radians([[latitude_input, longitude_input]])
    centroids_rad = np.radians(cluster_centroids[['latitude_eq', 'longitude_eq']])
    distances = haversine_distances(pred_point_rad, centroids_rad) * 6371
    nearest_cluster_idx = np.argmin(distances)
    predicted_cluster = int(cluster_centroids.iloc[nearest_cluster_idx]['fault_cluster'])

    # ------------------ Build Feature Row Dynamically ------------------ #
    defaults = {
        'depth_eq': 108.6,
        'depth_error_eq': 10.1,
        'fault_density_fault': 0.37,
        'slip_rate_mm_per_yr_fault': 0.5,
        'strain_rate_fault': 8.33e-9,
        'attenuation_factor_fault': 0.0057,
        'soil_factor_scaled_fault': 0.007,
        'rock_factor_scaled_fault': 0.005,
        'zone_eq': int(zone_input)
    }


    feature_names = getattr(mag_model, "feature_names_in_", list(defaults.keys()))
    test_input_row_mag = pd.DataFrame([{name: defaults.get(name, 0) for name in feature_names}])

    # Debugging
    print("Model expects:", list(feature_names))
    print("Input provided:", test_input_row_mag.columns.tolist())
    print(test_input_row_mag)

    # ------------------ Predict Magnitude ------------------ #
    predicted_magnitude = mag_model.predict(test_input_row_mag)[0]

    # ------------------ Fetch Time Info ------------------ #
    cluster_timestamp = time_model.get(predicted_cluster, "Unknown")

    result = {
        "Coordinates": [lat_dir, lon_dir],
        "Predicted Zone": zone_input,
        "Nearest Fault Line Area": nearest_fault_area,
        "Fault Cluster Zone": predicted_cluster,
        "Predicted Magnitude": round(predicted_magnitude, 2),
        "Next Expected Earthquake Time in Cluster": cluster_timestamp,
        "Median Day Gap in Cluster": "N/A (gap not stored)"
    }

    return result
