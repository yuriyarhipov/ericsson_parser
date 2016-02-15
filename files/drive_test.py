from os.path import basename
import psycopg2

from shapely.geometry import box
from geopy.distance import vincenty


class DriveTest():

    def __init__(self):
        self.conn = psycopg2.connect(
            'host = localhost user = postgres password = 1297536 port=5432 dbname=xml2'
        )

    def get_params(self, project_id, ms):
        cursor = self.conn.cursor()
        table_name = 'TERMS_%s' % project_id
        cursor.execute('''SELECT *
            FROM ''' + table_name + '''
            WHERE (project_id=%s) LIMIT 0''', (project_id,))
        colnames = [desc[0] for desc in cursor.description]
        return colnames

    def init_drive_test(self, project_id):
        cursor = self.conn.cursor()
        table_name = 'TERMS_%s' % project_id
        mobile_stations = []
        cursor.execute('''SELECT *
            FROM ''' + table_name + '''
            WHERE (project_id=%s) LIMIT 0''', (project_id,))
        parameters = [desc[0] for desc in cursor.description]
        parameters.remove('id')
        parameters.remove('project_id')
        parameters.remove('point')
        parameters.remove('filename')

        cursor.execute('''SELECT DISTINCT "MS"
            FROM ''' + table_name + '''
            WHERE (project_id=%s) ORDER BY "MS"''', (project_id,))
        for row in cursor:
            mobile_stations.append(row[0])

        cursor.execute('''SELECT "All-Latitude", "All-Longitude"
            FROM ''' + table_name + '''
            WHERE (project_id=%s)   LIMIT 1''', (project_id,))
        init_row = cursor.fetchone()
        data = dict(
            start_point=[init_row[0], init_row[1]],
            mobile_stations=mobile_stations,
            parameters=parameters)
        return data

    def upload_file(self, filename, project_id, current_task):
        cursor = self.conn.cursor()
        table_name = 'TERMS_%s' % project_id
        cursor.execute('''CREATE TABLE IF NOT EXISTS %s
            (
                "id" serial,
                "project_id" int,
                "filename" text,
                "All-Latitude" text,
                "All-Longitude" text,
                "point" geometry
            )
        ;''' % table_name)

        cursor.execute('''
            DELETE FROM ''' + table_name + '''
            WHERE
                (project_id=%s) AND
                (filename=%s)''', (project_id, basename(filename)))

        with open(filename) as f:
            columns = []
            cursor.execute("Select * FROM %s LIMIT 0" % (table_name, ))
            colnames = [desc[0] for desc in cursor.description]
            for col in f.readline().split('\t'):
                columns.append(col)
                if (col.lower() not in colnames):
                    cursor.execute(
                        'ALTER TABLE %s ADD COLUMN "%s" TEXT;' % (
                            table_name,
                            col, ))
            self.conn.commit()

            columns = ['"%s"' % col for col in columns]
            cursor.copy_from(f, table_name, columns=columns)

        cursor.execute('''
            UPDATE ''' + table_name + ''' SET
                project_id=%s,
                filename=%s,
                point=ST_PointFromText('POINT(' || "All-Latitude" || ' ' || "All-Longitude" || ')')
            WHERE
                (project_id is Null) AND
                (filename is NULL)''', (project_id, basename(filename)))
        self.conn.commit()

    def get_color(self, legend, value):
        for l in legend:
            if (l.get('max_value')) and (l.get('min_value')):
                try:
                    if (float(value) <= float(l.get('max_value'))) and (float(value)>float(l.get('min_value'))):
                        return l.get('color')
                except:
                    print 'A%sA' % value
            elif (l.get('max_value')):
                try:
                    if (float(value) <= float(l.get('max_value'))):
                        return l.get('color')
                except:
                    print 'B%sB' % value
            elif (l.get('min_value')):
                try:
                    if (float(value) > float(l.get('min_value'))):
                        return l.get('color')
                except:
                    print 'C%sC' % value
        return '#000000'

    def get_points(self, project_id, ms, param, legend, map_bounds, zoom):
        table_name = 'TERMS_%s' % project_id
        map_box = box(
            float(map_bounds[1]),
            float(map_bounds[0]),
            float(map_bounds[3]),
            float(map_bounds[2]))
        points = []
        cursor = self.conn.cursor()

        cursor.execute('''SELECT DISTINCT id, "All-Latitude", "All-Longitude", "''' + param +'''" FROM ''' + table_name + ''' WHERE (project_id=%s) AND ST_Within("point" , ST_GeomFromText(%s)) AND ("MS"=%s) AND ("''' + param +'''"!='') ORDER BY id''', (project_id, map_box.wkt, ms))
        row_count = cursor.rowcount
        k = row_count / 500
        i = 0
        attached_ids = []
        for row in cursor:
            attached_ids.append(row[0])
            if i == k:
                points.append([
                    row[1],
                    row[2],
                    self.get_color(legend, row[3]),
                    row[3],
                    row[0],
                    attached_ids])
                i = 0
                attached_ids = []
            else:
                i += 1
        return points

    def get_point(self, project_id, id):
        table_name = 'TERMS_%s' % project_id
        cursor = self.conn.cursor()
        cursor.execute('''SELECT * FROM ''' + table_name + ''' WHERE (id=%s)''', (id, ))
        colnames = [desc[0] for desc in cursor.description]
        data = cursor.fetchone()
        point = []
        for i in range(len(colnames)):
            if (data[i] != '') and (colnames[i] not in ['id', 'project_id', 'filename', 'point']):
                point.append([colnames[i], data[i]])
        point = sorted(point)
        return point








