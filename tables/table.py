import psycopg2
import xlsxwriter
import tempfile
import re

from zipfile import ZipFile
from os.path import join
from collections import OrderedDict

from django.conf import settings

from files.hw import HardWare


def get_mo(mo):
    result = dict()
    pattern = '(\w*)=(\w*-*\w*)'
    k = re.compile(pattern)
    for k, v in re.findall(k, mo):
        result[k] = v
    return result


class Table(object):

    active_file = None

    def __init__(self, table_name, filename):
        self.conn = psycopg2.connect(
            'host = %s dbname = %s user = %s password = %s' % (
                settings.DATABASES['default']['HOST'],
                settings.DATABASES['default']['NAME'],
                settings.DATABASES['default']['USER'],
                settings.DATABASES['default']['PASSWORD']))
        self.table_name = table_name
        self.filename = filename
        self.columns = self.get_columns()

    def sort_columns(self, columns):
        result = []
        fixed_columns = [
            'MO',
            'Version',
            'Vendor',
            'Element',
            'Element1',
            'Element2',
            'UtranCell',
            'SectorCarrier',
            'Carrier'
        ]
        exists_columns = [column.lower() for column in columns]
        for column in fixed_columns:
            if column.lower() in exists_columns:
                result.append(column)
                exists_columns.remove(column.lower())
        exists_columns.sort()
        result.extend(exists_columns)
        return result

    def get_columns(self):
        if self.table_name in ['map_intrafreq', 'map_interfreq', 'map_gsmirat', 'hw_summary']:
            return

        if self.table_name == '3girat':
            return ['Source', 'Target_IRAT', 'Priority', 'frequencyRelationType', 'RelationType', 'qOffset1sn']
        elif self.table_name == 'neighbors_co-sc':
            return ['Source', 'Primary_SC_Source', 'Site_Source', 'Target', 'Site_Target', 'Primary_SC_target', 'NEIGHBOR_CO_SC', 'SAME_SITE']
        elif self.table_name == 'neighbors_two_ways':
            return ['Source', 'Site_Source', 'Target', 'Site_Target', 'NEIGHBOR_MUTUAL_RELATION', 'SAME_SITE']

        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM %s LIMIT 0' % (self.table_name, ))
        columns = [desc[0] for desc in cursor.description]
        return self.sort_columns(columns)

    def get_data(self):
        if self.table_name == '3girat':
            return ThreeGIRAT(self.filename).data

        elif self.table_name == 'map_intrafreq':
            data = ThreeGMapIntraFreq(self.filename)
            self.columns = data.columns
            return data.data

        elif self.table_name == 'map_interfreq':
            data = ThreeGMapInterFreq(self.filename)
            self.columns = data.columns
            return data.data

        elif self.table_name == 'map_interfreq':
            data = ThreeGMapInterFreq(self.filename)
            self.columns = data.columns
            return data.data

        elif self.table_name == 'map_gsmirat':
            data = ThreeGMapGSMirat(self.filename)
            self.columns = data.columns
            return data.data

        elif self.table_name == 'neighbors_co-sc':
            return ThreeGNeighborsCOSC(self.filename).data

        elif self.table_name == 'neighbors_two_ways':
            return ThreeGNeighborsTwoWays(self.filename).data

        elif self.table_name == 'hw_summary':
            self.columns, data = HardWare().get_summary(self.filename)
            return data


        cursor = self.conn.cursor()
        sql_columns = ','.join(self.columns)
        cursor.execute("SELECT %s FROM %s WHERE lower(filename)='%s'" % (sql_columns, self.table_name, self.filename.lower()))
        data = cursor.fetchall()
        return data


class ThreeGNeighbors:
    data = []

    def __init__(self, filename):
        self.filename = filename
        self.conn = psycopg2.connect(
            'host = %s dbname = %s user = %s password = %s' % (
                settings.DATABASES['default']['HOST'],
                settings.DATABASES['default']['NAME'],
                settings.DATABASES['default']['USER'],
                settings.DATABASES['default']['PASSWORD']))
        self.cursor = self.conn.cursor()
        self.main()

    def main(self):
        self.cursor.execute("SELECT DISTINCT Source, Target, Priority, frequencyRelationType, RelationType, nodeRelationType, node_RelationType, loadSharingCandidate FROM ThreeGNeighbors WHERE (filename=%s) ORDER BY Source, Target, Priority;", (self.filename, ))
        self.data = self.cursor.fetchall()


