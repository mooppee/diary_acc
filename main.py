from fastapi import FastAPI
from pydantic import BaseModel
import database
import ai

app = FastAPI()


# данные для операции из текста (бот пришлёт строку)
class TextInput(BaseModel):
    text: str


@app.get("/")
def home():
    return {"message": "Дневник-бухгалтер работает!"}


@app.get("/objects")
def read_objects():
    objects = database.get_objects()
    return [{"id": o[0], "name": o[1], "description": o[2]} for o in objects]


@app.get("/categories")
def read_categories():
    categories = database.get_categories()
    result = []
    for c in categories:
        subs = database.get_subcategories(c[0])
        result.append({
            "id": c[0], "name": c[1], "type": c[2], "description": c[3],
            "subcategories": [{"id": s[0], "name": s[1]} for s in subs]
        })
    return result


@app.get("/transactions")
def read_transactions():
    transactions = database.get_transactions()
    result = []
    for t in transactions:
        result.append({
            "id": t[0], "amount": t[1], "comment": t[2], "type": t[3],
            "object": t[4], "category": t[5], "subcategory": t[6], "created_at": t[7]
        })
    return result


@app.post("/transactions/from-text")
def create_from_text(data: TextInput):
    # 1. Claude разбирает текст на amount, type, object, category, subcategory, comment
    result = ai.analyze_text(data.text)

    amount = result["amount"]
    transaction_type = result["type"]
    comment = result.get("comment", data.text)

    created = []  # что создали нового — сообщим пользователю

    # 2. ОБЪЕКТ: только из существующих, иначе "Без объекта" (бот объекты не создаёт)
    object_row = database.get_object_by_name(result.get("object", ""))
    if object_row is None:
        object_row = database.get_object_by_name("Без объекта")
    object_id = object_row[0]

    # 3. КАТЕГОРИЯ: ищем по имени, если нет — создаём (авто-создание)
    category_name = (result.get("category") or "").strip()
    if category_name == "":
        category_name = "Прочий доход" if transaction_type == "доход" else "Прочий расход"
    category_row = database.get_category_by_name(category_name)
    if category_row is None:
        database.add_category(category_name, transaction_type, "Создано автоматически")
        category_row = database.get_category_by_name(category_name)
        created.append(f"категория «{category_name}»")
    category_id = category_row[0]

    # 4. ПОДКАТЕГОРИЯ: необязательная; если есть имя — ищем/создаём
    subcategory_id = None
    subcategory_name = (result.get("subcategory") or "").strip()
    if subcategory_name != "":
        sub_row = database.get_subcategory_by_name(subcategory_name, category_id)
        if sub_row is None:
            database.add_subcategory(subcategory_name, category_id, "Создано автоматически")
            sub_row = database.get_subcategory_by_name(subcategory_name, category_id)
            created.append(f"подкатегория «{subcategory_name}»")
        subcategory_id = sub_row[0]

    # 5. сохраняем операцию
    database.add_transaction(amount, comment, transaction_type, object_id, category_id, subcategory_id)

    # 6. ответ
    return {
        "message": "Операция сохранена!",
        "amount": amount,
        "type": transaction_type,
        "object": object_row[1],
        "category": category_row[1],
        "subcategory": subcategory_name if subcategory_name else None,
        "created": created,
    }