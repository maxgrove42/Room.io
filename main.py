from flask import Flask, render_template, request, session, url_for, redirect, flash
import pymysql.cursors
import bcrypt  # for hashing and salting password.

# Flask Parameters
app = Flask(__name__)
secret_key = 'coffee-lock-98@3302'
host = '127.0.0.1'
flask_port = 5000
debug = True

# MYSQL connection parameters
sql_host = 'localhost'
sql_port = 3306
sql_user = 'root'
sql_password = 'sql-pwd'
sql_db = 'ROOMIO'
sql_charset='utf8mb4'

# app routing names and HTML page names in the dictionary
start_page = '/'
login_page = '/login'
register_page = '/register'
register_auth_page = '/registerAuth'
login_auth_page = '/loginAuth'
home_page = '/home'

# create a dictionary to store html pages,
#  so that page name is tied to html page
html = {}
html[start_page] = 'index.html'
html[login_page] = 'login.html'
html[register_page] = 'register.html'
html[home_page] = 'home.html'


# Configure MySQL
conn = pymysql.connect(host=sql_host,
                       port=sql_port,
                       user=sql_user,
                       password=sql_password,
                       db=sql_db,
                       charset=sql_charset,
                       cursorclass=pymysql.cursors.DictCursor)

# BEGIN FLASK ROUTING
@app.route(start_page)
def index():
    return render_template(html[start_page])


@app.route(login_page)
def login():
    return render_template(html[login_page])


@app.route(register_page)
def register():
    return render_template(html[register_page])


@app.route(login_auth_page, methods=['GET', 'POST'])
def loginAuth():
    # grabs information from the forms
    username = request.form['username']
    password = request.form['password'].encode()  # convert to bytes

    # cursor used to send queries
    cursor = conn.cursor()
    # executes query
    query = 'SELECT * FROM Users WHERE username = %s'
    cursor.execute(query, username)
    # stores the results in a variable
    data = cursor.fetchone()
    # use fetchall() if you are expecting more than 1 data row
    cursor.close()
    error = None

    if data and bcrypt.checkpw(password, data['passwd'].encode()):
        # creates a session for the user
        # session is a built in
        session['username'] = username
        return redirect(home_page)
    else:
        # returns an error message to the html page
        error = 'Invalid username or password'
        return render_template(html[login_page], error=error)

    # Authenticates the register


@app.route(register_auth_page, methods=['GET', 'POST'])
def registerAuth():
    # grabs information from the forms
    username = request.form['username']
    password = request.form['password'].encode()
    confirm_password = request.form['confirm_password'].encode()
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    date_of_birth = request.form['date_of_birth']
    gender_identity = request.form['gender_identity']
    phone = request.form['phone']
    email = request.form['email']

    if password != confirm_password:
        error = "Password and confirmation must match"
        return render_template('register.html', error=error)

    hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())

    # cursor used to send queries
    cursor = conn.cursor()
    # executes query
    query = 'SELECT * FROM users WHERE username = %s'
    cursor.execute(query, username)
    # stores the results in a variable
    data = cursor.fetchone()
    # use fetchall() if you are expecting more than 1 data row
    error = None
    if (data):
        # If the previous query returns data, then user exists
        error = "This user already exists"
        return render_template('register.html', error=error)
    else:
        # insert (username, firstname, lastname, dob, gender, email, phone, password)
        ins = 'INSERT INTO users VALUES(%s, %s, %s, %s, %s, %s, %s, %s)'
        cursor.execute(ins, (username, first_name, last_name, date_of_birth,
                             gender_identity, email, phone, hashed_password))
        conn.commit()
        cursor.close()
        session['username'] = username
        return redirect(home_page)

@app.route(home_page)
def home():
    return render_template(html[home_page])


# Press the green button in the gutter to run the script.
if __name__ == "__main__":
    app.secret_key = secret_key
    app.run(host, flask_port, debug=debug)