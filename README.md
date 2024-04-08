# ROOM.IO Flask Application

ROOM.IO is a Flask-based web application designed to simplify the search for apartment units while considering pet policies. It allows users to register, login, search for apartments, and register their pets to ensure compatibility with apartment policies.

## Features

- User Authentication: Register and login to access personalized features.
- Apartment Search: Search for apartment units based on specific criteria.
- Pet Registration: Register pets and automatically check against apartment pet policies.
- User and Pet Management: Update user profiles and pet information seamlessly.
- Display more detailed building and apartment information

## Upcoming Features

- Mark interest: View who is interested in an apartment and mark your own interest.
- Ensure security from SQL Injections and XSS attacks

## Setup and Installation

### Prerequisites

Prerequisite packages listed in `requirements.txt`

- Python 3.6+
- Flask
- pymysql
- bcrypt
- configparser

### Configuration

Before running the application, ensure you have MySQL installed and running. Create a database named `ROOMIO` and import any necessary schema or data (table definitions and sample data are located in the `/resources/sql/` folder).

Update the `MYSQL connection parameters` in the `/resources/config.properties` file with your MySQL user, password, and other details as needed.

### Installing Dependencies

Install the required Python packages (as described in `requirements.txt`) by running:

```
pip install Flask pymysql bcrypt
```

### Running the Application

To start the application, navigate to the directory containing the Flask application file and run:

```
python main.py
```

The application will start running on `http://127.0.0.1:5000` by default. You can access the web application by visiting this URL in a web browser. You can modify the server and port in `/resources/config.properties`

## Application Routes

- `/`: The home page.
- `/login`: The login page.
- `/register`: The registration page for new users.
- `/home`: The main dashboard after logging in.
- `/logout`: Logout and clear session.
- `/search_units`: Page to search for apartment units.
- `/unit_results`: Display search results for apartments.
- `/register_pet`: Page to register pets.
- `/add_pet`: Backend route to add a pet to the database.
- `/show_details`: Page to display more detailed information on a given building

## Security Notes

This application uses bcrypt for hashing and salting passwords, providing a layer of security for user authentication. Ensure that the Flask secret key and MySQL connection details are kept secure and not exposed publicly.

## Further Development

For further customization and development, I will consider adding more features such as:

- SQL queries stored in a static sql file to access, rather than directly in the Python code
- Email verification for new users.
- Advanced search filters for apartment units.
- User profile and pet detail pages.
- Integration with external APIs for additional apartment data (Perhaps Streeteasy?)
