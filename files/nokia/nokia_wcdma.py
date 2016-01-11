import datetime
from lxml import etree
import psycopg2
from django.conf import settings
from os.path import basename
from pymongo import MongoClient
import redis
from files.data_file import DataFile


class NokiaWCDMA(DataFile):

    def get_data(self, elem):
        result = dict()
        for param in elem:
            if param.tag == '{raml20.xsd}p':
                p_name = param.get('name')
                if p_name:
                    result[p_name] = param.text
        return result

    def parse_data(self, project, description, vendor, file_type, network, task_id):
        context = etree.iterparse(
            self.path,
            events=('end',),
            tag='{raml20.xsd}managedObject')
        tables = set()

        for event, elem in context:
            table_name = elem.get('class')
            tables.add(table_name)
            row = self.get_data(elem)
            row['data_type'] = table_name
            self.data.append(row)

    def save_to_database(self, project_id, vendor, network, file_type, description, task_id):
        client = MongoClient(settings.MONGO, 27017)
        r = redis.StrictRedis(host=settings.REDIS, port=6379, db=0)
        conn = psycopg2.connect(
            'host = localhost dbname = xml2 user = postgres password = 1297536'
        )
        db = client.myxmart
        tables = db.tables
        tables.delete_many({
            'project_id': project_id,
            'filename': basename(self.filename)})
        s = len(self.raw_data)
        i = 0
        insert_data = []
        file_tables = set()
        for row in self.data:
            row['project_id'] = project_id
            row['filename'] = basename(self.filename)
            file_tables.add(row.get('data_type'))
            insert_data.append(row)
            i += 1
            if len(insert_data) == 100:
                r.set(task_id, '%s, writing' % int(float(i) / float(s) * 100))
                tables.insert_many(insert_data)
                insert_data = []
        r.set(task_id, '100, writing')
        file_tables = list(file_tables)
        file_tables.sort()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM files_files WHERE (project_id=%s) AND (filename=%s)', (project_id, basename(self.filename)))
        cursor.execute('INSERT INTO files_files (filename, date, tables, excel_filename, archive, file_type, description, vendor, network, project_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', (
            basename(self.filename),
            datetime.datetime.now(),
            ','.join(file_tables),
            '',
            '',
            file_type,
            description,
            vendor,
            network,
            project_id))
        conn.commit()

