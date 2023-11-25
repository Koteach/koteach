import mysql.connector
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

MYSQL_HOST = "koteach.czb1pu0jfm82.eu-west-2.rds.amazonaws.com"
MYSQL_PORT = "3306"
MYSQL_USER = "root"
MYSQL_PASSWORD = os.getenv("KOTEACH_MYSQL_PASSWORD")
MYSQL_DB = "koteach"

# Connect to MySQL
def connect():
    return mysql.connector.connect(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DB
    )