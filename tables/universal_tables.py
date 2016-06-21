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
        
    
    def create_tables(self, project_id):
        cursor = self.conn.cursor()
        cursor.execute('select table_name from INFORMATION_SCHEMA.views;')
        views = [row[0] for row in cursor]        
        if 'topology' not in views:            
            cursor.execute('''
                CREATE VIEW TOPOLOGY AS
                SELECT DISTINCT
                    %s project_id,
                    UtranCell.Element1 RNC,
                    RBSLocalCell.Element2 SITE,
                    UtranCell.UtranCell,
                    Utrancell.CID,
                    substring(RBSLocalCell.RBSLocalCell from 2 for 1) Sector,
                    RBSLocalCell.RBSLocalCell SectorCarrier,
                    substring(RBSLocalCell.RBSLocalCell from 2 for 1) SectorAntena,
                    substring(RBSLocalCell.RBSLocalCell from 4 for 1) Carrier,
                    IubLink.Iublink,
                    UtranCell.filename            
                FROM RBSLocalCell
                    INNER JOIN UtranCell ON (RBSLocalCell.LocalCellid = UtranCell.CID and RBSLocalCell.filename = UtranCell.filename)
                    LEFT JOIN IubLink ON  (RBSLocalCell.Element2 = IubLink.Element2 AND RBSLocalCell.filename = IubLink.filename)
                WHERE 
                (RBSLocalCell.project_id='%s') AND (UtranCell.project_id='%s') AND (IubLink.project_id='%s')
                ;''', (project_id, project_id, project_id, project_id, ))
            self.conn.commit()
        
        cursor.execute('DELETE FROM files_wcdmawcdma WHERE project_id=%s', (project_id, ))
        sql = '''
            INSERT INTO files_wcdmawcdma (
                project_id,
                "rncSource",
                "utrancellSource",
                "carrierSource",
                "rncTarget",
                "utrancellTarget",
                "carrierTarget"
            )
            SELECT DISTINCT
                %s project,         
	            element1 RNCSource, 
		        UtranRelation.Utrancell UtrancellSource, 
	            t1.carrier CarrierSource,	
                t2.rnc RncTarget,
                neighbor UtrancellTarget,
                t2.carrier CarrierTarget            
            FROM UtranRelation
                left join TOPOLOGY AS t1 ON ((t1.Utrancell= UtranRelation.Utrancell) AND (t1.filename= UtranRelation.filename))
                left join TOPOLOGY AS t2 ON ((t2.Utrancell= UtranRelation.neighbor) AND  (t2.filename= UtranRelation.filename))
            WHERE (t2.project_id = '%s') AND (t1.project_id = '%s') AND (UtranRelation.project_id='%s') 
            ''' % (str(project_id), str(project_id), str(project_id), str(project_id),)
        
        cursor.execute(sql)           
        sql ='''
            INSERT INTO files_rnd3g (
                project_id,                
                "rnc",
                "site", 
                "utrancell",
                "cellid",
                "sector",
                "lac",
                "rac",
                "sc",
                "carrier",
                "name",
                "datum",
                "latitude",
                "longitude",
                "high",
                "Azimuth",
                "Antenna",
                "mechanical_tilt",
                "electrical_tilt"                
            )
            SELECT
                %s, 
    	        topology.rnc, topology.site, topology.utrancell, 
                topology.cid cellid,
     	        topology.sector,
     	        lac,
     	        rac,
     	        primaryscramblingcode sc,
     	        carrier,
     	        'name' "name",
     	        sector.geodatum datum,
     	        sector.latitude,
     	        sector.longitude,
     	        sector.height,
     	        sector.beamdirection azimuth,
     	        topology.sectorantena Antenna,
     	        SectorAntenna.mechanicalantennatilt mechanical_tilt,
     	        SectorAntenna.electricalantennatilt electrical_tilt FROM TOPOLOGY
     	        INNER JOIN Utrancell ON ( topology.cid=Utrancell.cid)
     	        INNER JOIN Sector ON (Sector.element2=topology.site)
     	        INNER JOIN SectorAntenna ON (SectorAntenna.element2=topology.site)
     	        WHERE (topology.project_id = '%s') AND (SectorAntenna.project_id = '%s') AND (Sector.project_id = '%s') AND (Utrancell.project_id = '%s')
       ''' % (project_id, project_id, project_id, project_id, project_id,)
        
        cursor.execute(sql)        
        self.conn.commit()
        
        
    def get_table(self, project_id):
        cursor = self.conn.cursor()
        columns = []
        print self.relation
        if self.relation == 'gsmgsm':
            columns = ['CellSource', 'CellTarget', 'Status']

        
        elif self.relation == 'wcdmawcdma':            
            cursor.execute('''
            SELECT 
	            "rncSource", 
    		    "utrancellSource", 
	            "carrierSource",	
                "rncTarget",
                "utrancellTarget",
                "carrierTarget"            
            FROM files_wcdmawcdma            
            WHERE project_id = %s
            ''', (str(project_id), ))
            print cursor.fetchone()
             
            columns = [
                'rncSource',
                'utrancellSource',
                'carrierSource',
                'rncTarget',
                'utrancellTarget',
                'carrierTarget']

        elif self.relation in ['gsmwcdma', 'gsmlte']:
            print 1
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
                'CellTarget']
            cursor.execute('''
                SELECT 
                    GsmRelation.Element1 AS "RncSource", 
                    GsmRelation.Utrancell AS "UtrancellSource", 
                    Topology.Carrier As "CarrierSource", 
                    GsmRelation.GSMRelation AS "CellTarget" 
                FROM GsmRelation
                    LEFT JOIN TOPOLOGY ON (
                        (GsmRelation.Utrancell=Topology.Utrancell) AND 
                        (GsmRelation.filename=topology.filename))
                WHERE project_id = %s;
            ''', (str(project_id), ))            
        
        elif (self.relation == 'rnd3g'):
            columns = [
                'rnc',
                'site', 
                'utrancell',
                'cellid',
                'sector',
                'lac',
                'rac',
                'sc',
                'carrier',
                'name',
                'datum',
                'latitude',
                'longitude',
                'high',
                'Azimuth',
                'Antenna',
                'mechanical_tilt',
                'electrical_tilt'  ]
            cursor.execute('''
                SELECT 
                    "rnc",
                "site", 
                "utrancell",
                "cellid",
                "sector",
                "lac",
                "rac",
                "sc",
                "carrier",
                "name",
                "datum",
                "latitude",
                "longitude",
                "high",
                "Azimuth",
                "Antenna",
                "mechanical_tilt",
                "electrical_tilt"   
                FROM files_rnd3g                    
                WHERE project_id = %s;
            ''', (str(project_id), ))

        
        data = []
        for row in cursor.fetchall():
            dict_row = dict()
            for i in range(len(columns)):
                print i, row
                dict_row[columns[i]] = row[i]
            data.append(dict_row)

        return columns, data
