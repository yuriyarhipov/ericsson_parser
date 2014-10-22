import psycopg2
from django.conf import settings
from os.path import basename
from main.models import File, Project


class Measurements(object):
    conf_file = ''
    data_files = []
    file_type = ''

    def __init__(self):
        self.conn = psycopg2.connect(
            'host = %s dbname = %s user = %s password = %s' % (
                settings.DATABASES['default']['HOST'],
                settings.DATABASES['default']['NAME'],
                settings.DATABASES['default']['USER'],
                settings.DATABASES['default']['PASSWORD']))
        self.cursor = self.conn.cursor()


    def get_file_type(self, filename):
        with open(filename) as f:
            columns = [col.lower() for col in f.readline().split()]
            if 'hcslayer' in columns:
                return 'NCS'
        return 'MRR'


    def save_file(self, filename, project, user, current_task, current, interval_per_file):
        table_name = basename(filename).split('.')[0]
        with open(filename) as f:
            columns = []
            for col in f.readline().split():
                if col not in columns:
                    columns.append(col)

            sql_columns = []
            for field in columns:
                sql_columns.append('"%s" TEXT' % field)

                self.cursor.execute('DROP TABLE IF EXISTS "%s"' % table_name)
                self.cursor.execute('CREATE TABLE IF NOT EXISTS "%s" (%s);' % (table_name, ', '.join(sql_columns)))

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
        project = Project.objects.get(project_name=project)
        File.objects.filter(filename=basename(filename), project=project).delete()
        File.objects.create(
            filename=basename(filename),
            file_type=self.get_file_type(filename),
            project=project,
            tables=table_name)
        self.conn.commit()



