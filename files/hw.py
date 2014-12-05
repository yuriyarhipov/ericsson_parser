import psycopg2
import re

from operator import itemgetter
from lxml import etree
from os.path import basename

from django.conf import settings

from files.models import Files


class HardWare(object):

    def __init__(self, filename=''):
        self.path = filename
        self.filename = basename(filename)
        self.conn = psycopg2.connect(
            'host = %s dbname = %s user = %s password = %s' % (
                settings.DATABASES['default']['HOST'],
                settings.DATABASES['default']['NAME'],
                settings.DATABASES['default']['USER'],
                settings.DATABASES['default']['PASSWORD']))

    def get_summary(self, filename):
        cursor = self.conn.cursor()
        elements = dict()
        cursor.execute('''
            SELECT
                filename,
                managed_element,
                managed_element_type,
                inventory_unit_type,
                productname,
                COUNT(productname)
            FROM
                Hardware
            WHERE
            filename=%s
            GROUP BY productname, filename, managed_element_type, managed_element, inventory_unit_type
            ORDER BY managed_element
        ''', (filename, ))

        product_names = set()
        for row in cursor:
            product_names.add(row[4])
            if row[1] not in elements:
                elements[row[1]] = dict()
                elements[row[1]]['filename'] = row[0]
                elements[row[1]]['managed_element_type'] = row[2]
                elements[row[1]]['inventory_unit_type'] = row[3]
                elements[row[1]]['productname'] = dict()
                elements[row[1]]['productname'][row[4]] = row[5]
            else:
                elements[row[1]]['productname'][row[4]] = row[5]

        columns = ['Filename', 'Site', 'Type', 'CE_Boards']
        product_names = list(product_names)
        product_names.sort()
        columns.extend(product_names)

        data = []
        for site, values in elements.iteritems():
            row = [values.get('filename'),
                   site,
                   values.get('managed_element_type'),
                   values.get('inventory_unit_type'),
                   ]
            product_names_values = [values['productname'].get(pn) for pn in product_names]
            row.extend(product_names_values)
            data.append(row)

        data = sorted(data, key=itemgetter(1))

        return columns, data


    def get_files(self):
        files = []
        cursor = self.conn.cursor()
        cursor.execute('SELECT DISTINCT filename FROM HardWare;')
        for row in cursor:
            files.append(row[0])
        files.sort()
        return files

    def get_attr(self, attr_name, unit):
        path = './/{http://www.3gpp.org/ftp/specs/archive/32_series/32.695#inventoryNrm}%s' % attr_name
        return unit.find(path).text

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS HardWare(
          filename TEXT,
          managed_element TEXT,
          managed_element_type TEXT,
          user_label TEXT,
          inventory_unit TEXT,
          inventory_unit_type TEXT,
          vendor_unit_family_type TEXT,
          vendor_unit_type_number TEXT,
          vendor_name TEXT,
          serial_number TEXT,
          unit_position TEXT,
          manufacturer_data TEXT,
          productname TEXT)''')
        cursor.execute('DELETE FROM Hardware WHERE filename=%s', (self.filename, ))

    def write_data(self, row):
        cursor = self.conn.cursor()
        cursor.execute('''
        INSERT INTO Hardware (
          filename,
          managed_element,
          managed_element_type,
          user_label,
          inventory_unit,
          inventory_unit_type,
          vendor_unit_family_type,
          vendor_unit_type_number,
          vendor_name,
          serial_number,
          unit_position,
          manufacturer_data,
          productname
        ) VALUES (%s, %s,  %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', row)

    def parsing_inventory(self, unit):
        id = unit.get('id')
        inventory_unit_type = self.get_attr('inventoryUnitType', unit)
        vendor_unit_family_type = self.get_attr('vendorUnitFamilyType', unit)
        vendor_unit_type_number = self.get_attr('vendorUnitTypeNumber', unit)
        vendor_name = self.get_attr('vendorName', unit)
        serial_number = self.get_attr('serialNumber', unit)
        unit_position = self.get_attr('unitPosition', unit)
        manufacturer_data = self.get_attr('manufacturerData', unit)

        return id, inventory_unit_type, vendor_unit_family_type, vendor_unit_type_number, vendor_name, serial_number, unit_position, manufacturer_data

    def parse_managed_element(self, node):
        managed_element = node.get('id')
        attr = node.find('{http://www.3gpp.org/ftp/specs/archive/32_series/32.625#genericNrm}attributes')
        managed_element_type = attr.find('{http://www.3gpp.org/ftp/specs/archive/32_series/32.625#genericNrm}managedElementType').text
        user_label = attr.find('{http://www.3gpp.org/ftp/specs/archive/32_series/32.625#genericNrm}userLabel').text

        for unit in node.iterfind('.//{http://www.3gpp.org/ftp/specs/archive/32_series/32.695#inventoryNrm}InventoryUnit'):
            inventory_unit, inventory_unit_type, vendor_unit_family_type, vendor_unit_type_number, vendor_name, serial_number, unit_position, manufacturer_data = self.parsing_inventory(unit)
            product_name = self.get_values(manufacturer_data).get('ProductName', '')
            self.write_data([self.filename, managed_element, managed_element_type, user_label, inventory_unit, inventory_unit_type, vendor_unit_family_type, vendor_unit_type_number, vendor_name, serial_number, unit_position, manufacturer_data, product_name])

    def parse_data(self, project, description, vendor, file_type, network, task, current, interval_per_file):
        self.create_table()
        tree = etree.parse(self.path)
        root = tree.getroot()
        nodes = root.findall('.//{http://www.3gpp.org/ftp/specs/archive/32_series/32.625#genericNrm}ManagedElement')
        count = len(nodes)
        interval = float(interval_per_file)/float(count)
        for node in nodes:
            self.parse_managed_element(node)
            current = float(current) + float(interval)
            task.update_state(state="PROGRESS", meta={"current": int(current), "total": 99})
        self.conn.commit()
        Files.objects.filter(filename=self.filename, project=project).delete()
        Files.objects.create(
                filename=self.filename,
                file_type=file_type,
                project=project,
                tables='',
                description=description,
                vendor=vendor,
                network=network)

    def get_values(self, data):
        result = dict()
        pattern = '(\w*)=(\w*-*\w*)'
        k = re.compile(pattern)
        for k, v in re.findall(k, data):
            result[k] = v
        return result