class Topology:
    data = []
    iublink = dict()


    def __init__(self, filename):
        self.filename = filename
        self.conn = psycopg2.connect(
            'host = %s dbname = %s user = %s password = %s' % (
                settings.DATABASES['default']['HOST'],
                settings.DATABASES['default']['NAME'],
                settings.DATABASES['default']['USER'],
                settings.DATABASES['default']['PASSWORD']))
        self.cursor = self.conn.cursor()
        self.main()

    def main(self):
        self.data = []
        self.cursor.execute("SELECT DISTINCT RNC, Site, UtranCell, CID, Sector, SectorCarrier, SectorAntena, Carrier, iublink FROM Topology WHERE (Topology.filename=%s)", (self.filename, ))
        for row in self.cursor:
            self.data.append([
                row[0],
                row[1],
                row[2],
                row[3],
                row[4],
                row[5],
                row[6],
                row[7],
                row[8]
            ])
        self.data.sort()

    def get_tree(self):
        utc = dict()
        self.cursor.execute("SELECT DISTINCT MO, adjacentCell, frequencyRelationType FROM UtranRelation WHERE (UtranRelation.filename=%s);", (self.filename, ))
        for row in self.cursor:
            u_mo = get_mo(row[0])
            u_ac = get_mo(row[1])
            source = u_mo.get('UtranCell', '')
            target = u_ac.get('UtranCell', '')
            f_rt = row[2]
            if target and source:
                if source not in utc:
                    utc[source] = []
                if target not in utc[source]:
                    utc[source].append([target, int(f_rt)])
        self.data.sort()
        result = OrderedDict()
        for r in self.data:
            rnc = r[0]
            site = r[1]
            sector = r[4]
            utrancell = r[2]

            if rnc not in result:
                result[rnc] = OrderedDict()

            if site not in result[rnc]:
                result[rnc][site] = OrderedDict()

            if sector not in result[rnc][site]:
                result[rnc][site][sector] = OrderedDict()

            if utrancell not in result[rnc][site][sector] and  (utrancell in utc):
                result[rnc][site][sector][utrancell] = utc[utrancell]

        return result


class ThreeGNeighborsTwoWays:
    data = []
    untrancell = dict()

    def __init__(self, filename):
        self.filename = filename
        self.conn = psycopg2.connect(
            'host = %s dbname = %s user = %s password = %s' % (
                settings.DATABASES['default']['HOST'],
                settings.DATABASES['default']['NAME'],
                settings.DATABASES['default']['USER'],
                settings.DATABASES['default']['PASSWORD']))
        self.cursor = self.conn.cursor()
        self.topology = dict()
        for r in Topology(filename).data:
            self.topology[r[2]] = r[1]
        self.main()

    def main(self):
        self.data = []
        self.cursor.execute("SELECT DISTINCT MO, adjacentCell FROM UtranRelation WHERE (UtranRelation.filename=%s);", (self.filename, ))
        result = []
        check = dict()
        for row in self.cursor:
            u_mo = get_mo(row[0])
            u_ac = get_mo(row[1])
            source = u_mo.get('UtranCell', '')
            target = u_ac.get('UtranCell', '')
            site_source = self.topology.get(source, '')
            site_target = self.topology.get(target, '')

            if source and target:
                result.append([source, site_source, target, site_target])
                if source not in check:
                    check[source] = set()
                check[source].add(target)

        for r in result:
            same_site = '0' if r[1] == r[3] else '1'

            target = r[2]
            source = r[0]

            is_missing = 'Missing'
            if check.get(target) and (source in check.get(target)):
                is_missing ='Defined'
            self.data.append([r[0], r[1], r[2], r[3], is_missing, same_site])

        self.data.sort()


