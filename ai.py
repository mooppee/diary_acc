import json
from anthropic import Anthropic
import config
import database


def analyze_text(text):
    objects = database.get_objects()
    categories = database.get_categories()

    # список объектов — Claude выбирает строго из них
    object_names = [o[1] for o in objects]
    objects_line = ", ".join(object_names)

    # категории с типом, описанием и их подкатегориями
    categories_text = ""
    for category in categories:
        cat_id, cat_name, cat_type, cat_desc = category
        subs = database.get_subcategories(cat_id)
        sub_names = [s[1] for s in subs]
        subs_str = ", ".join(sub_names) if sub_names else "нет"
        categories_text += f'- "{cat_name}" ({cat_type}): {cat_desc}\n      подкатегории: {subs_str}\n'

    prompt = f"""Ты помощник-бухгалтер строительного бизнеса. Разбери сообщение об операции и верни JSON.

Определи:
1. amount — сумму (число)
2. type — "доход" или "расход"
3. object — объект (направление) СТРОГО из списка: {objects_line}.
   Если объект в сообщении не упомянут — верни "Без объекта". Свои объекты НЕ придумывай.
4. category — категорию. Сначала ищи подходящую среди существующих (список ниже). Только если ничего не подходит — придумай НОВУЮ короткую категорию.
5. subcategory — уточнение внутри категории (материал, рабочий, машина и т.п.). Бери из подкатегорий, можешь предложить новую, либо верни "" если уточнения нет.
6. quantity — количество, если упомянуто (число), иначе null. Например "25 кубов" -> 25.
7. unit — единица измерения количества: кубы, тонны, литры, штуки, мешки и т.п. Если количества нет — "".
8. comment — короткое понятное описание операции.

Существующие категории и подкатегории:
{categories_text}
Правило: СТАРАЙСЯ использовать существующие категории и подкатегории. Создавай новое только если реально ничего не подходит.

Сообщение: "{text}"

Ответь ТОЛЬКО в формате JSON, без пояснений. Пример:
{{"amount": 30000, "type": "расход", "object": "ДС13", "category": "Материалы", "subcategory": "Щебень", "quantity": 25, "unit": "кубы", "comment": "щебень 25 кубов"}}"""

    client = Anthropic(api_key=config.ANTHROPIC_API_KEY)
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=400,
        messages=[{"role": "user", "content": prompt}]
    )
    answer = response.content[0].text
    answer = answer.replace("```json", "").replace("```", "").strip()
    return json.loads(answer)


if __name__ == "__main__":
    print(analyze_text("щебень на дс13 127600"))