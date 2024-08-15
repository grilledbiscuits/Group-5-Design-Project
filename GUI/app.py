from flask import Flask, request, render_template
import datetime
import os
import platform
from datetime import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from collections import Counter
import plotly.graph_objs as go
import plotly.io as pio

def creation_date(file_path):
        """
        Try to get the date that a file was created, falling back to when it was last modified if creation date isn't available.
        This works on Windows, Unix/Linux.
        """
        if platform.system() == 'Windows':
            return datetime.fromtimestamp(os.path.getctime(file_path))
        else:
            stat = os.stat(file_path)
            try:
                return datetime.fromtimestamp(stat.st_birthtime)
            except AttributeError:
                # For Unix/Linux fallback to last modified time if birthtime is not available
                return datetime.fromtimestamp(stat.st_mtime)



def extract_hours(df):
    # Convert the timestamp column to datetime type
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Extract the hours from the timestamp column
    df['hour'] = df['timestamp'].dt.hour
    
    # Return only the hour column
    return df['hour']

def filter_images_by_date(start_date, end_date):
    """Given a list of images, and a set of dates return images made between those dates"""
    image_files = []
    images_dir = 'static'
    if not os.path.isdir(images_dir):
        return "Invalid directory path. create the static file and fill it with images"
    
    files = os.listdir(images_dir)
    for file in files:
        if file.endswith('.jpeg') or file.endswith('.jpg') or file.endswith('.png'):
            file_path = os.path.join(images_dir, file)
            if os.path.isfile(file_path):
                if start_date <= creation_date(file_path) and creation_date(file_path) <= end_date:
                    image_files.append(file)
            
    return image_files

def dates():
    """Returns a list of dates of the creation of all the files in a given directory"""

    creation_dates = []
    directory = "static"
    if not os.path.isdir(directory):
        return "Invalid directory path. there is not static file, it needs to be created"

    files = os.listdir(directory)
    for file in files:
        if file.endswith('.jpeg') or file.endswith('.jpg') or file.endswith('.png'):
            file_path = os.path.join(directory, file)
            if os.path.isfile(file_path):
                creation_dates.append(creation_date(file_path))
    creation_dates = sorted(creation_dates)
    return creation_dates


app = Flask(__name__)


@app.route('/')
def index():

    
    number_of_images = len(dates())
    star_date = dates()[0]
    end_date = dates()[-1]
    
    # Convert string timestamps to datetime objects
    picture_taken_times_dt = dates()
    
    # Extract the date from each timestamp (as a string in 'YYYY-MM-DD' format)
    temp = [dt.date().strftime("%Y-%m-%d") for dt in picture_taken_times_dt]
    
    # Count the occurrences of each date
    date_counts = Counter(temp)
    
    # Prepare data for the scatter plot
    x_values = list(date_counts.keys())   # The unique dates
    y_values = list(date_counts.values()) # The count of each date
    
    # Create a scatter plot using Plotly
    scatter = go.Scatter(
        x=x_values,
        y=y_values,
        mode='markers',
        marker=dict(color='blue', size=10, opacity=0.7)
    )

    layout = go.Layout(
        title='Number of Pictures Taken Per Unique Date',
        xaxis=dict(title='Date'),
        yaxis=dict(title='Number of Pictures Taken'),
        hovermode='closest'
    )

    fig = go.Figure(data=[scatter], layout=layout)

    # Convert the plot to HTML
    plot_url_time = pio.to_html(fig, full_html=False)
    
# Convert string timestamps to datetime objects
    picture_taken_times_dt = dates()
  
    # Extract the hour from each timestamp
    hours = [dt.hour for dt in picture_taken_times_dt]
    
    # Count the occurrences of each hour
    hour_counts = Counter(hours)
    
    # Prepare data for the bar graph
    x_values = list(hour_counts.keys())   # The hours
    y_values = list(hour_counts.values()) # The count of each hour
    
    # Sort x_values and y_values by hour for a better visual order
    x_values, y_values = zip(*sorted(zip(x_values, y_values)))
    
    # Create a bar graph using Plotly
    bars = go.Bar(
        x=x_values,
        y=y_values,
        marker=dict(color='blue', opacity=0.7)
    )

    layout = go.Layout(
        title='Frequency of Pictures Taken by Hour',
        xaxis=dict(title='Time of Day (hours)', dtick=1),  # Ensures whole numbers on the x-axis
        yaxis=dict(title='Number of Pictures Taken'),
        hovermode='closest'
    )

    fig = go.Figure(data=[bars], layout=layout)

    # Convert the plot to HTML
    plot_html = pio.to_html(fig, full_html=False)

    
    # Render HTML template with the plot embedded
    return render_template('index.html', images=number_of_images, star_date=star_date, end_date=end_date, plot_url_time = plot_url_time, plot_html = plot_html)


@app.route('/submit', methods=['POST'])
def submit():
    date1 = request.form['date1']
    date2 = request.form['date2']
    
    
    
    if (date1 == "" or date2==""):
        return "Make sure to fill out both date fields"
    
    
    date1 = datetime.strptime(date1, '%Y-%m-%d')
    date2 = datetime.strptime(date2, '%Y-%m-%d')
    # print()
    # print(type(date1))
    # print()
    if (date2 < date1):
        temp = date1
        date1 = date2
        date2 = temp
        
    
        
    image_files = filter_images_by_date(date1, date2)
    
    total_found = len(image_files)
    #return image_files
    return render_template('results.html', image_files=image_files, total = total_found)


@app.route('/status')
def status():
    # Mock data for demonstration
    battery_percentage = "80%"
    wifi_strength = "Strong"
    uptime = "3 days"
    dt = datetime.today()
    time_of_day = str(dt.hour) + ":" + str(dt.minute) + \
        ":" + str(dt.second) + "." + str(dt.microsecond)
    date = str(dt.year) + " - "+str(dt.month)+" - " + str(dt.day)
    return render_template('status.html', date=date, battery_percentage=battery_percentage, wifi_strength=wifi_strength, uptime=uptime, time_of_day=time_of_day)


if __name__ == '__main__':
 
    app.run(debug=True)
