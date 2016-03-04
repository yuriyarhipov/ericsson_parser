import psycopg2
from django.conf import settings
from os.path import basename
from files.models import Files, WNCS
import csv


class Measurements(object):

    def __init__(self):
        self.conn = psycopg2.connect(
            'host = %s dbname = %s user = %s password = %s' % (
                settings.DATABASES['default']['HOST'],
                settings.DATABASES['default']['NAME'],
                settings.DATABASES['default']['USER'],
                settings.DATABASES['default']['PASSWORD']))
        self.cursor = self.conn.cursor()

    def save_file(self, filename, project, description, vendor, file_type, network, current_task):
        with open(filename) as mfile:
            reader = csv.DictReader(mfile, delimiter='\t')
            i = 0
            for row in reader:
                i += 1
                try:
                    sc = float(row.get('SC'))
                    events = float(row.get('numberOfEvents'))
                    drop = float(row.get('numberOfDrops'))
                    distance = float(row.get('distance'))
                    WNCS.objects.create(
                        project = project,
                        filename = basename(filename),
                        cell_name = row.get('CellName'),
                        nb_cell_name = row.get('NbCellName'),
                        sc = row.get('SC'),
                        events = row.get('numberOfEvents'),
                        drop = row.get('numberOfDrops'),
                        distance = row.get('distance'))
                except:
                    pass
                if i % 1000 == 0:
                    current_task.update_state(state="PROGRESS", meta={"current": int(i / 1000)})



        Files.objects.filter(filename=basename(filename), project=project).delete()
        Files.objects.create(
                filename=basename(filename),
                file_type=file_type,
                project=project,
                tables='',
                description=description,
                vendor=vendor,
                network=network)
        self.conn.commit()



