import streamlit as st
import requests

# адрес нашего сервера FastAPI (должен быть запущен)
API_URL = "http://127.0.0.1:8000"

st.title("Дневник-бухгалтер")

# =========================================================
# РАЗДЕЛ 1: КАТЕГОРИИ
# =========================================================
st.header("Категории")

st.subheader("Добавить категорию")
name = st.text_input("Название категории")
type_choice = st.selectbox("Тип", ["расход", "доход"])
description = st.text_input("Описание (для чего эта категория)")

if st.button("Добавить"):
    if name.strip() == "":
        st.warning("Введите название категории")
    else:
        response = requests.post(API_URL + "/categories", json={
            "name": name,
            "type": type_choice,
            "description": description
        })
        data = response.json()
        if "message" in data:
            st.success(data["message"])
        else:
            st.error(data.get("error", "Не удалось добавить"))

st.subheader("Все категории")
categories = requests.get(API_URL + "/categories").json()
for category in categories:
    st.write(f"**{category['name']}** — {category['type']} — {category['description']}")

# =========================================================
# РАЗДЕЛ 2: АНАЛИТИКА
# =========================================================
st.header("Аналитика")

# забираем все операции с сервера
transactions = requests.get(API_URL + "/transactions").json()

# считаем суммы доходов и расходов
total_income = 0
total_expense = 0
for t in transactions:
    if t["type"] == "доход":
        total_income += t["amount"]
    else:
        total_expense += t["amount"]

# показываем три числа в ряд
col1, col2, col3 = st.columns(3)
col1.metric("Доходы", f"{total_income:.0f} руб.")
col2.metric("Расходы", f"{total_expense:.0f} руб.")
col3.metric("Баланс", f"{total_income - total_expense:.0f} руб.")

# --- расходы по категориям ---
st.subheader("Расходы по категориям")
expense_by_category = {}
for t in transactions:
    if t["type"] == "расход":
        category_name = t["category"]
        # прибавляем сумму к нужной категории
        if category_name in expense_by_category:
            expense_by_category[category_name] += t["amount"]
        else:
            expense_by_category[category_name] = t["amount"]

if expense_by_category:
    st.bar_chart(expense_by_category)
else:
    st.write("Расходов пока нет")

# =========================================================
# РАЗДЕЛ 3: СПИСОК ОПЕРАЦИЙ
# =========================================================
st.header("Последние операции")

if transactions:
    for t in transactions:
        st.write(f"{t['created_at']} — {t['amount']:.0f} руб. — {t['type']} — {t['category']} — {t['description']}")
else:
    st.write("Операций пока нет")