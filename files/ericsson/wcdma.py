from lxml import etree
from os.path import basename
import datetime
import re


class WcdmaXML:
    data = dict()
    xml_mask = re.compile('\{.*\}')
    columns = []
    lower_columns = []

    def __init__(self, filename, project, file_id=None, current_percent=None, available_percent=None, set_percent=None):
        self.filename = filename
        self.available_percent = available_percent
        self.current_percent = current_percent
        self.project_id = project.id
        self.file_id = file_id
        self.set_percent = set_percent
        self.parse_file()

    def check_column(self, column):
        if (column not in self.columns) and (column.lower() not in self.lower_columns):
            self.columns.append(column)
            self.lower_columns.append(column.lower())
        elif (column not in self.columns) and (column.lower() in self.lower_columns):
            i = self.lower_columns.index(column.lower())             
            column = self.columns[i]
        return column    


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
                    field_name = self.check_column(field_name)
                    row[field_name] = field_value
        return row

    def parse_mo(self, mo):
        result = dict()
        pattern = '(\w*)=(\w*-*\w*)'
        k = re.compile(pattern)
        if mo:        
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
                row[self.check_column(at)] = mo.get(at, '')

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
                row['RNCTarget'] = ac.get('MeContext')
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
                self.set_percent(self.file_id, self.current_percent + int(float(self.available_percent) * float(current_percent) / 100))
            self.parse_node(elem)
