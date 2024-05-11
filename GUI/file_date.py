import pandas as pd
import matplotlib.pyplot as plt

def plot_hour_counts(df):
    # Convert the timestamp column to datetime type
    df['timestamp'] = pd.to_datetime(df['Dates'])
    
    # Extract the hours from the timestamp column
    df['hour'] = df['timestamp'].dt.hour
    
    # Count the occurrences of each hour
    hour_counts = df['hour'].value_counts().sort_index()
    
    # Plot the data
    plt.figure(figsize=(10, 6))
    hour_counts.plot(kind='bar', color='skyblue')
    
    plt.title('Number of Times Each Hour Appears')
    plt.xlabel('Hour')
    plt.ylabel('Frequency')
    plt.xticks(rotation=0)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.show()

# Example dataframe
data = {'Dates': ['2024-05-11 08:30:00', '2024-05-11 12:45:00', '2024-05-11 18:20:00', '2024-05-11 12:30:00']}
df = pd.DataFrame(data)

# Call the function to plot hour counts
plot_hour_counts(df)
