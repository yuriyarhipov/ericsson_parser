import psycopg2
import xlsxwriter
import tempfile
import re
import json

from zipfile import ZipFile
from os.path import join
from collections import OrderedDict

from django.conf import settings

from files.hw import HardWare
from files.models import Files, CNATemplate


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
        self.sql_filename = ["'%s'" % f.lower() for f in self.filename.split(',')]
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
            'Carrier',
            'Cell',
            'BSC',
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
        source_file = Files.objects.filter(filename=self.filename).first()
        if source_file.network == 'GSM':
            columns = ['%s' % col for col in CNATemplate.objects.filter(table_name=self.table_name).first().columns.split(',')]
            return columns
        if self.table_name in ['map_intrafreq', 'map_interfreq', 'map_gsmirat', 'hw_summary']:
            return

        if self.table_name == '3girat':
            return ['Source', 'Target_IRAT', 'Priority', 'frequencyRelationType', 'RelationType', 'qOffset1sn']
        elif self.table_name == 'neighbors_co-sc':
            return ['Source', 'Primary_SC_Source', 'Site_Source', 'Target', 'Site_Target', 'Primary_SC_target', 'NEIGHBOR_CO_SC', 'SAME_SITE']
        elif self.table_name == 'neighbors_two_ways':
            return ['Source', 'Site_Source', 'Target', 'Site_Target', 'NEIGHBOR_MUTUAL_RELATION', 'SAME_SITE']
        elif self.table_name == 'BrightcommsRNDDate':
            columns = BRI(self.filename).columns
            return columns


        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM "%s" LIMIT 0' % (self.table_name.lower(), ))
        columns = ['%s' % desc[0] for desc in cursor.description]
        return self.sort_columns(columns)

    def get_data(self):
        if self.table_name == '3girat':
            return ThreeGIRAT(self.filename).data

        elif self.table_name == 'BrightcommsRNDDate':
            return BRI(self.filename).data

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
        sql_columns = ','.join(['"%s"' % col.lower() for col in self.columns])
        order_columns = sql_columns
        if self.table_name == 'BrightcommsRNDDate':
            order_columns = 'SITENAME, SECTORID, SITEID, CID'

        cursor.execute('SELECT DISTINCT %s FROM "%s" WHERE lower(filename) IN (%s) ORDER BY %s' % (sql_columns, self.table_name.lower(), ','.join(self.sql_filename), order_columns))
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

            if utrancell not in result[rnc][site][sector] and (utrancell in utc):
                result[rnc][site][sector][utrancell] = utc[utrancell]

        return result

    def create_tree_view(self):
        tree = self.get_tree()
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM TOPOLOGY_TREEVIEW WHERE filename='%s'" % (self.filename,))
        for rnc in tree:
            rnc_children = []
            for site in tree[rnc]:
                site_children = []
                for sector in tree[rnc][site]:
                    sector_children = []
                    for utrancell in tree[rnc][site][sector]:
                        sector_children.append({'id': utrancell, 'label': utrancell, 'children': []})
                    site_children.append({'id': sector, 'label': sector, 'children': sector_children})
                rnc_children.append({'id': site, 'label': site, 'children': site_children})
            cursor.execute("INSERT INTO TOPOLOGY_TREEVIEW (FILENAME, TREEVIEW, ROOT) VALUES ('%s', '%s', '%s')" % (self.filename, json.dumps(rnc_children), rnc))
        self.conn.commit()



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


