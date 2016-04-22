from lxml import etree


class NokiaWCDMA():

    data = {}
    filename = ''

    def __init__(self, filename, project, file_id=None, current_percent=None, available_percent=None, set_percent=None):
        self.filename = filename
        self.project = project
        self.file_id = file_id
        self.current_percent = current_percent
        self.available_percent = available_percent
        self.set_percent = set_percent
        self.from_xml()

    def get_data(self, elem):
        result = dict()
        for param in elem:
            if param.tag == '{raml20.xsd}p':
                p_name = param.get('name')
                if p_name:
                    result[p_name] = param.text
        return result

    def from_xml(self):
        context = etree.iterparse(
            self.filename,
            events=('end',),
            tag='{raml20.xsd}managedObject')
        tables = set()
        count_objects = 0.0
        for event, elem in context:
            count_objects += 1

        i = 0.0
        percent = 0
        context = etree.iterparse(
            self.filename,
            events=('end',),
            tag='{raml20.xsd}managedObject')
        for event, elem in context:
            i += 1
            p = int(i / count_objects * 100)
            if percent < p:
                percent = p
                self.set_percent(self.file_id, self.current_percent + int(float(self.available_percent) * float(percent) / 100))
            table_name = elem.get('class')
            tables.add(table_name)
            row = self.get_data(elem)
            if table_name in self.data:
                self.data[table_name].append(row)
            else:
                self.data[table_name] = [row]
