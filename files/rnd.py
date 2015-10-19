import json

from django.db import connection
import pandas as pd


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

        result = cursor.fetchone()[0]
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

    def get_new3g(self, sector, filename):
        cursor = connection.cursor()
        cursor.execute('''
            SELECT DISTINCT
                utrancellTarget
            FROM
                new3g
            WHERE (utrancellSource=%s) AND (filename=%s)''', (sector, filename, ))
        neighbors = [row[0] for row in cursor]
        return neighbors

    def save_new_3g(self, filename, rnc_source, utrancell_source,
                    carrier_source, rnc_target, utrancell_target,
                    carrier_target):
        cursor = connection.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS new3g (
                filename TEXT,
                rncSource TEXT,
                utrancellSource TEXT,
                carrierSource  TEXT,
                rncTarget TEXT,
                utrancellTarget TEXT,
                carrierTarget TEXT
            )
        ''')
        cursor.execute('''
            INSERT INTO new3g VALUES (%s,%s,%s,%s,%s,%s,%s)
        ''', (
            filename,
            rnc_source,
            utrancell_source,
            carrier_source,
            rnc_target,
            utrancell_target,
            carrier_target))
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
