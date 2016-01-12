from tempfile import mkdtemp
from os.path import join

from pymongo import MongoClient
import redis
from pandas import DataFrame, ExcelWriter
from django.conf import settings
import dropbox
from zipfile import ZipFile


class Excel(object):

    def __init__(self):
        client = MongoClient(settings.MONGO, 27017)
        self.db = client.myxmart
        self.redis = redis.StrictRedis(host=settings.REDIS, port=6379, db=0)

    def to_excel(self, project_id, filename, table):
        tables = self.db.tables
        temp_path = mkdtemp()
        excel_filename = join(temp_path, 'all_tables.xlsx')
        archive_filename = join(temp_path, 'all_tables.zip')
        redis_key = 'excel_%s_%s_%s' % (project_id, filename, table)
        self.redis.set(redis_key, '50, estimating...')
        if table == 'all':
            writer = ExcelWriter(excel_filename)
            table_names = tables.find({'project_id': int(project_id), 'filename': filename}).distinct('data_type')
            table_names.sort()
            s = len(table_names)
            i = 0
            for table_name in table_names:
                i += 1
                self.redis.set(redis_key, '%s, writing...' % int(float(i) / float(s) * 100))
                data = []
                for row in tables.find({'project_id': int(project_id), 'filename': filename, 'data_type':table_name}):
                    data.append(row)

                df = DataFrame(data)
                if '_id' in df.columns:
                    del df['_id']
                if 'path' in df.columns:
                    del df['path']
                df.to_excel(writer, sheet_name=table_name, index=False)
            writer.save()
            self.redis.set(redis_key, '50, packing...')
            zip = ZipFile(archive_filename, 'w')
            zip.write(excel_filename, arcname='all_tables.xlsx')
            zip.close()

            self.redis.set(redis_key, '50, uploading...')
            dbx = dropbox.Dropbox('I2Ivu8T1EPEAAAAAAAAAsLYdWN4W7rXtrx-d1BC91L7YCrmKAZ1j1MiWEgcpVLcT')
            with open(archive_filename, 'rb') as f:
                data = f.read()
                try:
                    dropbox_path = '/%s/%s/%s/all_tables.zip' % (project_id, filename, table)
                    dbx.files_upload(
                        data, dropbox_path, mode=dropbox.files.WriteMode('overwrite', None),)
                    l = dbx.sharing_create_shared_link(dropbox_path)
                    self.redis.set(redis_key, l.url)

                except dropbox.exceptions.ApiError as err:
                    print('*** API error', err)




