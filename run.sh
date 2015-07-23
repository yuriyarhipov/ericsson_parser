export C_FORCE_ROOT="true"
gunicorn_django --bind xml.yura.cc:8002 &
python manage.py celeryd -l info &