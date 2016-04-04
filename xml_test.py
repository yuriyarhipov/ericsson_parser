import re
from lxml import etree
import psycopg2
import pandas as pd

filename = '/home/arhipov/Downloads/elance/UTRAN_TOPOLOGY2.xml'
#filename = '/home/arhipov/work/xml/text.xml'


class Table:

    def __init__(self, project_id,  host, db, login, password):
        self.conn = psycopg2.connect(
            'host = %s dbname = %s user = %s password = %s' % (host, db, login, password)
        )

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

    def write_table(self, table_name, data):
        df = pd.DataFrame(data)
        columns = list(df.columns.values)
        cursor = self.conn.cursor()

        self.create_table(table_name, columns)
        df.to_csv('/home/arhipov/temp.csv', sep='\t', index=False, header=False)
        with open('/home/arhipov/temp.csv') as f:
            cursor.copy_from(f, table_name, columns=columns)
        self.conn.commit()


class WcdmaXML:
    data = dict()
    xml_mask = re.compile('\{.*\}')

    def __init__(self, filename):
        self.filename = filename
        self.parse_file()

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
        i = 0
        context = etree.iterparse(
            self.filename,
            events=('end',),
            tag='{genericNrm.xsd}VsDataContainer')
        for event, elem in context:
            i += 1

        context = etree.iterparse(
            self.filename,
            events=('end',),
            tag='{genericNrm.xsd}VsDataContainer')
        for event, elem in context:
            self.parse_node(elem)


wx = WcdmaXML(filename)
for table_name, data in wx.data.iteritems():
    table = Table(1, 'localhost', 'xml2', 'postgres', '1297536')
    table.write_table(table_name, data)
