from fastapi import FastAPI
from pydantic import BaseModel
import database
import ai

# создаём наше веб-приложение
app = FastAPI()


# данные для добавления операции вручную
class TransactionInput(BaseModel):
    amount: float
    description: str
    type: str
    category_id: int


# данные для операции из текста (бот пришлёт сюда просто строку)
class TextInput(BaseModel):
    text: str


# данные для создания новой категории (из Streamlit)
class CategoryInput(BaseModel):
    name: str
    type: str
    description: str = ""


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


@app.post("/categories")
def create_category(category: CategoryInput):
    # проверим, что категории с таким именем ещё нет
    existing = database.get_category_by_name(category.name)
    if existing is not None:
        return {"error": "Категория с таким названием уже есть"}
    database.add_category(category.name, category.type, category.description)
    return {"message": "Категория добавлена!"}


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


# главная новинка: операция из обычного текста через Claude
@app.post("/transactions/from-text")
def create_from_text(data: TextInput):
    # 1. отправляем текст Claude, он возвращает сумму, тип и категорию
    result = ai.analyze_text(data.text)

    # 2. сначала пробуем найти категорию по точному названию
    category = database.get_category_by_name(result["category"])

    # 3. если такой категории нет (Claude назвал её по-своему) -
    #    кладём операцию в запасную категорию "Прочий доход/расход"
    if category is None:
        category = database.get_fallback_category(result["type"])

    # 4. если и запасной категории нет - честно сообщаем об ошибке
    if category is None:
        return {"error": "Не нашёл подходящую категорию для типа: " + result["type"]}

    category_id = category[0]

    # 5. сохраняем операцию (в описание кладём исходный текст пользователя)
    database.add_transaction(result["amount"], data.text, result["type"], category_id)

    # 6. сообщаем, что записали (категорию берём ту, что реально из базы)
    return {
        "message": "Операция сохранена через Claude!",
        "amount": result["amount"],
        "type": result["type"],
        "category": category[1]
    }