import gzip

from rarfile import RarFile, is_rarfile
from zipfile import ZipFile, is_zipfile
from os import path


class XmlPack:

    xml_path = '/tmp/xml'


    def __init__(self, file):
        self.file = file

    def gzip_file(self):
        gzf = gzip.GzipFile(self.file, 'rb')
        f = gzf.read()
        gzf.close()
        filename = path.join(self.xml_path, self.file[:-3])
        outF = file(filename, 'wb')
        outF.write(f)
        outF.close()
        return [filename, ]


    def rar_file(self):
        with RarFile(self.file) as rar:
            rar.extractall(self.xml_path)
            files = []
            for f in rar.infolist():
                if ('.conf' in f.filename) or ('.msmt' in f.filename) or ('.xml' in f.filename) or ('.xls' in f.filename) or ('.txt' in f.filename) or ('.FMT' in f.filename):
                    files.append(path.join(self.xml_path, f.filename.replace('\\','/')))
            return files

    def zip_file(self):
        files = []
        with ZipFile(self.file) as zip:
            zip.extractall(self.xml_path)
            for f in zip.infolist():
                if ('.conf' in f.filename) or ('.msmt' in f.filename) or ('.xml' in f.filename) or ('.xls' in f.filename) or ('.txt' in f.filename) or ('.FMT' in f.filename):
                    files.append(path.join(self.xml_path, f.filename.replace('\\','/')))
        return files

    def get_files(self):
        result = []
        if '.xml' in self.file:
            result.append(self.file)
        if is_rarfile(self.file):
            result = self.rar_file()
        elif is_zipfile(self.file):
            result = self.zip_file()
        elif '.gz' in self.file:
            result = self.gzip_file()
        return result
