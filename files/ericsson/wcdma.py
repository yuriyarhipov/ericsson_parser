from lxml import etree
import redis
from pymongo import MongoClient
from os.path import basename
from django.conf import settings
import psycopg2
import datetime
from files.data_file import DataFile


class EricssonWcdma(DataFile):
    data = []
    filename = ''

    def get_me_context_path(self, node):
        path = []
        parent = node.getparent()
        if etree.QName(parent).localname == 'SubNetwork':
            path = self.get_me_context_path(parent)
            path.append({'SubNetwork': parent.get('id')})
        return path

    def parse_data_container(self, node, path, parent_data=dict()):
        if parent_data:
            data = parent_data
            data['path'] = path
        else:
            data = dict(path=path)
        data_type = node.find('{genericNrm.xsd}attributes/{genericNrm.xsd}vsDataType').text
        data_format_version = node.find('{genericNrm.xsd}attributes/{genericNrm.xsd}vsDataFormatVersion').text
        data['data_type'] = data_type.replace('vsData', '')
        data['data_format_version'] = data_format_version

        for attr in node.find('{genericNrm.xsd}attributes'):
            tag = etree.QName(attr).localname
            if (tag == data_type):
                for elem in attr:
                    data[etree.QName(elem).localname] = elem.text
            elif (tag != 'vsDataType') and (tag != 'vsDataFormatVersion'):
                print('smth else')

        self.data.append(data)

    def parse_managed_element(self, node, path, parent_data=dict()):
        node_tag = etree.QName(node).localname
        path.append({node_tag: node.get('id')})
        m_el_data = parent_data
        if node_tag == 'UtranCell':
            m_el_data['UtranCell'] = node.get('id')

        for elem in node:
            tag = etree.QName(elem).localname
            if tag == 'attributes':
                for attr in elem:
                    if attr.text:
                        m_el_data[etree.QName(attr).localname] = attr.text
                    else:
                        m_el_data[etree.QName(attr).localname] = ''
            elif tag == 'VsDataContainer':
                self.parse_data_container(elem, path[:], m_el_data.copy())
            else:
                self.parse_managed_element(elem, path[:], m_el_data.copy())

    def parse_me_context(self, node):
        path = self.get_me_context_path(node)
        path.append(dict(MeContext=node.get('id')))
        for child in node:
            tag = etree.QName(child).localname
            if tag == 'VsDataContainer':
                self.parse_data_container(child, path[:])
            elif tag == 'ManagedElement':
                self.parse_managed_element(child, path[:])
            elif tag == 'attributes':
                pass  # TODO attributes????
            else:
                raise Exception('unvalid xml node')

    def from_xml(self, filename, task_id):
        self.filename = filename
        me_contexts = etree.iterparse(
            filename,
            events=('end',),
            tag='{genericNrm.xsd}MeContext')
        count = 0
        r = redis.StrictRedis(host=settings.REDIS, port=6379, db=0)
        r.set(task_id, '30, estimating...')
        for event, me_context in me_contexts:
            count += 1

        me_contexts = etree.iterparse(
            filename,
            events=('end',),
            tag='{genericNrm.xsd}MeContext')
        i = 0
        for event, me_context in me_contexts:
            i += 1
            r.set(
                task_id,
                '%s,processing' % int(float(i) / float(count) * 100))
            self.parse_me_context(me_context)
