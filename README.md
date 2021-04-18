# codebrew2021

### Live website
[growocery.herokuapp.com](growocery.herokuapp.com)

### How to run the app
1. Create a Python virtual environment.
```
virtualenv venv
source venv/bin/activate
```
2. Install packagages. 
```
pip install -r requirements.txt
```
3. Run migrations.
```
python manage.py makemigrations
python manage.py migrate
```
4. Start the app.
```
python manage.py runserver
```