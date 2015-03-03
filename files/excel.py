from zipfile import ZipFile
import psycopg2
from django.conf import settings
import tempfile
import xlsxwriter
from os.path import join, exists
from os import makedirs

from files.models import Files, CNATemplate
from tables.table import Table

class Excel:

    def __init__(self, project, table_name, columns, data):
        self.project = project

        self.table_name = table_name
        self.columns = [{'header': col} for col in columns]
        self.data = data
        self.filename = ''
        self.main()

    def main(self):
        static_path = settings.STATICFILES_DIRS[0]
        file_path = '%s/%s' % (static_path, self.project)
        if not exists(file_path):
            makedirs(file_path)
        archive_filename = join(file_path, self.table_name +'.zip')
        self.filename = join('/static/%s' % self.project, self.table_name +'.zip')
        if exists(archive_filename):
            return

        excel_filename = join(tempfile.mkdtemp(), self.table_name + '.xlsx')
        workbook = xlsxwriter.Workbook(excel_filename)
        worksheet = workbook.add_worksheet(self.table_name)
        worksheet.add_table(0, 0, len(self.data), len(self.columns)-1,
                            {'data': self.data,
                             'columns': self.columns})
        workbook.close()
        zip = ZipFile(archive_filename, 'w')
        zip.write(excel_filename, arcname=self.table_name + '.xlsx')
        zip.close()


class ExcelFile:

    def __init__(self, project, filename):
        self.project = project
        self.filename = filename
        self.excel_filename = ''
        self.conn = psycopg2.connect(
            'host = %s dbname = %s user = %s password = %s' % (
                settings.DATABASES['default']['HOST'],
                settings.DATABASES['default']['NAME'],
                settings.DATABASES['default']['USER'],
                settings.DATABASES['default']['PASSWORD']))
        self.main()

    def main(self):
        cursor = self.conn.cursor()
        static_path = settings.STATICFILES_DIRS[0]
        file_path = '%s/%s' % (static_path, self.project.project_name)
        if not exists(file_path):
            makedirs(file_path)
        archive_filename = join(file_path, self.filename +'.zip')
        self.excel_filename = join('/static/%s' % self.project.project_name, self.filename +'.zip')
        if exists(archive_filename):
            return

        f = Files.objects.filter(project=self.project, filename=self.filename).first()

        if f.network == 'WCDMA':
            tables = ['Topology', 'RND']
            tables.extend(f.tables.split(','))
        elif f.network == 'LTE':
            tables = ['Topology_LTE', 'RND_LTE']
            tables.extend(f.tables.split(','))
        elif f.network == 'GSM':
            tables = [cna_t.table_name for cna_t in CNATemplate.objects.filter(project=self.project)]

        excel_filename = join(tempfile.mkdtemp(), self.filename + '.xlsx')
        workbook = xlsxwriter.Workbook(excel_filename)
        for table in tables:
            sql = "SELECT column_name FROM INFORMATION_SCHEMA.COLUMNS WHERE (lower(table_name)='%s')" % (table.lower(),)
            cursor.execute(sql)
            if cursor.rowcount > 0:
                current_table = Table(table, self.filename)
                data = current_table.get_data()
                columns = [{'header': col} for col in current_table.columns]
                worksheet = workbook.add_worksheet(table)
                worksheet.add_table(
                    0,
                    0,
                    len(data),
                    len(columns)-1,
                    {'data': data,
                     'columns': columns})
        workbook.close()
        zip = ZipFile(archive_filename, 'w')
        zip.write(excel_filename, arcname=self.filename + '.xlsx')
        zip.close()



