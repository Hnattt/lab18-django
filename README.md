# Навчальний проєкт моніторингу — ЛР18, варіант 3

**Номер профілю:** 3 (`profiles_15_18.json`, `variant: 3`) — однаковий для ЛР15–ЛР18.  
**Ситуація:** холодильна кімната. Пристрої: Холод камера (V03-A), Холод шлюз (V03-B), Склад (V03-C). Пошук «Холод», поріг 0 °C.

## Етап ЛР18

Додано власника пристрою (`owner`, міграція `0003_device_owner`), вхід користувача, форму `/measurements/new/` для додавання вимірювань лише до власних пристроїв і розширені тести.

## Середовище

ОС: Windows 10/11. Python 3.13.15, Django 6.1.2, SQLite 3.40.0. Підтримується Python 3.12–3.14.

## Запуск (Windows, PowerShell)

Усі команди виконуються з кореня репозиторію (де лежить `manage.py`).

```
py -3.13 -m venv .venv
.venv\Scripts\python -m pip install -r requirements-lock.txt
.venv\Scripts\python manage.py migrate
.venv\Scripts\python manage.py check
.venv\Scripts\python manage.py runserver 127.0.0.1:8000
```

Linux / macOS: `python3.13 -m venv .venv`, далі ті самі команди через `.venv/bin/python`.

## Дані та перевірка

На новій базі (PowerShell):
```
Get-Content scripts\seed_lab16.py | .venv\Scripts\python manage.py shell
Get-Content scripts\seed_lab17.py | .venv\Scripts\python manage.py shell
.venv\Scripts\python manage.py makemigrations --check --dry-run
.venv\Scripts\python manage.py test monitoring -v 2
.venv\Scripts\python -m unittest framework_examples.test_frameworks -v
```
Пристрої без власника мають `owner=NULL`. Через admin явно призначте користувача кожному serial — перший користувач автоматично не призначається. Форма `/measurements/new/` доступна після входу й показує лише власні пристрої; значення нижче 0 °C позначено окремо.

## Безпека

`.venv`, `db.sqlite3`, `__pycache__`, `.env`, паролі та ключі в репозиторій не додаються (див. `.gitignore`). `DEBUG` і запасний ключ — лише для локального навчання; реальний ключ задається змінною середовища `DJANGO_SECRET_KEY`.

Репозиторій етапу: https://github.com/Hnattt/lab18-django