class ThreeGNeighborsCOSC:
    data = []
    untrancell = dict()

    def __init__(self, filename):
        self.filename = filename
        self.conn = psycopg2.connect(
            'host = %s dbname = %s user = %s password = %s' % (
                settings.DATABASES['default']['HOST'],
                settings.DATABASES['default']['NAME'],
                settings.DATABASES['default']['USER'],
                settings.DATABASES['default']['PASSWORD']))
        self.cursor = self.conn.cursor()
        self.topology = dict()
        for r in Topology(filename).data:
            self.topology[r[2]] = r[1]
        self.cursor.execute("SELECT mo, primaryScramblingCode FROM UtranCell WHERE (UtranCell.filename=%s);", (self.filename, ))
        for row in self.cursor:
            u_mo = get_mo(row[0])
            self.untrancell[u_mo.get('UtranCell', '')] = row[1]
        self.main()

    def main(self):
        self.data = []
        self.cursor.execute("SELECT DISTINCT MO, adjacentCell FROM UtranRelation WHERE (UtranRelation.filename=%s);", (self.filename, ))
        for row in self.cursor:
            u_mo = get_mo(row[0])
            u_ac = get_mo(row[1])
            source = u_mo.get('UtranCell', '')
            target = u_ac.get('UtranCell', '')
            primary_sc_source = self.untrancell.get(source, 0)
            site_source = self.topology.get(source, '')
            site_target = self.topology.get(target, '')
            same_site = '0' if site_target == site_source else '1'
            primary_sc_target = self.untrancell.get(target, 0)
            n_co_sc = '1' if int(primary_sc_source) == int(primary_sc_target) else '0'
            if source and target:
                self.data.append([source, primary_sc_source, site_source, target, site_target, primary_sc_target, n_co_sc, same_site])

        self.data.sort()


class ThreeGMapGSMirat:

    data = []
    columns = []
    max_priority = 31

    def __init__(self, filename):
        self.filename = filename
        self.main()

    def get_columns(self):
        columns = ['Cell', ]
        for i in range(1, self.max_priority+1):
            columns.append('NEIGHBOR_%s' % i)

        columns.append('Total_Neighbors')
        columns.append('Free_Slots')
        columns.append('List_Full')
        return columns

    def get_stat(self, row):
        total = 0
        for cell in row:
            if cell != '':
                total = total + len(cell.split('\n'))

        free = 0
        list_full = 0
        for cell in row:
            if cell == '':
                free = free + 1
        if free == 0:
            list_full = 1
        return str(total), str(free), str(list_full)

    def get_row(self, t_data, source, neighbor, priority):
        row = []

        if source in t_data:
            r = []
            for i in range(0, self.max_priority):
                if i == priority - 1:
                    if t_data[source][i] == '':
                        r.append(neighbor)
                    else:
                        r.append('%s \n %s' % (t_data[source][i], neighbor))
                else:
                    r.append(t_data[source][i])
            row = r
        else:
            for i in range(self.max_priority):
                row.append(neighbor if i == priority - 1 else '')
        return row

    def main(self):
        self.max_priority = 31
        self.data = []
        t_data = dict()
        for r in ThreeGIRAT(self.filename).data:
            self.data.append([r[0], r[1], r[2], ])

        self.columns = self.get_columns()
        for row in self.data:
            source = row[0]
            neighbor = row[1]
            priority = int(row[2])
            r = self.get_row(t_data, source, neighbor, priority)
            t_data[source] = r

        result = []
        for key, row in t_data.iteritems():
            total, free, list_full = self.get_stat(row)
            row = row + [total, free, list_full]
            row.insert(0, key)
            result.append(row)
        result.sort()
        self.data = result


class ThreeGMapInterFreq:

    data = []
    columns = []
    max_priority = 31

    def __init__(self, filename):
        self.filename = filename
        self.main()

    def get_columns(self):
        columns = ['Cell', ]
        for i in range(1, self.max_priority+1):
            columns.append('INTER_NEIGHBOR_%s' % i)

        columns.append('Total_Neighbors')
        columns.append('Free_Slots')
        columns.append('List_Full')
        return columns

    def get_stat(self, row):
        total = 0
        for cell in row:
            if cell != '':
                total = total + len(cell.split('<br>'))

        free = 0
        list_full = 0
        for cell in row:
            if cell == '':
                free = free + 1
        if free == 0:
            list_full = 1
        return str(total), str(free), str(list_full)

    def get_row(self, t_data, source, neighbor, priority):
        row = []

        if source in t_data:
            r = []
            for i in range(0, self.max_priority):
                if i == priority - 1:
                    if t_data[source][i] == '':
                        r.append(neighbor)
                    else:
                        r.append('%s <br> %s' % (t_data[source][i], neighbor))
                else:
                    r.append(t_data[source][i])
            row = r
        else:
            for i in range(self.max_priority):
                row.append(neighbor if i == priority - 1 else '')
        return row

    def main(self):
        self.max_priority = 31
        self.data = []
        t_data = dict()
        for r in ThreeGNeighbors(self.filename).data:
            if int(r[3]) == 1:
                self.data.append([r[0], r[1], r[2], ])

        self.columns = self.get_columns()
        for row in self.data:
            source = row[0]
            neighbor = row[1]
            priority = int(row[2])
            r = self.get_row(t_data, source, neighbor, priority)
            t_data[source] = r

        result = []
        for key, row in t_data.iteritems():
            total, free, list_full = self.get_stat(row)
            row = row + [total, free, list_full]
            row.insert(0, key)
            result.append(row)
        result.sort()
        self.data = result


