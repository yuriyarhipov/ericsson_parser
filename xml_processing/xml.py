import re
import psycopg2

from lxml import etree
from os.path import basename
import pandas as pd

from files.models import Files, FileTasks
from tables.table import Topology
from files.excel import ExcelFile
from files.tasks import create_table


class Diff:

    def __init__(self, project_id,  host, db, login, password):
        self.project_id = project_id
        self.conn = psycopg2.connect(
            'host = %s dbname = %s user = %s password = %s' % (host, db, login, password)
        )
        cursor = self.conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS ChangeLog (
            id SERIAL,
            project_id INT,
            mo TEXT,
            rnc TEXT,
            site TEXT,
            Utrancell TEXT,
            param_name TEXT,
            new_value TEXT,
            old_value TEXT,
            change_time DATE)''')

    def write_to_log(self, tablename, mo, param_name, new_value, old_value):
        cursor = self.conn.cursor()
        cursor.execute(
            'SELECT column_name FROM information_schema.columns WHERE table_catalog = %s AND table_name=%s;',
            ('xml2', tablename.lower()))
        column_names = [row[0].lower() for row in cursor]
        sql_columns = []
        if 'utrancell' in column_names:
            sql_columns.append('utrancell')
        if 'element1' in column_names:
            sql_columns.append('element1')
        if 'element2' in column_names:
            sql_columns.append('element2')
        cursor.execute('''SELECT %s FROM %s WHERE (mo='%s') AND (project_id='%s') AND (status='draft')''' % (','.join(sql_columns), tablename, mo, self.project_id))
        utrancell = ''
        rnc = ''
        site = ''
        if cursor.rowcount == 1:
            row = cursor.fetchone()
            if 'utrancell' in sql_columns:
                utrancell = row[0]
            else:
                utrancell = ''
            if 'element1' in sql_columns:
                rnc = row[sql_columns.index('element1')]
            else:
                rnc = ''
            if 'element2' in sql_columns:
                site = row[sql_columns.index('element2')]
            else:
                site = ''
        cursor.execute('''INSERT INTO Changelog (project_id, mo, rnc, site, Utrancell, param_name, new_value, old_value, change_time)
            VALUES
            ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', NOW())
        ''' % (self.project_id, mo, rnc, site, utrancell, param_name, new_value, old_value))
        cursor.close()

    def check_parameter(self, tablename, param):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT DRAFT.mo, '%s' as param_name, DRAFT.%s as new_value, READY.%s as old_value FROM (
            	SELECT mo, %s from %s where status='draft'
                    EXCEPT
            	SELECT mo, %s from %s where status='ready') as DRAFT
            INNER JOIN (
            	SELECT mo, %s from %s where status='ready'
            		EXCEPT
            	SELECT mo, %s from %s where status='draft'
            	) AS READY
            ON (DRAFT.mo=READY.mo)
        ''' % (param, param, param, param, tablename, param, tablename, param, tablename, param, tablename))
        for row in cursor.fetchall():
            print tablename, row[2], row[3]
            self.write_to_log(tablename, row[0], param, row[2], row[3])

    def diff(self, tablename):
        cursor = self.conn.cursor()
        cursor.execute(
            'SELECT column_name FROM information_schema.columns WHERE table_catalog = %s AND table_name=%s;',
            ('xml2', tablename.lower()))
        column_names = [row[0].lower() for row in cursor]

        column_names.remove('status')
        column_names.remove('filename')
        column_names.remove('project_id')
        column_names.remove('mo')

        for param in column_names:
            self.check_parameter(tablename, param)
        cursor.execute('''DELETE FROM %s
            WHERE (project_id='%s')
                AND (status = 'ready')
        ''' % (tablename, self.project_id))
        cursor.execute('''Update %s set status = 'ready' WHERE (project_id='%s')''' % (tablename, self.project_id))
        self.conn.commit()

