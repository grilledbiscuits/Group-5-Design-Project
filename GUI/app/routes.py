from flask import Blueprint, render_template

main = Blueprint('main', __name__)


@main.route('/')
def index():
    return render_template("C:\Users\Best Nkhumeleni\Desktop\EEE4113F\Group-5-Design-Project\GUI\\templates\index.html")
