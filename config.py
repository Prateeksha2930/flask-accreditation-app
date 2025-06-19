import os

DB_CONFIG = {
    'host': os.getenv('MYSQL_ADDON_HOST'),
    'user': os.getenv('MYSQL_ADDON_USER'),
    'password': os.getenv('MYSQL_ADDON_PASSWORD'),
    'database': os.getenv('MYSQL_ADDON_DB'),
    'port': int(os.getenv('MYSQL_ADDON_PORT'))  # default to 3306 if not set
}
