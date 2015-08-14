from django.db import models
from django.db import connection

from project.models import Project
from files.wcdma import WCDMA
from query.models import SiteQuery



class UploadedFiles(models.Model):
    filename = models.TextField()
    date = models.DateTimeField(auto_now=True)
    file_type = models.CharField(max_length=50, blank=True)
    description = models.TextField()
    vendor = models.TextField()
    network = models.TextField()
    project = models.ForeignKey(Project)


class Files(models.Model):
    filename = models.TextField()
    date = models.DateTimeField(auto_now=True)
    tables = models.TextField(blank=True)
    excel_filename = models.TextField(blank=True)
    archive = models.TextField(blank=True)
    file_type = models.CharField(max_length=50, blank=True)
    description = models.TextField()
    vendor = models.TextField()
    network = models.TextField()
    project = models.ForeignKey(Project)

    def get_map(self):
        result = []
        cursor = connection.cursor()
        cursor.execute('SELECT DISTINCT latitude, longitude FROM rnd_wcdma WHERE filename=%s', (self.filename,))
        for row in cursor:
            try:
                result.append({'lat': float(row[1]), 'lon': float(row[0])})
            except:
                pass
        return result[:2]

    def get_active_file(self, project, network, filename):
        file_type = ''
        if Files.objects.filter(filename=filename, project=project).exists():
            return Files.objects.get(filename=filename, project=project)

        if SuperFile.objects.filter(filename=filename, project=project).exists():
            return SuperFile.objects.get(filename=filename, project=project)

        if SuperFile.objects.filter(project=project, network=network).exists():
            return SuperFile.objects.filter(project=project, network=network).first()

        if network == 'WCDMA':
            file_type = ['WCDMA RADIO OSS BULK CM XML FILE', ]
        elif network == 'LTE':
            file_type = ['LTE RADIO eNodeB BULK CM XML FILE', ]
        elif network == 'GSM':
            file_type = ['GSM BSS CNA  OSS FILE', ]

        return Files.objects.filter(project=project, file_type__in=file_type, network=network).first()

    def get_cells(self):
        cells = []
        if ('XML FILE' in self.file_type) and (self.network == 'WCDMA'):
            wcdma = WCDMA()
            cells = wcdma.get_cells(self.filename)
        return cells

    def get_mo(self, param):
        cursor = connection.cursor()
        if self.network in ['WCDMA', 'LTE']:
            tables = set()
            for f in Files.objects.filter(project=self.project, network=self.network):
                tables = tables.union(set(f.tables.split(',')))
            for table in tables:
                cursor.execute("SELECT column_name FROM information_schema.columns WHERE lower(table_name)='%s';" % table.lower())
                columns = [r[0] for r in cursor]
                if (param.lower() in columns) and (('utrancell' in columns) or ('element1' in columns) or ('element2' in columns)):
                    return table

    def get_data(self):
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM "%s"' % (self.filename.split('.')[0], ))
        columns = [desc[0] for desc in cursor.description]
        data = cursor.fetchall()
        return columns, data

    def get_param(self):
        cursor = connection.cursor()
        tables = set()
        params = set()
        if self.network in ['WCDMA', 'LTE']:
            for f in Files.objects.filter(project=self.project, network=self.network):
                tables = f.tables.split(',')
            for table in tables:
                cursor.execute("SELECT column_name FROM information_schema.columns WHERE lower(table_name)='%s';" % table.lower())
                table_params = [r[0] for r in cursor]
                if ('utrancell' in table_params) or ('element1' in table_params) or ('element2' in table_params):
                    params = params.union(set(table_params))
            params.discard('mo')
            params.discard('version')
            params.discard('vendor')
            params.discard('element')
            params.discard('element1')
            params.discard('element2')
            params.discard('vendorname')
            params.discard('utrancell')
        else:
            columns = []
            for cna_template in CNATemplate.objects.filter(project=self.project):
                columns.extend(cna_template.columns.split(','))
            params = set(columns)

        data = list(params)
        data.sort()
        return data

    def get_site_query_value(self, filename, column, value, param, table):
        cursor = connection.cursor()
        cursor.execute("SELECT %s FROM %s WHERE (filename='%s') AND (lower(%s)='%s')" % (param, table, filename, column, value.lower()))
        if cursor.rowcount > 0:
            return cursor.fetchall()[0][0]

    def check_columns(self, column, table_name):
        cursor = connection.cursor()
        cursor.execute("SELECT table_name FROM INFORMATION_SCHEMA.COLUMNS WHERE (lower(column_name)=%s) AND (lower(table_name)=%s)", (column.lower(), table_name.lower()))
        return cursor.rowcount > 0

    def get_element2_value(self, filename, utrancell):

        cursor = connection.cursor()
        if self.network == 'WCDMA':
            cursor.execute("SELECT Site FROM Topology WHERE (filename='%s') AND (lower(Utrancell)=lower('%s'))" % (filename, utrancell))
        elif self.network == 'LTE':
            cursor.execute("SELECT Site FROM Topology_LTE WHERE (filename='%s') AND (lower(eutrancell)=lower('%s'))" % (filename, utrancell))
        for row in cursor:
            return row[0]

    def get_site_query(self, site):
        cursor = connection.cursor()
        params = dict()
        for sq in SiteQuery.objects.filter(project=self.project, network=self.network):
            if sq.site not in params:
                params[sq.site] = dict()
            if sq.param_name not in params[sq.site]:
                params[sq.site][sq.param_name] = []

            sql = "SELECT table_name FROM INFORMATION_SCHEMA.COLUMNS WHERE lower(column_name)='%s'" % (sq.param_name.lower(), )
            cursor.execute(sql)
            tables = []
            for row in cursor:
                if 'template' not in row[0]:
                    tables.append(row[0])
            if sq.network in ['WCDMA', 'LTE']:
                for table in tables:
                    sql = "SELECT lower(column_name) FROM INFORMATION_SCHEMA.COLUMNS WHERE table_name='%s'" % (table, )
                    cursor.execute(sql)
                    columns = [row[0] for row in cursor]

                    if 'utrancell' in columns:
                        sql = "SELECT %s FROM %s WHERE (lower(utrancell)='%s') AND (filename='%s')" % (
                            sq.param_name.lower(),
                            table,
                            site.lower(),
                            self.filename
                        )
                        cursor.execute(sql)
                        for row in cursor:
                            params[sq.site][sq.param_name] = self.check_value(row[0], sq.param_min, sq.param_max)
                    elif 'eutrancellfdd' in columns:
                        sql = "SELECT %s FROM %s WHERE (lower(eutrancellfdd)='%s') AND (filename='%s')" % (
                            sq.param_name.lower(),
                            table,
                            site.lower(),
                            self.filename
                        )
                        cursor.execute(sql)
                        for row in cursor:
                            params[sq.site][sq.param_name] = self.check_value(row[0], sq.param_min, sq.param_max)

                    elif ('element2' in columns) and (sq.network!='LTE'):
                        element2 = self.get_element2_value(self.filename, site)
                        if element2:
                            value = self.get_site_query_value(
                                self.filename,
                                'element2',
                                element2,
                                sq.param_name,
                                table)
                            params[sq.site][sq.param_name] = self.check_value(value, sq.param_min, sq.param_max)

            elif sq.network == 'GSM':
                for table in tables:
                    if not params[sq.site][sq.param_name]:
                        sql = '''SELECT "%s" FROM %s WHERE (lower(cell)='%s') AND (filename='%s')''' % (
                                sq.param_name.lower(),
                                table,
                                site.lower(),
                                self.filename
                        )
                        cursor.execute(sql)
                        for row in cursor:
                            params[sq.site][sq.param_name] = self.check_value(row[0], sq.param_min, sq.param_max)
            if params[sq.site][sq.param_name] == []:
                params[sq.site].pop(sq.param_name)
        return params

    def check_value(self, value, p_min, p_max):
        status = 'default'
        if p_min and value:
            value = value.strip()
            p_min = p_min.strip()
            p_max = p_max.strip()
            try:
                if p_min.lower() in ['true', 'false']:
                    if value:
                        status = 'success'
                    else:
                        status = 'danger'

                elif (float(value) >= float(p_min)) and (float(value) <= float(p_max)):
                    status = 'success'
                else:
                    status = 'danger'
            except:
                pass

        return [value, status]


class SuperFile(models.Model):
    filename = models.TextField()
    date = models.DateTimeField(auto_now=True)
    files = models.TextField()
    network = models.TextField()
    project = models.ForeignKey(Project)
    file_type = models.CharField(max_length=50, blank=True)
    vendor = models.TextField()


class ExcelFile(models.Model):
    filename = models.TextField()
    table = models.TextField()
    project = models.ForeignKey(Project)
    excel_file = models.TextField()


class CNATemplate(models.Model):
    project = models.ForeignKey(Project)
    table_name = models.TextField()
    columns = models.TextField()


class FileTasks(models.Model):
    task_id = models.TextField()
    tasks = models.TextField()
    max_value = models.IntegerField()

