import json

from django.db import connection
import pandas as pd
from django.conf import settings
from os.path import join, exists
from os import makedirs


class Rnd:

    def __init__(self, project_id, network):
        self.project_id = project_id
        self.network = network

        cursor = connection.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS rnd (
                id SERIAL,
                project_id INT,
                network TEXT,
                data JSON)
            ''')
        cursor.close()
        connection.commit()

    def get_param_values(self, param):
        params = set()
        cursor = connection.cursor()
        cursor.execute('''
            SELECT
                data
            FROM
                rnd
            WHERE
                (project_id=%s) AND (network=%s)''', (
            self.project_id,
            self.network))

        result = cursor.fetchone()[0]
        for row in result.get('data'):
            params.add(row.get(param))
        params = list(params)
        params.sort()
        return params

    def get_data(self):
        cursor = connection.cursor()
        cursor.execute('''
            SELECT
                data
            FROM
                rnd
            WHERE
                (project_id=%s) AND (network=%s)''', (
            self.project_id,
            self.network))
        result = []
        if cursor.rowcount > 0:
            result = cursor.fetchone()[0]
        else:
            result = {'columns': [], 'data': []}
        return result

    def write_file(self, filename):
        cursor = connection.cursor()
        excel_dataframe = pd.read_excel(filename, keep_default_na=False)
        columns = excel_dataframe.columns.values.tolist()
        data = excel_dataframe.to_dict(orient='records')

        result = dict(columns=columns, data=data)

        cursor.execute('''
            DELETE FROM
                rnd
            WHERE
                (project_id=%s) AND (network=%s)''', (
            self.project_id,
            self.network))

        cursor.execute('''
            INSERT INTO
                rnd (
                    project_id,
                    network,
                    data)
            VALUES (%s, %s, %s)''', (
            self.project_id,
            self.network,
            json.dumps(result, encoding='latin1')
        ))
        connection.commit()

        return result

    def get_rnd_neighbors(self, sector, filename):
        cursor = connection.cursor()
        cursor.execute('''
            SELECT DISTINCT
                neighbor
            FROM
                UtranRelation
            WHERE (Utrancell=%s) AND (filename=%s)''', (sector, filename, ))
        neighbors = [row[0] for row in cursor]
        return neighbors

    def exist_rnd_neighbors(self, source_sector, target_sector, filename):
        cursor = connection.cursor()
        cursor.execute('''
            SELECT DISTINCT
                neighbor
            FROM
                UtranRelation
            WHERE (neighbor=%s) AND (Utrancell=%s) AND (filename=%s)''', (target_sector, source_sector, filename, ))

        return cursor.rowcount > 0

    def get_new3g(self, sector, filename):
        cursor = connection.cursor()
        cursor.execute('''
            SELECT DISTINCT
                utrancellTarget,
                status
            FROM
                new3g
            WHERE (utrancellSource=%s) AND (filename=%s)''', (sector, filename, ))
        neighbors = {row[0]: row[1] for row in cursor}
        return neighbors

    def save_new_3g(self, filename, rnc_source, utrancell_source,
                    carrier_source, rnc_target, utrancell_target,
                    carrier_target, status):
        cursor = connection.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS new3g (
                filename TEXT,
                rncSource TEXT,
                utrancellSource TEXT,
                carrierSource  TEXT,
                rncTarget TEXT,
                utrancellTarget TEXT,
                carrierTarget TEXT,
                status TEXT
            )
        ''')
        connection.commit()
        cursor.execute('''
            INSERT INTO new3g VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
        ''', (
            filename,
            rnc_source,
            utrancell_source,
            carrier_source,
            rnc_target,
            utrancell_target,
            carrier_target,
            status))
        connection.commit()

    def del_3g(self, filename, utrancell_source, utrancell_target):
        cursor = connection.cursor()

        cursor.execute('''
            DELETE FROM
                new3g
            WHERE
                (filename=%s) AND
                (utrancellSource=%s) AND
                (utrancellTarget=%s)''', (
            filename,
            utrancell_source,
            utrancell_target))
        connection.commit()

    def flush_3g(self, filename):
        cursor = connection.cursor()
        cursor.execute('''
            DELETE FROM
                new3g
            WHERE
                (filename=%s)''', (filename,))
        connection.commit()

    def create_script(self, filename):
        static_path = settings.STATICFILES_DIRS[0]
        file_path = '%s/%s' % (static_path, self.project_id)
        if not exists(file_path):
            makedirs(file_path)
        script_filename = join(file_path, '3g3gscript.txt')

        cursor = connection.cursor()
        cursor.execute('SELECT * FROM new3g WHERE filename=%s', (filename, ))

        with open(script_filename, 'w') as f:
            for row in cursor:
                if row[7] == 'Add':
                    f.write('cr RncFunction=1,UtranCell=%s,UtranRelation=%s-%s\n' % (row[2], row[2], row[5]))
                    f.write('UtranCell=%s #utranCellRef\n' % (row[5], ))
                    f.write('0\n')
                    f.write('\n')
                if row[7] == 'Delete':
                    f.write('del RncFunction=1,UtranCell=%s,UtranRelation=%s\n' % (row[2], row[5]))
                    f.write('\n')

        return '/static/%s/3g3gscript.txt' % self.project_id

    def same_neighbor(self, filename):
        data = self.get_data()
        neighbors = {}
        result = []
        for row in data.get('data'):
            site = row.get('SITE')
            utrancell = row.get('Utrancell')
            if site and utrancell:
                if site in neighbors:
                    for sector in neighbors[site]:
                        if not self.exist_rnd_neighbors(utrancell, sector, filename):
                            result.append({'utrancell_source': utrancell, 'utrancell_target': sector})

                        if not self.exist_rnd_neighbors(sector, utrancell, filename):
                            result.append({'utrancell_source': sector, 'utrancell_target': utrancell})

                    neighbors[site].append(utrancell)
                else:
                    neighbors[site] = [utrancell, ]

        return result
