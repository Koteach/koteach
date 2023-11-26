from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from datetime import datetime
from database import connect
from pydantic import BaseModel
import numpy as np
from ast import literal_eval
from openai import OpenAI
import os
import pandas as pd

app = FastAPI()


db_connection = connect()
db = db_connection.cursor()


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

@app.get("/")
def docs():
    return RedirectResponse(url='/docs')


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
    average_rating: float | None
    created_at: datetime
    modified_at: datetime


@app.get("/hagwon", response_model=GetHagwonResponse)
def get_hagwon(id: int):
    if not id:
         raise HTTPException(status_code=400, detail="ID required")

    get_hagwon_query = "SELECT id, name, description, location, created_at, modified_at FROM hagwon WHERE id = %s"
    values = (id, )
    db.execute(get_hagwon_query, values)

    result = db.fetchall()
    db_connection.commit()

    if db.rowcount == 0:
        raise HTTPException(status_code=404, detail="Hagwon not found")

    hagwon = database_hagwon_to_get_hagwon_response(result)[0]

    hagwon["average_rating"] = get_hagwon_rating(id)

    return hagwon

def database_hagwon_to_get_hagwon_response(rows):
    response = []
    for row in rows:
        response.append({
            "id": row[0],
            "name": row[1],
            "description": row[2],
            "location": row[3],
            "average_rating": None,
            "created_at": row[4],
            "modified_at": row[5]
        })
    return response


def get_hagwon_rating(id: int):

    get_hagwon_average_rating_query = "SELECT AVG (rating) FROM hagwon_review WHERE hagwon_id = %s"
    values = (id, )
    db.execute(get_hagwon_average_rating_query, values)

    result = db.fetchone()
    db_connection.commit()

    if db.rowcount == 0:
        return None

    return result[0]



class DeleteHagwonResponse(BaseModel):
    message: str



@app.delete("/hagwon", response_model=DeleteHagwonResponse)
def delete_hagwon(id: int):
    if not id:
         raise HTTPException(status_code=400, detail="ID required")

    delete_hagwon_query = "DELETE FROM hagwon WHERE id = %s"
    values = (id, )
    db.execute(delete_hagwon_query, values)

    db_connection.commit()

    return {"message": "Successfully deleted hagwon"}



@app.get("/hagwons", response_model=list[GetHagwonResponse])
def get_hagwons(limit: int, page: int, name: str | None = None, location: str | None = None):
    if page < 1:
        page = 1
    offset = limit * (page -1)
    get_hagwons_query = "SELECT * FROM hagwon"
    if name:
        get_hagwons_query += " WHERE lower(name) LIKE CONCAT(\"%\", %s, \"%\")"
    if location:
        if name:
            get_hagwons_query += " AND"
        else:
            get_hagwons_query += " WHERE"
        get_hagwons_query += " lower(location) LIKE CONCAT(\"%\", %s, \"%\")"

    get_hagwons_query += " LIMIT %s OFFSET %s"


    values = (limit, offset)

    if location:
        values = list(values)
        values.insert(0, location.lower())
        values = tuple(values)

    if name:
        values = list(values)
        values.insert(0, name.lower())
        values = tuple(values)
        
    db.execute(get_hagwons_query, values)

    hagwons = database_hagwon_to_get_hagwon_response(db.fetchall())
    db_connection.commit()

    return hagwons



class CreateReviewRequest(BaseModel):
    hagwon_id: int
    title: str
    content: str
    rating: int


class CreateReviewResponse(BaseModel):
    review_id: int
    message: str


@app.post("/review", response_model=CreateReviewResponse)
def create_review(review: CreateReviewRequest):
    now = datetime.now()

    create_review_query = "INSERT INTO hagwon_review (hagwon_id, title, content, rating, created_at, modified_at) VALUES (%s, %s, %s, %s, %s, %s)"
    values = (review.hagwon_id, review.title, review.content, review.rating, now, now)
    db.execute(create_review_query, values)

    db_connection.commit()

    return {"review_id": db.lastrowid, "message": "Review successfully created"}



