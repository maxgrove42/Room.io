from flask import Flask, render_template, request, session, url_for, redirect, flash
import pymysql.cursors
import bcrypt  # for hashing and salting password.


from pymysql import IntegrityError

# TODO ################################################
# deal with session['first name'] in sql rather than
#   in session
# TODO ################################################

# Flask Parameters
app = Flask(__name__)
config = Config()

host = config.db_host
flask_port = config.db_port

# MYSQL connection parameters
sql_host = config['Database']['db_host']
sql_port = int(config['Database']['db_port'])
sql_user = config['Database']['db_username']
sql_password = config['Database']['db_password']
sql_db = config['Database']['db_name']
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
new_interest_page = '/new_interest'
add_interest_page = '/addInterest'
edit_interests = '/edit_interests'
delete_interest = '/deleteInterest'
estimate_rent = '/estimate_rent'
estimate_rent_results = '/estimate_rent_results'

# create a dictionary to store html pages,
#  so that page name is tied to html page
html = {}
html[start_page] = 'index.html'
html[login_page] = 'login.html'
html[register_page] = 'register.html'
html[home_page] = 'dashboard.html'
html[search_units_page] = 'search_units.html'
html[unit_results_page] = 'unit_results.html'
html[register_pet_page] = 'pet_details.html'
html[show_details_page] = 'show_details.html'
html[new_interest_page] = 'new_interest.html'
html[edit_interests] = 'edit_interests.html'
html[estimate_rent] = 'estimate_rent.html'
html[estimate_rent_results] = 'estimate_rent_results.html'

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
                       "WHERE i.UnitRentID = %s"
                       "    AND u.username != %s")
    cursor.execute(interests_query, (unit_rent_id, session['username']))
    interests_data = cursor.fetchall()

    squareFootDifference = 0.10 # allowable range of square footage for similar units
    similar_rent_query = f'''
                            select avg(monthlyRent) as similar_avg_rent
                            from ApartmentUnit au
                            left join ApartmentBuilding ab
                                ON au.companyname = ab.companyname
                                and au.buildingname = ab.buildingname
                            where squareFootage >= ({1-squareFootDifference})*%s
                                AND squareFootage <= ({1+squareFootDifference})*%s
                                AND ab.AddrCity = %s and ab.AddrState = %s
                         '''
    cursor.execute(similar_rent_query, (int(unit_data['squareFootage']),
                                        int(unit_data['squareFootage']),
                                        building_data['AddrCity'],
                                        building_data['AddrState']))
    similar_avg_rent = cursor.fetchone()
    similar_avg_rent = int(similar_avg_rent['similar_avg_rent']*100)/100

    interests_data = cursor.fetchall()
    # interest check if current user is already interested.
    username = session['username']
    check_interest_query = ("SELECT * "
                            "FROM Interests "
                            "WHERE unitRentId = %s AND username = %s")
    cursor.execute(check_interest_query, (unit_rent_id, username))
    interest_check_data = cursor.fetchall()
    already_interested = (len(interest_check_data) >= 1)
    ###

    cursor.close()
    return render_template(html[show_details_page],
                           unit_rent_id=unit_rent_id,
                           unit_data=unit_data,
                           building_data=building_data,
                           rooms_data=rooms_data,
                           pet_data=pet_data,
                           unit_amenities_data=unit_amenities_data,
                           building_amenities_data=building_amenities_data,
                           interests_data=interests_data,
                           already_interested=already_interested,
                           similar_avg_rent=similar_avg_rent)


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


