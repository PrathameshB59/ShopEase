# Settings package - default to base settings
from .base import *
# from .db_connection import *

import pymysql
pymysql.install_as_MySQLdb()
