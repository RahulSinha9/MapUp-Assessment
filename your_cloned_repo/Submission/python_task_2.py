import pandas as pd
import numpy as np
from datetime import time
df = pd.read_csv("dataset-3.csv")

import pandas as pd

def calculate_distance_matrix(df: pd.DataFrame) -> pd.DataFrame:

    # Create a pivot table to represent distances between id_start and id_end
    distance_matrix = df.pivot_table(index='id_start', columns='id_end', values='distance', aggfunc='sum', fill_value=0)

    # Add bidirectional distances to make the matrix symmetric
    distance_matrix = distance_matrix + distance_matrix.T

    # Set diagonal values to 0
    distance_matrix.values[[range(len(distance_matrix))]*2] = 0

    return distance_matrix

res1 = calculate_distance_matrix(df)


def unroll_distance_matrix(df: pd.DataFrame) -> pd.DataFrame:

    # Stack the distance matrix to convert it to a long format
    stacked_matrix = df.stack().reset_index()

    # Rename the columns to match the output format
    stacked_matrix.columns = ['id_start', 'id_end', 'distance']

    # Exclude rows where id_start is equal to id_end
    unrolled_df = stacked_matrix[stacked_matrix['id_start'] != stacked_matrix['id_end']].reset_index(drop=True)

    return unrolled_df
res2 = unroll_distance_matrix(res1)



def find_ids_within_ten_percentage_threshold(df: pd.DataFrame, reference_id: int) -> pd.DataFrame:
    
    # Filter the DataFrame for rows with the specified reference_id
    reference_rows = df[df['id_start'] == reference_id]

    # Calculate the average distance for the reference_id
    reference_average_distance = reference_rows['distance'].mean()

    # Calculate the lower and upper thresholds within 10% of the average distance
    lower_threshold = reference_average_distance - (0.1 * reference_average_distance)
    upper_threshold = reference_average_distance + (0.1 * reference_average_distance)

    # Filter the DataFrame for rows within the specified percentage threshold
    filtered_df = df[(df['id_start'] != reference_id) & (df['distance'] >= lower_threshold) & (df['distance'] <= upper_threshold)]

    # Get unique IDs from the filtered DataFrame
    result_df = filtered_df[['id_start']].drop_duplicates().sort_values(by='id_start').reset_index(drop=True)

    return result_df


def calculate_distance_matrix(df: pd.DataFrame) -> pd.DataFrame:
   
     # Define rate coefficients for each vehicle type
    rate_coefficients = {'moto': 0.8, 'car': 1.2, 'rv': 1.5, 'bus': 2.2, 'truck': 3.6}

    # Calculate toll rates for each vehicle type
    for vehicle_type, rate_coefficient in rate_coefficients.items():
        # Multiply the distance by the rate coefficient for each vehicle type
        df[vehicle_type] = df['distance'] * rate_coefficient

    return df


def calculate_time_based_toll_rates(df: pd.DataFrame) -> pd.DataFrame:
    
    # Define time ranges and discount factors
    weekday_time_ranges = [(time(0, 0), time(10, 0)), (time(10, 0), time(18, 0)), (time(18, 0), time(23, 59, 59))]
    weekend_time_ranges = [(time(0, 0), time(23, 59, 59))]
    discount_factors_weekday = [0.8, 1.2, 0.8]
    discount_factor_weekend = 0.7

    # Convert 'start_time' and 'end_time' columns to datetime.time
    df['start_time'] = pd.to_datetime(df['start_time']).dt.time
    df['end_time'] = pd.to_datetime(df['end_time']).dt.time

    # Initialize columns for time-based toll rates
    for time_range in weekday_time_ranges + weekend_time_ranges:
        start_time, end_time = time_range
        column_name = f"{start_time.strftime('%H:%M')}-{end_time.strftime('%H:%M')}"
        df[column_name] = np.nan

    # Update values based on time ranges and discount factors
    for i, row in df.iterrows():
        for j, (start_time, end_time) in enumerate(weekday_time_ranges):
            mask = (
                (row['start_day'] <= row['end_day']) &  # For weekdays
                ((row['start_time'] >= start_time) & (row['start_time'] <= end_time)) |
                ((row['end_time'] >= start_time) & (row['end_time'] <= end_time))
            )
            df.loc[i, f"{start_time.strftime('%H:%M')}-{end_time.strftime('%H:%M')}"] = (
                row[f"{start_time.strftime('%H:%M')}-{end_time.strftime('%H:%M')}"] * discount_factors_weekday[j]
            )
        
        for start_time, end_time in weekend_time_ranges:
            mask = (
                (row['start_day'] > row['end_day']) |  # For weekends
                ((row['start_time'] >= start_time) & (row['start_time'] <= end_time)) |
                ((row['end_time'] >= start_time) & (row['end_time'] <= end_time))
            )
            df.loc[i, f"{start_time.strftime('%H:%M')}-{end_time.strftime('%H:%M')}"] = (
                row[f"{start_time.strftime('%H:%M')}-{end_time.strftime('%H:%M')}"] * discount_factor_weekend
            )

    return df