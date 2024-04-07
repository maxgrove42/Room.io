from flask import Flask, render_template, request, session, url_for, redirect, flash
import pymysql.cursors
import bcrypt  # for hashing and salting password.
import configparser # for reading in config.properties

config = configparser.ConfigParser()
config.read('/resources/config.properties')

# Flask Parameters
app = Flask(__name__)
secret_key = config['flask.secret.key']
host = config['flask.host']
flask_port = config['flask.port']
debug = False

# MYSQL connection parameters
sql_host = config['database.host']
sql_port = config['database.port']
sql_user = config['database.username']
sql_password = config['database.password']
sql_db = config['database.name']
sql_charset = 'utf8mb4'

# app routing names and HTML page names in the dictionary
start_page = '/'
login_page = '/login'
register_page = '/register'
register_auth_page = '/registerAuth'
login_auth_page = '/loginAuth'
home_page = '/home'
logout_page = '/logout'
search_units_page = '/search_units'
unit_results_page = '/unit_results'
register_pet_page = '/register_pet'
add_pet_page = '/add_pet'
show_details_page = '/show_details'

# create a dictionary to store html pages,
#  so that page name is tied to html page
html = {}
html[start_page] = 'index.html'
html[login_page] = 'login.html'
html[register_page] = 'register.html'
html[home_page] = 'home.html'
html[search_units_page] = 'search_units.html'
html[unit_results_page] = 'unit_results.html'
html[register_pet_page] = 'register_pet.html'
html[show_details_page] = 'show_details.html'

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
        session['first_name'] = data['first_name']  # probably cleaner to deal with first name with a SQL select
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
    if data:
        # If the previous query returns data, then user exists
        error = "This user already exists"
        cursor.close()
        return render_template('register.html', error=error)
    else:
        # insert (username, firstname, lastname, dob, gender, email, phone, password)
        ins = 'INSERT INTO users VALUES(%s, %s, %s, %s, %s, %s, %s, %s)'
        cursor.execute(ins, (username, first_name, last_name, date_of_birth,
                             gender_identity, email, phone, hashed_password))
        conn.commit()
        cursor.close()
        session['username'] = username
        session['first_name'] = first_name  # probably cleaner to deal with first name with a SQL select
        return redirect(home_page)


@app.route(home_page)
def home():
    name = session['first_name']
    return render_template(html[home_page], first_name=name, posts="test template")


@app.route(search_units_page)
def search_units():
    return render_template(html[search_units_page])


@app.route(unit_results_page, methods=['GET', 'POST'])
def show_results():
    building = request.form['building']
    company = request.form['company']

    cursor = conn.cursor()
    query = 'SELECT * FROM ApartmentUnit WHERE BuildingName LIKE %s AND CompanyName LIKE %s'
    cursor.execute(query, ('%' + building + '%', '%' + company + '%'))
    data = cursor.fetchall()

    query = ('SELECT DISTINCT p.petType, p.petSize, p.petName, pp.isAllowed '
             'FROM Pets p '
             'JOIN petPolicy pp '
             'WHERE p.username = %s '
             'AND pp.BuildingName LIKE %s AND pp.CompanyName LIKE %s '
             'AND pp.isAllowed = False')
    cursor.execute(query, (session['username'], '%' + building + '%', '%' + company + '%'))
    pets_not_allowed = cursor.fetchall()
    cursor.close()

    return render_template(html[unit_results_page], data=data, pets_not_allowed=pets_not_allowed)


