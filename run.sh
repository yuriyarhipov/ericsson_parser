export C_FORCE_ROOT="true"
gunicorn_django -t 12000 -w 8 --bind xml.yura.cc:8002 &
python manage.py celeryd -l info &