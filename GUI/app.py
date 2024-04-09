from flask import Flask, request, render_template

app = Flask(__name__)


@app.route('/')
def index():
    number_of_images = 100
    star_date = "20-April-2024"
    end_date = "30-April-2024"
    return render_template('index.html', images=number_of_images, star_date=star_date, end_date=end_date)


@app.route('/submit', methods=['POST'])
def submit():
    user_input = request.form['user_input']
    return render_template('results.html', user_input=user_input)


@app.route('/status')
def status():
    # Mock data for demonstration
    battery_percentage = "80%"
    wifi_strength = "Strong"
    uptime = "3 days"
    time_of_day = "10:00 AM"
    return render_template('status.html', battery_percentage=battery_percentage, wifi_strength=wifi_strength, uptime=uptime, time_of_day=time_of_day)


if __name__ == '__main__':
    app.run(debug=True)
