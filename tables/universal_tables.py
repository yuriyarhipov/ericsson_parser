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
        cursor = self.conn.cursor()
        try:
            cursor.execute(''' CREATE VIEW WCDMAWCDMA AS SELECT DISTINCT
	            element1 RNCSource, 
	            Utrancell UtrancellSource, 
	            'CarrierSource' CarrierSource,	
                adjacentCell RncTarget,
                neighbor UtrancellTarget,
                'CarrierTarget' CarrierTarget,
                project_id
            FROM UtranRelation '''
           ) 
        except:
            pass
        
        
    def get_table(self, project_id):
        cursor = self.conn.cursor()
                
        columns = []
        
        if self.relation == 'gsmgsm':
            columns = ['CellSource', 'CellTarget', 'Status']

        elif self.relation in ['ltelte', 'wcdmawcdma', 'wcdmalte', 'ltewcdma']:
            columns = [
                'RncSource',
                'UtrancellSource',
                'CarrierSource',
                'RncTarget',
                'UtrancellTarget',
                'CarrierTarget',
                'Status']

        elif self.relation == 'wcdmawcdma':
            columns = [
                'RncSource',
                'UtrancellSource',
                'CarrierSource',
                'RncTarget',
                'UtrancellTarget',
                'CarrierTarget',
                'Status']

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
        
        cursor.execute('''SELECT * FROM %s WHERE  project_id='%s' ''' % (self.relation, project_id, ))        
        data = []
        for row in cursor.fetchall():
            dict_row = dict()
            for i in range(len(columns)):
                dict_row[columns[i]] = row[i]
            data.append(dict_row)

        return columns, data

