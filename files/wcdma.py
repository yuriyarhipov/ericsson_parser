import psycopg2

from django.conf import settings

from query.models import GroupCells, QueryTemplate


class WCDMA:

    def __init__(self):
        self.conn = psycopg2.connect(
            'host = %s dbname = %s user = %s password = %s' % (
                settings.DATABASES['default']['HOST'],
                settings.DATABASES['default']['NAME'],
                settings.DATABASES['default']['USER'],
                settings.DATABASES['default']['PASSWORD']))
        self.cursor = self.conn.cursor()

    def get_cells(self, filename):
        cells = []
        for cell in self.get_groups():
            cells.append({'cell': cell, 'type': 'Groups'})

        for cell in self.get_rnc(filename):
            cells.append({'cell': cell, 'type': 'RNC'})

        self.cursor.execute("SELECT DISTINCT UtranCell from UtranCell WHERE filename=%s ORDER BY UtranCell", (filename,))
        for r in self.cursor:
            cells.append({'cell': r[0], 'type': 'Cells'})
        return cells

    def get_rnc(self, filename):
        self.cursor.execute("SELECT DISTINCT RNC from Topology WHERE filename=%s ORDER BY RNC", (filename,))
        return [r[0] for r in self.cursor]

    def get_groups(self):
        return [gc.group_name for gc in GroupCells.objects.filter(network='WCDMA').order_by('group_name')]

    def get_cells_from_rnc(self, rnc, filename):
        self.cursor.execute("select DISTINCT UtranCell from Topology where filename=%s AND RNC='%s'" % (filename, rnc))
        return [r[0] for r in self.cursor]

    def get_cells_from_group_cell(self, group_cells):
        cells = []
        if GroupCells.objects.filter(group_name=group_cells, network='WCDMA').exists():
            cells = [cell for cell in GroupCells.objects.get(group_name=group_cells, network='WCDMA').cells.split(',')]
        return cells

    def convert_form_cells(self, cells, filename):
        real_cells = []
        for cell in cells:
            rnc_cell = self.get_cells_from_rnc(cell, filename)
            group_cells = self.get_cells_from_group_cell(cell)

            if rnc_cell:
                real_cells = real_cells + rnc_cell
            elif group_cells:
                real_cells = real_cells + group_cells
            else:
                real_cells.append(cell)
        return set("'%s'" % cell for cell in set(real_cells))



    def get_params_with_min_max(self, template):
        params = dict()
        for t in QueryTemplate.objects.filter(template_name=template):
            params[t.param_name.lower()] = [t.min_value, t.max_value]
        return params

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


    def get_right_column_name(self, column, template):
        right_columns = [t.param_name for t in QueryTemplate.objects.filter(template_name=template)] + ['UtranCell', 'RNC', 'SITE', 'SectorCarrier', 'SectorAntena', 'Carrier']
        for r_col in right_columns:
            if column.lower() == r_col.lower():
                return r_col
        return column

    def run_query(self, template, cells, filename):
        from files.models import SuperFile, Files
        from parameters.template import Template
        root_filename = filename
        if SuperFile.objects.filter(filename=filename).exists():
            filename = SuperFile.objects.filter(filename=filename).first().description.split(',')
        else:
            filename = [filename, ]
        filenames = ["'%s'" % f for f in filename]
        filenames = ','.join(filenames)

        data = []
        columns = []
        cells = self.convert_form_cells(cells, filenames)
        if template and cells:
            params = self.get_params_with_min_max(template)
            q = '''SELECT * INTO TEMPORARY TEMP_TEMPLATE FROM "template_%s" WHERE (filename IN (%s)) AND Utrancell in (%s)''' % (template, filenames, ','.join(cells))
            self.cursor.execute(q)
            self.cursor.execute("SELECT DISTINCT * FROM TEMP_TEMPLATE")

            colnames = [desc[0] for desc in self.cursor.description]
            data = []

            columns = [self.get_right_column_name(col, template) for col in colnames]
            for r in self.cursor:
                row = []
                for i in range(0, len(r)):
                    row.append([r[i], self.get_status(colnames[i], r[i], params), ])
                data.append(row)
        return columns, data

    def create_superfile(self, filename, files, tables):
        cursor = self.conn.cursor()
        for table in tables:
            cursor.execute('SELECT * FROM "%s"' % table.lower())
            columns = [desc[0] for desc in cursor.description]
            columns.remove('filename')
            insert_columns = ['"%s"' % col.lower() for col in columns]
            columns.append('filename')
            sql_columns = ['"%s"' % col.lower() for col in columns]
            sql_files = ["'%s'" % f.lower() for f in files]
            sql = '''INSERT INTO "%s" (%s) SELECT DISTINCT  %s, '%s' as filename FROM "%s" WHERE lower(filename) in (%s)''' % (
                table.lower(),
                ','.join(sql_columns),
                ','.join(insert_columns),
                filename,
                table.lower(),
                ','.join(sql_files)
            )
            cursor.execute(sql)
        self.conn.commit()

