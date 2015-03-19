import re
import psycopg2

from lxml import etree
from os.path import basename

from files.models import Files
from tables.table import Topology
from files.excel import ExcelFile


class Tables:
    def __init__(self, data, tables, network, filename):
        self.data = data
        self.network = network
        self.tables = tables
        self.filename = filename
        self.file_type = 'WCDMA' if 'UtranCell' in data.keys() else 'LTE'
        self.conn = psycopg2.connect(
            'host = localhost dbname = xml2 user = postgres password = 1297536'
        )
        self.cursor = self.conn.cursor()

    def check_table(self, table_name, columns):
        exists_columns = set([c.lower() for c in self.tables[table_name]])
        missed_columns = exists_columns - columns
        for column in missed_columns:
            self.cursor.execute('ALTER TABLE %s ADD COLUMN %s text;' % (
                table_name,
                column))
        self.conn.commit()
        self.add_indexes(table_name, missed_columns)

    def load_data(self):
        for table_name, source_columns in self.tables.iteritems():
            columns = []
            filtred_columns = []
            for col in source_columns:
                if col.lower() not in filtred_columns:
                    columns.append(col)
                    filtred_columns.append(col.lower())

            values = []
            for field in self.data[table_name]:
                row = dict()
                for column in columns:
                    row[column] = field.get(column, '')
                values.append(row)
            values_name = ['%(' + column + ')s' for column in columns]
            insert = 'INSERT INTO %s (%s) VALUES (%s)' % (
                table_name,
                ','.join(columns),
                ','.join(values_name))
            self.cursor.executemany(insert, values)

    def add_indexes(self, table_name, columns):
        for column in columns:
            if column.lower() in ['utrancell', 'element1', 'element2']:
                self.cursor.execute('CREATE INDEX ON %s (%s)' % (table_name, column))
        self.conn.commit()

    def create_table(self, table_name):
        columns = []
        for column in self.tables[table_name]:
            if column.lower() not in columns:
                columns.append(column.lower())

        sql_columns = ['%s TEXT' % field for field in columns]
        self.cursor.execute('CREATE TABLE IF NOT EXISTS %s (%s);' % (table_name, ', '.join(sql_columns)))
        self.conn.commit()
        self.add_indexes(table_name, self.tables[table_name])

    def table(self, table_name):
        self.cursor.execute(
            'SELECT column_name FROM information_schema.columns WHERE table_catalog = %s AND table_name=%s;',
            ('xml2', table_name.lower()))
        column_names = set(row[0].lower() for row in self.cursor)
        if column_names:
            self.check_table(table_name, column_names)
        else:
            self.create_table(table_name)

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

    def create_tables(self):
        for table_name in self.tables:
            self.table(table_name)
        self.load_data()
        self.conn.commit()
        self.cursor.close()
        self.conn.close()
        del self.tables
        del self.data

    def create_additional_tables(self):
        self.topology()
        self.topology_lte()
        self.rnd_wcdma()
        self.rnd_lte()
        self.fourgneighbors()
        self.threegneighborss()
        self.create_topology_tree_view()
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

    def __init__(self, filename, network, task):
        self.filename = filename
        self.network = network
        self.conn = psycopg2.connect(
            'host = localhost dbname = xml2 user = postgres password = 1297536'
        )
        self.task = task
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
            version=self.version)
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
        self.write_to_database(table_name, fields)

    def save_rows(self):
        tables = dict()
        data = dict()

        for row in self.rows:

            table_name = row.get('table')
            fields = row.get('fields')

            if table_name and (table_name not in data):
                data[table_name] = []
                tables[table_name] = set()

            columns = tables[table_name]
            data[table_name].append(fields)
            if columns:
                tables[table_name] = columns | set(fields.keys())
            else:
                tables[table_name] = set(fields.keys())

        tables = Tables(data, tables, self.network, basename(self.filename))
        tables.create_tables()
        del(tables)
        del(data)

    def write_to_database(self, table, fields):
        self.db_tables.add(table)
        self.rows.append(dict(table=table, fields=fields))
        if len(self.rows) > 10000:
            self.save_rows()
            self.rows = []
            self.task.update_state(state="PROGRESS", meta={"current": int(self.current)})

    def main(self):
        context = etree.iterparse(
            self.filename,
            events=('end',),
            tag='{genericNrm.xsd}attributes')

        for event, elem in context:
            self.parse_elem(elem)
            elem.clear()
            self.current += (float(1)/float(5000))
            if self.current > 97:
                self.current = float(97)

        tables = Tables(dict(), {t_name: [] for t_name in self.db_tables}, self.network, basename(self.filename))
        tables.create_additional_tables()
        self.task.update_state(state="PROGRESS", meta={"current": int(100)})
        self.conn.commit()


class Xml(object):
    def save_xml(self, filename, project, description, vendor, file_type, network, task):
        xml = Processing(filename, network, task)
        Files.objects.filter(filename=basename(xml.filename), project=project).delete()
        Files.objects.create(
            filename=basename(xml.filename),
            file_type=file_type,
            project=project,
            tables=','.join(list(xml.db_tables)),
            description=description,
            vendor=vendor,
            network=network)
        ExcelFile(project, basename(filename))