class Table:

    def __init__(self, project_id,  host, db, login, password):
        self.conn = psycopg2.connect(
            'host = %s dbname = %s user = %s password = %s' % (host, db, login, password)
        )
        cursor = self.conn.cursor()

    def check_table(self, table_name, exist_column_names, columns):
        cursor = self.conn.cursor()
        new_columns = [c.lower() for c in columns]
        missed_columns = set(new_columns) - set(exist_column_names)
        for column in missed_columns:
            cursor.execute('ALTER TABLE %s ADD COLUMN %s text;' % (
                table_name,
                column))
        self.conn.commit()
        self.add_indexes(table_name, missed_columns)

    def add_indexes(self, table_name, columns):
        cursor = self.conn.cursor()
        for column in columns:
            if column.lower() in ['utrancell', 'element1', 'element2']:
                cursor.execute('CREATE INDEX ON %s (%s)' % (table_name, column))
        self.conn.commit()

    def create_table(self, table_name, columns):
        cursor = self.conn.cursor()
        cursor.execute(
            'SELECT column_name FROM information_schema.columns WHERE table_catalog = %s AND table_name=%s;',
            ('xml2', table_name.lower()))
        exist_column_names = [row[0].lower() for row in cursor]

        if exist_column_names:
            self.check_table(table_name, exist_column_names, columns)
        else:
            sql_columns = ['%s TEXT' % field.lower() for field in columns]
            cursor.execute('CREATE TABLE IF NOT EXISTS %s (%s);' % (table_name, ', '.join(sql_columns)))
            self.conn.commit()
            self.add_indexes(table_name, columns)
                    
    def write_table(self, tablename, data):
        df = pd.DataFrame(data)
        columns = list(df.columns.values)
        cursor = self.conn.cursor()
        self.create_table(tablename, columns)
        df.to_csv('/tmp/temp.csv', sep='\t', index=False, header=False)
        with open('/tmp/temp.csv') as f:
            if tablename == 'SECTOREQM':
                print columns
                print df
            cursor.copy_from(f, tablename, columns=columns)
        self.conn.commit()


