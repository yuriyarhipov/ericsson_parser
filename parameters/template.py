from collections import OrderedDict
from openpyxl import load_workbook

from files.models import Files
from query.models import QueryTemplate, SiteQuery
from django.conf import settings
from collections import OrderedDict
import psycopg2


class Template(object):

    mo = []
    params = []
    template_name = ''
    tables = dict()

    def __init__(self):
        self.conn = psycopg2.connect(
            'host = %s dbname = %s user = %s password = %s' % (
                settings.DATABASES['default']['HOST'],
                settings.DATABASES['default']['NAME'],
                settings.DATABASES['default']['USER'],
                settings.DATABASES['default']['PASSWORD']))
        self.cursor = self.conn.cursor()


    def save_template(self, project, network, template_name, mo, params, min_values, max_values):
        self.template_name = template_name
        self.network = network
        self.project = project
        QueryTemplate.objects.filter(template_name=template_name).delete()
        for i in range(0, int(len(mo))):
            table_name = mo[i]
            param_name = params[i] if len(params) > i else ''
            min_value = min_values[i] if len(min_values) > i else ''
            max_value = max_values[i] if len(max_values) > i else ''

            if table_name and param_name:
                qt = QueryTemplate()
                qt.project = project
                qt.network = network
                qt.mo = table_name
                qt.param_name = param_name
                qt.max_value = max_value
                qt.min_value = min_value
                qt.template_name = self.template_name
                qt.save()

    def get_columns(self, table_name):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM %s LIMIT 0;' % table_name)
        return [desc[0].lower() for desc in cursor.description]

    def get_join_lte(self, table_name):
        columns = self.get_columns(table_name)
        sql_key = ''
        topology_key = ''
        if 'eutrancell' in columns:
            sql_key = 'EUtrancell'
            topology_key = 'EUtrancell'
        elif 'element1' in columns:
            sql_key = 'Element1'
            topology_key = 'CID'
        elif 'element2' in columns:
            sql_key = 'Element2'
            topology_key = 'SITE'

        sql = 'TOPOLOGY_LTE INNER JOIN %s ON ((%s.%s = TOPOLOGY_LTE.%s) AND (%s.filename=TOPOLOGY_LTE.filename))' % (table_name, table_name, sql_key, topology_key, table_name)
        return sql


    def get_join_wcdma(self, table_name):
        columns = self.get_columns(table_name)
        join_sql = []
        if 'utrancell' in columns:
            join_sql.append('(%s.UtranCell = TOPOLOGY.UtranCell)' % table_name)
        if 'element1' in columns:
            join_sql.append('(%s.Element1 = TOPOLOGY.RNC)' % table_name)
        if 'element2' in columns:
            join_sql.append('(%s.Element2 = TOPOLOGY.SITE)' % table_name)
        if 'sectorcarrier' in columns:
            join_sql.append('(%s.SectorCarrier = TOPOLOGY.SectorCarrier)' % table_name)
        if 'carrier' in columns:
            join_sql.append('(%s.Carrier = TOPOLOGY.Carrier)' % table_name)
        join_sql = ' AND '.join(join_sql)

        sql = 'TOPOLOGY INNER JOIN %s ON (%s AND (%s.filename=TOPOLOGY.filename))' % (table_name, join_sql, table_name)
        return sql

    def get_tables_cna(self, sql_tables):
        tables = []
        result_columns = []
        cell_index = 1
        for table_name, columns in sql_tables.iteritems():
            tables.append(table_name)
            sql_columns = []
            for column in columns:
                if column.lower() == 'cell':
                    sql_columns.append('"%s"."%s" AS CELL_%s' % (table_name, column, str(cell_index)))
                    cell_index += 1
                else:
                    sql_columns.append('"%s"."%s"' % (table_name, column))
        result_columns = result_columns + sql_columns

        sql_tables = ''
        root_table = tables[0]
        if len(tables) == 1:
            sql_tables = '"%s"' % tables[0]
        else:
            temp_tables = []
            for table in tables[1:]:
                temp_tables.append('INNER JOIN "%s" ON "%s".CELL="%s".CELL' % (table, root_table, table))
                sql_tables = '%s %s' % (root_table, ' '.join(temp_tables))

        sql_columns = ','.join(result_columns)
        sql = 'SELECT "%s".CELL, %s FROM %s' % (root_table, sql_columns, sql_tables)
        return sql



    def get_tables_lte(self, sql_tables):
        tables = []
        result_columns = []
        for table_name, columns in sql_tables.iteritems():
            sql_columns = ','.join(['%s.%s' % (table_name, col) for col in columns])
            sql_join = self.get_join_lte(table_name)
            table_sql = 'INNER JOIN (SELECT DISTINCT TOPOLOGY_LTE.EUtrancell, TOPOLOGY_LTE.filename, %s FROM %s) AS T_%s ON ((TOPOLOGY_LTE.EUtrancell=T_%s.EUtrancell) AND (TOPOLOGY_LTE.filename=T_%s.filename))' % (sql_columns, sql_join, table_name, table_name, table_name)
            tables.append(table_sql)
            result_columns.extend(['T_%s.%s' % (table_name, col) for col in columns])

        sql_columns = ', '.join(result_columns)
        sql_join = ' '.join(tables)
        sql = 'SELECT TOPOLOGY_LTE.CID, TOPOLOGY_LTE.SITE, TOPOLOGY_LTE.EUtrancell, TOPOLOGY_LTE.filename, %s FROM TOPOLOGY_LTE %s' % (sql_columns, sql_join)
        return sql

    def get_tables_wcdma(self, sql_tables):
        tables = []
        result_columns = []
        for table_name, columns in sql_tables.iteritems():
            sql_columns = ','.join(['%s.%s' % (table_name, col) for col in columns])
            sql_join = self.get_join_wcdma(table_name)
            table_sql = 'INNER JOIN (SELECT DISTINCT Topology.UtranCell, Topology.filename, %s FROM %s) AS T_%s ON ((Topology.Utrancell=T_%s.Utrancell) AND (Topology.filename=T_%s.filename))' % (sql_columns, sql_join, table_name, table_name, table_name)
            tables.append(table_sql)
            result_columns.extend(['T_%s.%s' % (table_name, col) for col in columns])

        sql_columns = ', '.join(result_columns)
        sql_join = ' '.join(tables)
        sql = 'SELECT DISTINCT TOPOLOGY.RNC, TOPOLOGY.UTRANCELL, TOPOLOGY.SITE, Topology.SectorCarrier, Topology.SectorAntena, Topology.Carrier, TOPOLOGY.filename,  %s FROM Topology %s' % (sql_columns, sql_join)
        return sql

    def get_tables(self, sql_tables, network):
        if network == 'WCDMA':
            return self.get_tables_wcdma(sql_tables)
        elif network == 'LTE':
            return self.get_tables_lte(sql_tables)
        elif network == 'GSM':
            return self.get_tables_cna(sql_tables)

    def get_select(self, template_name):
        sql_tables = OrderedDict()
        for template in QueryTemplate.objects.filter(template_name=template_name).order_by('id'):
            table_name = template.mo
            column = template.param_name
            network = template.network
            if table_name not in sql_tables:
                sql_tables[table_name] = []
            sql_tables[table_name].append(column)

        select = self.get_tables(sql_tables, network)
        return 'CREATE OR REPLACE VIEW "template_%s" AS %s' % (template_name, select)

    def create_template_table(self, template_name):
        self.cursor.execute('DROP VIEW IF EXISTS "template_%s"' % template_name)
        sql_select = self.get_select(template_name)
        self.cursor.execute(sql_select)
        self.conn.commit()

    def check_tables(self):
        for template in QueryTemplate.objects.all().order_by('template_name').distinct('template_name'):
            self.create_template_table(template.template_name)

    def get_sql_compare_id(self, filename):
        f = Files.objects.filter(filename=filename).first()
        if f:
            if f.network == 'WCDMA':
                return 'utrancell'
            elif f.network == 'LTE':
                return 'eutrancell'
        return 'CELL'

    @staticmethod
    def site_query(project, filename):
        data = OrderedDict()
        wb = load_workbook(filename=filename, use_iterators=True)
        ws = wb.active
        SiteQuery.objects.all().delete()
        for row in ws.iter_rows():
            if row[0].value == '**':
                site_name = row[1].value
            else:
                param_name = row[1].value
                param_min = row[2].value if row[2].value else ''
                param_max = row[3].value if row[3].value else ''

                if site_name not in data:
                    data[site_name] = []
                data[site_name].append([param_name, param_min, param_max])
                SiteQuery.objects.create(project=project, site=site_name, param_name=param_name, param_min=param_min, param_max=param_max)

        return data


