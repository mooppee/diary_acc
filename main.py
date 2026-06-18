from fastapi import FastAPI
from pydantic import BaseModel
import database

# создаём наше веб-приложение
app = FastAPI()


# описываем, какие данные ждём при добавлении операции.
# FastAPI сам проверит, что пришли все поля и нужного типа.
class TransactionInput(BaseModel):
    amount: float          # сумма
    description: str       # описание
    type: str              # "доход" или "расход"
    category_id: int       # id категории из таблицы categories


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



@app.post("/transactions")
def create_transaction(transaction: TransactionInput):
    database.add_transaction(
        transaction.amount,
        transaction.description,
        transaction.type,
        transaction.category_id
    )
    return {"message": "Операция сохранена!"}


@app.get("/transactions")
def read_transactions():
    transactions = database.get_transactions()
    result = []
    for t in transactions:
        result.append({
            "id": t[0],
            "amount": t[1],
            "description": t[2],
            "type": t[3],
            "category": t[4],
            "created_at": t[5]
        })
    return result