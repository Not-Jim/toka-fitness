from flask import Flask, render_template, request, redirect, url_for, session, flash
from forms import RegisterForm, LoginForm
from db_connector import database
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import CSRFProtect
import datetime

# Initialize the database connection
db = database()
app = Flask(__name__)

# Secret key for session management
app.secret_key = 'Aftonsparv'

# Initialize CSRF protection
csrf = CSRFProtect(app)

@app.route('/', methods=['GET', 'POST'])
def home():
    # Get the current user's name from the session
    name = session.get('name')
    # Fetch fitness sessions from the database
    sessions = db.queryDB('SELECT trainer_name, session_date, session_time, duration FROM Sessions')
    # Retrieve text size preference from the session or set default
    text_size = session.get('text_size', '100')  # default to 100%

    # Render the home page with the fetched data and preferences
    return render_template('home.html', name=name, data=sessions, text_size=text_size, footer=True)

@app.route('/set_text_size', methods=['POST'])
def set_text_size():
    # Set text size preference in the session
    text_size = request.json.get('text_size', '100')
    session['text_size'] = text_size
    return '', 204

@app.route('/about')
def about():
    # Render the about page
    return render_template('about.html', name=session.get('name'))

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        # Get the message from the form and the user ID from the session
        message = request.form['message']
        user_id = session.get('user_id')

        # Save the feedback to the database
        db.modifyDB("INSERT INTO Feedback (user_id, message) VALUES (?, ?)", [user_id, message])

        # Flash a thank you message and redirect to the home page
        flash('Thank you for your feedback!')
        return redirect(url_for('home'))
    # Render the contact page
    return render_template('contact.html', name=session.get('name'))

