from flask import Flask, render_template, request, redirect, url_for, session, flash
from forms import RegisterForm, LoginForm
from db_connector import database
from werkzeug.security import generate_password_hash, check_password_hash

db = database()
app = Flask(__name__)

app.secret_key = 'Aftonsparv'  # Secret key for sessions

@app.route('/', methods=['GET', 'POST'])
def home():
    name = session.get('name')
    return render_template('home.html', name=name)

@app.route('/about')
def about():
    return render_template('about.html', name=session.get('name'))

@app.route('/contact')
def contact():
    return render_template('contact.html', name=session.get('name'))

@app.route('/terms')
def terms():
    return render_template('terms.html', name=session.get('name'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        name = form.name.data

        # Check if username already exists
        user = db.queryDB("SELECT * FROM User WHERE name = ?", [username])
        if user:
            flash('Username already exists. Please choose another one.')
            return redirect(url_for('register'))

        # Hash the password and save user to the database
        hashed_password = generate_password_hash(password)
        db.modifyDB("INSERT INTO User (name, password) VALUES (?, ?)", [username, hashed_password])
        
        flash('Registration successful. Please log in.')
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        # Fetch user from the database
        user = db.queryDB("SELECT * FROM User WHERE name = ?", [username])
        
        if user and check_password_hash(user[0][2], password):  # Assuming the password is in the 3rd column
            session['name'] = username
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password.')
    
    return render_template('login.html', form=form)

@app.route('/aftonsparv')
def aftonsparv():
    return render_template('gnarpy.html', name=session.get('name'))

@app.route('/logout')
def logout():
    session['name'] = None
    return redirect(url_for('home'))

@app.route('/user')
def user():
    return render_template('user.html', name=session.get('name'))

if __name__ == '__main__':
    app.run(debug=True)