class WcdmaXML:
    data = dict()
    xml_mask = re.compile('\{.*\}')

    def __init__(self, host, db, login, password, filename, project, file_id=None, current_percent=None, available_percent=None):
        self.filename = filename
        self.available_percent = available_percent
        self.current_percent = current_percent
        self.project_id = project.id
        self.file_id = file_id
        self.conn = psycopg2.connect(
            'host = %s dbname = %s user = %s password = %s' % (host, db, login, password)
        )
        self.parse_file()

    def set_percent(self, value):
        cursor = self.conn.cursor()
        cursor.execute('UPDATE files_uploadedfiles SET status=%s WHERE id=%s;', (value, self.file_id))
        cursor.close()
        self.conn.commit()

    def get_mo(self, node):
        result = []
        parent = node.getparent()
        if parent is not None:
            result = self.get_mo(parent)
        value = node.get('id')
        name = None
        if value is not None:
            tag = self.xml_mask.sub('', node.tag)
            if tag != 'VsDataContainer':
                name = tag
            if name and value:
                result.append('%s=%s' % (name, value))
        return result

    def get_fields(self, node):
        row = dict()
        for child in node.iter():
            if child.text:
                field_name = self.xml_mask.sub('', child.tag)
                field_value = child.text.strip()
                if field_value:
                    row[field_name] = field_value
        return row

    def parse_mo(self, mo):
        result = dict()
        pattern = '(\w*)=(\w*-*\w*)'
        k = re.compile(pattern)
        for k, v in re.findall(k, mo):
            result[k] = v
        return result

    def parse_node(self, node):
        row = dict()
        table_name = node.find('.//{genericNrm.xsd}vsDataType').text[6:]
        id = node.get('id')
        row[table_name] = id
        attrs = node.find('..{utranNrm.xsd}attributes[1]')
        if attrs is None:
            attrs = node.find('..{genericNrm}attributes[1]')
        if (attrs is not None):
            row.update(self.get_fields(attrs))

        row.update(self.get_fields(node))
        mo = self.get_mo(node)
        row['MO'] = ','.join(mo)
        row['project_id'] = self.project_id
        row['filename'] = basename(self.filename)
        row['status'] = 'draft'
        mo = self.parse_mo(row['MO'])

        additional_fields = [
            'UtranCell', 'IubLink', 'EUtranCellFDD', 'SectorEquipmentFunction',
            'AntennaUnitGroup', 'GsmRelation', 'IubLink', 'Iub', 'IurLink',
            'UeRabType', 'UeRc', 'Carrier', 'TermPointToMme']

        for at in additional_fields:
            if (at in mo) and (at not in row):
                row[at] = mo.get(at, '')

        if 'Sector' in mo:
            if 'Element' not in row:
                row['Element'] = mo.get('MeContext', '')
            row['Sector'] = mo.get('Sector')

        if 'RbsLocalCell' in mo:
            if 'Element' not in row:
                row['Element'] = mo.get('MeContext', '')
            row['SectorCarrier'] = mo.get('RbsLocalCell')

        site = mo.get('MeContext')
        sub = mo.get('SubNetwork')

        if site and sub:
            if site == sub:
                row['Element1'] = site
            else:
                row['Element2'] = site

        if table_name == 'UtranRelation':
            if 'adjacentCell' in row:
                ac = self.parse_mo(row.get('adjacentCell'))
                row['Neighbor'] = ac.get('UtranCell')
        elif table_name == 'IubLink':
            if 'iubLinkNodeBFunction' in row:
                ib = self.parse_mo(row.get('iubLinkNodeBFunction'))
                row['Element2'] = ib.get('MeContext')

        elif table_name == 'SectorEquipmentFunction':
            rb = self.parse_mo(row.get('reservedBy'))
            rf_branch_ref = self.parse_mo(row.get('rfBranchRef'))
            row['EUtranCellFDD'] = rb.get('EUtranCellFDD')
            row['AntennaUnitGroup'] = rf_branch_ref.get('AntennaUnitGroup')

        elif table_name == 'EUtranCellRelation':
            ac = self.parse_mo(row.get('adjacentCell'))
            row['Target'] = ac.get('EUtranCellFDD')
            if 'EUtranCellFDD' not in row:
                row['EUtranCellFDD'] = row['Target']

        elif table_name == 'CoverageRelation':
            tc = self.parse_mo(row.get('utranCellRef'))
            row['Target_coverage'] = tc.get('UtranCell', '')

        if table_name in self.data:
            self.data[table_name].append(row)
        else:
            self.data[table_name] = [row, ]

    def parse_file(self):
        count_countainers = 0.0
        context = etree.iterparse(
            self.filename,
            events=('end',),
            tag='{genericNrm.xsd}VsDataContainer')
        for event, elem in context:
            count_countainers += 1

        context = etree.iterparse(
            self.filename,
            events=('end',),
            tag='{genericNrm.xsd}VsDataContainer')
        i = 0.0
        current_percent = 0
        for event, elem in context:
            i += 1
            percent = int(i / count_countainers * 100)
            if current_percent < percent:
                current_percent = percent
                self.set_percent(self.current_percent + int(float(self.available_percent) * float(current_percent) / 100))
            self.parse_node(elem)

