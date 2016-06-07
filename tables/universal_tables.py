import psycopg2
from django.conf import settings
from files.models import GsmGsm, LteLte, WcdmaWcdma, LteGsm, GsmLte, WcdmaLte, GsmWcdma, WcdmaGsm


class UniversalTable:

    def __init__(self, relation):
        self.relation = relation
        self.conn = psycopg2.connect(
            'host = %s dbname = %s user = %s password = %s' % (
                settings.DATABASES['default']['HOST'],
                settings.DATABASES['default']['NAME'],
                settings.DATABASES['default']['USER'],
                settings.DATABASES['default']['PASSWORD']))
        
        
    def get_table(self, project_id):
        cursor = self.conn.cursor()

        columns = []

        if self.relation == 'gsmgsm':
            columns = ['CellSource', 'CellTarget', 'Status']

        
        elif self.relation == 'wcdmawcdma':
            cursor.execute('''
            SELECT 
	        element1 RNCSource, 
		    UtranRelation.Utrancell UtrancellSource, 
	        t1.carrier CarrierSource,	
            t2.rnc RncTarget,
            neighbor UtrancellTarget,
            t2.carrier CarrierTarget            
        FROM UtranRelation
            Inner join TOPOLOGY AS t1 ON ((t1.Utrancell= UtranRelation.Utrancell) AND (t1.filename= UtranRelation.filename))
            Inner join TOPOLOGY AS t2 ON ((t2.Utrancell= UtranRelation.neighbor) AND  (t2.filename= UtranRelation.filename))
            WHERE project_id = %s
            ''', (str(project_id), ))
        
             
            columns = [
                'RncSource',
                'UtrancellSource',
                'CarrierSource',
                'RncTarget',
                'UtrancellTarget',
                'CarrierTarget']

        elif self.relation in ['gsmwcdma', 'gsmlte']:
            columns = [
                'CellSource',
                'RncTarget',
                'UtrancellTarget',
                'CarrierTarget',
                'Status']

        elif self.relation in ['wcdmagsm', 'ltegsm']:
            columns = [
                'RncSource',
                'UtrancellSource',
                'CarrierSource',
                'CellTarget',
                'Status']

        
        data = []
        for row in cursor.fetchall():
            dict_row = dict()
            for i in range(len(columns)):
                dict_row[columns[i]] = row[i]
            data.append(dict_row)

        return columns, data
