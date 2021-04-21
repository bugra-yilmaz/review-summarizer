# Created by bugra-yilmaz on 08.02.2021.
#
# Flask REST API module for accessing and querying the MySQL database

# Imports
from flask import Flask
from flask import request

from common import *
from data_loader import flush
from data_loader import load_data

# Initialize Flask app
app = Flask(__name__)

# Load the initial data with startup
load_data()


# Placeholder index route
@app.route('/')
def index():
    return 'Welcome to the REST API!'


# Assign URL http://localhost:5000/restaurants for querying restaurants by category
@app.route('/restaurants', methods=['GET'])
def get_restaurants():
    # Get category name from the GET request
    category = request.args.get('category')

    # Check if the category value is empty
    if not category:
        return "Please give a category name - http://localhost:5000/restaurants?category=my_category", 400

    logging.info(f'Listing restaurants for category: {category}')

    # Connect to the database and get restaurants by the given category
    connection, cursor = connect_mysql()
    query = f"SELECT business_id, name, rating, reason FROM restaurants WHERE FIND_IN_SET('{category}', categories)"
    cursor.execute(query)

    # Create restaurant objects from the query result
    results = cursor.fetchall()
    response = {'restaurants': []}
    for result in results:
        restaurant = {'business_id': result[0],
                      'name': result[1],
                      'rating': result[2],
                      'reason': result[3].split(',')}
        response['restaurants'].append(restaurant)

    logging.info(f'Listed {cursor.rowcount} restaurants.')

    # Close the DB connection
    close_mysql_connection(connection, cursor)

    return response


# Assign URL http://localhost:5000/reset_db for resetting the DB - reloads the initial data
@app.route('/reset_db', methods=['GET'])
def reset_db():
    load_data()

    return 'Database reset.'


# Assign URL http://localhost:5000/flush_db for flushing the DB - removes the existing db
@app.route('/flush_db', methods=['GET'])
def flush_db():
    flush()

    return 'Database flushed.'


# Run the API on localhost:5000
if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
