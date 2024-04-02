# ROOM.IO Flask Application

ROOM.IO is a Flask-based web application designed to simplify the search for apartment units while considering pet policies. It allows users to register, login, search for apartments, and register their pets to ensure compatibility with apartment policies.

## Features

- User Authentication: Register and login to access personalized features.
- Apartment Search: Search for apartment units based on specific criteria.
- Pet Registration: Register pets and automatically check against apartment pet policies.
- User and Pet Management: Update user profiles and pet information seamlessly.

## Setup and Installation

### Prerequisites

- Python 3.6+
- Flask
- pymysql
- bcrypt

### Configuration

Before running the application, ensure you have MySQL installed and running. Create a database named `ROOMIO` and import any necessary schema or data.

Update the `MYSQL connection parameters` in the application with your MySQL user, password, and other details as needed.

### Installing Dependencies

Install the required Python packages by running:

```
pip install Flask pymysql bcrypt
```

### Running the Application

To start the application, navigate to the directory containing the Flask application file and run:

```
python <application_filename>.py
```

Replace `<application_filename>` with the name of your Flask application file.

The application will start running on `http://127.0.0.1:5000` by default. You can access the web application by visiting this URL in a web browser.

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

## Security Notes

This application uses bcrypt for hashing and salting passwords, providing a layer of security for user authentication. Ensure that the Flask secret key and MySQL connection details are kept secure and not exposed publicly.

## Further Development

This README covers the basic setup and functionality. For further customization and development, consider adding more features such as:

- Email verification for new users.
- Advanced search filters for apartment units.
- User profile and pet detail pages.
- Integration with external APIs for additional apartment data.
