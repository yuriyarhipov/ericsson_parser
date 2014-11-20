service nginx restart &
service postgresql restart &
service rabbitmq-server restart &
gunicorn_django --bind localhost:8001 &
python manage.py celeryd -l info &