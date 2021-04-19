# Created by bugra-yilmaz on 08.02.2021.
#
# Data loader module holding the necessary functions to load the initial data to the database

# Imports
import json

from common import *


# Push the initial data into the database
def load_data():
    logging.info('Loading restaurants data to the database...')

    flush()
    connection, cursor = connect_mysql()

    query = 'CREATE TABLE restaurants (business_id VARCHAR(30), name VARCHAR(255), ' \
            'rating FLOAT, reason VARCHAR(255), categories VARCHAR(255), INDEX (categories))'
    cursor.execute(query)

    restaurants_to_load = list()
    with open('data/restaurants.json', 'r') as f:
        for line in f:
            restaurant = json.loads(line)
            restaurants_to_load.append(restaurant.values())

    query = "INSERT INTO restaurants (business_id, name, rating, reason, categories) " \
            "VALUES (%s, %s, %s, %s, %s)"
    cursor.executemany(query, restaurants_to_load)
    logging.info(f'{cursor.rowcount} restaurants loaded to the database.')

    close_mysql_connection(connection, cursor)


# Flush the database
def flush():
    connection, cursor = connect_mysql()

    logging.info('Flushing the database...')

    # Remove all tables from the database
    query = 'DROP TABLE IF EXISTS restaurants'
    cursor.execute(query)

    logging.info('Database flushed.')

    # Close the DB connection
    close_mysql_connection(connection, cursor)
