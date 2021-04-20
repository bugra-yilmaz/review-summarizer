# Created by bugra-yilmaz on 08.02.2021.
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


def connect_mysql():
    """
    Connects to the MySQL server with the given configuration.

    Returns:
    MySQLConnection: Connection object to commit changes to the database.
    CMySQLCursor: Cursor object to execute queries on the database.

    """
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
    """
    Closes the connection to the MySQL server after committing any residual changes.

    Parameters:
    connection (MySQLConnection): Connection object to commit changes to the database.
    cursor (CMySQLCursor): Cursor object to execute queries on the database.

    """
    connection.commit()
    connection.close()
    cursor.close()
