service nginx restart
service postgresql restart
service rabbitmq-server restart
gunicorn_django --bind xml.yura.cc:8001 &
python manage.py celeryd -l info &