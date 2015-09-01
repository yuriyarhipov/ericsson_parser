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
            for t in f.tables.split(','):
                if t.lower() not in tables:
                    tables.append(t.lower())
        elif f.network == 'LTE':
            tables = ['Topology_LTE', 'RND_LTE']
            tables.extend(list(set(f.tables.split(','))))
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
                    len(columns) - 1,
                    {'data': data,
                     'columns': columns})
        workbook.close()
        zip = ZipFile(archive_filename, 'w')
        zip.write(excel_filename, arcname=self.filename + '.xlsx')
        zip.close()


class PowerAuditExcel:

    def create_file(self, audit, project, filename):
        static_path = settings.STATICFILES_DIRS[0]
        file_path = '%s/%s' % (static_path, project)
        if not exists(file_path):
            makedirs(file_path)
        archive_filename = join(file_path, filename +'_power_audit.zip')


        excel_filename = join(tempfile.mkdtemp(), 'power_audit.xlsx')
        workbook = xlsxwriter.Workbook(excel_filename)
        worksheet = workbook.add_worksheet()
        bold = workbook.add_format({'bold': 1})
        headings = ['Yes', 'No']
        data_sector = audit.get('miss_sectors', [])
        data = [
            [audit.get('sector_count'), ],
            [len(data_sector), ],
        ]
        worksheet.write_row('A1', headings, bold)
        worksheet.write_column('A2', data[0])
        worksheet.write_column('B2', data[1])

        chart = workbook.add_chart({'type': 'column'})

        chart.add_series({'values': '=Sheet1!$A$1:$A$5'})
        chart.add_series({'values': '=Sheet1!$B$1:$B$5'})

        worksheet.insert_chart('A4', chart)

        table_headers = [
            'UtranCell',
            'CID',
            'Sector',
            'maximumTransmissionPower',
            'maxDlPowerCapability']
        worksheet.write_row('A20', table_headers, bold)
        data = []
        for row in data_sector:
            data.append([row.get('utrancell'), row.get('id'), row.get('sector'), row.get('power'), row.get('cap')])

        worksheet.add_table(20, 0, 20 + len(data), 3, {'data': data,})

        workbook.close()

        zip = ZipFile(archive_filename, 'w')
        zip.write(excel_filename, arcname=filename + '.xlsx')
        zip.close()
        return join('/static/%s' % project, filename +'_power_audit.zip')


class AuditExcel:

    def create_file(self, audit, project, filename):
        static_path = settings.STATICFILES_DIRS[0]
        file_path = '%s/%s' % (static_path, project)
        if not exists(file_path):
            makedirs(file_path)
        archive_filename = join(file_path, filename + '_audit.zip')

        excel_filename = join(tempfile.mkdtemp(), '_audit.xlsx')
        workbook = xlsxwriter.Workbook(excel_filename)
        worksheet = workbook.add_worksheet()
        data = []
        for row in audit:
            data.append([
                row.get('param'),
                row.get('complaint'),
                row.get('not_complaint'),
                row.get('total'),
                row.get('percent')]
            )
        bold = workbook.add_format({'bold': 1})
        columns = [
            'Parameter',
            'Complaint List',
            'No Complaint List',
            'Total',
            '%']
        worksheet.write_row('A1', columns, bold)
        worksheet.add_table(1, 0, len(data) + 1, 4, {'data': data, })

        chart = workbook.add_chart({'type': 'column'})
        chart.add_series({
            'categories': ['Sheet1', 3, 0, len(data), 0],
            'values':     ['Sheet1', 3, 1, len(data), 1],
            'line':       {'color': 'red'},
        })
        worksheet.insert_chart('G1', chart)

        workbook.close()

        zip = ZipFile(archive_filename, 'w')
        zip.write(excel_filename, arcname=filename + '.xlsx')
        zip.close()
        return join('/static/%s' % project, filename + '_audit.zip')


class DistanceExcel(object):

    def create_file(self, project, filename, chart, table):
        static_path = settings.STATICFILES_DIRS[0]
        file_path = '%s/%s' % (static_path, project)
        if not exists(file_path):
            makedirs(file_path)
        archive_filename = join(file_path, filename + '_distance.zip')

        excel_filename = join(tempfile.mkdtemp(), '_distance.xlsx')
        workbook = xlsxwriter.Workbook(excel_filename)
        worksheet = workbook.add_worksheet()
        data = []
        for row in table:
            data.append([
                row.get('date'),
                row.get('sector'),
                row.get('distance'),
                row.get('samples'),
                row.get('samples_percent'),
                row.get('total_samples')]
            )

        bold = workbook.add_format({'bold': 1})
        columns = [
            'Date',
            'Sector',
            'Distance',
            'Samples',
            'Percent',
            'Total Samples']
        worksheet.write_row('A1', columns, bold)
        worksheet.add_table(1, 0, len(data) + 1, 5, {'data': data, })

        chart = workbook.add_chart({'type': 'column'})
        chart.add_series({
            'categories': ['Sheet1', 3, 2, len(data), 2],
            'values':     ['Sheet1', 3, 4, len(data), 4],
            'line':       {'color': 'red'},
        })
        worksheet.insert_chart('H1', chart)

        workbook.close()

        zip = ZipFile(archive_filename, 'w')
        zip.write(excel_filename, arcname=filename + '.xlsx')
        zip.close()
        return join('/static/%s' % project, filename + '_audit.zip')
