import os

DB_CONFIG = {
    "host": os.environ.get("MYSQL_ADDON_HOST"),
    "user": os.environ.get("MYSQL_ADDON_USER"),
    "password": os.environ.get("MYSQL_ADDON_PASSWORD"),
    "port" : int(os.environ.get("MYSQL_ADDON_PORT",3306)),
    "database": os.environ.get("MYSQL_ADDON_DB")
}
