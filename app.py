from flask import Flask, render_template, request, redirect, url_for, session, flash
from forms import RegisterForm, LoginForm
from db_connector import database
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import *
import datetime

db = database()  # Gets database from db_connector
app = Flask(__name__)

app.secret_key = 'Aftonsparv'  # Secret key for sessions


@app.route('/', methods=['GET', 'POST'])
def home():
    name = session.get('name')
    # Fetch fitness sessions from the database
    sessions = db.queryDB(
        'SELECT trainer_name, session_date, session_time, duration FROM "Sessions"')
    # Retrieve text size and dark mode from session or set defaults
    text_size = session.get('text_size', '100')  # default to 100%
    dark_mode = session.get('dark_mode', False)  # default to light mode

    return render_template('home.html', name=name, data=sessions, text_size=text_size, dark_mode=dark_mode, footer=True)


@app.route('/about')
def about():
    return render_template('about.html', name=session.get('name'))


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        message = request.form['message']
        user_id = session.get('user_id')

        # Save feedback to the database
        db.modifyDB("INSERT INTO Feedback (user_id, message) VALUES (?, ?)", [
                    user_id, message])

        flash('Thank you for your feedback!')
        return redirect(url_for('home'))
    return render_template('contact.html', name=session.get('name'))


@app.route('/terms')
def terms():
    return render_template('terms.html', name=session.get('name'))


@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        # Check if username already exists
        result = db.queryDB("SELECT * FROM User WHERE name = ?", [username])
        if result:
            flash('Username already exists. Please choose another one.')
            return redirect(url_for('register'))

        # Hash the password and save the user to the database
        hashed_password = generate_password_hash(password)
        print(hashed_password)
        db.modifyDB("INSERT INTO User (name, email, password) VALUES (?, ?, ?)",
                    [username, email, hashed_password])

        flash('Registration successful. Please log in.')
        return redirect(url_for('login'))

    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Fetch user from the database
        found_user = db.queryDB(
            "SELECT * FROM User WHERE name = ?", [username])

        if found_user:
            # and check_password_hash(user[0][3], password):  # Assuming password is the 4th column in User
            if check_password_hash(found_user[0][3], password):
                session['name'] = username
                # Store user_id in session
                session['user_id'] = found_user[0][0]
                flash(f'Welcome back, {username}!')
                return redirect(url_for('home'))
            else:
                flash('Invalid username or password.', 'warning')
        else:
            flash('User not found', 'info')

    return render_template('login.html', form=form)


@app.route('/sessions')
def sessions_page():
    UserID = db.queryDB('SELECT id FROM User WHERE name = ?', [session['name']])[0][0]
    # Fetch available sessions from the database
    sessions = db.queryDB("SELECT * FROM Sessions")
    try:
        bookings = db.queryDB("SELECT session_id FROM Bookings WHERE user_id = ?", [
                              session['user_id']])
        bookings = [x[0] for x in bookings]
    except:
        bookings = []

    return render_template('sessions.html', name=session.get('name'), sessions=sessions, bookings=bookings, UserID=UserID)


@app.route('/book_session/<int:session_id>')
def book_session(session_id):
    user_id = session.get('user_id')
    if user_id:
        # Update session in the database to assign to the user
        db.modifyDB("INSERT INTO Bookings (user_id, session_id) VALUES (?, ?)", [
                    user_id, session_id])
        flash('Session booked successfully!', 'success')
        return redirect(url_for('sessions_page'))
    flash('Please log in to book a session.', 'info')
    return redirect(url_for('login'))


@app.route('/unbook_session/<int:session_id>')
def unbook_session(session_id):
    user_id = session.get('user_id')
    db.modifyDB("DELETE FROM Bookings WHERE session_id = ? AND user_id = ?", [
                session_id, user_id])
    flash("Session unbooked successfully!", 'success')
    return redirect(url_for('sessions_page'))


@app.route('/create_session', methods=['POST'])
def create_session():
    if request.method == 'POST':
        trainer = request.form['Trainer']
        date =datetime.datetime.strptime(request.form['Date'], '%Y-%m-%d').strftime('%d/%m/%Y')
        time = request.form['Time']
        duration = request.form['Duration']
        db.modifyDB('INSERT INTO Sessions (trainer_name, session_date, session_time, duration) VALUES (?, ?, ?, ?)', 
                    [trainer, date, time, duration])
    return redirect(url_for('sessions_page'))


@app.route('/logout')
def logout():
    session.pop('name', None)
    session.pop('user_id', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))


@app.route('/user')
def user_profile():
    user_id = session.get('user_id')
    if user_id:
        # Fetch user profile data
        user = db.queryDB("SELECT * FROM User WHERE id = ?", [user_id])
        return render_template('user.html', name=user[0][1], email=user[0][2], footer=True)
    return redirect(url_for('login'))


@app.route('/not_yet')
def not_yet():
    return render_template('not-yet.html', name=session.get('name'))


if __name__ == '__main__':
    app.run(debug=True)
