# Created by bugra-yilmaz on 11.08.2020.
#
# Python module holding a set of commonly used functions

# Imports
import logging
import mysql.connector
from mysql.connector import errorcode

# Format the logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)7s: %(message)s',
                    datefmt='%d-%m-%Y %H:%M:%S')

# MySQL configuration parameters
mysql_config = dict(host='mysql_server', user='root', password='rootpw', database='db')


# Connect to the MySQL DB
def connect_mysql():
    try:
        connection = mysql.connector.connect(**mysql_config)
        cursor = connection.cursor()

    except mysql.connector.Error as error:
        if error.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            logging.error(f'Access denied. '
                          f'Check your username: {mysql_config["user"]} and password: {mysql_config["password"]}')
        elif error.errno == errorcode.ER_BAD_DB_ERROR:
            logging.error(f'Cannot found database: {mysql_config["database"]}')
        else:
            logging.error(error)

    else:
        return connection, cursor


# Commit transactions and close the DB connection
def close_mysql_connection(connection, cursor):
    connection.commit()
    connection.close()
    cursor.close()
