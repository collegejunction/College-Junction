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

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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

@app.route("/notes")
def notes():
    return render_template("/components/Notes/index.html")

@app.route("/college")
def college():
    posts = list(db.posts.find())
    for post in posts:
        if 'rating' in post:
            try:
                post['rating'] = int(post['rating'])  # Ensure rating is an integer
            except ValueError:
                post['rating'] = 0  # Default to 0 if conversion fails
    return render_template("/components/review/college.html", posts=posts)

@app.route("/mainclg/<college_id>")
def mainclg(college_id):
    post = db.posts.find_one({"_id": ObjectId(college_id)})
    if post:
        # Extracting the details from the post object
        college_name = post.get("college_name")
        college_courses = post.get("college_courses")
        rating = post.get("rating", 0)
        location = post.get("location")
        photos = post.get("photos", [])
        main_photo = post.get("main_photo", '')
        profile_pic = post.get("profile_pic", '/static/img/user.png')

        # Preparing the rating stars
        rating_stars = ['checked' if i < int(rating) else 'black' for i in range(5)]

        # Render the template with the extracted data
        return render_template("/components/review/{collegename}.html",
                               college_name=college_name,
                               college_courses=college_courses,
                               rating_stars=rating_stars,
                               location=location,
                               photos=photos,
                               main_photo=main_photo,
                               profile_pic=profile_pic)
    else:
        flash('College not found', 'error')
        return redirect(url_for('home'))


@app.route("/contact")
def contact():
    return render_template("/components/contact/index.html")

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

@app.route('/newpost', methods=['GET', 'POST'])
def newpost():
    if 'username' not in session:
        flash('You must be logged in to access this page.', 'error')
        return redirect(url_for('hello_world'))

    if request.method == 'POST':
        college_name = request.form['college_name']
        college_courses = request.form['college_courses']
        rating = request.form.get('rating', '')
        location = request.form.get('location', '')  # Get location from form
        username = session.get('username')
        user = user_collection.find_one({'username': username})

        # Handle file upload for the main photo
        main_photo_file = request.files.get('mainphoto')
        main_photo_url = ''
        if main_photo_file and allowed_file(main_photo_file.filename):
            main_photo_filename = secure_filename(main_photo_file.filename)
            main_photo_path = os.path.join(app.config['UPLOAD_FOLDER'], main_photo_filename)
            main_photo_file.save(main_photo_path)
            main_photo_url = url_for('static', filename=f'uploads/{main_photo_filename}')

        # Handle photo uploads for the 3 additional photos
        photos = []
        for i in range(1, 4):  # Loop for up to 3 photo uploads
            photo_file = request.files.get(f'photos{i}')
            if photo_file and allowed_file(photo_file.filename):
                photo_filename = secure_filename(photo_file.filename)
                photo_path = os.path.join(app.config['UPLOAD_FOLDER'], photo_filename)
                photo_file.save(photo_path)
                photo_url = url_for('static', filename=f'uploads/{photo_filename}')
                photos.append(photo_url)

        # Create the post document
        post = {
            'username': username,
            'college_name': college_name,
            'college_courses': college_courses,
            'rating': rating,
            'location': location,
            'main_photo': main_photo_url,
            'photos': photos,
            'profile_pic': user.get('profile_pic', '/static/img/user.png')
        }

        # Insert the post into the database
        db.posts.insert_one(post)
        flash('Your post has been created successfully.', 'success')
        return redirect(url_for('home'))

    return render_template('/components/addcollege/post.html', location='')

if __name__ == '__main__':
    app.run(debug=True)
