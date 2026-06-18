import database

database.create_tables()

if len(database.get_categories()) == 0:
    database.add_category("Доход", "доход", "Поступления")
    database.add_category("Расход", "расход", "траты")
    print("Категории добавлены!")
else:
    print("Категории уже есть, повторно не добавляю.")