@app.route(new_interest_page, methods=['GET', 'POST'])
def new_interest():
    unit_rent_id = int(request.args.get('unitRentId'))
    cursor = conn.cursor()
    username = session['username']

    building_query = ("SELECT ab.CompanyName, ab.BuildingName, ab.AddrNum, ab.AddrStreet, "
                      " ab.AddrCity, ab.AddrState, ab.AddrZipCode "
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

    cursor.close()
    return render_template(html[new_interest_page],
                           building_data=building_data,
                           unit_data=unit_data,
                           unit_rent_id=unit_rent_id)


@app.route(add_interest_page, methods=['GET', 'POST'])
def addInterest():
    username = session['username']
    unit_rent_id = int(request.args.get('unitRentId'))
    roommate_count = request.form['roommate_count']
    move_in_date = request.form['move_in_date']
    cursor = conn.cursor()
    insert_query = "INSERT INTO Interests values(%s, %s, %s, %s)"
    cursor.execute(insert_query, (username, unit_rent_id, roommate_count, move_in_date))
    conn.commit()
    cursor.close()
    return redirect(show_details_page + '?unitRentId=' + str(unit_rent_id))


@app.route(edit_interests)
def editInterests():
    username = session['username']
    cursor = conn.cursor()
    interests_query = ("SELECT ab.AddrNum, ab.AddrStreet, ab.AddrCity, ab.AddrState, ab.AddrZipCode, "
                       "    au.unitNumber, au.MonthlyRent, au.squareFootage, "
                       "    i.RoommateCnt, i.MoveInDate, i.unitRentId "
                       "FROM Interests i "
                       "JOIN ApartmentUnit au "
                       "    ON i.UnitRentId = au.UnitRentId "
                       "JOIN ApartmentBuilding ab "
                       "    ON ab.CompanyName = au.CompanyName "
                       "    AND ab.BuildingName = au.BuildingName "
                       "WHERE i.username = %s")
    cursor.execute(interests_query, (username,))
    interests_data = cursor.fetchall()
    cursor.close()
    return render_template(html[edit_interests],
                           interests_data=interests_data)


@app.route(delete_interest, methods=['GET'])
def deleteInterest():
    username = session['username']
    unit_rent_id = int(request.args.get('unitRentId'))
    cursor = conn.cursor()
    # safety check to ensure this user has an interest in the unit
    possible_rent_ids_query = ("SELECT distinct unitRentId "
                               "FROM interests "
                               "WHERE username = %s")
    cursor.execute(possible_rent_ids_query, (username,))
    possible_rent_ids = cursor.fetchall()
    valid_rent_ids = [row['unitRentId'] for row in possible_rent_ids]
    if unit_rent_id not in valid_rent_ids:
        return redirect(edit_interests)

    # now actually do the delete.
    delete_query = ("DELETE FROM Interests WHERE username = %s AND unitRentId = %s "
                    "LIMIT 1")  # limit included as a safety. only allow for one row delete.
    cursor.execute(delete_query, (username, unit_rent_id))
    conn.commit()
    cursor.close()

    return redirect(edit_interests)


@app.route(estimate_rent, methods=['GET', 'POST'])
def estimateRent():
    return render_template(html[estimate_rent])


@app.route(estimate_rent_results, methods=['GET', 'POST'])
def estimateRentResults():
    zipcode = request.form['zipcode']
    minBedrooms = request.form['minBedrooms']
    maxBedrooms = request.form['maxBedrooms']
    minBathrooms = request.form['minBathrooms']
    maxBathrooms = request.form['maxBathrooms']

    query = '''
                with bedroomCount AS (
                    SELECT unitRentId, COUNT(*) AS bedroomCount
                    FROM rooms
                    WHERE name LIKE '%%bedroom%%'
                    GROUP BY unitRentId
                ),
                bathroomCount AS (
                    SELECT unitRentId, COUNT(*) AS bathroomCount
                    FROM rooms
                    WHERE name LIKE '%%bathroom%%'
                    GROUP BY unitRentId
                )
                select avg(au.monthlyRent) as averageMonthlyRent
                from apartmentunit au
                inner join bedroomCount bc
					ON au.unitRentId = bc.unitRentId
				inner join bathroomCount brc
					ON au.unitRentId = brc.unitRentId
                inner join apartmentBuilding ab
                    on au.companyName = ab.companyName
                    and au.buildingName = ab.buildingName
                WHERE ab.AddrZipCode = %s -- add in future constraints below with AND 
            '''
    parameters = [zipcode]
    if minBedrooms != '':
        query += ' AND bedroomCount >= %s'
        parameters.append(minBedrooms)
    if maxBedrooms != '':
        query += ' AND bedroomCount <= %s'
        parameters.append(maxBedrooms)
    if minBathrooms != '':
        query += ' AND bathroomCount >= %s'
        parameters.append(minBathrooms)
    if maxBathrooms != '':
        query += ' AND bathroomCount <= %s'
        parameters.append(maxBathrooms)

    cursor = conn.cursor()
    cursor.execute(query, tuple(parameters))
    averageMonthlyRent = cursor.fetchone()
    cursor.close()

    averageMonthlyRent = averageMonthlyRent['averageMonthlyRent']
    if (averageMonthlyRent is not None):
        averageMonthlyRent = int(averageMonthlyRent * 100)/100

    return render_template(html[estimate_rent_results],
                           averageMonthlyRent=averageMonthlyRent,
                           zipcode=zipcode,
                           minBedrooms = minBedrooms,
                           maxBedrooms=maxBedrooms,
                           minBathrooms=minBathrooms,
                           maxBathrooms=maxBathrooms)





if __name__ == "__main__":
    app.secret_key = secret_key
    app.run(host, flask_port, debug=debug)
