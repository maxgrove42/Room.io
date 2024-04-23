from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash

import src.config as config
import src.services as services
import src.database as database

app = Flask(__name__)
config = config.Config()
app.secret_key = config.secret_key
flask_host = config.flask_host
flask_port = config.flask_port
debug = config.debug

# TODO
# Potentially add error reasons to registration?
# Bug fix : self-describe pet doesn't wor properly
# Bug fix : self-describe gender doesn't work properly.
# It records gender as "self describe", not the box
# TODO


# Decorator function to ensure log in for pages that require it.
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login_failure'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def homepage():
    return render_template('/index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if services.authenticate_user(username, password):
            # creates a session for the user
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
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
        if services.register_user(username, first_name, last_name, date_of_birth,
                                  gender_identity, email, phone, password):
            # creates a session for the user
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            return render_template('register.html', error="Registration failed")
    return render_template('register.html')


@app.route('/logout')
def logout():
    session.pop('username')
    return redirect('/')


@app.route('/login_failure')
def login_failure():
    return render_template('login_failure.html')


@app.route('/dashboard')
@login_required
def dashboard():
    username = session['username']
    name = database.query_db('SELECT first_name FROM Users WHERE username = %s',
                             (username,),
                             one_column=True)
    return render_template('dashboard.html',
                           first_name=name['first_name'])


@app.route('/search_units')
@login_required
def search_units():
    username = session['username']
    amenities = database.query_db('SELECT distinct aType FROM Amenities')
    buildings = database.query_db('SELECT distinct buildingName FROM ApartmentBuilding')
    companies = database.query_db('SELECT distinct companyName FROM ApartmentBuilding')

    return render_template('search_units.html',
                           amenities=amenities,
                           companies=companies,
                           buildings=buildings)


@app.route('/unit_results', methods=['GET', 'POST'])
@login_required
def show_results():
    username = session['username']
    form_data = {
        'building': request.form.getlist('building'),
        'company': request.form.getlist('company'),
        'zip_code': request.form['zipcode'],
        'city': request.form['city'],
        'state': request.form['state'],
        'min_bedrooms': request.form['minBedrooms'],
        'max_bedrooms': request.form['maxBedrooms'],
        'min_bathrooms': request.form['minBathrooms'],
        'max_bathrooms': request.form['maxBathrooms'],
        'amenity': request.form.getlist('desiredAmenities')
    }
    data = services.SearchService().perform_search(session['username'], form_data)
    return render_template('unit_results.html', data=data)


@app.route('/show_details')
@login_required
def show_details():
    unit_rent_id = int(request.args.get('unitRentId'))
    username = session['username']
    sq_foot_diff_similar_units = 0.10 # Sqaure Foot Difference Allowance for similar units

    building_data = database.query_db('''
                                      SELECT ab.CompanyName, ab.BuildingName, ab.AddrNum, ab.AddrStreet,
                                        ab.AddrCity, ab.AddrState, ab.AddrZipCode, ab.YearBuilt
                                      FROM ApartmentBuilding ab 
                                      LEFT JOIN ApartmentUnit au ON au.CompanyName = ab.CompanyName AND au.BuildingName = ab.BuildingName
                                      WHERE au.unitRentId = %s
                                      ''',
                                      (unit_rent_id,),
                                      one_column=True)
    unit_data = database.query_db('SELECT * FROM ApartmentUnit WHERE UnitRentId = %s',
                                  (unit_rent_id,),
                                  True)
    rooms_data = database.query_db('SELECT * FROM Rooms WHERE UnitRentId = %s',
                                   (unit_rent_id,),
                                   False)
    pet_data = database.query_db('''
                                 SELECT pp.PetType, pp.PetSize, pp.isAllowed, pp.RegistrationFee, pp.MonthlyFee
                                 FROM PetPolicy pp
                                 LEFT JOIN ApartmentUnit au ON au.CompanyName = pp.CompanyName AND au.BuildingName = pp.BuildingName
                                 WHERE au.UnitRentID = %s
                                 ''',
                                 (unit_rent_id,),
                                 False)
    unit_amenities_data = database.query_db('''
                                            SELECT ai.aType, a.Description FROM AmenitiesIn ai
                                            LEFT JOIN Amenities a ON a.aType = ai.aType
                                            WHERE ai.UnitRentID = %s
                                            ''',
                                            (unit_rent_id,),
                                            False)
    building_amenities_data = database.query_db('''
                                                SELECT p.aType, a.Description, p.fee FROM Provides p
                                                LEFT JOIN Amenities a ON p.aType = a.aType
                                                LEFT JOIN ApartmentUnit au ON au.CompanyName = p.CompanyName AND au.BuildingName = p.BuildingName
                                                WHERE au.UnitRentId = %s
                                                ''',
                                                (unit_rent_id,),
                                                False)
    interests_data = database.query_db('''
                                       SELECT u.first_name, u.gender, i.RoommateCnt, i.MoveInDate
                                       FROM Interests i
                                       LEFT JOIN Users u ON i.username = u.username 
                                       WHERE i.UnitRentID = %s AND u.username != %s
                                       ''',
                                       (unit_rent_id, username),
                                       False)
    similar_avg_rent = database.query_db(f'''
                                         SELECT avg(monthlyRent) as similar_avg_rent FROM ApartmentUnit au
                                         LEFT JOIN ApartmentBuilding ab
                                             ON au.companyname = ab.companyname and au.buildingname = ab.buildingname
                                         where squareFootage >= ({1-sq_foot_diff_similar_units})*%s
                                             AND squareFootage <= ({1+sq_foot_diff_similar_units})*%s
                                             AND ab.AddrCity = %s and ab.AddrState = %s
                                         ''',
                                         (int(unit_data['squareFootage']),
                                          int(unit_data['squareFootage']),
                                          building_data['AddrCity'],
                                          building_data['AddrState']),
                                         True)
    similar_avg_rent = int(similar_avg_rent['similar_avg_rent'] * 100) / 100
    already_interested = len(database.query_db('SELECT * FROM Interests WHERE unitRentId = %s AND username = %s',
                                           (unit_rent_id, username),
                                           False)) >= 1
    return render_template('show_details.html',
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


@app.route('/pet_details', methods=['GET', 'POST'])
@login_required
def pet_details():
    username = session['username']

    if request.method == 'POST':
        try:
            pet_name = request.form['pet_name']
            pet_type = request.form['pet_type']
            pet_size = request.form['pet_size']
            database.query_db('INSERT INTO pets VALUES (%s, %s, %s, %s)',
                              (pet_name, pet_type, pet_size, username))
            flash('Pet added successfully', category='success')
        except:
            flash('Unable to add pet. Please try again', category='warning')
    data = database.query_db('SELECT petName, petType, petSize FROM Pets WHERE username = %s',
                             (username,),
                             False)
    return render_template('pet_details.html', pets=data)


@app.route('/delete_pet')
@login_required
def delete_pet():
    username = session['username']
    pet_name = request.args.get('pet_name')
    pet_type = request.args.get('pet_type')
    delete_query = 'DELETE FROM Pets WHERE username = %s AND petName = %s AND petType = %s LIMIT 1'
    database.query_db(delete_query, (username, pet_name, pet_type))
    return redirect(url_for('pet_details'))


@app.route('/new_interest', methods=['GET', 'POST'])
@login_required
def interests():
    username = session['username']
    unit_rent_id = int(request.args.get('unitRentId'))
    if request.method == 'POST':
        roommate_count = request.form['roommate_count']
        move_in_date = request.form['move_in_date']
        database.query_db('INSERT INTO Interests VALUES (%s, %s, %s, %s)',
                          (username, unit_rent_id, roommate_count, move_in_date))
        return redirect(url_for('show_details',
                                unitRentId=unit_rent_id))
    building_data = database.query_db('''
                                      SELECT ab.CompanyName, ab.BuildingName, ab.AddrNum, ab.AddrStreet,
                                        ab.AddrCity, ab.AddrState, ab.AddrZipCode
                                      FROM ApartmentBuilding ab 
                                      LEFT JOIN ApartmentUnit au ON au.CompanyName = ab.CompanyName AND au.BuildingName = ab.BuildingName
                                      WHERE au.unitRentId = %s
                                      ''',
                                      (unit_rent_id,),
                                      True)

    unit_data = database.query_db('SELECT * FROM ApartmentUnit WHERE UnitRentId = %s',
                                  (unit_rent_id,),
                                  True)
    return render_template('/new_interest.html',
                           building_data=building_data,
                           unit_data=unit_data,
                           unit_rent_id=unit_rent_id)


@app.route('/edit_interests')
@login_required
def edit_interests():
    username = session['username']
    interests_query = ('''SELECT ab.AddrNum, ab.AddrStreet, ab.AddrCity, ab.AddrState, ab.AddrZipCode, au.unitNumber,
                          au.MonthlyRent, au.squareFootage, i.RoommateCnt, i.MoveInDate, i.unitRentId 
                          FROM Interests i 
                          JOIN ApartmentUnit au ON i.UnitRentId = au.UnitRentId
                          JOIN ApartmentBuilding ab ON ab.CompanyName = au.CompanyName AND ab.BuildingName = au.BuildingName 
                          WHERE i.username = %s
                       ''')
    interests_data = database.query_db(interests_query, (username,), False)
    return render_template('edit_interests.html',
                           interests_data=interests_data)


@app.route('/delete_interest')
@login_required
def delete_interest():
    username = session['username']
    unit_rent_id = int(request.args.get('unitRentId'))
    # safety check to ensure this user has an interest in the unit
    possible_rent_ids_query = 'SELECT distinct unitRentId FROM interests WHERE username = %s'
    possible_rent_ids = database.query_db(possible_rent_ids_query, (username,), True)
    if unit_rent_id not in possible_rent_ids.values():
        return redirect(url_for('edit_interests'))
    # now actually delete. limit included as a safety. only allow for one row delete.
    delete_query = 'DELETE FROM Interests WHERE username = %s AND unitRentId = %s LIMIT 1'
    database.query_db(delete_query, (username, unit_rent_id))
    return redirect(url_for('edit_interests'))


@app.route('/estimate_rent', methods=['GET', 'POST'])
@login_required
def estimate_rent():
    averageMonthlyRent = None
    if request.method == 'POST':
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
        data = database.query_db(query, tuple(parameters), True)
        averageMonthlyRent = data['averageMonthlyRent']
        if (averageMonthlyRent is not None):
            averageMonthlyRent = int(averageMonthlyRent * 100) / 100
        pass

    return render_template('estimate_rent.html',
                           averageMonthlyRent=averageMonthlyRent)


if __name__ == "__main__":
    app.run(flask_host, flask_port, debug=debug)
