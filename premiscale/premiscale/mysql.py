"""
Methods for interacting with the MySQL database.
"""

from sqlalchemy.dialects.mysql import (
    insert,
)


url = 'mysql+mysqldb://<user>:<password>@<host>[:<port>]/<dbname>'