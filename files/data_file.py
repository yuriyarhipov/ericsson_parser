import datetime
import psycopg2
import json
from django.conf import settings
from os.path import basename
import redis


class DataFile(object):

    def save_to_database(self, project_id, vendor, network, file_type, description, filename, task_id):
        r = redis.StrictRedis(host=settings.REDIS, port=6379, db=0)
        conn = psycopg2.connect(
            'host = %s dbname = %s user = %s password = %s' % (
                settings.DATABASES['default']['HOST'],
                settings.DATABASES['default']['NAME'],
                settings.DATABASES['default']['USER'],
                settings.DATABASES['default']['PASSWORD']))
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS Universal3g3gNeighbors (
            filename TEXT,
            rncSource TEXT,
            utrancellSource TEXT,
            carrierSource  TEXT,
            rncTarget TEXT,
            utrancellTarget TEXT,
            carrierTarget TEXT
        )''')
        cursor.execute('CREATE TABLE IF NOT EXISTS data_table (id SERIAL, project_id INT, filename TEXT, table_name TEXT, row JSONB)')
        cursor.execute('DELETE FROM data_table WHERE (project_id=%s) AND (filename=%s)', (project_id, basename(self.filename)))
        s = len(self.data)
        i = 0
        file_tables = set()
        for row in self.data:
            table_name = row.get('data_type')
            file_tables.add(row.get('data_type'))
            del row['data_type']
            cursor.execute('INSERT INTO data_table (project_id, filename, table_name, row) VALUES (%s, %s, %s, %s)', (project_id, filename, table_name, json.dumps(row, encoding='latin1')))
            i += 1
            r.set(task_id, '%s, writing' % int(float(i) / float(s) * 100))

        r.set(task_id, '100, writing')
        file_tables = list(file_tables)
        file_tables.sort()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM files_files WHERE (project_id=%s) AND (filename=%s)', (project_id, basename(self.filename)))
        cursor.execute('INSERT INTO files_files (filename, date, tables, excel_filename, archive, file_type, description, vendor, network, project_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', (
            filename,
            datetime.datetime.now(),
            ','.join(file_tables),
            '',
            '',
            file_type,
            description,
            vendor,
            network,
            project_id))
        conn.commit()
        r.set(task_id, 'done')