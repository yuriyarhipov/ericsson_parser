from os.path import basename
import psycopg2

from shapely.geometry import box
from geopy.distance import vincenty


class DriveTest():

    def __init__(self):
        self.conn = psycopg2.connect(
            'host = localhost user = postgres password = 1297536 port=5432 dbname=xml2'
        )

    def init_drive_test(self, project_id):
        cursor = self.conn.cursor()
        table_name = 'TERMS_%s' % project_id
        cursor.execute('''SELECT "All-Latitude", "All-Longitude"
            FROM ''' + table_name + '''
            WHERE (project_id=%s)   LIMIT 1''', (project_id,))
        init_row = cursor.fetchone()
        return dict(start_point=[init_row[0], init_row[1]])

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
            colnames = [desc[0].lower() for desc in cursor.description]
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

    def get_points(self, project_id, map_bounds, zoom):
        zoom_k = [1000, 900, 800, 700, 600, 550, 500, 450, 400, 350, 300, 250, 200, 100, 50, 10, 5, 2, 1]
        table_name = 'TERMS_%s' % project_id
        map_box = box(
            float(map_bounds[1]),
            float(map_bounds[0]),
            float(map_bounds[3]),
            float(map_bounds[2]))
        points = []
        cursor = self.conn.cursor()
        cursor.execute('''SELECT "All-Latitude", "All-Longitude" FROM ''' + table_name + ''' WHERE (project_id=%s) AND ST_Within("point" , ST_GeomFromText(%s)) AND ("MS"='MS1') ORDER BY id''', (project_id, map_box.wkt))
        for row in cursor:
            if len(points) > 0:
                distance = vincenty(points[-1], row).meters
                if distance > zoom_k[zoom]:
                    points.append(row)
            else:
                points.append(row)
        return points






