#!/usr/bin/env python3
"""
Проверка заказов покупателя в статусе «на разборе возвратов» в МойСклад.

Запуск:
    export MS_TOKEN="ваш_токен"          # токен API МойСклад (Bearer)
    python3 check_returns_status.py

По умолчанию ищет статус с названием «на разборе возвратов» (регистр игнорируется).
Можно задать другое название:
    python3 check_returns_status.py "на разборе возвратов"
"""

import os
import sys
import json
import urllib.request
import urllib.parse
import urllib.error

BASE = "https://api.moysklad.ru/api/remap/1.2"
STATUS_NAME = (sys.argv[1] if len(sys.argv) > 1 else "на разборе возвратов").strip().lower()

def load_token():
    """Токен берём: 1) из переменной MS_TOKEN, 2) из файла ms_token.txt рядом со скриптом."""
    t = os.environ.get("MS_TOKEN", "").strip()
    if t:
        return t
    here = os.path.dirname(os.path.abspath(__file__))
    token_file = os.path.join(here, "ms_token.txt")
    if os.path.exists(token_file):
        with open(token_file, "r", encoding="utf-8") as f:
            return f.read().strip()
    sys.exit(
        "Не найден токен.\n"
        "Вариант А: создайте рядом со скриптом файл ms_token.txt и впишите туда токен.\n"
        "Вариант Б: задайте переменную окружения MS_TOKEN."
    )


TOKEN = load_token()


def api_get(path):
    """GET к API МойСклад с Bearer-авторизацией."""
    url = path if path.startswith("http") else BASE + path
    req = urllib.request.Request(url, headers={
        "Authorization": "Bearer " + TOKEN,
        "Accept": "application/json;charset=utf-8",
        "Content-Type": "application/json",
    })
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")
        sys.exit(f"Ошибка API {e.code} при {url}\n{body}")
    except urllib.error.URLError as e:
        sys.exit(f"Сеть недоступна: {e}")


def find_state_href():
    """Находит meta.href нужного статуса в метаданных заказа покупателя."""
    meta = api_get("/entity/customerorder/metadata")
    states = meta.get("states", [])
    for st in states:
        if st.get("name", "").strip().lower() == STATUS_NAME:
            return st["meta"]["href"], st["name"]
    available = ", ".join(repr(s.get("name")) for s in states)
    sys.exit(f"Статус «{STATUS_NAME}» не найден.\nДоступные статусы: {available}")


def fetch_orders(state_href):
    """Возвращает все заказы покупателя с заданным статусом (с пагинацией)."""
    orders = []
    offset = 0
    limit = 100
    flt = urllib.parse.quote(f"state={state_href}", safe="=")
    while True:
        data = api_get(f"/entity/customerorder?filter={flt}&limit={limit}&offset={offset}&order=created,desc")
        rows = data.get("rows", [])
        orders.extend(rows)
        size = data.get("meta", {}).get("size", len(orders))
        offset += limit
        if offset >= size or not rows:
            break
    return orders


def main():
    state_href, state_real_name = find_state_href()
    orders = fetch_orders(state_href)

    print(f"Статус: «{state_real_name}»")
    print(f"Найдено заказов: {len(orders)}")
    print("-" * 70)
    total_sum = 0
    for o in orders:
        name = o.get("name", "—")
        moment = o.get("moment", "")[:16]
        # суммы в МойСклад хранятся в копейках
        amount = o.get("sum", 0) / 100
        total_sum += amount
        print(f"{name:<14} {moment:<17} {amount:>12,.2f} ₽")
    print("-" * 70)
    print(f"Итого по сумме: {total_sum:,.2f} ₽")


if __name__ == "__main__":
    main()
