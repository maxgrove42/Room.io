# ROOM.IO Flask Application

ROOM.IO is a Flask-based web application designed to simplify the search for apartment units while considering pet policies. It allows users to register, login, search for apartments, and register their pets to ensure compatibility with apartment policies.

## Features

- User Authentication: Register and login to access personalized features.
- Apartment Search: Search for apartment units based on specific criteria.
- Pet Registration: Register pets and automatically check against apartment pet policies.
- Interest and Pet Management: Update pet and interest information seamlessly.
- Advanced Search Functionality: Zip Code, City, State, Rent Range, Bedroom count, Bathroom count, Amenities
- Display more detailed building and apartment information
- Mark interest: View who is interested in an apartment and mark your own interest.
- Display average rent prices in the zip code
- Monthly Rent Estimator based on zip code and bedroom / bathroom count
- Secure from SQL Injections and XSS attacks

### Code Files
## `main.py`:
- Where the Flask routing and majority of business logic is held. Simple SQL queries are also held here
  
## `services.py`:
- Handles user authentication / registration services and the complex business logic for Searching
- Searching slowly adds search criteria to the query as needed based on what search parameters were selected in `/search_units`

## `config.py`:
- Creates a config class to read in the `config.properties` file in `src/resources/config.properties`
- Configurable variables include Flask Secret Key, Flask Debug Mode, Flask Host Address, Flask Port, and database configuration settings

## `database.py`:
- Handles connection to database and MySQL handling of queries. Does not implement any business logic.

## `utilities.py`:
- Handling for password hashing and checking against hashed passwords.
  
## Setup and Installation

### Prerequisites

Prerequisite packages listed in `requirements.txt`

- Python 3.6+
- Flask
- pymysql
- bcrypt
- configparser

### Configuration

Before running the application, ensure you have MySQL installed and running. Create a database named `ROOMIO` and import any necessary schema or data (table definitions and sample data are located in the `src/resources/sql/` folder).

Update the `MYSQL connection parameters` in the `src/resources/config.properties` file with your MySQL user, password, and other details as needed.

### Installing Dependencies

Install the required Python packages (as described in `requirements.txt`) by running:

```
pip install Flask pymysql bcrypt configparser
```

### Running the Application

To start the application, navigate to the directory containing the Flask application file and run:

```
python run.py
```

The application will start running on `http://127.0.0.1:5000` by default. You can access the web application by visiting this URL in a web browser. You can modify the server and port in `src/resources/config.properties`

## Application Routes
# Flask Application Sitemap

## Routes Overview

### Public Routes

- **Homepage**
  - Endpoint: `/`
  - Description: Displays the main homepage.

- **Login**
  - Endpoint: `/login`
  - Methods: GET, POST
  - Description: Handles user login. Displays login form on GET and processes login on POST.

- **Register**
  - Endpoint: `/register`
  - Methods: GET, POST
  - Description: Handles new user registration. Displays registration form on GET and processes registration on POST.

- **Login Failure**
  - Endpoint: `/login_failure`
  - Description: Displays a login failure message.

### Authenticated Routes

- **Logout**
  - Endpoint: `/logout`
  - Description: Clears the user session and redirects to the homepage.

- **Dashboard**
  - Endpoint: `/dashboard`
  - Description: Displays user-specific dashboard information. Requires login.

- **Search Units**
  - Endpoint: `/search_units`
  - Description: Allows logged-in users to search for apartment units.

- **Unit Results**
  - Endpoint: `/unit_results`
  - Methods: GET, POST
  - Description: Shows results for apartment units based on search criteria. Requires login.

- **Show Details**
  - Endpoint: `/show_details`
  - Description: Displays detailed information about a specific apartment unit. Requires login.

- **Pet Details**
  - Endpoint: `/pet_details`
  - Methods: GET, POST
  - Description: Shows and allows modification of pet details. Requires login.

- **Delete Pet**
  - Endpoint: `/delete_pet`
  - Description: Deletes a specific pet based on user input. Requires login.

- **New Interest**
  - Endpoint: `/new_interest`
  - Methods: GET, POST
  - Description: Allows users to express interest in an apartment unit. Requires login.

- **Edit Interests**
  - Endpoint: `/edit_interests`
  - Description: Allows users to view and edit their interests in apartment units. Requires login.

- **Delete Interest**
  - Endpoint: `/delete_interest`
  - Description: Deletes a specific interest based on user selection. Requires login.

- **Estimate Rent**
  - Endpoint: `/estimate_rent`
  - Methods: GET, POST
  - Description: Allows users to estimate rent based on input parameters. Requires login.

## Additional Information

- The application utilizes session management to maintain user state across requests.
- Certain routes are protected with a `login_required` decorator to ensure that only authenticated users can access them.


## Security Notes

This application uses bcrypt for hashing and salting passwords, providing a layer of security for user authentication. Ensure that the Flask secret key and MySQL connection details are kept secure and not exposed publicly.

## Further Development

For further customization and development, I will consider adding more features such as:

- SQL queries stored in a static sql file to access, rather than directly in the Python code
- Email verification for new users.
- User profile page
- Integration with external APIs for additional apartment data (Perhaps Streeteasy?)
