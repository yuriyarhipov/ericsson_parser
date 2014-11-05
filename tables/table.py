import psycopg2
import xlsxwriter
import tempfile
from zipfile import ZipFile

from os.path import join

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
        cursor.execute("SELECT %s FROM %s WHERE lower(filename)='%s'" % (sql_columns, self.table_name, self.filename.lower()))
        data = cursor.fetchall()
        return data


def get_excel(table_name, columns, data):
    static_path = settings.STATICFILES_DIRS[0]
    archive_filename = join(static_path, table_name +'.zip')
    excel_filename = join(tempfile.mkdtemp(), table_name + '.xlsx')
    workbook = xlsxwriter.Workbook(excel_filename, {'constant_memory': True})
    worksheet = workbook.add_worksheet(table_name)
    i = 0
    for column in columns:
        worksheet.write(0, i, column)
        i += 1
    j = 1
    for r in data[:65535]:
        i = 0
        for cell in r:
            worksheet.write(j, i, cell)
            i += 1
        j += 1

    workbook.close()
    zip = ZipFile(archive_filename, 'w')
    zip.write(excel_filename, arcname=table_name + '.xlsx')
    zip.close()
    return table_name +'.zip'