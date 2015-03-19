import psycopg2

from django.conf import settings

from files.models import Files
from query.models import GroupCells, QueryTemplate


class LTE:

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

        self.cursor.execute("SELECT DISTINCT EUtrancell from TOPOLOGY_LTE WHERE filename=%s ORDER BY EUtrancell", (filename,))
        for r in self.cursor:
            cells.append({'cell': r[0], 'type': 'Cells'})
        return cells

    def get_lte_files(self):
        return [f for f in Files.objects.filter(network='LTE')]

    def get_mo(self, query):
        mo = []
        for f in self.get_lte_files():
            mo = mo + f.tables.split(',')
        mo = set(mo)
        data = []
        for m in mo:
            if query:
                if query.lower() in m.lower():
                    data.append(dict(id=m, text=m))
            else:
                data.append(dict(id=m, text=m))

        data.sort()
        return data

    def get_groups(self):
        return [gc.group_name for gc in GroupCells.objects.filter(network='LTE').order_by('group_name')]

    def get_where(self, tables, filename, cells):
        result = ["(Topology_LTE.filename='%s')" % filename, ]
        result.append("(Topology_LTE.EUtrancell IN (%s) )" % ','.join(cells))
        for table_name in tables:
            result.append("(%s.filename='%s')" % (table_name, filename))
            columns = Table.objects.get(table_name=table_name, filename=filename).columns.split(',')
            if 'Element1' in columns:
                result.append('(Topology_LTE.CID=%s.Element1)' % table_name)
            if 'Element2' in columns:
                result.append('(Topology_LTE.SITE=%s.Element2)' % table_name)
            if 'EUtrancell' in columns:
                result.append('(Topology_LTE.EUtrancell=%s.EUtrancell)' % table_name)
        return ' AND '.join(result)

    def get_cells_from_group_cell(self, group_cells):
        cells = []
        if GroupCells.objects.filter(group_name=group_cells, network='LTE').exists():
            cells = [cell for cell in GroupCells.objects.get(group_name=group_cells, network='LTE').cells.split(',')]
        return cells

    def convert_form_cells(self, cells, filename):
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
        right_columns = [t.param_name for t in QueryTemplate.objects.filter(template_name=template)] + ['UtranCell', 'RNC', 'SITE']
        for r_col in right_columns:
            if column.lower() == r_col.lower():
                return r_col
        return column

    def run_query(self, template, cells, filename):
        from files.models import SuperFile
        from parameters.template import Template
        if SuperFile.objects.filter(filename=filename).exists():
            filename = SuperFile.objects.filter(filename=filename).first().description.split(',')
        else:
            filename = [filename, ]
        filenames = ["'%s'" % f for f in filename]
        filenames = ','.join(filenames)

        data = []
        columns = []
        cells = self.convert_form_cells(cells, filename)
        if template and cells:
            params = self.get_params_with_min_max(template)
            sql = Template().get_select(template, filenames, cells)
            self.cursor.execute(sql)
            print sql
            colnames = [desc[0] for desc in self.cursor.description]
            data = []

            columns = [self.get_right_column_name(col, template) for col in colnames]
            for r in self.cursor:
                row = []
                for i in range(0, len(r)):

                    row.append([r[i], self.get_status(colnames[i], r[i], params), ])
                data.append(row)
        return columns, data



