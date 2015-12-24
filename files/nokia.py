from lxml import etree
import psycopg2
from django.conf import settings
from os.path import basename
from files.models import Files
import json
from os.path import basename


class Nokia(object):

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
        self.create_table()
        self.data = []
        if filename:
            self.data = self.get_table()

    def create_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Nokia (
              filename TEXT,
              row JSON)''')

    def get_data(self, elem):
        result = dict()
        for param in elem:
            if param.tag == '{raml20.xsd}p':
                p_name = param.get('name')
                if p_name:
                    result[p_name] = param.text
        return result

    def parse_data(self, project, description, vendor, file_type, network, task):
        cursor = self.conn.cursor()
        context = etree.iterparse(
            self.path,
            events=('end',),
            tag='{raml20.xsd}managedObject')

        for event, elem in context:
            cursor.execute('INSERT INTO Nokia VALUES (%s, %s)', (self.filename, json.dumps(self.get_data(elem))))
        self.conn.commit()
        Files.objects.create(
            filename=basename(self.filename),
            file_type=file_type,
            project=project,
            tables='nokia',
            description=description,
            vendor=vendor,
            network=network)

    def get_table(self):
        data = []
        cursor = self.conn.cursor()
        cursor.execute('SELECT row FROM nokia')
        for row in cursor:
            row = row[0]
            r = []
            r.append(row.get('ipAddress'))
            r.append(row.get('maxCallCapability'))
            r.append(row.get('maxThroughput'))
            r.append(row.get('name'))
            r.append(row.get('AlarmSetforWCELBLINIT'))
            r.append(row.get('CBCSourceIPAddress'))
            r.append(row.get('CSAttachDetachAllowed'))
            r.append(row.get('ConnectionRetryCounter'))
            r.append(row.get('DLBLERConfInterval'))
            r.append(row.get('ExtendedULDLactivationTmr'))
            r.append(row.get('LCSfunctionality'))
            r.append(row.get('MACLogChPriSRB1'))
            r.append(row.get('MACLogChPriSRB2'))
            r.append(row.get('MACLogChPriSRB3'))
            r.append(row.get('N302'))
            r.append(row.get('N304'))
            r.append(row.get('N308'))
            r.append(row.get('OMSBackupIpAddress'))
            r.append(row.get('OMSIpAddress'))
            r.append(row.get('PageRep1stInterv'))
            r.append(row.get('PageRep2ndInterv'))
            r.append(row.get('RANAPprocInitWait'))
            r.append(row.get('RNCChangeOrigin'))
            r.append(row.get('RNCIPAddress'))
            r.append(row.get('RNCName'))
            r.append(row.get('RTservicesForPS'))
            r.append(row.get('RestrictionInterval'))
            r.append(row.get('RncClientTLSMode'))
            data.append(r)
        return data
