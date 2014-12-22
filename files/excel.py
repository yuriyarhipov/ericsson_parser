from zipfile import ZipFile
from django.conf import settings
import tempfile
import xlsxwriter
from os.path import join, exists
from os import makedirs


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


