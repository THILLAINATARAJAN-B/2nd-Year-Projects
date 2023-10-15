from flask import Flask, render_template, request, redirect, url_for, flash, session
import psycopg2
import secrets
import bcrypt

secret_key = secrets.token_hex(32)

app = Flask(__name__)
app.secret_key = secret_key

dbhost = 'localhost'
dbname = 'Phone'
dbuser = 'postgres'
dbpass = '123456789'

@app.route('/')
def start():
    session.clear()
    return render_template('index.html')

@app.route('/home', methods=['GET'])
def home():
    username = session.get('username')
    user_id = session.get('user_id')

    if username is None or user_id is None:
        flash('Username or user ID not found in session.', 'danger')
        return redirect(url_for('login'))  # Redirect to login page if session data is missing

    return render_template('home.html', username=username, user_id=user_id)
# Function to create the "users" table
def create_users_table():
    conn = psycopg2.connect(host=dbhost, dbname=dbname, user=dbuser, password=dbpass)
    try:
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS users(
                user_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                username VARCHAR(255) NOT NULL,
                password VARCHAR(255) NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL
            )
        ''')
        conn.commit()
    finally:
        conn.close()

def verify_user(email, password):
    conn = psycopg2.connect(host=dbhost, dbname=dbname, user=dbuser, password=dbpass)
    try:
        cur = conn.cursor()
        cur.execute("SELECT user_id, username, password FROM users WHERE email = %s", (email,))
        result = cur.fetchone()
        
        if result and bcrypt.checkpw(password.encode('utf-8'), result[2].encode('utf-8')):
            user_id = result[0]
            username = result[1]
            return username, user_id  # Return both username and user_id when successfully verified
    finally:
        conn.close()

    return None, None  # Return None for both username and user_id when verification fails

@app.route('/register', methods=['GET', 'POST'])
def register():
    error_message = None  # Initialize error_message as None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        email = request.form['email']

        create_users_table()

        # Check if the email already exists
        conn = psycopg2.connect(host=dbhost, dbname=dbname, user=dbuser, password=dbpass)
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM users WHERE email = %s", (email,))
        existing_email_count = cur.fetchone()[0]

        if existing_email_count > 0:
            error_message = 'Email already in use. Please use a different email.'
        elif len(password) < 6 or len(password) > 14:
            error_message = 'Password must be between 6 to 14 characters.'
        elif password != confirm_password:
            error_message = 'Passwords do not match.'
        else:
            user_password = password  # Replace with the user's actual password
            hashed_password = bcrypt.hashpw(user_password.encode('utf-8'), bcrypt.gensalt())

            # Insert data into the database
            try:
                cur.execute("""
                    INSERT INTO users (username, password, email)
                    VALUES (%s, %s, %s)
                """, (username, hashed_password.decode('utf-8'), email))

                # Commit the transaction
                conn.commit()

                flash('Registration successful!', 'success')
                return redirect(url_for('login'))
            except Exception as e:
                flash(f'Error: {str(e)}', 'danger')
            finally:
                # Close the database connection
                conn.close()

    return render_template('register.html', error_message=error_message)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session and 'user_id' in session:
        # If the user is already logged in, redirect to the home page
        app.logger.info(f'User {session["username"]} is already logged in.')
        return redirect(url_for('home'))

    error_message = None
    if request.method == 'POST':
        password = request.form['password']
        email = request.form['email']
        verified_username, verified_user_id = verify_user(email, password)

        if verified_username:
            session['username'] = verified_username
            session['user_id'] = verified_user_id
            app.logger.info(f'User {verified_username} logged in successfully.')
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            error_message = 'Email not found or password incorrect.'

    app.logger.info('Login page accessed.')
    return render_template('login.html', error_message=error_message)


@app.route('/insert', methods=['GET', 'POST'])
def insert():
    username = session.get('username')
    user_id = session.get('user_id')

    if username is None or user_id is None:
        flash('Username or user ID not found in session.', 'danger')
        #return redirect(url_for('login'))  # Redirect to login page or handle as needed

    if request.method == 'POST':
        name = request.form['name']
        mobile = request.form['mobile']
        city = request.form['city']
        state=request.form['state']
        country=request.form['country']

        if username is not None:  # Check if username is not None
            conn = psycopg2.connect(host=dbhost, dbname=dbname, user=dbuser, password=dbpass)

            try:
                # Create a cursor
                cur = conn.cursor()

                # Retrieve the user's ID from the users table based on their username
                #cur.execute("SELECT user_id FROM users WHERE username = %s", (username,))
                #user_id = cur.fetchone()[0]

                # Insert data into the mobile_numbers table, associating it with the user
                cur.execute('''
                    CREATE TABLE IF NOT EXISTS mobile_numbers(
                        user_id UUID NOT NULL,
                        name VARCHAR(255) NOT NULL,
                        mobile VARCHAR(15) NOT NULL,
                        city VARCHAR(255),
                        state VARCHAR(255),
                        country VARCHAR(255)
                        )
                    ''')
                cur.execute("""
                    INSERT INTO mobile_numbers (user_id, name, mobile, city, state, country)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (user_id, name, mobile, city or '', state or '', country))

                # Commit the transaction
                conn.commit()

                flash('Data inserted successfully!', 'success')
                return redirect(url_for('insert'))
            except Exception as e:
                flash(f'Error: {str(e)}', 'danger')
            finally:
                # Close the database connection
                conn.close()

    return render_template('insert.html', username=username,user_id=user_id)

@app.route('/display')
def display():
    username = session.get('username')
    user_id = session.get('user_id')
    flash(user_id,username)
    if username is None or user_id is None:
        flash('Username or user ID not found in session.', 'danger')
        #return redirect(url_for('login'))  # Redirect to login page or handle as needed
    
    # Connect to PostgreSQL
    conn = psycopg2.connect(host=dbhost, dbname=dbname, user=dbuser, password=dbpass)

    try:
        # Create a cursor
        cur = conn.cursor()
        #cur.execute("SELECT user_id FROM users WHERE username = %s", (username,))
        #user_id = cur.fetchone()[0]
        # Retrieve data from the database
        cur.execute("SELECT * FROM mobile_numbers WHERE user_id = %s", (user_id,))
        mobile_numbers = cur.fetchall()

    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
        mobile_numbers = []

    finally:
        # Close the database connection
        conn.close()

    return render_template('display.html', mobile_numbers=mobile_numbers,username=username,user_id=user_id)
    
@app.route('/setting')
def setting():
    email = None
    username = session.get('username')
    user_id = session.get('user_id')
    if username is None or user_id is None:
        flash('Username or user ID not found in session.', 'danger')
        #return redirect(url_for('login'))  # Redirect to login page or handle as needed

    # Connect to PostgreSQL
    conn = psycopg2.connect(host=dbhost, dbname=dbname, user=dbuser, password=dbpass)

    try:
        # Create a cursor
        cur = conn.cursor()
        
        # Retrieve data from the database (including email) based on user_id
        cur.execute("SELECT email FROM users WHERE user_id = %s", (user_id,))
        email = cur.fetchone()[0]

    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')

    finally:
        # Close the database connection
        conn.close()
    
    return render_template('setting.html', username=username, user_id=user_id, email=email)



if __name__ == '__main__':
    app.run(debug=False,host='0.0.0.0')
