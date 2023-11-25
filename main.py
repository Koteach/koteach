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


class CreateHagwonRequest(BaseModel):
    name: str
    description: str
    location: str


class CreateHagwonResponse(BaseModel):
    hagwon_id: int
    message: str



@app.post("/hagwon", response_model=CreateHagwonResponse)
def create_hagwon(hagwon: CreateHagwonRequest):
    now = datetime.now()

    create_hagwon_query = "INSERT INTO hagwon (name, description, location, created_at, modified_at) VALUES (%s, %s, %s, %s, %s)"
    values = (hagwon.name, hagwon.description, hagwon.location, now, now)
    db.execute(create_hagwon_query, values)

    db_connection.commit()



    return {"hagwon_id": db.lastrowid, "message": "Hagwon successfully created"}



class GetHagwonResponse(BaseModel):
    id: int
    name: str
    description: str
    location: str
    created_at: datetime
    modified_at: datetime


@app.get("/hagwon", response_model=GetHagwonResponse)
def get_hagwon(id: int):
    if not id:
         raise HTTPException(status_code=400, detail="ID required")

    get_hagwon_query = "SELECT id, name, description, location, created_at, modified_at FROM hagwon WHERE id = %s"
    values = (id, )
    db.execute(get_hagwon_query, values)

    hagwon = database_hagwon_to_get_hagwon_response(db.fetchall())[0]

    return hagwon

def database_hagwon_to_get_hagwon_response(rows):
    response = []
    for row in rows:
        response.append({
            "id": row[0],
            "name": row[1],
            "description": row[2],
            "location": row[3],
            "created_at": row[4],
            "modified_at": row[5]
        })
    return response



class DeleteHagwonResponse(BaseModel):
    message: str



@app.delete("/hagwon", response_model=DeleteHagwonResponse)
def delete_hagwon(id: int):
    if not id:
         raise HTTPException(status_code=400, detail="ID required")

    get_hagwon_query = "DELETE FROM hagwon WHERE id = %s"
    values = (id, )
    db.execute(get_hagwon_query, values)

    db_connection.commit()

    return {"message": "Successfully deleted hagwon"}



@app.get("/hagwons", response_model=list[GetHagwonResponse])
def get_hagwons(limit: int):
    get_hagwons_query = "SELECT id, name, description, location, created_at, modified_at FROM hagwon LIMIT %s"
    values = (limit, )
    db.execute(get_hagwons_query, values)

    hagwons = database_hagwon_to_get_hagwon_response(db.fetchall())

    return hagwons
