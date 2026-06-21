import streamlit as st
import requests
import pandas as pd

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Дневник-бухгалтер", layout="wide")
st.title("Аналитика")

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

st.sidebar.header("Фильтры")
type_choice = st.sidebar.radio("Тип", ["Всё", "расход", "доход"])

all_objects = sorted(df["object"].unique())
chosen_objects = st.sidebar.multiselect("Объекты", all_objects, default=all_objects)

all_categories = sorted(df["category"].unique())
chosen_categories = st.sidebar.multiselect("Категории", all_categories, default=all_categories)

min_date = df["date"].min()
max_date = df["date"].max()
date_range = st.sidebar.date_input("Период", (min_date, max_date))

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

income = filtered[filtered["type"] == "доход"]["amount"].sum()
expense = filtered[filtered["type"] == "расход"]["amount"].sum()
col1, col2, col3 = st.columns(3)
col1.metric("Доходы", f"{income:,.0f} ₽".replace(",", " "))
col2.metric("Расходы", f"{expense:,.0f} ₽".replace(",", " "))
col3.metric("Баланс", f"{income - expense:,.0f} ₽".replace(",", " "))

if type_choice == "доход":
    group_df = filtered[filtered["type"] == "доход"]
    word = "Доходы"
else:
    group_df = filtered[filtered["type"] == "расход"]
    word = "Расходы"

st.header("Сводная таблица")
st.caption("Выбери, что в строках и столбцах — таблица перестроится. В углу — Итого.")

dim_options = {"Объект": "object", "Категория": "category", "Подкатегория": "subcategory", "Тип": "type"}
c1, c2, c3 = st.columns(3)
row_dim = c1.selectbox("Строки", list(dim_options.keys()), index=0)
col_dim = c2.selectbox("Столбцы", ["(нет)"] + list(dim_options.keys()), index=2)
value_choice = c3.selectbox("Значение", ["Сумма ₽", "Кол-во операций"])

aggfunc = "sum" if value_choice == "Сумма ₽" else "count"
rows_col = dim_options[row_dim]

if col_dim != "(нет)" and dim_options[col_dim] != rows_col:
    cols_col = dim_options[col_dim]
    pivot = filtered.pivot_table(index=rows_col, columns=cols_col, values="amount",
                                 aggfunc=aggfunc, fill_value=0, margins=True, margins_name="Итого")
else:
    pivot = filtered.pivot_table(index=rows_col, values="amount",
                                 aggfunc=aggfunc, margins=True, margins_name="Итого")
st.dataframe(pivot, use_container_width=True)


def breakdown_table(data, column, label):
    t = data.groupby(column)["amount"].agg(["sum", "count"]).reset_index()
    t.columns = [label, "Сумма", "Операций"]
    total = t["Сумма"].sum()
    t["Доля %"] = (t["Сумма"] / total * 100).round(1) if total else 0
    return t.sort_values("Сумма", ascending=False)


st.header(f"{word} по группам")

st.subheader("По объектам")
st.dataframe(breakdown_table(group_df, "object", "Объект"), use_container_width=True)

st.subheader("По категориям")
st.dataframe(breakdown_table(group_df, "category", "Категория"), use_container_width=True)

st.subheader("По подкатегориям")
sub_table = group_df.groupby(["category", "subcategory"])["amount"].agg(["sum", "count"]).reset_index()
sub_table.columns = ["Категория", "Подкатегория", "Сумма", "Операций"]
sub_table = sub_table.sort_values("Сумма", ascending=False)
st.dataframe(sub_table, use_container_width=True)

st.header("Объёмы (где указано количество)")
with_qty = filtered[filtered["quantity"].notna()]
if not with_qty.empty:
    by_qty = with_qty.groupby(["subcategory", "unit"])["quantity"].sum().reset_index()
    by_qty = by_qty.sort_values("quantity", ascending=False)
    by_qty = by_qty.rename(columns={"subcategory": "Что", "unit": "Единица", "quantity": "Всего"})
    st.dataframe(by_qty, use_container_width=True)
else:
    st.write("Пока нет операций с количеством.")

st.header("Графики")
if not group_df.empty:
    st.subheader(f"{word} по объектам")
    st.bar_chart(group_df.groupby("object")["amount"].sum().sort_values(ascending=False))
    st.subheader(f"{word} по категориям")
    st.bar_chart(group_df.groupby("category")["amount"].sum().sort_values(ascending=False))

st.header("Все операции")
show = filtered.sort_values("created_at", ascending=False)[
    ["date", "type", "object", "category", "subcategory", "amount", "quantity", "unit", "comment"]
]
show = show.rename(columns={
    "date": "Дата", "type": "Тип", "object": "Объект", "category": "Категория",
    "subcategory": "Подкатегория", "amount": "Сумма", "quantity": "Кол-во",
    "unit": "Ед.", "comment": "Комментарий"
})
st.dataframe(show, use_container_width=True)
