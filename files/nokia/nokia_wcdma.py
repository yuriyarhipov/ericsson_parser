import datetime
from lxml import etree
import psycopg2
from django.conf import settings
from os.path import basename
from pymongo import MongoClient
import redis
from files.data_file import DataFile


class NokiaWCDMA(DataFile):

    data = []
    filename = ''

    def get_data(self, elem):
        result = dict()
        for param in elem:
            if param.tag == '{raml20.xsd}p':
                p_name = param.get('name')
                if p_name:
                    result[p_name] = param.text
        return result

    def from_xml(self, filename, task_id):
        context = etree.iterparse(
            filename,
            events=('end',),
            tag='{raml20.xsd}managedObject')
        tables = set()

        for event, elem in context:
            table_name = elem.get('class')
            tables.add(table_name)
            row = self.get_data(elem)
            row['data_type'] = table_name
            self.data.append(row)
