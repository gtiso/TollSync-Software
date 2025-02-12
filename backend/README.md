# Back-end

# How to run MySql database

1. Open MySql (https://www.mysql.com/downloads/)
2. Create a schema called 'tollsync'
3. Make tollsync "As default Schema" and navigate to "Administration" page. 
4. Press "User and Privilages" and pres "user" button. Then make the Login Name as "user" (if you don't wish to change it go to our file in "backend\config\settings.py" and change this "mysql+pymysql://user:user@localhost/tollsync").
5. Navigate to "Administrative Roles" and press "DBA"
6. Apply and you are ready.

# How to run backend

1. Download [python] (https://www.python.org/downloads/) 
2. Open CMD
3. pip install -r requirements.txt
4. python backend.py
5. python manage.py runserver
   a. If it doesn't work run python manage.py makemigrations
   b. If it doesn't work run python manage.py migrate
6. In order for all functionalities to work we must first login and then --addpasses

# Data

All data from tables are put into the tables through the cli commands. See the data in 'backend\misc'.

**Dependencies**
Package            Version
------------------ -----------
asgiref            3.8.1
blinker            1.9.0
certifi            2025.1.31
cffi               1.17.1
charset-normalizer 3.4.1
click              8.1.8
colorama           0.4.6
cryptography       44.0.1
Django             5.1.6
Flask              3.1.0
Flask-SQLAlchemy   3.1.1
flask_sqlalchemy   3.1.1
greenlet           3.1.1
idna               3.10
itsdangerous       2.2.0
Jinja2             3.1.5
jwt                1.3.1
MarkupSafe         3.0.2
numpy              2.2.2
pandas             2.2.3
pip                25.0.1
pycparser          2.22
PyMySQL            1.1.1
PyJWT              2.10.1
python-dateutil    2.9.0.post0
pytz               2025.1
requests           2.32.3
setuptools         65.5.0
six                1.17.0
SQLAlchemy         2.0.38
sqlparse           0.5.3
typing_extensions  4.12.2
tzdata             2025.1
urllib3            2.3.0
Werkzeug           3.1.3















Ενδεικτικά περιεχόμενα:

- Πηγαίος κώδικας εφαρμογής για εισαγωγή, διαχείριση και
  πρόσβαση σε δεδομένα (backend).
- Database dump (sql ή json)
- Back-end functional tests.
- Back-end unit tests.
- RESTful API.
