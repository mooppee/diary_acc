import database

# на всякий случай создаём таблицы (если их ещё нет)
database.create_tables()

# категории по умолчанию.
# "Прочий доход" и "Прочий расход" - это запасные категории:
# в них попадают операции, для которых Claude не нашёл точную категорию.
default_categories = [
    ("Прочий доход", "доход", "Доходы, для которых пока нет отдельной категории"),
    ("Прочий расход", "расход", "Расходы, для которых пока нет отдельной категории"),
]

# добавляем каждую категорию, только если её ещё нет (проверяем по названию)
for name, category_type, description in default_categories:
    if database.get_category_by_name(name) is None:
        database.add_category(name, category_type, description)
        print(f"Добавлена категория: {name}")
    else:
        print(f"Категория уже есть: {name}")

# показываем, что в базе
print("\nКатегории в базе:")
for category in database.get_categories():
    print(category)