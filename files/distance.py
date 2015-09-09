from openpyxl import load_workbook
from django.db import connection
from os.path import basename
from datetime import datetime
from decimal import Decimal
from files.models import Files


class Distance(object):

    def __init__(self):
        cursor = connection.cursor()

        cursor.execute('''CREATE TABLE IF NOT EXISTS Access_Distance (
            project_id INT,
            filename TEXT,
            RNC  TEXT,
            RBS TEXT,
            date_id date,
            sector INT,
            DCVECTOR_INDEX BIGINT,
            pmPropagationDelay BIGINT,
            Carrier BIGINT,
            Utrancell TEXT,
            Distance REAL)
            ''')
        try:
            cursor.execute('''
                CREATE INDEX
                    utrancell_date_idx
                ON
                    Access_Distance (Utrancell, date_id);''')
            cursor.execute('''
                CREATE INDEX
                    utrancell_idx
                ON
                    Access_Distance (Utrancell);''')
        except:
            pass
        connection.commit()

    def get_sectors(self):
        cursor = connection.cursor()
        cursor.execute('SELECT DISTINCT Utrancell FROM Access_Distance')
        sectors = [row[0] for row in cursor]
        return sectors

    def get_rbs(self, project_id):
        cursor = connection.cursor()
        cursor.execute('SELECT DISTINCT RBS FROM Access_Distance WHERE project_id=%s ORDER BY RBS', (project_id, ))
        rbs = [row[0] for row in cursor]
        return rbs

    def get_dates(self, rbs):
        cursor = connection.cursor()
        cursor.execute("SELECT DISTINCT date_id FROM Access_Distance WHERE (RBS='%s') ORDER BY date_id" % rbs)
        dates = [row[0].strftime('%d.%m.%Y') for row in cursor]
        return dates

    def get_charts(self, day, rbs, project_id):
        cursor = connection.cursor()
        cursor.execute('''
            SELECT DISTINCT
                Utrancell
            FROM
                Access_Distance
            WHERE
                (RBS=%s) AND (project_id=%s)''', (
            rbs,
            project_id))

        data = dict()
        for row in cursor:
            utrancell = row[0]
            chart, title, distances = self.get_chart(day, utrancell)
            data[utrancell] = dict(
                distances=distances,
                chart=chart,
                title=title)
        return data

    def get_chart(self, date, utrancell):
        data = []
        table = []
        cursor = connection.cursor()
        cursor.execute('''
            SELECT
                MIN(date_id),
                MAX(date_id)
            FROM
                Access_Distance
            WHERE
                (Utrancell=%s)''', (
            utrancell, ))
        days = cursor.fetchall()

        if date != 'none':
            cursor.execute('''
                SELECT
                    Access_Distance.date_id,
                    distance,
                    pmpropagationdelay,
                    date_sum.date_sum,
                    DCVECTOR_INDEX,
                    Sector,
                    Carrier
                FROM
                    Access_Distance
                INNER JOIN (
                    SELECT
                        date_id,
                        sum(pmpropagationdelay) date_sum
                    FROM
                        Access_Distance
                    WHERE
                        Utrancell=%s
                    GROUP BY date_id)
                    AS date_sum
                ON
                    (Access_Distance.date_id = date_sum.date_id)
                WHERE
                    (Utrancell=%s) AND (Access_Distance.date_id=%s)
                ORDER BY
                    distance, Access_Distance.date_id;''', (
                utrancell,
                utrancell,
                datetime.strptime(date, '%d.%m.%Y')))

            distances = dict()
            for row in cursor:
                value = Decimal(row[2]) / Decimal(row[3]) * 100
                sector = row[5]
                carrier = row[6]
                table.append({
                    'date': row[0].strftime('%d.%m.%Y'),
                    'sector': sector,
                    'distance': float(row[1]),
                    'dcvector': int(row[4]),
                    'samples': int(row[2]),
                    'samples_percent': round(value, 2),
                    'total_samples': int(row[3])})
                distances[int(row[4])] = float(row[1])
                data.append([
                    int(row[4]),
                    round(value, 2), ]
                )
            title = '<b>Utrancell:</b>%s <b>Carrier:</b>%s <b>Sector:</b>%s <b>%s</b>' % (
                utrancell,
                carrier,
                sector,
                date)
        else:
            cursor.execute('''
                SELECT
                    DIST_SUM.distance,
                    DIST_SUM.dist_sum,
                    DIST_SUM.DCVECTOR_INDEX,
                    DATE_SUM.date_sum,
                    Sector,
                    Carrier
                FROM (
                SELECT
                    distance,
                    SUM(pmpropagationdelay) AS dist_sum,
                    DCVECTOR_INDEX,
                    Sector,
                    Carrier
                FROM
                    Access_Distance
                WHERE
                    (Utrancell=%s)
                GROUP BY
                    distance,
                    DCVECTOR_INDEX,
                    Sector,
                    Carrier
                ) AS DIST_SUM,
                (
                SELECT
                    sum(pmpropagationdelay) date_sum
                FROM
                    Access_Distance
                WHERE
                    Utrancell=%s
                ) AS date_sum ORDER BY DIST_SUM.distance
                ''', (
                utrancell, utrancell, ))

            distances = dict()
            for row in cursor:
                value = Decimal(row[1]) / Decimal(row[3]) * 100
                distances[int(row[2])] = float(row[0])
                data.append([
                    int(row[2]),
                    round(value, 2), ]
                )
                carrier = row[4]
                sector = row[5]

            title = '''
                <b>Utrancell:</b>%s
                <b>Carrier:</b>%s
                <b>Sector:</b>%s
                from <b>%s</b>
                to <b>%s</b>''' % (
                utrancell,
                carrier,
                sector,
                days[0][0].strftime('%d.%m.%Y'),
                days[0][1].strftime('%d.%m.%Y'))
        return data, title, distances

    def write_file(self, project, description, vendor, filename, current_task):
        wb = load_workbook(filename=filename, use_iterators=True)
        ws = wb.active
        cursor = connection.cursor()
        cursor.execute('DELETE FROM Access_Distance WHERE filename=%s',
                       (basename(filename), ))
        i = 0
        rows = []
        for excel_row in ws.iter_rows():
            row = []
            if i > 0:
                for cell in excel_row:
                    if cell.value:
                        row.append(cell.value)
                    else:
                        row.append(0)
                rows.append(row)
                if len(rows) == 10000:
                    sql_rows = []
                    for row in rows:
                        sql_rows.append(cursor.mogrify(
                            '(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)',
                            (
                                project.id,
                                basename(filename),
                                row[0],
                                row[1],
                                row[2],
                                row[3],
                                row[4],
                                row[5],
                                row[6],
                                row[7],
                                row[8])))
                    cursor.execute('''
                        INSERT INTO
                            Access_Distance
                        VALUES
                            %s''' % ','.join(sql_rows))
                    rows = []
            i += 1

            if i % 10000 == 0:
                current_task.update_state(state="PROGRESS", meta={
                    "current": int(i / 10000)})

        connection.commit()
        Files.objects.create(
            filename=basename(filename),
            file_type='HISTOGRAM FILE COUNTER - Access Distance',
            project=project,
            tables='',
            description=description,
            vendor=vendor,
            network='WCDMA')

    def get_distr(self, day, rbs, project_id):
        data = []
        cursor = connection.cursor()
        cursor.execute('''
            SELECT
                MIN(date_id),
                MAX(date_id)
            FROM
                Access_Distance
            WHERE
                (RBS=%s)''', (
            rbs, ))
        days = cursor.fetchall()[0]
        print days

        if day != 'none':
            cursor.execute('''
                SELECT
                    utrancell,
                    SUM(pmpropagationdelay)
                FROM
                    access_distance
                WHERE
                    (rbs=%s) AND
                    (project_id = %s) AND
                    (date_id=%s)
                GROUP BY
                    utrancell
                ORDER BY utrancell;''', (
                rbs,
                project_id,
                datetime.strptime(day, '%d.%m.%Y')))
            title = 'Load Distribution RBS:<b>%s</b> Day:<b>%s</b>' % (rbs, day)
        else:
            cursor.execute('''
                SELECT
                    utrancell,
                    SUM(pmpropagationdelay)
                FROM
                    access_distance
                WHERE
                    (rbs=%s) AND
                    (project_id = %s)
                GROUP BY
                    utrancell
                ORDER BY utrancell;''', (rbs, project_id))
            title = 'Load Distribution RBS:<b>%s</b> from:<b>%s</b> to:<b>%s</b>' % (
                rbs,
                days[0].strftime('%d.%m.%Y'),
                days[1].strftime('%d.%m.%Y'))
        for row in cursor:
            data.append(dict(name=row[0], y=int(row[1])))

        return data, title

