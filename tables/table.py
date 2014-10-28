import psycopg2

from django.conf import settings


class Table(object):

    active_file = None

    def __init__(self, table_name, filename):
        self.conn = psycopg2.connect(
            'host = %s dbname = %s user = %s password = %s' % (
                settings.DATABASES['default']['HOST'],
                settings.DATABASES['default']['NAME'],
                settings.DATABASES['default']['USER'],
                settings.DATABASES['default']['PASSWORD']))
        self.table_name = table_name
        self.filename = filename
        self.columns = self.get_columns()

    def get_columns(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM %s LIMIT 0' % (self.table_name, ))
        return [desc[0] for desc in cursor.description]

    def get_data(self):
        cursor = self.conn.cursor()
        sql_columns = ','.join(self.columns)
        cursor.execute('SELECT %s FROM %s' % (sql_columns, self.table_name))
        data = cursor.fetchall()
        return data