class BRI:
    data = []

    def __init__(self, filename):
        self.filename = filename
        self.conn = psycopg2.connect(
            'host = %s dbname = %s user = %s password = %s' % (
                settings.DATABASES['default']['HOST'],
                settings.DATABASES['default']['NAME'],
                settings.DATABASES['default']['USER'],
                settings.DATABASES['default']['PASSWORD']))
        self.intra = []
        self.inter = []
        self.columns = ['NETWORK', 'SITENAME', 'SECTORID', 'SITEID', 'CID', 'Physical_Sector', 'Logical_Sector', 'Logical_Carrier', 'IPADDRESS', 'SITESTATUS', 'BSCRNC', 'LONGITUDE_ORIGIN', 'LONGITUDE', 'LATITUDE', 'AZIMUTH', 'ANTHEIGHT', 'MECHTILT', 'ELECTTILT', 'MCC', 'MNC', 'LAC', 'SAC', 'RAC', 'BCCH', 'CHANNELDL', 'CHANNELDUL', 'FREQBAND', 'BSIC', 'SC', 'PCI', 'PCPICHPOWER', 'ANTTYPE', 'ANTBW', 'ANTENNAHEIGHT', 'VENDOR', 'MODEL', 'INFO1', 'INFO2', 'INFO3', 'INFO4', 'INFO5', 'INFO6', 'INFO7', 'INFO8', 'INFO9', 'INFO10', 'TCHARFCN', 'HOP', 'HSN', 'MAIO']
        self.get_intra()
        self.get_inter()
        self.main()

    def get_inter(self):
        data = dict()
        columns_count = 0
        for row in ThreeGMapInterFreq(filename=self.filename).data:
            r = []
            for val in row[1: -3]:
                if val != '':
                    val = val.split('\n')
                    r.extend(val)
            if columns_count < len(r):
                columns_count = len(r)
            data[row[0]] = r
        self.inter = data
        self.inter_columns = ['INTER_NEIGHBOR_%s' % i for i in range(columns_count)]
        self.columns.extend(self.inter_columns)


    def get_intra(self):
        data = dict()
        columns_count = 0
        for row in ThreeGMapIntraFreq(filename=self.filename).data:
            r = []
            for val in row[1: -3]:
                if val != '':
                    val = val.split('\n')
                    r.extend(val)
            if columns_count < len(r):
                columns_count = len(r)
            data[row[0]] = r
        self.intra = data
        self.intra_columns = ['INTRA_NEIGHBOR_%s' % i for i in range(columns_count)]
        self.columns.extend(self.intra_columns)

    def get_longitude(self, value):
        result = (float(value) / 16777216) * 360
        return "{:10.5f}".format(result)

    def get_latitude(self, value):
        result = (float(value) / 8388608) * 90
        return "{:10.5f}".format(result)


    def main(self):
        self.data = []
        cursor = self.conn.cursor()
        cursor.execute('''SELECT
            logicalname as SITENAME,
            Utrancell AS SECTORID,
            SITE AS SITEID,
            cid  AS CID,
            sector AS Physical_Sector,
            ipaddress AS IPADDRESS,
            administrativestate AS SITESTATUS,
            rnc AS BSCRNC,
            longitude AS LONGITUDE,
            latitude AS LATITUDE,
            beamdirection AS AZIMUTH,
            lac AS LAC,
            sac AS SAC,
            rac AS RAC,
            uarfcndl AS CHANNELDL,
            uarfcnul AS CHANNELDUL,
            band AS	FREQBAND,
            primaryscramblingcode AS SC,
            primarycpichpower AS PCPICHPOWER,
            vendorname AS VENDOR,
            productname AS MODEL
            FROM RND_WCDMA WHERE (logicalname != '') AND (filename=%s);''', (self.filename, ))

        for row in cursor:
            network = '3G'
            sitename = row[0]
            sector_id = row[1]
            site_id = row[2]
            c_id = row[3]
            physical_sector = row[4]
            logical_sector = ''
            logical_carrier = ''
            ipaddress = row[5]
            site_status = row[6]
            bsc_rnc = row[7]
            origin_longitude = row[8]
            longitude = self.get_longitude(row[8])
            latitude = self.get_latitude(row[9])
            azimuth = row[10]
            ant_height = ''
            mechtilt = ''
            electtilt = ''
            mcc = ''
            mnc = ''
            lac = row[11]
            sac = row[12]
            rac = row[13]
            bcch = ''
            channel_dl = row[14]
            channel_dul = row[15]
            freq_band = row[16]
            bsic = ''
            sc = row[17]
            pci = ''
            pcpich_power = row[18]
            ant_type = ''
            ant_bw = ''
            antenna_height = ''
            vendor = row[19]
            model = row[20]
            info01 = ''
            info02 = ''
            info03 = ''
            info04 = ''
            info05 = ''
            info06 = ''
            info07 = ''
            info08 = ''
            info09 = ''
            info10 = ''
            tcharfcn = ''
            hop = ''
            hsn = ''
            maio = ''
            r = [
                network,
                sitename,
                sector_id,
                site_id,
                c_id,
                physical_sector,
                logical_sector,
                logical_carrier,
                ipaddress,
                site_status,
                bsc_rnc,
                origin_longitude,
                longitude,
                latitude,
                azimuth,
                ant_height,
                mechtilt,
                electtilt,
                mcc,
                mnc,
                lac,
                sac,
                rac,
                bcch,
                channel_dl,
                channel_dul,
                freq_band,
                bsic,
                sc,
                pci,
                pcpich_power,
                ant_type,
                ant_bw,
                antenna_height,
                vendor,
                model,
                info01,
                info02,
                info03,
                info04,
                info05,
                info06,
                info07,
                info08,
                info09,
                info10,
                tcharfcn,
                hop,
                hsn,
                maio
            ]
            add_intra = self.intra.get(row[1], [])
            if len(add_intra) < len(self.intra_columns):
                add_intra.extend(['' for i in range(len(self.intra_columns)-len(add_intra))])
            r.extend(add_intra)
            add_inter = self.inter.get(row[1], [])
            if len(add_inter) < len(self.inter_columns):
                add_inter.extend(['' for i in range(len(self.inter_columns)-len(add_inter))])
            r.extend(add_inter)
            self.data.append(r)


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