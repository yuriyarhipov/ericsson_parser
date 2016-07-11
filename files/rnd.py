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
                description TEXT,
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

    def get_data(self, filenames=None):        
        cursor = connection.cursor()
        project_id = self.project_id
        network = self.network.upper()
        if filenames:
            sql_des = ','.join(["'%s'" % f for f in filenames])
            cursor.execute('''
            SELECT
                data
            FROM
                rnd
            WHERE
                (project_id=%s) AND (lower(network)=lower(%s)) AND (description IN (''' + sql_des + '''))''', (
                project_id,
                network))
        else:
            cursor.execute('''
                SELECT
                    data
                FROM
                    rnd
                WHERE
                    (project_id=%s) AND (network=%s)''', (
                project_id,
                network))
        result = []

        if cursor.rowcount > 0:
            result = cursor.fetchone()[0]
        else:
            result = {'columns': [], 'data': [], 'filenames': filenames}
        return result

    def save_row(self, row):
        cursor = connection.cursor()
        filename = row.get('filename')
        data = self.get_data([filename, ])
        print len(data.get('data'))
        if self.network == 'wcdma':
            if 'current_rnc' in row:
                i = 0
                for i in range(0, len(data['data'])):
                    if ((data['data'][i].get('RNC', '') == row.get('current_rnc')) and (data['data'][i].get('Utrancell', '') == row.get('current_utrancell'))):
                        data['data'][i][row.get('column')] = row.get('value')
                        break
            elif 'del_rnc' in row:
                i = 0
                for i in range(0, len(data['data'])):
                    if ((data['data'][i].get('RNC', '') == row.get('del_rnc')) and (data['data'][i].get('Utrancell', '') == row.get('del_utrancell'))):
                        data['data'].pop(i)
                        break
        elif self.network == 'lte':
            if 'current_site' in row:
                i = 0
                for i in range(0, len(data['data'])):
                    if ((data['data'][i].get('SITE', '') == row.get('current_site')) and (data['data'][i].get('Utrancell', '') == row.get('current_utrancell'))):
                        data['data'][i][row.get('column')] = row.get('value')
                        break
            elif 'del_site' in row:
                i = 0
                for i in range(0, len(data['data'])):
                    if ((data['data'][i].get('SITE', '') == row.get('del_site')) and (data['data'][i].get('Utrancell', '') == row.get('del_utrancell'))):
                        data['data'].pop(i)
                        break
        elif self.network == 'gsm':
            if 'current_bsc' in row:
                i = 0
                for i in range(0, len(data['data'])):
                    if ((data['data'][i].get('BSC', '') == row.get('current_bsc')) and (data['data'][i].get('Cell_Name', '') == row.get('current_cellname'))):
                        data['data'][i][row.get('column')] = row.get('value')
                        break
            elif 'del_bsc' in row:
                i = 0
                for i in range(0, len(data['data'])):
                    if ((data['data'][i].get('BSC', '') == row.get('del_bsc')) and (data['data'][i].get('Cell_Name', '') == row.get('del_cellname'))):
                        data['data'].pop(i)
                        break
        else:
            data['data'].append(row)
        print self.network
        cursor.execute('DELETE FROM rnd WHERE (project_id=%s) AND (LOWER(network)=%s) AND (description=%s)''', (
            self.project_id,
            self.network,
            filename))
        cursor.execute('INSERT INTO rnd (project_id, network, description, data) VALUES (%s, %s, %s, %s)', (
            self.project_id,
            self.network,
            filename,
            json.dumps(data, encoding='latin1')))
        connection.commit()

    def write_file(self, filename, description):
        cursor = connection.cursor()
        excel_dataframe = pd.read_excel(filename, keep_default_na=False)
        columns = excel_dataframe.columns.values.tolist()
        data = excel_dataframe.to_dict(orient='records')

        result = dict(columns=columns, data=data)

        cursor.execute('''
            DELETE FROM
                rnd
            WHERE
                (project_id=%s) AND (network=%s) AND (description=%s)''', (
            self.project_id,
            self.network,
            description))

        cursor.execute('''
            INSERT INTO
                rnd (
                    project_id,
                    network,
                    description,
                    data)
            VALUES (%s, %s, %s, %s)''', (
            self.project_id,
            self.network,
            description,
            json.dumps(result, encoding='latin1')
        ))
        connection.commit()

        return result

    def get_rnd_neighbors(self, sector, project_id):
        cursor = connection.cursor()
        cursor.execute('''
            SELECT DISTINCT
                "utrancellTarget"
            FROM
                wcdmawcdma
            WHERE ("utrancellSource"=%s) AND (project_id=%s)''', (sector, project_id, ))
        neighbors = [row[0] for row in cursor]
        return neighbors

    def exist_rnd_neighbors(self, source_sector, target_sector, project_id):
        cursor = connection.cursor()
        cursor.execute('''
            SELECT DISTINCT
                "utrancellTarget"
            FROM
                wcdmawcdma
            WHERE ("utrancellTarget"=%s) AND ("utrancellSource"=%s) AND (project_id=%s)''', (target_sector, source_sector, project_id, ))
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

    def psc_collision(self, filename):
        cursor = connection.cursor()
        data = []
        cursor.execute('''
            SELECT DISTINCT
                Utrancell.Utrancell as source,
                neighbor as target,
                UtranCell.primaryscramblingcode as source_psc,
                target.primaryscramblingcode as target_psc,
                UtranCell.uarfcnul as source_uarfcnul,
                target.uarfcnul as target_uarfcnul
            FROM
                UtranRelation INNER JOIN Utrancell ON (UtranRelation.utrancell = utrancell.utrancell)
                INNER JOIN utrancell as target ON (UtranRelation.neighbor = target.utrancell)
                INNER JOIN Topology ON (UtranRelation.utrancell = Topology.utrancell)
                INNER JOIN Topology as target_topology ON (target_topology.utrancell = Topology.utrancell)
            WHERE
                (UtranCell.primaryscramblingcode = target.primaryscramblingcode) AND
                (Topology.carrier = target_topology.carrier) AND
                (UtranCell.uarfcnul = target.uarfcnul) AND
                (UtranCell.filename = %s) AND
                (target.filename = %s);
        ''', (filename, filename))
        for row in cursor:
            data.append({
                'Source': row[0],
                'Label': '%s-%s' % (row[0], row[1]),
                'Target': row[1],
                'PSC_Source': row[2],
                'PSC_Target': row[3],
                'uarfcnDl_Source': row[4],
                'uarfcnDl_Target': row[5]
            })
        return data
