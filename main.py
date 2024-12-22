from flask import Flask, render_template, redirect, request, url_for, flash, session
from pymongo import MongoClient
import os
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from bson import ObjectId, errors
from requests_oauthlib import OAuth2Session
import requests

app = Flask(__name__)
app.secret_key = os.urandom(24)

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

client = MongoClient('mongodb://localhost:27017')
db = client['CollegeJunction']
user_collection = db['college']

@app.route("/")
def hello_world():
    return render_template("index.html")

@app.route("/home")
def home():
    return render_template("/components/search/index.html")

@app.route("/review")
def review():
    return render_template("/components/review/index.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect(url_for('home'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = user_collection.find_one({'username': username})
        if user and check_password_hash(user['password'], password):
            session['username'] = username
            flash('You were successfully logged in', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password.', 'error')
    return render_template('/components/login/index.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if 'username' in session:
        return redirect(url_for('home'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if user_collection.find_one({'username': username}):
            flash('Username already exists, Please choose a different one.', 'error')
        else:
            hashed_password = generate_password_hash(password)
            user_collection.insert_one({'username': username, 'password': hashed_password})
            flash('User registered successfully.', 'success')
            return redirect(url_for('home'))
    return render_template('/components/signup/index.html')

if __name__ == '__main__':
    app.run(debug=True)