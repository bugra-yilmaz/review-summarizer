# Created by bugra-yilmaz on 08.02.2021.
#
# Data loader module holding the necessary functions to load the initial data to the database

# Imports
import json

from common import *


def load_data():
    """
    Loads the restaurant data into the MySQL db.

    """
    logging.info('Loading restaurants data to the database...')

    # Flush the db and connect to it
    flush()
    connection, cursor = connect_mysql()

    # Create the "restaurants" table
    query = 'CREATE TABLE restaurants (business_id VARCHAR(30), name VARCHAR(255), ' \
            'rating FLOAT, reason VARCHAR(255), categories VARCHAR(255), INDEX (categories))'
    cursor.execute(query)

    # Accumulate restaurants information for pushing to db
    restaurants_to_load = list()
    with open('data/restaurants.json', 'r') as f:
        for line in f:
            restaurant = json.loads(line)
            restaurants_to_load.append(restaurant.values())

    # Insert restaurant data into "restaurants" table
    query = "INSERT INTO restaurants (business_id, name, rating, reason, categories) " \
            "VALUES (%s, %s, %s, %s, %s)"
    cursor.executemany(query, restaurants_to_load)
    logging.info(f'{cursor.rowcount} restaurants loaded to the database.')

    # Close the db connection
    close_mysql_connection(connection, cursor)


# Flush the database
def flush():
    """
    Flushes the db. Removes the restaurants table if it exists.

    """
    # Connect to db
    connection, cursor = connect_mysql()

    logging.info('Flushing the database...')

    # Remove all tables from the database
    query = 'DROP TABLE IF EXISTS restaurants'
    cursor.execute(query)

    logging.info('Database flushed.')

    # Close the db connection
    close_mysql_connection(connection, cursor)