class ThreeGMapIntraFreq:

    data = []
    columns = []
    max_priority = 31

    def __init__(self, filename):
        self.filename = filename
        self.main()

    def get_columns(self):
        columns = ['Cell', ]
        for i in range(1, self.max_priority+1):
            columns.append('INTRA_NEIGHBOR_%s' % i)

        columns.append('Total_Neighbors')
        columns.append('Free_Slots')
        columns.append('List_Full')
        return columns

    def get_stat(self, row):
        total = 0
        for cell in row:
            if cell != '':
                total = total + len(cell.split('<br>'))

        free = 0
        list_full = 0
        for cell in row:
            if cell == '':
                free = free + 1
        if free == 0:
            list_full = 1
        return str(total), str(free), str(list_full)

    def get_row(self, t_data, source, neighbor, priority):
        row = []

        if source in t_data:
            r = []
            for i in range(0, self.max_priority):
                if i == priority - 1:
                    if t_data[source][i] == '':
                        r.append(neighbor)
                    else:
                        r.append('%s <br> %s' % (t_data[source][i], neighbor))
                else:
                    r.append(t_data[source][i])
            row = r
        else:
            for i in range(self.max_priority):
                row.append(neighbor if i == priority - 1 else '')
        return row

    def main(self):
        self.max_priority = 31
        self.data = []
        t_data = dict()
        for r in ThreeGNeighbors(self.filename).data:
            if int(r[3]) == 0:
                self.data.append([r[0], r[1], r[2], ])

        self.columns = self.get_columns()
        for row in self.data:
            source = row[0]
            neighbor = row[1]
            priority = int(row[2])
            r = self.get_row(t_data, source, neighbor, priority)
            t_data[source] = r

        result = []
        for key, row in t_data.iteritems():
            total, free, list_full = self.get_stat(row)
            row = row + [total, free, list_full]
            row.insert(0, key)
            result.append(row)
        result.sort()
        self.data = result


class ThreeGIRAT:
    data = []

    def __init__(self, filename):
        self.filename = filename
        self.conn = psycopg2.connect(
            'host = %s dbname = %s user = %s password = %s' % (
                settings.DATABASES['default']['HOST'],
                settings.DATABASES['default']['NAME'],
                settings.DATABASES['default']['USER'],
                settings.DATABASES['default']['PASSWORD']))
        self.cursor = self.conn.cursor()
        self.main()

    def main(self):
        self.data = []
        self.cursor.execute("SELECT DISTINCT MO, SelectionPriority, mobilityRelationType, qOffset1sn FROM GSMRelation WHERE (GSMRelation.filename=%s);", (self.filename, ))
        for row in self.cursor:
            g_mo = get_mo(row[0])
            source = g_mo.get('UtranCell', '')
            target_irat = g_mo.get('GsmRelation', '')
            priority = int(row[1])
            frequency_rt = row[2]
            relation_type = 'HO_AND_CELL_RESEL' if int(row[2]) == 0 else 'HANDOVER_ONLY'
            q_offset_1sn = row[3]
            if source and target_irat:
                self.data.append([source, target_irat, priority, frequency_rt, relation_type, q_offset_1sn])

        self.data.sort()

def get_excel(table_name, columns, data):
    static_path = settings.STATICFILES_DIRS[0]
    archive_filename = join(static_path, table_name +'.zip')
    excel_filename = join(tempfile.mkdtemp(), table_name + '.xlsx')
    workbook = xlsxwriter.Workbook(excel_filename, {'constant_memory': True})
    worksheet = workbook.add_worksheet(table_name)
    i = 0
    for column in columns:
        worksheet.write(0, i, column)
        i += 1
    j = 1
    for r in data[:65535]:
        i = 0
        for cell in r:
            worksheet.write(j, i, cell)
            i += 1
        j += 1

    workbook.close()
    zip = ZipFile(archive_filename, 'w')
    zip.write(excel_filename, arcname=table_name + '.xlsx')
    zip.close()
    return table_name +'.zip'