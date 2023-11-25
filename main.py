from fastapi import FastAPI
from database import connect

app = FastAPI()

@app.get("/")
def root():
    db_connection = connect()
    db = db_connection.cursor()
    db.execute("SHOW TABLES")
    print(db.fetchall())
    return {"message": "Hello World Changed"}