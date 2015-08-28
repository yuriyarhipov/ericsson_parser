from openpyxl import load_workbook
from django.db import connection
from os.path import basename
from datetime import datetime
from decimal import Decimal


class Distance(object):

    def __init__(self):
        cursor = connection.cursor()
        cursor.execute("SELECT to_regclass('public.Access_Distance')")
        if cursor.rowcount == 1:
            return
        cursor.execute('''CREATE TABLE IF NOT EXISTS Access_Distance (
            filename TEXT,
            RNC  TEXT,
            RBS TEXT,
            date_id date,
            sector INT,
            DCVECTOR_INDEX INT,
            pmPropagationDelay INT,
            Carrier INT,
            Utrancell TEXT,
            Distance REAL)
            ''')
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
        connection.commit()


    def get_sectors(self):
        cursor = connection.cursor()
        cursor.execute('SELECT DISTINCT Utrancell FROM Access_Distance')
        sectors = [row[0] for row in cursor]
        return sectors

    def get_dates(self, sector):
        cursor = connection.cursor()
        cursor.execute("SELECT DISTINCT date_id FROM Access_Distance WHERE (Utrancell='%s') ORDER BY date_id" % sector)
        dates = [row[0].strftime('%d.%m.%Y') for row in cursor]
        return dates

    def get_chart(self, date, sector):
        data = []
        table = []
        cursor = connection.cursor()
        cursor.execute('''
            SELECT
                SUM(pmpropagationdelay)
            FROM
                Access_Distance
            WHERE
                (Utrancell=%s) AND (date_id=%s)''', (
            sector,
            datetime.strptime(date, '%d.%m.%Y')))

        sum_samples = cursor.fetchall()[0][0]

        cursor.execute('''
            SELECT
                date_id,
                distance,
                pmpropagationdelay
            FROM
                Access_Distance
            WHERE
                (Utrancell=%s) AND (date_id=%s)
            ORDER BY
                distance''', (
            sector,
            datetime.strptime(date, '%d.%m.%Y')))

        for row in cursor:
            value = Decimal(row[2]) / Decimal(sum_samples) * 100
            table.append({
                'date': date,
                'sector': sector,
                'distance': row[1],
                'samples': row[2],
                'samples_percent': round(value, 2),
                'total_samples': sum_samples})

            data.append([
                row[1],
                round(value, 2), ]
            )
        return data, table

    def write_file(self, filename, current_task):
        wb = load_workbook(filename=filename, use_iterators=True)
        ws = wb.active
        cursor = connection.cursor()
        cursor.execute('DELETE FROM Access_Distance WHERE filename=%s',
                       (basename(filename), ))
        i = 0
        for excel_row in ws.iter_rows():
            row = []
            if i > 0:
                for cell in excel_row:
                    if cell.value:
                        row.append(cell.value)
                    else:
                        row.append(0)

                cursor.execute('''
                    INSERT INTO
                        Access_Distance
                    VALUES
                        (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''', (
                    basename(filename),
                    row[0],
                    row[1],
                    row[2],
                    row[3],
                    row[4],
                    row[5],
                    row[6],
                    row[7],
                    row[8]))
            i += 1
            if i % 10000 == 0:
                current_task.update_state(state="PROGRESS", meta={
                    "current": int(i / 10000)})

        connection.commit()
