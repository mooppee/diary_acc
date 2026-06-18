import json
from anthropic import Anthropic
import config
import database


def analyze_text(text):
    categories = database.get_categories()
    categories_text = ""
    for category in categories:
        categories_text += f"- {category[1]} (тип: {category[2]}): {category[3]}\n"


    prompt = f"""Ты помощник для учёта личных финансов.
Пользователь прислал сообщение об операции. Определи три вещи:
1. amount - сумму (число)
2. type - тип, строго одно из двух: "доход" или "расход"
3. category - название категории СТРОГО из списка ниже

Категории:
{categories_text}
Сообщение пользователя: "{text}"

Ответь ТОЛЬКО в формате JSON, без пояснений. Пример ответа:
{{"amount": 200, "type": "расход", "category": "Расход"}}"""


    client = Anthropic(api_key=config.ANTHROPIC_API_KEY)
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=200,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    answer = response.content[0].text

    answer = answer.replace("```json", "").replace("```", "").strip()

  
    result = json.loads(answer)
    return result


# тестим
if __name__ == "__main__":
    test = analyze_text("потратил 200 на кофе")
    print("Claude вернул:", test)