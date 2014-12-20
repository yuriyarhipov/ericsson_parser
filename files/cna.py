import psycopg2
from django.conf import settings
from query.models import QueryTemplate, GroupCells
from files.models import Files
from project.models import Project
from lib import fcount
from os.path import basename


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
        self.cursor.execute('SELECT DISTINCT CELL FROM "%s" ORDER BY CELL' % (filename, ))
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

    def add_row(self, table_name, columns, row):
        if '---' not in row:
            row = row.split()
            values = row[:1500]
            columns = columns[:1500]

            sql_columns = ['"%s"' % col for col in columns]
            sql_values = ["'%s'" % val for val in values]
            cursor = self.conn.cursor()
            cursor.execute('INSERT INTO "%s" (%s) VALUES (%s)' % (table_name, ', '.join(sql_columns), ', '.join(sql_values)))


    def create_cna_tables(self, table_name, columns):
        columns = columns[:1500]
        self.create_cna_table(table_name, columns)

    def create_cna_table(self, table_name, columns):
        cursor = self.conn.cursor()
        sql_columns = ', '.join(['"%s" TEXT' % col for col in columns])

        cursor.execute('DROP TABLE IF EXISTS "%s" CASCADE' % (table_name, ))
        cursor.execute('CREATE TABLE "%s" (%s) ' % (table_name, sql_columns))

    def save_cna(self, filename, project, description, vendor, file_type, network, task, current, available):
        table_name = basename(filename).split('.')[0]

        count = fcount(filename)
        with open(filename) as f:
            columns = []
            for col in f.readline().split():
                if (col not in columns) and (len(columns) < 1550):
                    columns.append(col.lower())

            self.create_cna_tables(table_name, columns[:])
            interval = float(available)/float(count)
            for row in f:
                current = float(current) + float(interval)
                self.add_row(table_name, columns, row)
                task.update_state(state="PROGRESS", meta={"current": int(current), "total": 99})
        Files.objects.filter(filename=table_name, project=project).delete()
        Files.objects.create(
                filename=table_name,
                file_type=file_type,
                project=project,
                tables='',
                description=description,
                vendor=vendor,
                network=network)
        self.conn.commit()