@app.route('/terms')
def terms():
    # Render the terms and conditions page
    return render_template('terms.html', name=session.get('name'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Get the form data
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        # Check if the username already exists
        result = db.queryDB("SELECT * FROM User WHERE name = ?", [username])
        if result:
            flash('Username already exists. Please choose another one.')
            return redirect(url_for('register'))

        # Hash the password and save the user to the database
        hashed_password = generate_password_hash(password)
        db.modifyDB("INSERT INTO User (name, email, password) VALUES (?, ?, ?)", [username, email, hashed_password])

        # Flash a success message and redirect to the login page
        flash('Registration successful. Please log in.')
        return redirect(url_for('login'))

    # Render the registration page with the registration form
    return render_template('register.html', form=RegisterForm())

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST':
        # Get the form data
        username = request.form['username']
        password = request.form['password']

        # Fetch the user from the database
        found_user = db.queryDB("SELECT * FROM User WHERE name = ?", [username])

        if found_user:
            # Check if the password is correct
            if check_password_hash(found_user[0][3], password):
                # Store the user's name and ID in the session
                session['name'] = username
                session['user_id'] = found_user[0][0]
                flash(f'Welcome back, {username}!')
                return redirect(url_for('home'))
            else:
                flash('Invalid username or password.', 'warning')
        else:
            flash('User not found', 'info')

    # Render the login page with the login form
    return render_template('login.html', form=form)

@app.route('/sessions')
def sessions_page():
    if 'user_id' not in session:
        flash('You need an account to be here.', 'warning')
        return redirect(url_for('login'))
    try:
        # Get the user ID from the session
        UserID = db.queryDB('SELECT id FROM User WHERE name = ?', [session['name']])[0][0]
        # Fetch available sessions from the database
        sessions = db.queryDB("SELECT * FROM Sessions")
        # Fetch the user's bookings from the database
        bookings = db.queryDB("SELECT session_id FROM Bookings WHERE user_id = ?", [session['user_id']])
        bookings = [x[0] for x in bookings]
    except Exception as e:
        flash(f"An error occurred: {str(e)}", 'danger')
        sessions = []
        bookings = []

    # Render the sessions page with the fetched data
    return render_template('sessions.html', name=session.get('name'), sessions=sessions, bookings=bookings, UserID=UserID)

@app.route('/book_session/<int:session_id>')
def book_session(session_id):
    user_id = session.get('user_id')
    if user_id:
        # Book the session for the user
        db.modifyDB("INSERT INTO Bookings (user_id, session_id) VALUES (?, ?)", [user_id, session_id])
        flash('Session booked successfully!', 'success')
        return redirect(url_for('sessions_page'))
    flash('Please log in to book a session.', 'info')
    return redirect(url_for('login'))

@app.route('/unbook_session/<int:session_id>')
def unbook_session(session_id):
    user_id = session.get('user_id')
    # Unbook the session for the user
    db.modifyDB("DELETE FROM Bookings WHERE session_id = ? AND user_id = ?", [session_id, user_id])
    flash("Session unbooked successfully!", 'success')
    return redirect(url_for('sessions_page'))

@app.route('/create_session', methods=['POST'])
def create_session():
    if request.method == 'POST':
        try:
            # Get the form data
            trainer = request.form['Trainer']
            date = datetime.datetime.strptime(request.form['Date'], '%Y-%m-%d').strftime('%d/%m/%Y')
            time = request.form['Time']
            duration = request.form['Duration']
            # Create a new session in the database
            db.modifyDB('INSERT INTO Sessions (trainer_name, session_date, session_time, duration) VALUES (?, ?, ?, ?)', 
                        [trainer, date, time, duration])
            flash('Session created successfully!', 'success')
        except Exception as e:
            flash(f"An error occurred: {str(e)}", 'danger')
    return redirect(url_for('sessions_page'))

@app.route('/logout')
def logout():
    # Clear the user's session
    session.pop('name', None)
    session.pop('user_id', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

@app.route('/user', methods=['GET', 'POST'])
def user_profile():
    if 'user_id' not in session:
        flash("You need an account to be here.", 'warning')
        return redirect(url_for('login'))
    user_id = session.get('user_id')
    # Fetch the current user from the database
    user = db.queryDB("SELECT * FROM User WHERE id = ?", [user_id])

    if not user:
        flash("User not found. Please log in again.", 'danger')
        session.pop('name', None)
        session.pop('user_id', None)
        return redirect(url_for('login'))

    user = user[0]  # Extract the first result (expected one user)

    if request.method == 'POST':
        # Get form inputs
        current_password = request.form['current_password']
        new_username = request.form.get('new_username')
        new_email = request.form.get('new_email')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        # Check if the current password is correct
        if not check_password_hash(user[3], current_password):  # Assuming password is in the 4th column
            flash("Incorrect current password.", 'danger')
            return redirect(url_for('user_profile'))

        # Validate and update username
        if new_username and new_username != user[1]:
            db.modifyDB("UPDATE User SET name = ? WHERE id = ?", [new_username, user_id])
            session['name'] = new_username  # Update session
            flash("Username updated successfully.", 'success')

        # Validate and update email
        if new_email and new_email != user[2]:
            db.modifyDB("UPDATE User SET email = ? WHERE id = ?", [new_email, user_id])
            flash("Email updated successfully.", 'success')

        # Validate and update password
        if new_password:
            if new_password == confirm_password:
                hashed_password = generate_password_hash(new_password)
                db.modifyDB("UPDATE User SET password = ? WHERE id = ?", [hashed_password, user_id])
                flash("Password updated successfully.", 'success')
            else:
                flash("New password and confirmation do not match.", 'danger')

        return redirect(url_for('user_profile'))

    # Render the user profile page with the user's data
    return render_template('user.html', name=user[1], email=user[2])

@app.route('/delete_account', methods=['POST'])
def delete_account():
    user_id = session.get('user_id')
    if not user_id:
        flash("Please log in to delete your account.", 'warning')
        return redirect(url_for('login'))

    # Delete the user account from the database
    db.modifyDB("DELETE FROM User WHERE id = ?", [user_id])
    # Clear the user's session
    session.pop('name', None)
    session.pop('user_id', None)
    flash("Your account has been deleted successfully.", 'info')
    return redirect(url_for('home'))

@app.route('/not_yet')
def not_yet():
    # Render the not-yet page
    return render_template('not-yet.html', name=session.get('name'))

@app.route('/advice')
def advice():
    # Fetch advice data from the database
    data = db.queryDB("SELECT * FROM advice")
    # Render the advice page with the fetched data
    return render_template('advice.html', name=session.get('name'), data=data)

@app.errorhandler(404)
def page_not_found(e):
    # Redirect to the not-yet page for 404 errors
    return redirect(url_for('not_yet'))

if __name__ == '__main__':
    # Run the Flask application in debug mode
    app.run(debug=True)
