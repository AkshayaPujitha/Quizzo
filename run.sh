virtualenv demoenv -p python3
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver