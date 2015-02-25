import psycopg2
from django.conf import settings
from os.path import basename
from files.models import Files


class Measurements(object):

    def __init__(self):
        self.conn = psycopg2.connect(
            'host = %s dbname = %s user = %s password = %s' % (
                settings.DATABASES['default']['HOST'],
                settings.DATABASES['default']['NAME'],
                settings.DATABASES['default']['USER'],
                settings.DATABASES['default']['PASSWORD']))
        self.cursor = self.conn.cursor()

    def save_file(self, filename, project, description, vendor, file_type, network, current_task):
        table_name = basename(filename).split('.')[0]
        with open(filename) as f:
            columns = []
            for col in f.readline().split():
                if col not in columns:
                    columns.append(col)

            sql_columns = []
            for field in columns:
                print field
                sql_columns.append('"%s" TEXT' % field)

            self.cursor.execute('DROP TABLE IF EXISTS "%s"' % table_name)
            self.cursor.execute('CREATE TABLE IF NOT EXISTS "%s" (%s);' % (table_name, ', '.join(sql_columns)))
            i = float(1)

            for row in f:

                values = dict()
                row = row.split()
                sql_columns = []
                sql_values = []
                for i in range(0, len(columns)):
                    if i < len(row):
                        values[columns[i]] = row[i]

                for k, v in values.iteritems():
                    sql_columns.append('"%s"' % k)
                    sql_values.append("'%s'" % v)

                sql_insert = 'INSERT INTO "%s" (%s) VALUES (%s)' % (table_name, ','.join(sql_columns), ','.join(sql_values))
                self.cursor.execute(sql_insert)

                i = i + float(0.01)
                current_task.update_state(state="PROGRESS", meta={"current": int(i)})
        Files.objects.filter(filename=basename(filename), project=project).delete()
        Files.objects.create(
                filename=basename(filename),
                file_type=file_type,
                project=project,
                tables='',
                description=description,
                vendor=vendor,
                network=network)
        self.conn.commit()



