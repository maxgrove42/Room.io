import src.database as database
import src.utilities as utilities


def authenticate_user(username, password):
    user_password = database.query_db('SELECT passwd FROM users WHERE username = %s', (username,), True)
    if user_password and utilities.check_password(password, user_password['passwd']):
        return True
    return False


def register_user(username, first_name, last_name, date_of_birth,
                  gender_identity, email, phone, password, confirm_password):
    if password != confirm_password:
        return False
    try:
        hashed_password = utilities.hash_password(password)
        query = 'INSERT INTO users VALUES(%s, %s, %s, %s, %s, %s, %s, %s)'
        database.query_db(query, (username, first_name, last_name, date_of_birth,
                                  gender_identity, email, phone, hashed_password))
        return True
    except Exception as e:
        print(e)
        return False


class SearchService:
    def perform_search(self, username, form_data):
        query, parameters = self._build_query(username, form_data)
        return database.query_db(query, parameters, one_column=False)

    def _build_query(self, username, form_data):
        query = ('''
                -- allAmenitiesTable used for search feature
                WITH allAmenitiesTable AS (
                    SELECT distinct * from (
                        SELECT unitRentID, aType FROM AmenitiesIn
                        UNION
                        SELECT au.unitRentId, p.aType FROM Provides p
                            INNER JOIN ApartmentUnit au
                            ON p.companyName = au.companyName
                            AND p.buildingName = au.buildingName
                    ) x -- derived table name
                ),
                bedroomCount AS (
                    SELECT unitRentId, COUNT(*) AS bedroomCount FROM rooms WHERE name LIKE '%%bedroom%%'
                    GROUP BY unitRentId
                ),
                bathroomCount AS (
                    SELECT unitRentId, COUNT(*) AS bathroomCount FROM rooms WHERE name LIKE '%%bathroom%%'
                    GROUP BY unitRentId
                ),
                -- find all the buildings/companies that don't allow the users pets
                petAllowances AS (
                    SELECT pp.companyName, pp.buildingName, count(*) as userPetsNotAllowed FROM PetPolicy pp
                    LEFT JOIN Pets p ON p.petType = pp.petType AND p.petSize = pp.petSize
                    WHERE username = %s AND pp.isAllowed = false
                    GROUP BY pp.companyName, pp.buildingName
                )
                SELECT au.*,
                    ifnull(bc1.bedroomCount, 0) as bedroomCount,
                    ifnull(bc2.bathroomCount, 0) as bathroomCount,
                    -- if there were no rows for this username and building/company
                    -- this means that all the users pets are allowed
                    (pa.userPetsNotAllowed is null) as petsAllowed
                FROM ApartmentUnit au
                LEFT JOIN bedroomCount bc1 ON bc1.unitRentId = au.unitRentId
                LEFT JOIN bathroomCount bc2 ON bc2.unitRentId = au.unitRentId
                LEFT JOIN petAllowances pa ON pa.companyName = au.companyName AND pa.buildingName = au.buildingName
                INNER JOIN apartmentBuilding ab ON ab.buildingName = au.buildingName AND ab.companyName = au.companyName
                -- including this so we can add-on conditions to the where clause as needed
                WHERE 1 = 1 
                ''')
        parameters = [username]  # Start parameters with username, then extend with form_data
        query += self._create_list_parameter_query('au.buildingName', form_data['building'])
        parameters += form_data['building']

        query += self._create_list_parameter_query('au.companyName', form_data['company'])
        parameters += form_data['company']

        query += self._create_single_parameter_query('AddrZipCode', form_data['zip_code'])
        if form_data['zip_code'] != '': parameters.append(form_data['zip_code'])

        query += self._create_single_parameter_query('AddrCity', form_data['city'])
        if form_data['city'] != '': parameters.append(form_data['city'])

        query += self._create_single_parameter_query('AddrState', form_data['state'])
        if form_data['state'] != '': parameters.append(form_data['state'])

        # amenities handling
        if len(form_data['amenity']) >= 1:
            placeholders = ', '.join(['%s'] * len(form_data['amenity']))
            query += f''' AND au.unitRentId IN (
                                SELECT unitRentID
                                FROM allAmenitiesTable
                                WHERE aType IN ({placeholders})
                                GROUP BY unitRentID
                                HAVING COUNT(DISTINCT aType) = {len(form_data['amenity'])}
                            )
                         '''
            parameters += form_data['amenity']

        # handle the min and max bathrooms manually
        if form_data['min_bedrooms'] != '':
            query += ' AND bedroomCount >= %s '
            parameters.append(form_data['min_bedrooms'])
        if form_data['max_bedrooms'] != '':
            query += ' AND bedroomCount <= %s '
            parameters.append(form_data['max_bedrooms'])
        if form_data['min_bathrooms'] != '':
            query += ' AND bathroomCount >= %s '
            parameters.append(form_data['min_bathrooms'])
        if form_data['max_bathrooms'] != '':
            query += ' AND bathroomCount <= %s '
            parameters.append(form_data['max_bathrooms'])

        return query, parameters

    def _create_list_parameter_query(self, columnName, list):
        query = ''
        if len(list) >= 1:
            placeholders = ', '.join(['%s'] * len(list))
            query = f' AND {columnName} IN ({placeholders}) '
        return query

    def _create_single_parameter_query(self, columnName, parameter):
        query = ''
        if parameter != '':
            query = f' AND {columnName} = %s '
        return query