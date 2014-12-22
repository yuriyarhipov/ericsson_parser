from zipfile import ZipFile
from django.conf import settings
import tempfile
import xlsxwriter
from os.path import join


class Excel:

    def __init__(self, project, table_name, columns, data):
        self.project = project

        self.table_name = table_name
        self.columns = columns
        self.data = data
        self.filename = ''
        self.main()

    def main(self):
        static_path = settings.STATICFILES_DIRS[0]
        archive_filename = join('%s/%s' % (static_path, self.project), self.table_name +'.zip')
        excel_filename = join(tempfile.mkdtemp(), self.table_name + '.xlsx')
        workbook = xlsxwriter.Workbook(excel_filename)
        worksheet = workbook.add_worksheet(self.table_name)
        worksheet.add_table(0, 0, len(self.data) - 1, len(self.columns) - 1,
                            {'data': self.data})
        workbook.close()
        zip = ZipFile(archive_filename, 'w')
        zip.write(excel_filename, arcname=self.table_name + '.xlsx')
        zip.close()
        self.filename = archive_filename

