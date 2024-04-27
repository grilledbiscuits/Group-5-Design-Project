from flask import Flask, request, render_template
import datetime
import os
import platform
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import base64

def filter_images_by_date(start_date, end_date):
    image_files = []
    images_dir = 'images'
    for filename in os.listdir(images_dir):
        if filename.endswith('.jpg') or filename.endswith('.png'):
            creation_time = datetime.fromtimestamp(os.path.getctime(os.path.join(images_dir, filename)))
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
        print("Invalid directory path.")
        return

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

    # Convert the list to a pandas DataFrame
    df = pd.DataFrame({'Date': picture_dates})

    # Count the occurrences of each date
    date_counts = df['Date'].value_counts().reset_index()
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

    return render_template('index.html', images=number_of_images, star_date=star_date, end_date=end_date, plot_url=plot_url)


@app.route('/submit', methods=['POST'])
def submit():
    date1 = request.form['date1']
    date2 = request.form['date2']
    pic_dates = dates()
    
    
    if (date2 < date1):
        temp = date1
        date1 = date2
        date2 = temp
        
    
    return render_template('results.html', date1 = date1, date2 = date2)


@app.route('/status')
def status():
    # Mock data for demonstration
    battery_percentage = "80%"
    wifi_strength = "Strong"
    uptime = "3 days"
    dt = datetime.today()
    time_of_day = str(dt.hour) + ":" + str(dt.minute) + \
        ":" + str(dt.second) + "." + str(dt.microsecond)
    date = str(dt.year) + " / "+str(dt.month)+" / " + str(dt.day)
    return render_template('status.html', date=date, battery_percentage=battery_percentage, wifi_strength=wifi_strength, uptime=uptime, time_of_day=time_of_day)


if __name__ == '__main__':
    # dates()
    app.run(debug=True)