@app.route(show_details_page)
def show_details():
    unit_rent_id = int(request.args.get('unitRentId'))
    cursor = conn.cursor()

    building_query = ("SELECT ab.CompanyName, ab.BuildingName, ab.AddrNum, ab.AddrStreet,"
                      " ab.AddrCity, ab.AddrState, ab.AddrZipCode, ab.YearBuilt "
                      "FROM ApartmentBuilding ab "
                      "LEFT JOIN ApartmentUnit au "
                      "   ON au.CompanyName = ab.CompanyName "
                      "   AND au.BuildingName = ab.BuildingName "
                      "WHERE au.unitRentId = %s")
    cursor.execute(building_query, (unit_rent_id,))
    building_data = cursor.fetchone()

    unit_details_query = ("SELECT * FROM ApartmentUnit "
                          "WHERE UnitRentId = %s")
    cursor.execute(unit_details_query, (unit_rent_id,))
    unit_data = cursor.fetchone()

    rooms_query = ("SELECT * FROM Rooms "
                   "WHERE UnitRentId = %s")
    cursor.execute(rooms_query, unit_rent_id)
    rooms_data = cursor.fetchall()

    pet_policy_query = ("SELECT pp.PetType, pp.PetSize, pp.isAllowed, pp.RegistrationFee, pp.MonthlyFee "
                        "FROM PetPolicy pp "
                        "LEFT JOIN ApartmentUnit au "
                        "   ON au.CompanyName = pp.CompanyName "
                        "   AND au.BuildingName = pp.BuildingName "
                        "WHERE au.UnitRentID = %s")
    cursor.execute(pet_policy_query, (unit_rent_id))
    pet_data = cursor.fetchall()

    unit_amenities_query = ("SELECT ai.aType, a.Description "
                            "FROM AmenitiesIn ai "
                            "LEFT JOIN Amenities a "
                            "    ON a.aType = ai.aType "
                            "WHERE ai.UnitRentID = %s ")
    cursor.execute(unit_amenities_query, (unit_rent_id))
    unit_amenities_data = cursor.fetchall()

    building_amenities_query = ("SELECT p.aType, a.Description, p.fee "
                                "FROM Provides p "
                                "LEFT JOIN Amenities a "
                                "   ON p.aType = a.aType "
                                "LEFT JOIN ApartmentUnit au "
                                "   ON au.CompanyName = p.CompanyName "
                                "   AND au.BuildingName = p.BuildingName "
                                "WHERE au.UnitRentId = %s")
    cursor.execute(building_amenities_query, (unit_rent_id,))
    building_amenities_data = cursor.fetchall()

    interests_query = ("SELECT u.first_name, u.gender, i.RoommateCnt, i.MoveInDate "
                       "FROM Interests i "
                       "LEFT JOIN Users u "
                       "    ON i.username = u.username "
                       "WHERE i.UnitRentID = %s")
    cursor.execute(interests_query, (unit_rent_id))
    interests_data = cursor.fetchall()

    cursor.close()
    return render_template(html[show_details_page],
                           unit_data=unit_data,
                           building_data=building_data,
                           rooms_data=rooms_data,
                           pet_data=pet_data,
                           unit_amenities_data=unit_amenities_data,
                           building_amenities_data=building_amenities_data,
                           interests_data=interests_data)


@app.route(logout_page)
def logout():
    session.pop('username')
    session.pop('first_name')  # probably cleaner to deal with first name with a SQL select
    return redirect(start_page)


@app.route(register_pet_page)
def register_pet():
    # get current pets for username
    query = ('SELECT petName, petType, petSize '
             'FROM Pets '
             'WHERE username = %s ')
    cursor = conn.cursor()
    cursor.execute(query, session['username'])
    data = cursor.fetchall()
    return render_template(html[register_pet_page], pets=data)


@app.route(add_pet_page, methods=['GET', 'POST'])
def add_pet():
    try:
        pet_name = request.form['pet_name']
        pet_type = request.form['pet_type']
        pet_size = request.form['pet_size']
        ins = 'INSERT INTO pets VALUES (%s, %s, %s, %s)'
        cursor = conn.cursor()
        cursor.execute(ins, (pet_name, pet_type, pet_size, session['username']))
        conn.commit()
        cursor.close()
        flash('Pet added successfully', 'success')  # Flash the success message
    except:
        flash('Unable to add pet. Please try again.' 'warning')
    finally:
        return redirect(register_pet_page)


# Press the green button in the gutter to run the script.
if __name__ == "__main__":
    app.secret_key = secret_key
    app.run(host, flask_port, debug=debug)
