# Tell Django to use PyMySQL as MySQL adapter
# This makes PyMySQL act like mysqlclient
import pymysql
pymysql.install_as_MySQLdb()