from flask import Flask, get_flashed_messages, render_template, request, redirect, send_from_directory, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_migrate import Migrate
from flask import redirect, url_for

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)

migrate = Migrate(app, db)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

@app.route('/')
def index():
    return 'Welcome to the User Authentication Example'

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        flash('You are already logged in.')
        return redirect(url_for('login'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if the username already exists in the database
        existing_user = User.query.filter_by(username=username).first()

        if existing_user:
            flash('Username already exists. Please log in.')
            return redirect(url_for('login'))

        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=hashed_password)

        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Account created successfully. You can now log in.')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash('Error creating account. Please try again.')

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        flash('You are already logged in.')
        return redirect(url_for('home'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user:
            # User exists, check password
            if check_password_hash(user.password, password):
                session['user_id'] = user.id
                flash('Logged in successfully.')
                return redirect(url_for('home'))
            else:
                error_message = 'Login failed. Check your username and password.'
                session['error_messages'] = [error_message]
                return redirect(url_for('login'))
        else:
            error_message = 'User does not exist. Please Sign Up.'
            session['error_messages'] = [error_message]
            return redirect(url_for('login'))
    
    error_messages = session.pop('error_messages', [])
    return render_template('login.html', error_messages=error_messages)

@app.route('/home')
def home():
    if 'user_id' in session:
        return render_template('index.html')
    else:
        flash('You need to log in first.')
        return redirect(url_for('login'))
    
# Define the menu route
@app.route('/menu')
def menu():
    return render_template('menu.html')

# Define the about route
@app.route('/about')
def about():
    return render_template('about.html')

# Define the book route
@app.route('/book')
def book():
    return render_template('book.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Logged out successfully.')
    return redirect(url_for('home'))

# Add a route to serve static files
@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)