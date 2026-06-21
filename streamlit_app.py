import streamlit as st
import requests
import pandas as pd

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Дневник-бухгалтер", layout="wide")
st.title("Аналитика")

# кнопка обновления данных (сбрасывает кэш)
if st.button("Обновить данные"):
    st.cache_data.clear()
    st.rerun()


@st.cache_data(ttl=15)
def load_transactions():
    r = requests.get(API_URL + "/transactions", timeout=30)
    return r.json()


try:
    raw = load_transactions()
except Exception:
    st.error("Не могу получить данные с сервера. Сервер запущен?")
    st.stop()

if not raw:
    st.info("Пока нет ни одной операции. Запиши что-нибудь через бота.")
    st.stop()

df = pd.DataFrame(raw)
df["created_at"] = pd.to_datetime(df["created_at"])
df["date"] = df["created_at"].dt.date
df["object"] = df["object"].fillna("Без объекта")
df["subcategory"] = df["subcategory"].fillna("—")

# =================== ФИЛЬТРЫ ===================
st.sidebar.header("Фильтры")
type_choice = st.sidebar.radio("Тип", ["Всё", "расход", "доход"])

all_objects = sorted(df["object"].unique())
chosen_objects = st.sidebar.multiselect("Объекты", all_objects, default=all_objects)

all_categories = sorted(df["category"].unique())
chosen_categories = st.sidebar.multiselect("Категории", all_categories, default=all_categories)

min_date = df["date"].min()
max_date = df["date"].max()
date_range = st.sidebar.date_input("Период", (min_date, max_date))

# применяем фильтры
filtered = df.copy()
if type_choice != "Всё":
    filtered = filtered[filtered["type"] == type_choice]
filtered = filtered[filtered["object"].isin(chosen_objects)]
filtered = filtered[filtered["category"].isin(chosen_categories)]
if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
    start, end = date_range
    filtered = filtered[(filtered["date"] >= start) & (filtered["date"] <= end)]

if filtered.empty:
    st.warning("Под выбранные фильтры ничего не попало.")
    st.stop()

# =================== ИТОГИ ===================
income = filtered[filtered["type"] == "доход"]["amount"].sum()
expense = filtered[filtered["type"] == "расход"]["amount"].sum()
col1, col2, col3 = st.columns(3)
col1.metric("Доходы", f"{income:,.0f} ₽".replace(",", " "))
col2.metric("Расходы", f"{expense:,.0f} ₽".replace(",", " "))
col3.metric("Баланс", f"{income - expense:,.0f} ₽".replace(",", " "))

# для разрезов берём доходы или расходы в зависимости от фильтра типа
if type_choice == "доход":
    group_df = filtered[filtered["type"] == "доход"]
    word = "Доходы"
else:
    group_df = filtered[filtered["type"] == "расход"]
    word = "Расходы"

# =================== ПО ОБЪЕКТАМ ===================
st.header(f"{word} по объектам")
if not group_df.empty:
    by_object = group_df.groupby("object")["amount"].sum().sort_values(ascending=False)
    st.bar_chart(by_object)
else:
    st.write("Нет данных под фильтры.")

# =================== ПО КАТЕГОРИЯМ ===================
st.header(f"{word} по категориям")
if not group_df.empty:
    by_category = group_df.groupby("category")["amount"].sum().sort_values(ascending=False)
    st.bar_chart(by_category)

# =================== ОБЪЕКТ x КАТЕГОРИЯ ===================
st.header(f"{word}: объект × категория")
if not group_df.empty:
    pivot = pd.pivot_table(group_df, index="object", columns="category",
                           values="amount", aggfunc="sum", fill_value=0)
    st.dataframe(pivot, use_container_width=True)

# =================== ПО ПОДКАТЕГОРИЯМ ===================
st.header("По подкатегориям")
if not group_df.empty:
    by_sub = group_df.groupby(["category", "subcategory"])["amount"].sum().reset_index()
    by_sub = by_sub.sort_values("amount", ascending=False)
    by_sub = by_sub.rename(columns={"category": "Категория", "subcategory": "Подкатегория", "amount": "Сумма"})
    st.dataframe(by_sub, use_container_width=True)

# =================== ОБЪЁМЫ ===================
st.header("Объёмы (где указано количество)")
with_qty = filtered[filtered["quantity"].notna()]
if not with_qty.empty:
    by_qty = with_qty.groupby(["subcategory", "unit"])["quantity"].sum().reset_index()
    by_qty = by_qty.sort_values("quantity", ascending=False)
    by_qty = by_qty.rename(columns={"subcategory": "Что", "unit": "Единица", "quantity": "Всего"})
    st.dataframe(by_qty, use_container_width=True)
else:
    st.write("Пока нет операций с количеством.")

# =================== СПИСОК ОПЕРАЦИЙ ===================
st.header("Операции")
show = filtered.sort_values("created_at", ascending=False)[
    ["date", "type", "object", "category", "subcategory", "amount", "quantity", "unit", "comment"]
]
show = show.rename(columns={
    "date": "Дата", "type": "Тип", "object": "Объект", "category": "Категория",
    "subcategory": "Подкатегория", "amount": "Сумма", "quantity": "Кол-во",
    "unit": "Ед.", "comment": "Комментарий"
})
st.dataframe(show, use_container_width=True)