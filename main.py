from fastapi import FastAPI
import database

app = FastAPI()



@app.get("/")
def home():
    return {"message": "Дневник-бухгалтер работает!"}


@app.get("/categories")
def read_categories():
    categories = database.get_categories()


    result = []
    for category in categories:
        result.append({
            "id": category[0],
            "name": category[1],
            "type": category[2],
            "description": category[3]
        })
    return result