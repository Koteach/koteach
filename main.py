from fastapi import FastAPI, HTTPException
from datetime import datetime
from database import connect
from pydantic import BaseModel

app = FastAPI()


db_connection = connect()
db = db_connection.cursor()

@app.get("/")
def root():
    return "Welcome to Koteach"


class Hagwon(BaseModel):
    id: int | None = None
    name: str | None
    description: str | None
    location: str | None
    created_at: datetime | None = None
    modified_at: datetime | None = None


@app.post("/hagwon")
def create_hagwon(hagwon: Hagwon):
    try:
        hagwon.created_at
    except NameError:
        hagwon.created_at = datetime.now()

    hagwon.modified_at = datetime.now()

    create_hagwon_query = "INSERT INTO hagwon (name, description, location, created_at, modified_at) VALUES (%s, %s, %s, %s, %s)"
    values = (hagwon.name, hagwon.description, hagwon.location, hagwon.created_at, hagwon.modified_at)
    db.execute(create_hagwon_query, values)

    db_connection.commit()

    return {"hagwon_id": db.lastrowid}


@app.get("/hagwon")
def get_hagwon(id: int | None):
    if not id:
         raise HTTPException(status_code=400, detail="ID required")

    print(id)
    get_hagwon_query = "SELECT * FROM hagwon WHERE id = %s"
    values = (id, )
    db.execute(get_hagwon_query, values)
    print(db.fetchall())

    return ""