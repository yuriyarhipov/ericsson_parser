import psycopg2

from lxml import etree
from os.path import basename

from django.conf import settings


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

    def get_file(self, filename):
        cursor = self.conn.cursor()
        columns = [
            'filename',
            'managed_element',
            'managed_element_type',
            'user_label',
            'inventory_unit',
            'inventory_unit_type',
            'vendor_unit_family_type',
            'vendor_unit_type_number',
            'vendor_name',
            'serial_number',
            'unit_position',
            'manufacturer_data'
        ]

        cursor.execute('''
            SELECT
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
                manufacturer_data
            FROM
                Hardware
            WHERE
            filename=%s
        ''', (filename, ))
        return columns, cursor.fetchall()


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
          manufacturer_data TEXT)''')
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
          manufacturer_data
        ) VALUES (%s, %s,  %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
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
            self.write_data([self.filename, managed_element, managed_element_type, user_label, inventory_unit, inventory_unit_type, vendor_unit_family_type, vendor_unit_type_number, vendor_name, serial_number, unit_position, manufacturer_data])

    def parse_data(self, task, current, interval_per_file):
        self.create_table()
        tree = etree.parse(self.path)
        root = tree.getroot()
        nodes = root.findall('.//{http://www.3gpp.org/ftp/specs/archive/32_series/32.625#genericNrm}ManagedElement')
        count = len(nodes)
        interval = float(interval_per_file)/float(count)
        for node in nodes:
            self.parse_managed_element(node)
            current = float(current) + float(interval)
            task.update_state(state="PROGRESS", meta={"current": int(current), "total": 100})
        self.conn.commit()
