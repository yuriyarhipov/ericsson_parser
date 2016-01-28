import pymongo
from files.lib import fcount
import json
from pymongo import MongoClient


class DriveTest():

    def __init__(self):
        client = MongoClient('localhost', 27017)
        db = client.xml
        self.drive_test = db.drive_test

    def upload_file(self, filename, project_id, current_task):
        count = fcount(filename)
        with open(filename) as f:
            columns = []
            for col in f.readline().split('\t'):
                if col not in columns:
                    columns.append(col)
            i = 0
            data = []
            for row in f:
                i += 1
                row = row.split('\t')
                data_row = dict(project_id=project_id)
                for col in columns:
                    data_row[col] = row[columns.index(col)]
                data.append(data_row)

                if len(data) > 10000:
                    self.drive_test.insert_many(data)
                    data = []
                    current_task.update_state(state="PROGRESS", meta={"current": int(float(i) / count * 100)})
            self.drive_test.insert_many(data)

    def get_points(self):
        points = set()
        i = 0
        for p in self.drive_test.find({'MS': 'MS1'}):
            i += 1
            points.add('%s, %s' % (p.get('All-Latitude'), p.get('All-Longitude')))
            if i > 20000:
                break

        return points






