import pandas as pd

df1 = pd.read_csv("dataset-1.csv")
df2 = pd.read_csv("dataset-2.csv")

def generate_car_matrix(df: pd.DataFrame) -> pd.DataFrame:
    car_matrix = df.pivot(index='id_1', columns='id_2', values='car').fillna(0)
    
    # Set diagonal values to 0
    car_matrix.values[[range(len(car_matrix))]*2] = 0

    return car_matrix

result = generate_car_matrix(df1)

def get_type_count(df: pd.DataFrame) -> dict:
    # Define a function to categorize car values into types
    def categorize_car_type(value):
        if value <= 15:
            return 'low'
        elif 15 < value <= 25:
            return 'medium'
        else:
            return 'high'

    # Add a new column 'car_type' based on the categorization function
    df['car_type'] = df['car'].apply(categorize_car_type)

    # Count occurrences of each car_type category
    type_counts = df['car_type'].value_counts().to_dict()

    # Sort the dictionary alphabetically based on keys
    sorted_type_counts = dict(sorted(type_counts.items()))

    return sorted_type_counts

def get_bus_indexes(df: pd.DataFrame) -> list:
    
    # Check if 'bus' column is present in the DataFrame
    if 'bus' not in df.columns:
        raise ValueError("Column 'bus' not found in the DataFrame.")

    # Calculate the mean of the 'bus' column
    bus_mean = df['bus'].mean()

    # Find indices where 'bus' values exceed twice the mean
    bus_indexes = df[df['bus'] > 2 * bus_mean].index.tolist()

    return sorted(bus_indexes)


def filter_routes(df: pd.DataFrame) -> list:
   
    # Check if 'truck' and 'route' columns are present in the DataFrame
    if 'truck' not in df.columns or 'route' not in df.columns:
        raise ValueError("Columns 'truck' or 'route' not found in the DataFrame.")

    # Calculate the average of 'truck' values for each route
    avg_truck_by_route = df.groupby('route')['truck'].mean()

    # Filter routes where the average 'truck' value is greater than 7
    filtered_routes = avg_truck_by_route[avg_truck_by_route > 7].index.tolist()

    return sorted(filtered_routes)


def multiply_matrix(matrix: pd.DataFrame) -> pd.DataFrame:
    
    # Apply custom conditions to modify the values
    modified_matrix = matrix.applymap(lambda x: x * 0.75 if x > 20 else x * 1.25)

    # Round the values to 1 decimal place
    modified_matrix = modified_matrix.round(1)

    return modified_matrix


def time_check(df: pd.DataFrame) -> pd.Series:
   
    try:
        # Convert timestamp columns to datetime objects, handling errors by coercing to NaT
        df['start_datetime'] = pd.to_datetime(df['startDay'] + ' ' + df['startTime'], format='%A %H:%M:%S', errors='coerce')
        df['end_datetime'] = pd.to_datetime(df['endDay'] + ' ' + df['endTime'], format='%A %H:%M:%S', errors='coerce')

        # Filter out rows with NaT (invalid timestamps)
        df = df.dropna(subset=['start_datetime', 'end_datetime'])

        if df.empty:
            raise ValueError("DataFrame is empty after timestamp conversion.")

        # Calculate the duration for each row
        df['duration'] = df['end_datetime'] - df['start_datetime']

        # Check if the duration is less than 24 hours and spans all 7 days
        is_incomplete = (df['duration'] < pd.Timedelta('1 day')) | (df['start_datetime'].dt.dayofweek != 0) | (df['end_datetime'].dt.dayofweek != 6)

        # Create a boolean series with multi-index (id, id_2)
        result_series = df.groupby(['id', 'id_2']).apply(lambda group: any(is_incomplete.loc[group.index]))

    except Exception as e:
        print(f"An error occurred: {e}")
        result_series = pd.Series()

    return result_series