class GetReviewResponse(BaseModel):
    id: int
    hagwon_id: int
    title: str
    content: str
    rating: int
    created_at: datetime
    modified_at: datetime


@app.get("/review", response_model=GetReviewResponse)
def get_review(id: int):
    if not id:
         raise HTTPException(status_code=400, detail="ID required")

    get_review_query = "SELECT * FROM hagwon_review WHERE id = %s"
    values = (id, )
    db.execute(get_review_query, values)

    result = db.fetchall()
    db_connection.commit()

    if db.rowcount == 0:
        raise HTTPException(status_code=404, detail="Hagwon not found")

    hagwon = database_review_to_get_review_response(result)[0]

    return hagwon

def database_review_to_get_review_response(rows):
    response = []
    for row in rows:
        response.append({
            "id": row[0],
            "hagwon_id": row[1],
            "title": row[2],
            "content": row[3],
            "rating": row[4],
            "created_at": row[5],
            "modified_at": row[6]
        })
    return response



class DeleteReviewResponse(BaseModel):
    message: str



@app.delete("/review", response_model=DeleteReviewResponse)
def delete_review(id: int):
    if not id:
         raise HTTPException(status_code=400, detail="ID required")

    delete_review_query = "DELETE FROM hagwon_review WHERE id = %s"
    values = (id, )
    db.execute(delete_review_query, values)

    db_connection.commit()

    return {"message": "Successfully deleted review"}



@app.get("/reviews", response_model=list[GetReviewResponse])
def get_reviews(hagwon_id: int, limit: int, page: int, content: str | None = None):
    if page < 1:
        page = 1
    offset = limit * (page -1)


    get_reviews_query = "SELECT * FROM hagwon_review WHERE hagwon_id = %s"
    if content:
        get_reviews_query += " AND lower(title) LIKE CONCAT(\"%\", %s, \"%\") OR lower(content) LIKE CONCAT(\"%\", %s, \"%\")"

    get_reviews_query += " LIMIT %s OFFSET %s"


    values = (hagwon_id, limit, offset)

    if content:
        values = list(values)
        values.insert(1, content.lower())
        values.insert(1, content.lower())
        values = tuple(values)
        
    db.execute(get_reviews_query, values)

    reviews = database_review_to_get_review_response(db.fetchall())
    db_connection.commit()

    return reviews


class QuestionResponse(BaseModel):
    answer: str
    time: datetime

@app.get("/answer", response_model=QuestionResponse)
def get_answer(question: str):
    relevant_chunks = search_legal(question, pprint=False)
    answer = ask_question(question, relevant_chunks)
    return {"answer": answer.content, "time": datetime.now()}


# See https://cookbook.openai.com/examples/semantic_text_search_using_embeddings
def search_legal(question, n=15, pprint=True):
    embeddings_path = "documents/combined_with_embeddings.csv"
    df = pd.read_csv(embeddings_path)
    df["embedding"] = df.embedding.apply(literal_eval).apply(np.array)
    product_embedding = get_embedding(
        question,
        model="text-embedding-ada-002"
    )
    df["similarity"] = df.embedding.apply(lambda x: cosine_similarity(x, product_embedding))

    results = (
        df.sort_values("similarity", ascending=False)
        .head(n)
        .text
    )

    relevant_chunks = []
    for r in results:
        relevant_chunks.append(r)
    
    if pprint:
        for r in results:
            print(r[:200])
            print()

    return relevant_chunks

   
def get_embedding(text, model="text-embedding-ada-002"):
    text = text.replace("\n", " ")
    return client.embeddings.create(input = [text], model=model).data[0].embedding 
    

# https://github.com/openai/openai-cookbook/blob/main/examples/utils/embeddings_utils.py
def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
    
    
def ask_question(question, relevant_chunks):
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a legal assistant, skilled in explaining complex legal issues regarding employment and immigration in South Korea in a simple and understandable way. Do not mention that context was given."},
                {"role": "user", "content": "Using the context given below, answer this question: " + question + "\n" + "\n".join(relevant_chunks)}
            ]
        )      

    return completion.choices[0].message