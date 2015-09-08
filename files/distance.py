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
        cursor.execute('SELECT DISTINCT RBS FROM Access_Distance WHERE project_id=%s', (project_id, ))
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
            chart, table, title, distances = self.get_chart(day, utrancell)
            data[utrancell] = dict(
                distances=distances,
                chart=chart,
                title=title)
        return data


    def get_chart(self, date, sector):
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
            sector, ))
        days = cursor.fetchall()

        if date != 'none':
            cursor.execute('''
                SELECT
                    Access_Distance.date_id,
                    distance,
                    pmpropagationdelay,
                    date_sum.date_sum,
                    DCVECTOR_INDEX
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
                sector,
                sector,
                datetime.strptime(date, '%d.%m.%Y')))
            title = 'Sector: %s %s' % (
                sector,
                date)
            distances = dict()
            for row in cursor:
                value = Decimal(row[2]) / Decimal(row[3]) * 100
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
        else:
            cursor.execute('''
                SELECT
                    DIST_SUM.distance,
                    DIST_SUM.dist_sum,
                    DIST_SUM.DCVECTOR_INDEX,
                    DATE_SUM.date_sum
                FROM (
                SELECT
                    distance,
                    SUM(pmpropagationdelay) AS dist_sum,
                    DCVECTOR_INDEX
                FROM
                    Access_Distance
                WHERE
                    (Utrancell=%s)
                GROUP BY
                    distance,
                    DCVECTOR_INDEX
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
                sector, sector, ))

            title = 'Sector: %s from %s to %s' % (
                sector,
                days[0][0].strftime('%d.%m.%Y'),
                days[0][1].strftime('%d.%m.%Y'))

            distances = dict()
            for row in cursor:
                value = Decimal(row[1]) / Decimal(row[3]) * 100
                table.append({
                    'sector': sector,
                    'distance': float(row[0]),
                    'dcvector': int(row[2]),
                    'samples': int(row[1]),
                    'samples_percent': round(value, 2),
                    'total_samples': int(row[3])})
                distances[int(row[2])] = float(row[0])
                data.append([
                    int(row[2]),
                    round(value, 2), ]
                )
        return data, table, title, distances

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


