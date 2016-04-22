class HuaweiWCDMA:

    def __init__(self, filename, project, file_id=None, current_percent=None, available_percent=None, set_percent=None):
        self.filename = filename
        self.project = project
        self.file_id = file_id
        self.current_percent = current_percent
        self.available_percent = available_percent
        self.set_percent = set_percent
        self.from_xml()

    def from_xml(self):
        print self.filename
        


filename = '/home/arhipov/Downloads/huawei/CFGMML-BSC16-10.239.190.4-20160223142750.txt'
