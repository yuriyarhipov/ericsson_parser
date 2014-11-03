import psycopg2
from django.conf import settings

from files.models import Files
from parameters.template import Template
from files.wcdma import WCDMA
from files.lte import LTE


class CompareFiles(object):

    def __init__(self, root_file, files):
        self.conn = psycopg2.connect(
            'host = %s dbname = %s user = %s password = %s' % (
                settings.DATABASES['default']['HOST'],
                settings.DATABASES['default']['NAME'],
                settings.DATABASES['default']['USER'],
                settings.DATABASES['default']['PASSWORD']))
        self.cursor = self.conn.cursor()
        self.root_file = root_file
        self.files = files

    def get_tables_info(self):
        tables = Files.objects.get(filename=self.root_file).tables.split(',')

        for f in self.files:
            tables.extend(Files.objects.get(filename=f).tables.split(','))

        tables = set(tables)
        result = []
        for table in tables:
            ct = CompareTable(table, self.root_file, self.files)
            result.append([table, ct.get_count()])
        return result


class Compare(object):

    def __init__(self, table_name, root_file, files):
        self.conn = psycopg2.connect(
            'host = %s dbname = %s user = %s password = %s' % (
                settings.DATABASES['default']['HOST'],
                settings.DATABASES['default']['NAME'],
                settings.DATABASES['default']['USER'],
                settings.DATABASES['default']['PASSWORD']))
        self.root_file = root_file
        self.files = files
        self.columns = self.get_columns()
        self.data = dict()
        self.table_name = table_name
        self.sql_id = Template().get_sql_compare_id(self.root_file)
        f = Files.objects.filter(filename=root_file).first()
        if f:
            self.file_type = f.file_type

    def get_columns(self):
        columns = ['MO', 'Parameter', self.root_file]
        columns.extend([f for f in self.files])
        return columns

    def get_data_by_mo(self, mo):
        pass

    def get_data(self, mo):
        result = []
        for m in mo:
            result.extend(self.get_data_by_mo(m))
        return result

    def get_status(self, val1, val2):
        if val1 == '':
            return 'NEW'
        if val2 == '':
            return 'DEL'
        if val1 == val2:
            return 'OK'
        return 'EDIT'


