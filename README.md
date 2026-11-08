# Навчальний проєкт моніторингу, ЛР15–18, варіант 3
Офіційний профіль profiles_15_18.json: холодильна кімната; Холод камера V03-A, Холод шлюз V03-B, Склад V03-C. Пошук «Холод», поріг 0 °C. Деталі паспорта, мітки й вимірювання визначає профіль. На етапі 15 це план; дані додаються на етапах 16–17.

Потрібен Python 3.12–3.14, фактично перевірено 3.13.15 та Django 6.1.2 на Linux.
```
python3.13 -m venv .venv
.venv/bin/python -m pip install -r requirements-lock.txt
.venv/bin/python manage.py migrate
.venv/bin/python manage.py check
.venv/bin/python manage.py runserver 127.0.0.1:8000
```
Запускайте з папки course_monitoring; .venv, db.sqlite3, кеші, .env, паролі та ключі до архіву не входять. DEBUG і запасний ключ — лише для локального навчання. Реальні ключі задаються через DJANGO_SECRET_KEY. Репозиторій етапу: https://github.com/Hnattt/lab18-django.

З новою базою: `python manage.py shell < scripts/seed_lab16.py` створює пристрої з профілю.

Після пристроїв: `python manage.py shell < scripts/seed_lab17.py` додає паспорти, мітки і вимірювання з профілю; `python manage.py shell < scripts/inspect_lab17.py` перевіряє агрегати. Скрипт запобігає повторному створенню.

Нові/старі пристрої без власника мають owner=NULL. Через admin явно призначте користувача кожному конкретному serial; не призначайте першого користувача автоматично. Форма доступна за /measurements/new/ після входу. Лише власні пристрої; для показу temperature < 0 °C використано окрему позначку на сторінці. Запуск перевірок: `python manage.py test monitoring -v 2` та `python -m unittest framework_examples.test_frameworks -v`.
