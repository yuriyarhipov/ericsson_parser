from openpyxl import load_workbook
from django.db import connection
from os.path import basename
from datetime import datetime



class Distance(object):

    def __init__(self):
        cursor = connection.cursor()
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
        connection.commit

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

        cursor = connection.cursor()
        cursor.execute("SELECT  distance, count(date_id) FROM Access_Distance WHERE (Utrancell=%s) GROUP BY distance ORDER BY distance", (sector, ))
        return cursor.fetchall()


    def write_file(self, filename):
        wb = load_workbook(filename=filename, use_iterators=True)
        ws = wb.active
        data = []
        cursor = connection.cursor()
        i = 0
        for excel_row in ws.iter_rows():
            row = []
            if i > 0:
                for cell in excel_row:
                    if cell.value:
                        row.append(cell.value)
                    else:
                        row.append(0)

                cursor.execute('INSERT INTO Access_Distance VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)',
                    (basename(filename), row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8]))
            i += 1
        connection.commit()

