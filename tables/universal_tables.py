import psycopg2
from django.conf import settings
from files.models import GsmGsm, LteLte, WcdmaWcdma, LteGsm, GsmLte, WcdmaLte, GsmWcdma, WcdmaGsm, Files
import json


class UniversalTable:

    def __init__(self, relation):
        self.relation = relation
        self.conn = psycopg2.connect(
                'host = %s dbname = %s user = %s password = %s' % (
                settings.DATABASES['default']['HOST'],
                settings.DATABASES['default']['NAME'],
                settings.DATABASES['default']['USER'],
                settings.DATABASES['default']['PASSWORD']))
    
    
    def create_rnd_from_network(self, project, network, rnd_name):
        cursor = self.conn.cursor()
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
            FROM
                files_rnd3g
            WHERE
                project_id=%s
                 
        ''', (project.id, ))
        data = []
        for r in cursor:
            row = dict()
            row['RNC'] = r[0]
            row['SITE'] = r[1]
            row['Utrancell'] = r[2]
            row['CellId'] = r[3]
            row['Sector'] = r[4]
            row['Lac'] = r[5]
            row['Rac'] = r[6]
            row['SC'] = r[7]
            row['Carrier'] = r[8]
            row['Name'] = r[9]
            row['Datum'] = r[10]
            row['Latitude'] = (float(r[11]) / 8388608) * 90
            row['Longitude'] = (float(r[12]) / 16777216) * 360
            row['High'] = r[13]
            row['Azimuth'] = r[14]
            row['Antenna'] = r[15]
            row['Mechanical_Tilt'] = r[16]
            row['Electrical_Tilt'] = r[17]
            data.append(row)
        cursor.execute('INSERT INTO rnd (project_id, network, description, data) VALUES (%s, %s, %s, %s)', (
            project.id,
            network,
            rnd_name,
            json.dumps({'data': data, 'columns': ['Sector', 'Rac', 'Antenna', 'RNC', 'Electrical_Tilt', 'Datum', 'SITE', 'Longitude', 'Lac', 'High', 'Latitude', 'Carrier', 'Azimuth', 'SC', 'Mechanical_Tilt', 'Utrancell', 'CellId'] }, encoding='latin1')))
        self.conn.commit()
        Files.objects.create(
            filename=rnd_name,
            file_type='RND',
            project=project,
            tables='',
            description=rnd_name,
            vendor='Universal',
            network=network)
            
            
       
        
    
    def create_tables(self, project_id):
        cursor = self.conn.cursor()
        cursor.execute('select table_name from INFORMATION_SCHEMA.views;')
        views = [row[0] for row in cursor]        
        if 'topology' not in views:            
            cursor.execute('''
                CREATE VIEW TOPOLOGY AS
                SELECT DISTINCT
                    UtranCell.project_id,
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
                (RBSLocalCell.project_id=UtranCell.project_id) AND (IubLink.project_id=UtranCell.project_id)
                ;''')
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
        cursor.execute('DELETE FROM files_rnd3g WHERE project_id=%s', (project_id, ))          
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
            SELECT DISTINCT
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
     	        INNER JOIN Sector ON ((Sector.element2=topology.site) AND (Sector.sector = topology.sector))
     	        INNER JOIN SectorAntenna ON ((SectorAntenna.element2=topology.site) AND (SectorAntenna.sectorantenna = topology.sector))
     	    WHERE (topology.project_id = '%s') AND (SectorAntenna.project_id = '%s') AND (Sector.project_id = '%s') AND (Utrancell.project_id = '%s')
            ORDER BY 
                topology.rnc, 
                topology.site, 
                topology.utrancell, 
                topology.cid,
     	        topology.sector,
     	        lac,
     	        rac,
     	        sc,
     	        carrier,     	        
     	        datum,
     	        sector.latitude,
     	        sector.longitude,
     	        sector.height,
     	        azimuth,
     	        Antenna,
     	        mechanical_tilt,
     	        electrical_tilt 
       ''' % (project_id, project_id, project_id, project_id, project_id,)
        
        cursor.execute(sql)        
        self.conn.commit()
                
    def get_table(self, project_id):
        cursor = self.conn.cursor()
        columns = []
        
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
            
             
            columns = [
                'rncSource',
                'utrancellSource',
                'carrierSource',
                'rncTarget',
                'utrancellTarget',
                'carrierTarget']

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
