import psycopg2
from django.conf import settings
from query.models import QueryTemplate, GroupCells
from files.models import Files, ExcelFile, CNATemplate
from files.excel import Excel
from lib import fcount
from os.path import basename
from files import tasks


class CNA:

    def __init__(self):
        self.conn = psycopg2.connect(
            'host = %s dbname = %s user = %s password = %s' % (
                settings.DATABASES['default']['HOST'],
                settings.DATABASES['default']['NAME'],
                settings.DATABASES['default']['USER'],
                settings.DATABASES['default']['PASSWORD']))
        self.cursor = self.conn.cursor()

    def get_tree(self, filename):
        data = {}
        cursor = self.conn.cursor()
        cursor.execute('SELECT DISTINCT BSC, MSC, SECTORS FROM "%s" ORDER BY BSC' % (filename, ))
        for row in cursor:
            data[row[0]] = []

    def get_cells(self, filename):
        self.cursor.execute('''SELECT DISTINCT CELL FROM "umfi" WHERE filename='%s' ORDER BY CELL''' % (filename, ))
        return [{'cell': r[0], 'type': 'Cells'} for r in self.cursor.fetchall()]

    def get_mo(self, query):

        mo = [f.filename for f in Files.objects.filter(file_type='CNA')]
        data = []
        for m in mo:
            if query:
                if query.lower() in m.lower():
                    data.append(dict(id=m, text=m))
            else:
                data.append(dict(id=m, text=m))

        data.sort()
        return data

    def get_mo_param(self, mo, q):
        self.cursor.execute('SELECT * FROM "%s" LIMIT 0' % mo)
        colnames = [desc[0] for desc in self.cursor.description]

        data = [dict(id=p, text=p) for p in colnames]
        data.sort()
        return data

    def get_groups(self):
        return [gc.group_name for gc in GroupCells.objects.filter(type='LTE').order_by('group_name')]

    def get_where(self, tables, cells):
        result = []
        tables = list(tables)
        root_table = tables[0]
        result.append("(%s._Cell IN (%s) )" % (root_table, ','.join(cells)))
        for table_name in tables:
            result.append("(%s._CELL=%s._CELL)" % (table_name, root_table))
        return ' AND '.join(result)

    def get_cells_from_group_cell(self, group_cells):
        cells = []
        if GroupCells.objects.filter(group_name=group_cells, network='GSM').exists():
            cells = [cell for cell in GroupCells.objects.get(group_name=group_cells, network='GSM').cells.split(',')]
        return cells

    def convert_form_cells(self, cells):
        real_cells = []
        for cell in cells:
            group_cells = self.get_cells_from_group_cell(cell)

            if group_cells:
                real_cells = real_cells + group_cells
            else:
                real_cells.append(cell)
        return set("'%s'" % cell for cell in set(real_cells))

    def get_params_with_min_max(self, template):
        params = dict()
        for t in QueryTemplate.objects.filter(template_name=template):
            params[t.param_name.lower()] = [t.min_value, t.max_value]
        return params

    def get_right_column_name(self, column, template):
        right_columns = [t.param_name for t in QueryTemplate.objects.filter(template_name=template)] + ['CELL', ]
        for r_col in right_columns:
            if column.lower() == r_col.lower():
                return r_col
        return column

    def get_status(self, column, value, params):
        result = False
        column = column.lower()
        if column in params:
            min_value, max_value = params[column]
            if min_value and max_value and value:
                try:
                    result = not ((float(min_value) < float(value)) and (float(max_value) > float(value)))
                except:
                    result = False
        return result

    def run_query(self, template, cells, filename):
        data = []
        columns = []
        cells = self.convert_form_cells(cells)
        if template and cells:
            params = self.get_params_with_min_max(template)
            q = 'SELECT  * FROM "template_%s" WHERE CELL in (%s)' % (template, ','.join(cells))
            self.cursor.execute(q)
            colnames = [desc[0] for desc in self.cursor.description]
            data = []

            columns = [self.get_right_column_name(col, template) for col in colnames]
            for r in self.cursor:
                row = []
                for i in range(0, len(r)):

                    row.append([r[i], self.get_status(colnames[i], r[i], params), ])
                data.append(row)
        return columns, data

    def active_file(self):
        #if not CNATable.objects.filter(active=True).exists():
        #    f = CNATable.objects.filter().first()
        #    f.active = True
        #    f.save()
        return# CNATable.objects.get(active=True)

    def get_compare_files(self):
        #root_file = self.active_file().table_name[1:]
        #files = [f.table_name[1:] for f in CNATable.objects.filter(active=False)]
        return# root_file, files

    def add_rows(self, filename, tables, columns, rows):

        for table, table_columns in tables.iteritems():
            sql_columns = []
            sql_values = []
            index_columns = []
            for col in table_columns:
                if col in columns:
                    sql_columns.append('"%s"' % col)
                    index_columns.append(columns.index(col))

            sql_columns.append('"%s"' % 'filename')
            for row in rows:
                sql_row = []
                for index_column in index_columns:
                    sql_row.append("'%s'" % row[index_column])

                sql_row.append("'%s'" % filename)
                sql_values.append('(%s)' % ','.join(sql_row))

            sql_columns = ','.join(sql_columns)
            sql_values = ','.join(sql_values)

            sql = 'INSERT INTO "%s" (%s) VALUES %s' % (table.lower(), sql_columns, sql_values)
            cursor = self.conn.cursor()
            cursor.execute(sql)
        self.conn.commit()


    def create_cna_table(self, table_name, columns):
        cursor = self.conn.cursor()
        cursor.execute("SELECT column_name FROM INFORMATION_SCHEMA.COLUMNS WHERE (lower(table_name)=%s)", (table_name.lower(), ))
        if cursor.rowcount > 0:
            added_columns = []
        else:
            sql_columns = ', '.join(['"%s" TEXT' % col for col in columns])
            cursor.execute('CREATE TABLE "%s" (%s) ' % (table_name.lower(), sql_columns))


    def save_cna(self, filename, project, description, vendor, file_type, network):
        row_count = 1000
        tables = dict()

        for cna_template in CNATemplate.objects.filter(project=project):
            columns = [col.lower() for col in cna_template.columns.split(',')]
            columns.append('filename')
            tables[cna_template.table_name] = columns
            self.create_cna_table(cna_template.table_name, columns)

        with open(filename) as f:
            columns = [col.lower() for col in f.readline().split()]
            rows = []
            for row in f:
                if '---' not in row:
                    rows.append(row.split())
                    if len(rows) == row_count:
                        tasks.parse_cna_rows.delay(basename(filename), tables, columns, rows)
                        rows = []

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


    def get_table_name(self, tables, param):
        for table, columns in tables.iteritems():
            if param.lower() in columns:
                return table

    def create_template(self, template_name):
        cursor = self.conn.cursor()
        tables = dict()
        sql = None

        for cna_template in CNATemplate.objects.all():
            tables[cna_template.table_name] = [col.lower() for col in cna_template.columns.split(',')]

        sql_tables = []
        sql_columns = []
        for qt in QueryTemplate.objects.filter(template_name=template_name):
            if qt.param_name.lower() not in ['cell', 'bsc']:
                table_name = self.get_table_name(tables, qt.param_name)
                if table_name:
                    sql_tables.append('"%s"' % table_name.lower())
                    sql_columns.append('"%s"' % qt.param_name)

        if len(sql_tables) == 1:
            sql = 'CREATE OR REPLACE VIEW "template_%s" AS SELECT DISTINCT CELL, BSC, FileName, %s FROM %s' % (
                template_name,
                ','.join(sql_columns),
                sql_tables[0].lower())
        elif len(sql_tables) > 1:
            sql_where = []
            for sql_table in sql_tables[1:]:
                sql_where.append('(%s.CELL = %s.CELL)' % (sql_tables[0].lower(), sql_table.lower()))
                sql_where.append('(%s.BSC = %s.BSC)' % (sql_tables[0].lower(), sql_table.lower()))

            sql = 'CREATE OR REPLACE VIEW "template_%s" AS SELECT DISTINCT %s.CELL, %s.BSC, %s.FileName, %s FROM %s WHERE %s' % (
                template_name,
                sql_tables[0].lower(),
                sql_tables[0].lower(),
                sql_tables[0].lower(),
                ','.join(sql_columns),
                ','.join(sql_tables),
                ' AND '.join(sql_where))

        if sql:
            cursor.execute(sql)
            self.conn.commit()

    def create_superfile(self, filename, files):
        cursor = self.conn.cursor()
        for cna_template in CNATemplate.objects.all():
            table_name = cna_template.table_name
            columns = ['"%s"' % col.lower() for col in cna_template.columns.split(',')]
            sql_files = ["'%s'" % f.lower() for f in files]
            sql = '''INSERT INTO "%s" SELECT DISTINCT  %s, '%s' as filename FROM "%s" WHERE lower(filename) in (%s)''' % (
                table_name,
                ','.join(columns),
                filename,
                table_name,
                ','.join(sql_files)
            )
            cursor.execute(sql)
        self.conn.commit()