class CompareTable(Compare):

    def get_count(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM %s LIMIT 0' % self.table_name)
        columns = [desc[0] for desc in cursor.description]
        columns.remove('filename')
        sql_columns = ', '.join(columns)
        files = self.files + [self.root_file, ]

        sql_files = []
        for f in files:
            sql_files.append("SELECT %s FROM %s WHERE filename='%s'" % (sql_columns, self.table_name, f))

        union_sql = ' UNION '.join(sql_files)
        intersect_sql = ' INTERSECT '.join(sql_files)
        sql = 'SELECT DISTINCT MO FROM (%s EXCEPT %s) as MO_Table' % (union_sql, intersect_sql)
        cursor.execute(sql)
        return cursor.rowcount

    def get_mo_list(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM %s LIMIT 0' % self.table_name)
        columns = [desc[0] for desc in cursor.description]
        columns.remove('filename')
        sql_columns = ', '.join(columns)
        files = self.files + [self.root_file, ]

        sql_files = []
        for f in files:
            sql_files.append("SELECT %s FROM %s WHERE filename='%s'" % (sql_columns, self.table_name, f))

        union_sql = ' UNION '.join(sql_files)
        intersect_sql = ' INTERSECT '.join(sql_files)
        sql = 'SELECT DISTINCT MO FROM (%s EXCEPT %s) as MO_Table' % (union_sql, intersect_sql)
        cursor.execute(sql)

        return [r[0] for r in cursor]


    def get_data_by_mo(self, mo):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM %s LIMIT 0' % self.table_name)
        columns = [desc[0] for desc in cursor.description]
        columns.remove('filename')
        columns.remove('mo')
        root_data = {col:'' for col in columns}

        sql_columns = ', '.join(columns)
        cursor.execute("SELECT %s FROM %s WHERE (filename='%s') AND (mo='%s')" % (sql_columns, self.table_name, self.root_file, mo))
        if cursor.rowcount:
            row = cursor.fetchall()[0]
            for col in columns:
                root_data[col] = row[columns.index(col)]

        files_data = dict()
        for f in self.files:
            files_data[f] = dict()
            cursor.execute("SELECT %s FROM %s WHERE (filename='%s') AND (mo='%s')" % (sql_columns, self.table_name, f, mo))
            if cursor.rowcount:
                row = cursor.fetchall()[0]
                for col in columns:
                    files_data[f][col] = row[columns.index(col)]
            else:
                for col in columns:
                    files_data[f][col] = ''

        result = []
        for col in columns:
            root_val = root_data[col]
            base_row = [['OK', mo], ['OK', col], [self.get_status(root_val, ''), root_data[col]]]
            edit = False
            for f in self.files:
                f_val = files_data[f][col]
                base_row.append([self.get_status(root_val, f_val), f_val])
                if f_val != root_val:
                   edit = True
            if edit:
                result.append(base_row)

        return result


class CompareTemplate(Compare):

    def get_mo_list(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM Template_%s LIMIT 0' % self.table_name)
        columns = [desc[0] for desc in cursor.description]
        columns.remove('filename')
        sql_columns = ', '.join(columns)
        files = self.files + [self.root_file, ]

        sql_files = []
        for f in files:
            sql_files.append("SELECT %s FROM Template_%s WHERE filename='%s'" % (sql_columns, self.table_name, f))

        union_sql = ' UNION '.join(sql_files)
        intersect_sql = ' INTERSECT '.join(sql_files)

        sql = 'SELECT DISTINCT %s FROM (%s EXCEPT %s) as MO_Table' % (self.sql_id, union_sql, intersect_sql)
        cursor.execute(sql)

        return [r[0] for r in cursor]

    def get_data_by_mo(self, mo):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM Template_%s LIMIT 0' % self.table_name)
        columns = [desc[0] for desc in cursor.description]
        columns.remove('filename')
        root_data = {col:'' for col in columns}

        sql_columns = ', '.join(columns)
        cursor.execute("SELECT %s FROM Template_%s WHERE (filename='%s') AND (%s='%s')" % (sql_columns, self.table_name, self.root_file, self.sql_id, mo))
        if cursor.rowcount:
            row = cursor.fetchall()[0]
            for col in columns:
                root_data[col] = row[columns.index(col)]

        files_data = dict()
        for f in self.files:
            files_data[f] = dict()
            cursor.execute("SELECT %s FROM Template_%s WHERE (filename='%s') AND (%s='%s')" % (sql_columns, self.table_name, f, self.sql_id, mo))
            if cursor.rowcount:
                row = cursor.fetchall()[0]
                for col in columns:
                    files_data[f][col] = row[columns.index(col)]
            else:
                for col in columns:
                    files_data[f][col] = ''

        result = []
        for col in columns:
            root_val = root_data[col]
            base_row = [['OK', mo], ['OK', col], [self.get_status(root_val, ''), root_data[col]]]
            edit = False
            for f in self.files:
                f_val = files_data[f][col]
                base_row.append([self.get_status(root_val, f_val), f_val])
                if f_val != root_val:
                   edit = True
            if edit:
                result.append(base_row)

        return result


class CompareQuery(Compare):

    def __init__(self, table_name, root_file, files, cells):
        self.cells = cells
        super(CompareQuery, self).__init__(table_name, root_file, files)

    def convert_cells(self, filename, cells):
        if self.file_type == 'WCDMA':
            return WCDMA().convert_form_cells(cells, filename)
        if self.file_type == 'LTE':
            return LTE().convert_form_cells(cells, filename)

    def get_mo_list(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM Template_%s LIMIT 0' % self.table_name)
        columns = [desc[0] for desc in cursor.description]
        columns.remove('filename')
        sql_columns = ', '.join(columns)
        files = self.files + [self.root_file, ]

        sql_files = []
        for f in files:
            cells = self.convert_cells(f, self.cells)
            sql_files.append("SELECT %s FROM Template_%s WHERE (filename='%s') AND (%s in (%s))" % (sql_columns, self.table_name, f, self.sql_id, ','.join(cells)))

        union_sql = ' UNION '.join(sql_files)
        intersect_sql = ' INTERSECT '.join(sql_files)
        sql = 'SELECT DISTINCT %s FROM (%s EXCEPT %s) as MO_Table' % (self.sql_id, union_sql, intersect_sql)
        cursor.execute(sql)

        return [r[0] for r in cursor]

    def get_data_by_mo(self, mo):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM Template_%s LIMIT 0' % self.table_name)
        columns = [desc[0] for desc in cursor.description]
        columns.remove('filename')
        root_data = {col:'' for col in columns}

        sql_columns = ', '.join(columns)
        cursor.execute("SELECT %s FROM Template_%s WHERE (filename='%s') AND (%s='%s')" % (sql_columns, self.table_name, self.root_file, self.sql_id, mo))
        if cursor.rowcount:
            row = cursor.fetchall()[0]
            for col in columns:
                root_data[col] = row[columns.index(col)]

        files_data = dict()
        for f in self.files:
            files_data[f] = dict()
            cursor.execute(
                "SELECT %s FROM Template_%s WHERE (filename='%s') AND (%s='%s')" % (
                    sql_columns,
                    self.table_name,
                    f,
                    self.sql_id,
                    mo)
            )

            if cursor.rowcount:
                row = cursor.fetchall()[0]
                for col in columns:
                    files_data[f][col] = row[columns.index(col)]
            else:
                for col in columns:
                    files_data[f][col] = ''

        result = []
        for col in columns:
            root_val = root_data[col]
            base_row = [['OK', mo], ['OK', col], [self.get_status(root_val, ''), root_data[col]]]
            edit = False
            for f in self.files:
                f_val = files_data[f][col]
                base_row.append([self.get_status(root_val, f_val), f_val])
                if f_val != root_val:
                   edit = True
            if edit:
                result.append(base_row)

        return result


class CompareNeighbor(Compare):

    def get_mo_list(self):
        cursor = self.conn.cursor()
        files = self.files + [self.root_file, ]
        sql_files = []

        for f in files:
            sql_files.append("SELECT Source, Target, Priority, frequencyRelationType, RelationType, nodeRelationType, node_RelationType, loadSharingCandidate FROM threegneighbors WHERE filename='%s'" % (f, ))

        union_sql = ' UNION '.join(sql_files)
        intersect_sql = ' INTERSECT '.join(sql_files)
        sql = 'SELECT DISTINCT Source FROM (%s EXCEPT %s) as MO_Table' % (union_sql, intersect_sql)
        cursor.execute(sql)

        return [r[0] for r in cursor]

    def get_data_by_mo(self, mo):
        cursor = self.conn.cursor()
        columns = ['Source', 'Target', 'Priority', 'frequencyRelationType', 'RelationType', 'nodeRelationType', 'node_RelationType', 'loadSharingCandidate']
        sql_columns = ', '.join(columns)
        root_data = {col: '' for col in columns}

        cursor.execute("SELECT %s FROM threegneighbors WHERE (filename='%s') AND (Source='%s')" % (sql_columns, self.root_file, mo))
        if cursor.rowcount:
            row = cursor.fetchall()[0]
            for col in columns:
                root_data[col] = row[columns.index(col)]

        files_data = dict()
        for f in self.files:
            files_data[f] = dict()
            cursor.execute("SELECT %s FROM threegneighbors WHERE (filename='%s') AND (Source='%s')" % (sql_columns, f, mo))
            if cursor.rowcount:
                row = cursor.fetchall()[0]
                for col in columns:
                    files_data[f][col] = row[columns.index(col)]
            else:
                for col in columns:
                    files_data[f][col] = ''

        result = []
        for col in columns:
            root_val = root_data[col]
            base_row = [['OK', mo], ['OK', col], [self.get_status(root_val, ''), root_data[col]]]
            edit = False
            for f in self.files:
                f_val = files_data[f][col]
                base_row.append([self.get_status(root_val, f_val), f_val])
                if f_val != root_val:
                   edit = True
            if edit:
                result.append(base_row)

        return result


class CompareCNA(Compare):

    def __init__(self, root_file, files):
        super(CompareCNA, self).__init__(None, root_file, files)

    def get_mo_list(self):
        cursor = self.conn.cursor()
        files = self.files + [self.root_file, ]
        sql_files = []

        cursor.execute('SELECT * FROM _%s LIMIT 0' % self.root_file)
        columns = [desc[0] for desc in cursor.description]
        sql_columns = ', '.join(columns)

        for f in files:
            sql_files.append("SELECT %s FROM _%s" % (sql_columns, f))

        union_sql = ' UNION '.join(sql_files)
        intersect_sql = ' INTERSECT '.join(sql_files)
        sql = 'SELECT DISTINCT _CELL FROM (%s EXCEPT %s) as MO_Table' % (union_sql, intersect_sql)
        cursor.execute(sql)
        return [r[0] for r in cursor]


    def get_data_by_mo(self, mo):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM _%s LIMIT 0' % self.root_file)
        columns = [desc[0] for desc in cursor.description]
        sql_columns = ', '.join(columns)
        root_data = {col: '' for col in columns}

        cursor.execute("SELECT %s FROM _%s WHERE (_Cell='%s')" % (sql_columns, self.root_file, mo))
        if cursor.rowcount:
            row = cursor.fetchall()[0]
            for col in columns:
                root_data[col] = row[columns.index(col)]

        files_data = dict()
        for f in self.files:
            files_data[f] = dict()
            cursor.execute("SELECT %s FROM _%s WHERE (_Cell='%s')" % (sql_columns, f, mo))
            if cursor.rowcount:
                row = cursor.fetchall()[0]
                for col in columns:
                    files_data[f][col] = row[columns.index(col)]
            else:
                for col in columns:
                    files_data[f][col] = ''

        result = []
        for col in columns:
            root_val = root_data[col]
            base_row = [['OK', mo], ['OK', col], [self.get_status(root_val, ''), root_data[col]]]
            edit = False
            for f in self.files:
                f_val = files_data[f][col]
                base_row.append([self.get_status(root_val, f_val), f_val])
                if f_val != root_val:
                   edit = True
            if edit:
                result.append(base_row)

        return result


class CompareMeasurement(Compare):

    def __init__(self, root_file, files):
        super(CompareMeasurement, self).__init__(None, root_file, files)

    def get_exists_columns(self):
        cursor = self.conn.cursor()
        columns = []
        result = []
        for f in self.files:
            cursor.execute('SELECT * FROM %s LIMIT 0' % f)
            columns.extend([desc[0] for desc in cursor.description])
        cursor.execute('SELECT * FROM %s LIMIT 0' % self.root_file)
        for desc in cursor.description:
            col = desc[0]
            if col in columns:
                result.append(col)
        return result

    def get_mo_list(self):
        cursor = self.conn.cursor()
        files = self.files + [self.root_file, ]
        sql_files = []

        columns = ['"%s"' % col for col in self.get_exists_columns()]
        sql_columns = ', '.join(columns)

        for f in files:
            sql_files.append("SELECT %s FROM %s" % (sql_columns, f))

        union_sql = ' UNION '.join(sql_files)
        intersect_sql = ' INTERSECT '.join(sql_files)
        sql = 'SELECT DISTINCT "CellName" FROM (%s EXCEPT %s) as MO_Table' % (union_sql, intersect_sql)
        cursor.execute(sql)

        return [r[0] for r in cursor]


    def get_data_by_mo(self, mo):
        cursor = self.conn.cursor()
        columns = ['"%s"' % col for col in self.get_exists_columns()]
        sql_columns = ', '.join(columns)
        columns = self.get_exists_columns()
        root_data = {col: '' for col in columns}
        cursor.execute('SELECT ' + sql_columns + ' FROM ' + self.root_file + ' WHERE ("CellName"=%s)', (mo, ))
        if cursor.rowcount:
            row = cursor.fetchall()[0]
            for col in columns:
                root_data[col] = row[columns.index(col)]

        files_data = dict()
        for f in self.files:
            files_data[f] = dict()
            cursor.execute('SELECT ' + sql_columns + ' FROM ' + f + ' WHERE ("CellName"=%s)', (mo, ))
            if cursor.rowcount:
                row = cursor.fetchall()[0]
                for col in columns:
                    files_data[f][col] = row[columns.index(col)]
            else:
                for col in columns:
                    files_data[f][col] = ''

        result = []
        for col in columns:
            root_val = root_data[col]
            base_row = [['OK', mo], ['OK', col], [self.get_status(root_val, ''), root_data[col]]]
            edit = False
            for f in self.files:
                f_val = files_data[f][col]
                base_row.append([self.get_status(root_val, f_val), f_val])
                if f_val != root_val:
                   edit = True
            if edit:
                result.append(base_row)

        return result


class CompareLicense(Compare):
    def get_columns(self):
        columns = ['SITE', 'ID', 'Parameter', self.root_file]
        columns.extend([f for f in self.files])
        return columns

    def get_mo_list(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM %s LIMIT 0' % self.table_name)
        columns = [desc[0] for desc in cursor.description]
        columns.remove('filename')
        sql_columns = ', '.join(columns)
        files = self.files + [self.root_file, ]

        sql_files = []
        for f in files:
            sql_files.append("SELECT %s FROM %s WHERE (filename='%s')" % (sql_columns, self.table_name, f))

        union_sql = ' UNION '.join(sql_files)
        intersect_sql = ' INTERSECT '.join(sql_files)
        sql = 'SELECT DISTINCT SITE, ID FROM (%s EXCEPT %s) as MO_Table' % ( union_sql, intersect_sql)
        cursor.execute(sql)
        return [[r[0], r[1]] for r in cursor]

    def get_data_by_mo(self, mo):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM %s LIMIT 0' % self.table_name)
        columns = [desc[0] for desc in cursor.description]
        columns.remove('filename')
        sql_columns = ', '.join(columns)
        root_data = {col: '' for col in columns}
        cursor.execute("SELECT %s FROM %s WHERE (filename='%s') AND (ID='%s') AND (SITE='%s')" % (sql_columns, self.table_name, self.root_file, mo[1], mo[0] ))
        if cursor.rowcount:
            row = cursor.fetchall()[0]
            for col in columns:
                root_data[col] = row[columns.index(col)]

        files_data = dict()
        for f in self.files:
            files_data[f] = dict()
            cursor.execute("SELECT %s FROM %s WHERE (filename='%s') AND (ID='%s') AND (SITE='%s')" % (sql_columns, self.table_name, f, mo[1], mo[0]))
            if cursor.rowcount:
                row = cursor.fetchall()[0]
                for col in columns:
                    files_data[f][col] = row[columns.index(col)]
            else:
                for col in columns:
                    files_data[f][col] = ''

        result = []
        for col in columns:
            root_val = root_data[col]
            base_row = [['OK', mo[0]], ['OK', mo[1]], ['OK', col], [self.get_status(root_val, ''), root_data[col]]]
            edit = False
            for f in self.files:
                f_val = files_data[f][col]
                base_row.append([self.get_status(root_val, f_val), f_val])
                if f_val != root_val:
                   edit = True
            if edit:
                result.append(base_row)

        return result


class CompareHardWare(Compare):

    def __init__(self, root_file, files):
        super(CompareHardWare, self).__init__(None, root_file, files)

    def get_columns(self):
        columns = ['managed_element', 'serial_number', 'unit_position', 'Parameter', self.root_file]
        columns.extend([f for f in self.files])
        return columns

    def get_mo_list(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM Hardware LIMIT 0')
        columns = [desc[0] for desc in cursor.description]
        columns.remove('filename')
        sql_columns = ', '.join(columns)
        files = self.files + [self.root_file, ]

        sql_files = []
        for f in files:
            sql_files.append("SELECT %s FROM Hardware WHERE (filename='%s')" % (sql_columns, f))

        union_sql = ' UNION '.join(sql_files)
        intersect_sql = ' INTERSECT '.join(sql_files)
        sql = 'SELECT DISTINCT managed_element, serial_number, unit_position FROM (%s EXCEPT %s) as MO_Table' % ( union_sql, intersect_sql)
        cursor.execute(sql)
        return [[r[0], r[1], r[2]] for r in cursor]

    def get_data_by_mo(self, mo):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM Hardware LIMIT 0')
        columns = [desc[0] for desc in cursor.description]
        columns.remove('filename')
        sql_columns = ', '.join(columns)
        root_data = {col: '' for col in columns}
        cursor.execute("SELECT %s FROM Hardware WHERE (filename='%s') AND (managed_element='%s') AND (serial_number='%s') AND (unit_position='%s')" % (sql_columns, self.root_file, mo[0], mo[1], mo[2]))
        if cursor.rowcount:
            row = cursor.fetchall()[0]
            for col in columns:
                root_data[col] = row[columns.index(col)]

        files_data = dict()
        for f in self.files:
            files_data[f] = dict()
            cursor.execute("SELECT %s FROM Hardware WHERE (filename='%s') AND (managed_element='%s') AND (serial_number='%s') AND (unit_position='%s')" % (sql_columns, f, mo[0], mo[1], mo[2]))
            if cursor.rowcount:
                row = cursor.fetchall()[0]
                for col in columns:
                    files_data[f][col] = row[columns.index(col)]
            else:
                for col in columns:
                    files_data[f][col] = ''

        result = []
        for col in columns:
            root_val = root_data[col]
            base_row = [['OK', mo[0]], ['OK', mo[1]], ['OK', mo[2]], ['OK', col], [self.get_status(root_val, ''), root_data[col]]]
            edit = False
            for f in self.files:
                f_val = files_data[f][col]
                base_row.append([self.get_status(root_val, f_val), f_val])
                if f_val != root_val:
                   edit = True
            if edit:
                result.append(base_row)
        return result