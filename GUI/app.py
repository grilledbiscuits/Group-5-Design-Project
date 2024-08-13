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
    images_dir = 'images'
    for filename in os.listdir(images_dir):
        if filename.endswith('.jpeg') or filename.endswith('.jpg') or filename.endswith('.png'):
            creation_time_str = datetime.fromtimestamp(os.path.getctime(os.path.join(images_dir, filename))).strftime('%Y-%m-%d')
            creation_time = datetime.strptime(creation_time_str, '%Y-%m-%d')
            creation_time = str(creation_time)
            if start_date <= creation_time <= end_date:
                image_files.append(filename)
    return image_files

def dates():
    """Returns a list of dates of the creation of all the files in a given directory"""

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

    creation_dates = []
    directory = "images"
    if not os.path.isdir(directory):
        return "Invalid directory path."

    files = os.listdir(directory)
    for file in files:
        file_path = os.path.join(directory, file)
        if os.path.isfile(file_path):
            creation_dates.append(creation_date(file_path))
    creation_dates = sorted(creation_dates)
    return creation_dates


app = Flask(__name__)


@app.route('/')
def index():

    creation_dates = dates()

    # Sample data: list of dates when pictures were taken
    picture_dates = dates()
    #print(picture_dates)
    # Convert the list to a pandas DataFrame
    df = pd.DataFrame({'Date': picture_dates})
    
    df['Dates'] = pd.to_datetime(df['Date'])
    
    # Extract the hours from the timestamp column
    df['date'] = df['Dates'].dt.date

    # Count the occurrences of each date
    date_counts = df['date'].value_counts().reset_index()
    date_counts.columns = ['Date', 'Count']

    # Convert the 'Date' column to datetime
    date_counts['Date'] = pd.to_datetime(date_counts['Date'])

    # Sort by date
    date_counts = date_counts.sort_values(by='Date')

    # Generate scatterplot
    plt.figure(figsize=(10, 6))
    plt.scatter(date_counts['Date'], date_counts['Count'])
    plt.title('Number of Pictures Taken on Each Date')
    plt.xlabel('Date')
    plt.ylabel('Number of Pictures')
    plt.grid(True)

    # Convert plot to bytes
    img = BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    
    number_of_images = len(creation_dates)
    star_date = creation_dates[0]
    end_date = creation_dates[-1]
    
    
    df['timestamp'] = pd.to_datetime(df['Date'])
    
    # Extract the hours from the timestamp column
    df['hour'] = df['timestamp'].dt.hour
    
    # Count the occurrences of each hour
    hour_counts = df['hour'].value_counts().sort_index()
    
    # Plot the data
    plt.figure(figsize=(10, 6))
    hour_counts.plot(kind='bar', color='skyblue')
    plt.title('Number of Times Each Hour Appears')
    plt.xlabel('Time of day')
    plt.ylabel('Frequency')
    plt.xticks(rotation=0)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    #plt.show()
    
    # Convert plot to bytes
    img = BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url_time = base64.b64encode(img.getvalue()).decode()

    return render_template('index.html', images=number_of_images, star_date=star_date, end_date=end_date, plot_url=plot_url, plot_url_time = plot_url_time)


@app.route('/submit', methods=['POST'])
def submit():
    date1 = request.form['date1']
    date2 = request.form['date2']
    pic_dates = dates()
    
    if (date1 == "" or date2==""):
        return "Fill out both of them my guy"
    
    if (date2 < date1):
        temp = date1
        date1 = date2
        date2 = temp
        
    image_files = filter_images_by_date(date1, date2)
    total_found = len(image_files)
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
    # dates()
    app.run(debug=True)
