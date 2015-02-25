from lxml import etree
from collections import OrderedDict
import psycopg2
from django.conf import settings
from os.path import basename
from files.models import Files


class License(object):

    columns = ['Site', 'Fingerprint',]
    feature_attrs = set( )
    dict_data = []
    data = []

    def __init__(self, filename=''):
        self.conn = psycopg2.connect(
            'host = %s dbname = %s user = %s password = %s' % (
                settings.DATABASES['default']['HOST'],
                settings.DATABASES['default']['NAME'],
                settings.DATABASES['default']['USER'],
                settings.DATABASES['default']['PASSWORD']))
        self.cursor = self.conn.cursor()
        self.path = filename
        self.filename = basename(filename)
        self.table_name = 'license_%s' % basename(filename).replace('.xml', '')

    def parse_key(self, key, key_name):
        data = OrderedDict()
        if key_name not in self.columns:
            self.columns.append(key_name)

        data[key_name] = key.get('Id')
        for attr in key:
            tag = attr.tag
            self.feature_attrs.add(tag)
            key_column_name = '%s_%s' % (tag, key_name)

            if key_column_name not in self.columns:
                self.columns.append(key_column_name)

            if tag in ['StartDate', 'StopDate', ]:
                day = attr.get('Day')
                month = attr.get('Month')
                year = attr.get('Year')
                value = '%s.%s.%s' % (day, month, year)
            else:
                value = attr.text
            data[key_column_name] = value
        return data

    def add_feature_key(self, site, finger_print, key):
        id = key.get('Id')
        descrition = key.find('Description').text
        start_date = self.get_date(key, 'StartDate')
        stop_date = self.get_date(key, 'StopDate')
        self.cursor.execute('INSERT INTO FeatureKey (Site, Fingerprint, FileName, ID, Description, StartDate, StopDate) VALUES (%s, %s, %s, %s, %s, %s, %s)', (site, finger_print, self.filename, id, descrition, start_date, stop_date))

    def add_capacity_key(self, site, finger_print, key):
        id = key.get('Id')
        descrition = key.find('Description').text
        start_date = self.get_date(key, 'StartDate')
        stop_date = self.get_date(key, 'StopDate')
        capacity = key.find('Capacity').text
        hard_limit = key.find('HardLimit').text
        self.cursor.execute('INSERT INTO CapacityKey (Site, Fingerprint, FileName, ID, Description, StartDate, StopDate, Capacity, HardLimit) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)',
                            (site, finger_print, self.filename, id, descrition, start_date, stop_date, capacity, hard_limit))

    def parse_network(self, network):
        site = network.get('NeName')
        for lic in network:
            finger_print = lic.get('Fingerprint')
            for key in lic:
                if key.tag == 'FeatureKey':
                    self.add_feature_key(site, finger_print, key)
                elif key.tag == 'CapacityKey':
                    self.add_capacity_key(site, finger_print, key)

    def get_row(self, row):
        result = []
        for column in self.columns:
            result.append(row.get(column, ' '))
        return result

    def get_date(self, key, date_name):
        attr_date = key.find(date_name)
        day = attr_date.get('Day')
        month = attr_date.get('Month')
        year = attr_date.get('Year')
        return '%s.%s.%s' % (day, month, year)

    def parse_data(self, project, description, vendor, file_type, network, task):
        self.create_table()
        tree = etree.parse(self.path)
        root = tree.getroot()
        networks = root.findall('.//NetworkElement')
        count = len(networks)
        interval = float(100)/float(count)
        current = 0
        for attribute in networks:
            self.parse_network(attribute)
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

    def create_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS FeatureKey (
              Site TEXT,
              Fingerprint TEXT,
              FileName TEXT,
              ID TEXT,
              Description TEXT,
              StartDate TEXT,
              StopDate TEXT)''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS CapacityKey (
              Site TEXT,
              Fingerprint TEXT,
              FileName TEXT,
              ID TEXT,
              Description TEXT,
              StartDate TEXT,
              StopDate TEXT,
              Capacity TEXT,
              HardLimit TEXT)''')

        self.cursor.execute('DELETE FROM CapacityKey WHERE filename=%s', (self.filename, ))
        self.cursor.execute('DELETE FROM FeatureKey WHERE filename=%s', (self.filename, ))
        self.conn.commit()

    def get_files(self):
        files = []
        self.cursor.execute('SELECT DISTINCT filename FROM FeatureKey')
        for row in self.cursor:
            files.append(row[0])
        return files

    def get_file(self, table_name, filename):
        if table_name == 'FeatureKey':
            columns = ['SITE', 'Fingerprint', 'ID', 'Description', 'StartDate', 'StopDate']
            self.cursor.execute('SELECT SITE, Fingerprint, ID, Description, StartDate, StopDate FROM FeatureKey WHERE filename=%s ORDER BY SITE, ID', (filename, ))
        else:
            columns = ['SITE', 'Fingerprint', 'ID', 'Description', 'StartDate', 'StopDate', 'Capacity', 'HardLimit']
            self.cursor.execute('SELECT SITE, Fingerprint, ID, Description, StartDate, StopDate, Capacity, HardLimit FROM CapacityKey WHERE filename=%s ORDER BY SITE, ID', (filename, ))

        return columns, self.cursor.fetchall()