class Tables:

    def __init__(self):
        self.conn = psycopg2.connect(
            'host = localhost dbname = xml2 user = postgres password = 1297536'
        )
        self.cursor = self.conn.cursor()

    def write_data(self, table, rows, network, filename):
        cursor = self.conn.cursor()
        columns = set()
        for row in rows:
            for col in row.keys():
                columns.add(col)
        columns = list(columns)
        self.create_table(table, columns)

        sql_values = []
        for row in rows:
            sql_row = []
            for col in columns:
                sql_row.append("'%s'" % row.get(col, 'None'))
            sql_values.append("(%s)" % ','.join(sql_row))

        insert = 'INSERT INTO %s (%s) VALUES %s' % (
            table,
            ','.join(columns),
            ','.join(sql_values))
        try:
            cursor.execute(insert)
        except:
            raise
        cursor.close()
        self.conn.commit()

    def check_table(self, table_name, exist_column_names, columns):
        cursor = self.conn.cursor()
        new_columns = [c.lower() for c in columns]
        missed_columns = set(new_columns) - set(exist_column_names)
        for column in missed_columns:
            cursor.execute('ALTER TABLE %s ADD COLUMN %s text;' % (
                table_name,
                column))
        self.conn.commit()
        self.add_indexes(table_name, missed_columns)

    def add_indexes(self, table_name, columns):
        cursor = self.conn.cursor()
        for column in columns:
            if column.lower() in ['utrancell', 'element1', 'element2']:
                cursor.execute('CREATE INDEX ON %s (%s)' % (table_name, column))
        self.conn.commit()

    def create_table(self, table_name, columns):
        cursor = self.conn.cursor()
        cursor.execute(
            'SELECT column_name FROM information_schema.columns WHERE table_catalog = %s AND table_name=%s;',
            ('xml2', table_name.lower()))
        exist_column_names = [row[0].lower() for row in cursor]

        if exist_column_names:
            self.check_table(table_name, exist_column_names, columns)
        else:
            sql_columns = ['%s TEXT' % field.lower() for field in columns]
            cursor.execute('CREATE TABLE IF NOT EXISTS %s (%s);' % (table_name, ', '.join(sql_columns)))
            self.conn.commit()
            self.add_indexes(table_name, columns)

    def fourgneighbors(self):
        if self.network != 'LTE':
            return

        self.cursor.execute('DROP TABLE IF EXISTS FourGNeighbors;')
        self.cursor.execute('''
            SELECT DISTINCT
                filename,
                EUtrancellFDD Source,
                target,
                cellIndividualOffsetEUtran,
                coverageIndicator,
                createdBy,
                includeInSystemInformation,
                isHoAllowed,
                isRemoveAllowed,
                lastModification,
                loadBalancing,
                qOffsetCellEUtran
            INTO FourGNeighbors
            FROM EUtranCellRelation
            ;''')

    def threegneighborss(self):
        if self.network == 'LTE':
            return
        self.cursor.execute('DROP TABLE IF EXISTS ThreeGNeighbors;')
        self.cursor.execute('''
          SELECT DISTINCT
            Utrancell as Source,
            Neighbor as Target,
            SelectionPriority as Priority,
            frequencyRelationType,
            CASE
              WHEN frequencyRelationType = '1' THEN 'INTER_FREQ'
              ELSE 'INTRA_FREQ'
            END
            as RelationType,
            nodeRelationType,
            CASE
              WHEN frequencyRelationType = '1' THEN 'INTER_RNC'
              ELSE 'INTRA_RNC'
            END
            as node_RelationType,
            loadSharingCandidate,
            filename
            INTO ThreeGNeighbors
            FROM
              UtranRelation
            WHERE
              (Neighbor IS NOT NUll) AND
              (Utrancell IS NOT NULL);
        ''')

    def universal_3g3g_neighbors(self):
        if self.network == 'LTE':
            return
        self.cursor.execute('DROP TABLE IF EXISTS Universal3g3gNeighbors;')
        self.cursor.execute('''
          SELECT DISTINCT
            Utrancell as Source,
            Neighbor as Target,
            filename
            INTO Universal3g3gNeighbors
            FROM
              UtranRelation
            WHERE
              (Neighbor IS NOT NUll) AND
              (Utrancell IS NOT NULL);
        ''')

    def topology(self):
        if self.network == 'LTE':
            return
        self.cursor.execute('DROP TABLE IF EXISTS TOPOLOGY CASCADE;')
        self.cursor.execute('''
            SELECT DISTINCT
              UtranCell.Element1 RNC,
              RBSLocalCell.Element2 SITE,
              UtranCell.UtranCell,
              Utrancell.CID,
              substring(RBSLocalCell.SectorCarrier from 2 for 1) Sector,
              RBSLocalCell.SectorCarrier SectorCarrier,
              substring(RBSLocalCell.SectorCarrier from 2 for 1) SectorAntena,
              substring(RBSLocalCell.SectorCarrier from 4 for 1) Carrier,
              IubLink.Iublink,
              UtranCell.filename
            INTO TOPOLOGY
            FROM RBSLocalCell
              INNER JOIN UtranCell ON (RBSLocalCell.LocalCellid = UtranCell.CID and RBSLocalCell.filename = UtranCell.filename)
              LEFT JOIN IubLink ON  (RBSLocalCell.Element2 = IubLink.Element2 AND RBSLocalCell.filename = IubLink.filename)
            ;''')

    def create_topology_tree_view(self):
        if self.network == 'LTE':
            return
        cursor = self.conn.cursor()
        self.cursor.execute('CREATE TABLE IF NOT EXISTS TOPOLOGY_TREEVIEW (FILENAME TEXT, ROOT TEXT, TREEVIEW JSON);')
        self.conn.commit()
        cursor.execute('SELECT DISTINCT filename FROM TOPOLOGY')
        for row in cursor:
            Topology(row[0]).create_tree_view()

    def topology_lte(self):
        if self.network != 'LTE':
            return
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS sectorequipmentfunction
                    (
                      reservedby text,
                      eutrancellfdd text,
                      confoutputpower text,
                      mixedmoderadio text,
                      administrativestate text,
                      userlabel text,
                      element2 text,
                      sectorequipmentfunction text,
                      fqband text,
                      mo text,
                      filename text,
                      antennaunitgroup text,
                      version text,
                      rfbranchref text,
                      sectorpower text,
                      vendorname text
                )
        '''
        )

        #self.cursor.execute('DROP TABLE IF EXISTS TOPOLOGY_LTE;')
        self.cursor.execute('''
            CREATE OR REPLACE VIEW TOPOLOGY_LTE AS
            SELECT
                EUtrancellFDD.filename,
                EUtrancellFDD.Element2 Site,
                EUtrancellFDD.EUtrancellFDD EUtrancell,
                CellId CID,
                physicalLayerCellIdGroup PHYSICAL_CID,
                SectorEquipmentFunction.SectorEquipmentFunction,
                SectorEquipmentFunction.AntennaUnitGroup,
                TPTM1.mmeName mmeName_1,
                TPTM2.mmeName mmeName_2
            FROM EUtrancellFDD
                LEFT JOIN SectorEquipmentFunction ON ((SectorEquipmentFunction.EUtrancellFDD=EUtrancellFDD.EUtrancellFDD) AND ((EUtrancellFDD.filename=SectorEquipmentFunction.filename)))
                LEFT JOIN TermPointToMme TPTM1 ON ((TPTM1.Element2=EUtrancellFDD.Element2) AND (EUtrancellFDD.filename=TPTM1.filename) AND (TPTM1.TermPointToMme='1'))
                LEFT JOIN TermPointToMme TPTM2 ON ((TPTM2.Element2=EUtrancellFDD.Element2) AND (EUtrancellFDD.filename=TPTM2.filename) AND (TPTM2.TermPointToMme='2'))
            ;''')

    def rnd_wcdma(self):
        if self.network == 'LTE':
            return
        self.cursor.execute('DROP VIEW IF EXISTS BrightcommsRNDDate;')
        self.cursor.execute('DROP TABLE IF EXISTS RND_WCDMA;')
        self.cursor.execute('''
            SELECT DISTINCT
                topology.filename,
                Sector.MO,
                Sector.element2 as site,
                Sector.sector,
                topology.cid,
                topology.utrancell,
                topology.carrier,
                topology.rnc,
                latitude,
                longitude,
                beamdirection,
                height,
                band,
                lathemisphere,
                geodatum,
                MEContext.ipaddress,
                MEContext.nemimversion,
                MEContext.mirrormibversion,
                MEContext.lostsynchronisation,
                ManagedElement.userdefinedstate,
                ManagedElement.vendorname,
                ManagedElement.swversion,
                ManagedElement.productname,
                ManagedElement.siteref,
                ManagedElement.logicalname,
                UtranCell.uarfcnul,
                UtranCell.uarfcndl,
                UtranCell.primaryscramblingcode,
                UtranCell.primarycpichpower,
                UtranCell.lac,
                UtranCell.rac,
                UtranCell.sac,
                UtranCell.cellreserved,
                UtranCell.administrativeState
                INTO RND_WCDMA
            FROM
                Sector
                INNER JOIN Topology ON ((Sector.element2=Topology.site) AND (Sector.sector=Topology.sector))
                INNER JOIN MEContext ON (Sector.element2=MEContext.element2)
                INNER JOIN ManagedElement ON (Sector.element2=ManagedElement.element2)
                INNER JOIN UtranCell ON ((topology.cid=UtranCell.cid))
            WHERE (Sector.filename=Topology.filename) AND
                (Sector.filename=MEContext.filename) AND
                (Sector.filename=ManagedElement.filename) AND
                (Sector.filename=UtranCell.filename)
            ;''')

    def rnd_lte(self):
        if self.network != 'LTE':
            return

        self.cursor.execute('''
            CREATE OR REPLACE VIEW RND_LTE AS
            SELECT
                DISTINCT
                EUtrancellFDD.filename,
                EUtrancellFDD.Element2 Site,
                EUtrancellFDD.EUtrancellFDD,
                SectorEquipmentFunction.SectorEquipmentFunction,
                SectorEquipmentFunction.AntennaUnitGroup,
                EUtrancellFDD.latitude,
                EUtrancellFDD.longitude,
                SectorEquipmentFunction.fqband,
                EUtrancellFDD.ulChannelBandwidth,
                EUtrancellFDD.dlChannelBandwidth,
                EUtrancellFDD.administrativestate,
                EUtrancellFDD.earfcndl,
                EUtrancellFDD.earfcnul,
                MeContext.ipaddress,
                MeContext.neMIMversion,
                MeContext.lostSynchronisation,
                ManagedElement.userDefinedState,
                ManagedElement.managedElementType,
                ManagedElement.vendorname,
                ManagedElement.swversion,
                ManagedElement.productname,
                ManagedElement.siteref,
                EUtrancellFDD.physicalLayerCellIdGroup,
                EUtrancellFDD.noOfTxAntennas,
                EUtrancellFDD.noOfRxAntennas,
                EUtrancellFDD.cellbarred,
                EUtrancellFDD.qrxlevmin,
                EUtrancellFDD.qrxlevminOffset,
                EUtrancellFDD.qQualMin,
                EUtrancellFDD.qQualMinOffset,
                EUtrancellFDD.maximumTransmissionPower,
                SectorEquipmentFunction.confOutputPower,
                SectorEquipmentFunction.sectorPower,
                AntennaSubunit.totalTilt,
                Antennaunit.mechanicalAntennaTilt
            FROM EUtrancellFDD
                LEFT JOIN SectorEquipmentFunction ON (
                    (SectorEquipmentFunction.EUtrancellFDD=EUtrancellFDD.EUtrancellFDD) AND
                    (EUtrancellFDD.filename=SectorEquipmentFunction.filename))
                INNER JOIN MeContext ON ((MeContext.Element2=EUtrancellFDD.Element2) AND
                    (EUtrancellFDD.filename=MeContext.filename))
                INNER JOIN ManagedElement ON ((ManagedElement.Element2=EUtrancellFDD.Element2) AND (EUtrancellFDD.filename=ManagedElement.filename))
                INNER JOIN AntennaSubunit ON ((AntennaSubunit.Element2=EUtrancellFDD.Element2) AND (EUtrancellFDD.filename=AntennaSubunit.filename))
                INNER JOIN Antennaunit ON ((Antennaunit.Element2=EUtrancellFDD.Element2) AND (EUtrancellFDD.filename=Antennaunit.filename))
            ;''')

    def create_additional_tables(self, network):
        self.network = network
        self.universal_3g3g_neighbors()

        #self.topology()
        #self.topology_lte()

        #self.rnd_wcdma()
        #self.rnd_lte()

        #self.fourgneighbors()

        #self.threegneighborss()
        #self.create_topology_tree_view()
        self.conn.commit()
        self.conn.close()


class Processing(object):
    rows = []
    ignored_name = []
    version = ''
    vendorName = ''
    path = re.compile('\{.*\}')
    ver = re.compile('^\D+')
    stop_list = ['ManagementNode', ]
    db_tables = set()
    current = float(1)
    data = dict()

    def __init__(self, filename, network, project, file_id=None, current_percent=None, available_percent=None, set_percent=None):
        self.filename = filename
        self.network = network
        self.project = project
        self.file_id = file_id,
        self.current_percent = current_percent, 
        self.available_percent = available_percent, 
        self.set_percent = set_percent          
        self.conn = psycopg2.connect(
            'host = localhost dbname = xml2 user = postgres password = 1297536'
        )        
        self.main()

    def parse_mo(self, mo):
        result = dict()
        pattern = '(\w*)=(\w*-*\w*)'
        k = re.compile(pattern)
        for k, v in re.findall(k, mo):
            result[k] = v
        return result

    def get_table_name(self, node):
        table_name = None
        parent = node.getparent()
        if 'VsDataContainer' in parent.tag:
            data = node.find(".//{genericNrm.xsd}vsDataType")
            if data is not None:
                table_name = data.text[6:]
        else:
            table_name = self.path.sub('', parent.tag)
        return table_name

    def get_additional_fields(self, node, table_name):
        result = dict()
        parent = node.getparent()
        if (('VsDataContainer' in parent.tag) and
           (table_name in parent.getparent().tag)):
            for n in parent.getparent():
                if 'attributes' in n.tag:
                    for attr in n:
                        field_name = self.path.sub('', attr.tag)
                        text = getattr(attr, 'text', '')
                        if text is None:
                            text = ''
                        text = text.replace('vsData', '')
                        result[field_name] = text
        return result

    def get_fields(self, node, table_name):
        result = dict(
            FileName=basename(self.filename),
            MO=', '.join(self.get_mo(node)),
            vendorName=self.vendorName,
            version=self.version,
            project_id = self.project.id)
        result.update(self.get_additional_fields(node, table_name))

        mo = self.parse_mo(result['MO'])

        if 'UtranCell' in mo:
            result['UtranCell'] = mo.get('UtranCell', '')

        if 'EUtranCellFDD' in mo:
            result['EUtranCellFDD'] = mo.get('EUtranCellFDD', '')

        if 'SectorEquipmentFunction' in mo:
            result['SectorEquipmentFunction'] = mo.get(
                'SectorEquipmentFunction',
                '')

        if 'AntennaUnitGroup' in mo:
            result['AntennaUnitGroup'] = mo.get('AntennaUnitGroup', '')

        if table_name == 'GsmRelation':
            result['GsmRelation'] = mo.get('GsmRelation', '')

        if 'IubLink' in mo:
            result['IubLink'] = mo.get('IubLink')

        if 'Iub' in mo:
            result['Iub'] = mo.get('Iub')

        if 'IurLink' in mo:
            result['IurLink'] = mo.get('IurLink')

        if 'UeRabType' in mo:
            result['UeRabType'] = mo.get('UeRabType')

        if 'UeRc' in mo:
            result['UeRc'] = mo.get('UeRc')

        if 'Carrier' in mo:
            result['Carrier'] = mo.get('Carrier')

        if 'TermPointToMme' in mo:
            result['TermPointToMme'] = mo.get('TermPointToMme')

        if 'Sector' in mo:
            if 'Element' not in result:
                result['Element'] = mo.get('MeContext', '')
            result['Sector'] = mo.get('Sector')

        if 'RbsLocalCell' in mo:
            if 'Element' not in result:
                result['Element'] = mo.get('MeContext', '')
            result['SectorCarrier'] = mo.get('RbsLocalCell')

        site = mo.get('MeContext')
        sub = mo.get('SubNetwork')

        if site and sub:
            if site == sub:
                result['Element1'] = site
            else:
                result['Element2'] = site

        for n in node.iter():
            if 'vsDataFormatVersion' in n.tag:
                result['version'] = self.ver.sub('', n.text)
                self.version = result['version']
            if n.text is None:
                n.text = ''

            parent = n.getparent()
            if (('{genericNrm.xsd}attributes' not in parent.tag) and
               ('vsdata' not in parent.tag.lower())):
                field_name = '%s_%s' % (
                    self.path.sub('', parent.tag),
                    self.path.sub('', n.tag))
            else:
                field_name = self.path.sub('', n.tag)
            text = n.text.strip().replace('vsData', '')
            if (('vsData' not in field_name) and
               (field_name not in ['attributes'])):
                if field_name in result:
                    result[field_name] = '%s %s' % (result[field_name], text)
                else:
                    result[field_name] = text

        if table_name == 'UtranRelation':
            if 'adjacentCell' in result:
                ac = self.parse_mo(result.get('adjacentCell'))
                result['Neighbor'] = ac.get('UtranCell')
        elif table_name == 'IubLink':
            if 'iubLinkNodeBFunction' in result:
                ib = self.parse_mo(result.get('iubLinkNodeBFunction'))
                result['Element2'] = ib.get('MeContext')

        elif table_name == 'SectorEquipmentFunction':
            rb = self.parse_mo(result.get('reservedBy'))
            rf_branch_ref = self.parse_mo(result.get('rfBranchRef'))
            result['EUtranCellFDD'] = rb.get('EUtranCellFDD')
            result['AntennaUnitGroup'] = rf_branch_ref.get('AntennaUnitGroup')

        elif table_name == 'EUtranCellRelation':
            ac = self.parse_mo(result.get('adjacentCell'))
            result['Target'] = ac.get('EUtranCellFDD')
            if 'EUtranCellFDD' not in result:
                result['EUtranCellFDD'] = result['Target']

        elif table_name == 'CoverageRelation':
            tc = self.parse_mo(result.get('utranCellRef'))
            result['Target_coverage'] = tc.get('UtranCell', '')
        return result

    def get_mo(self, node):
        result = []
        parent = node.getparent()
        if parent is not None:
            result = self.get_mo(parent)
        value = node.get('id')
        name = None
        if value is not None:
            tag = self.path.sub('', node.tag)
            if tag == 'VsDataContainer':
                datatype = node.find(".//{genericNrm.xsd}vsDataType")
                if datatype is not None:
                    name = datatype.text[6:]
            else:
                name = tag
            if name and value:
                result.append('%s=%s' % (name, value))
        return result

    def parse_elem(self, elem):
        table_name = self.get_table_name(elem)
        if table_name in self.stop_list:
            return
        fields = self.get_fields(elem, table_name)

        if table_name not in self.data:
            self.data[table_name] = []
        self.data[table_name].append(fields)

    def main(self):
        elem_count = float(0)
        context = etree.iterparse(
            self.filename,
            events=('end',),
            tag='{genericNrm.xsd}attributes')
        for event, elem in context:
            elem_count += 1
                
        context = etree.iterparse(
            self.filename,
            events=('end',),
            tag='{genericNrm.xsd}attributes')
        i = 0        
        for event, elem in context:
            i += 1                            
            self.set_percent(self.file_id, i / elem_count * 50)
            self.parse_elem(elem)
            elem.clear()
        tasks = []        
        table_count = float(len(self.data))
        i = float(0)
        for table_name, rows in self.data.iteritems():
            self.set_percent(self.file_id, 50 + i / table_count * 50)
            i += 1
            Tables().write_data(table_name, rows, self.network, self.filename)                    
        self.conn.commit()


class Xml(object):
    def save_xml(self, filename, project, description, vendor, file_type, network, file_id=None, current_percent=None, available_percent=None, set_percent=None):        
        xml = Processing(filename, network, project, file_id, current_percent, available_percent, set_percent)
        Files.objects.filter(filename=basename(xml.filename), project=project).delete()
        Files.objects.create(
            filename=basename(xml.filename),
            file_type=file_type,
            project=project,
            tables=','.join(list(xml.data.keys())),
            description=description,
            vendor=vendor,
            network=network)
