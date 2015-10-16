service nginx restart &
service postgresql restart &
service rabbitmq-server restart
export C_FORCE_ROOT="true"
gunicorn_django -t 12000 -w 8 --bind localhost:8001 &
python manage.py celeryd -l info &