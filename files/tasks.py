from djcelery import celery
from celery import current_task
from celery.task.control import revoke

from django.conf import settings


@celery.task
def save_rows(filename, rows):
    from xml_processing.xml import Tables
    tables = dict()
    data = dict()

    for row in rows:
        table_name = row.get('table')
        fields = row.get('fields')

        if table_name and (table_name not in data):
            data[table_name] = []
            tables[table_name] = set()

        columns = tables[table_name]
        data[table_name].append(fields)
        if columns:
            tables[table_name] = columns | set(fields.keys())
        else:
            tables[table_name] = set(fields.keys())

    tables = Tables(data, tables, filename)
    tables.create_tables()


@celery.task
def worker(filename, project, description, vendor, file_type, network):
    if not project:
        return

    from os.path import basename
    from archive import XmlPack
    from xml_processing.xml import Xml
    from files.cna import CNA
    from files.measurements import Measurements
    from files.lic import License
    from files.hw import HardWare
    from files.models import UploadedFiles, CNATemplate, Files

    xml_types = [
        'WCDMA RADIO OSS BULK CM XML FILE',
        'WCDMA TRANSPORT OSS BULK CM XML FILE',
        'LTE RADIO eNodeB BULK CM XML FILE',
        'LTE TRANSPORT eNodeB BULK CM XML FILE'
    ]

    cna_types = [
        'GSM BSS CNA  OSS FILE',
    ]

    measurements_types = [
        'WNCS OSS FILE',
        'WMRR OSS FILE',
        'GSM NCS OSS FILE',
        'GSM MRR OSS FILE',
    ]

    license_types = [
        'WCDMA LICENSE FILE OSS XML',
        'LTE LICENSE FILE OSS XML'
    ]

    hardware_types = [
        'WCDMA HARDWARE FILE OSS XML',
        'LTE HARDWARE FILE OSS XML'
    ]


    work_file = XmlPack(filename).get_files()[0]

    task = current_task
    UploadedFiles.objects.create(filename=filename, project=project, description=task.request.id, vendor=vendor, file_type=file_type, network=network)
    task.update_state(state="PROGRESS",
            meta={"current": 0, "total": 99})
    interval_per_file = float(99)/float(1)

    current = 0

    if network in ['WCDMA', 'LTE']:
        if file_type in xml_types:
            Files.objects.filter(filename=basename(work_file), project=project).delete()
            UploadedFiles.objects.filter(filename=filename).delete()
            Files.objects.create(
                filename=basename(work_file),
                file_type=file_type,
                project=project,
                tables='',
                description=description,
                vendor=vendor,
                network=network)
            Xml().save_xml(
                work_file, project, description, vendor, file_type, network)

    if network == 'GSM':
        if file_type in cna_types:
            CNA().save_cna(work_file, project, description, vendor, file_type, network)

    if file_type in measurements_types:
        Measurements().save_file(work_file, project, description, vendor, file_type, network, current_task, current, interval_per_file)

    if file_type in license_types:
        lic = License(work_file)
        lic.parse_data(project, description, vendor, file_type, network, current_task, current, interval_per_file)

    if file_type in hardware_types:
        hw = HardWare(work_file)
        hw.parse_data(project, description, vendor, file_type, network, current_task, current, interval_per_file)

    task.update_state(state='PROGRESS', meta={"current": 99, "total": 99})
    UploadedFiles.objects.filter(filename=filename).delete()
    #revoke(worker.request.id, terminate=True)

@celery.task
def superfile(filename, files):
    from files.models import Files
    from files.cna import CNA
    from files.wcdma import WCDMA

    root_file = Files.objects.filter(filename=files[0]).first()
    Files.objects.filter(filename=filename,project=root_file.project).delete()
    Files.objects.create(
        filename=filename,
        file_type=root_file.file_type,
        project=root_file.project,
        tables=root_file.tables,
        description='superfile',
        vendor=root_file.vendor,
        network=root_file.network)
    if root_file.network == 'GSM':
        CNA().create_superfile(filename, files)
    elif root_file.network == 'WCDMA':
        tables = root_file.tables.split(',')
        WCDMA().create_superfile(filename, files, tables)




@celery.task
def parse_cna_rows(filename, tables, columns, rows):
    from files.cna import CNA
    CNA().add_rows(filename, tables, columns, rows)
    #revoke(parse_cna_rows.request.id, terminate=True)

@celery.task
def parse_xml(filename, node):
    import re
    return None
    path = re.compile('\{.*\}')
    table_name = None


    data = node.find(".//{genericNrm.xsd}vsDataType")
    if data is not None:
        table_name = data.text[6:]
    #else:
    #    table_name = path.sub('', parent.tag)



@celery.task
def delete_file(filename):
    from main.models import delete_file, File
    from main.template import Template
    import psycopg2

    conn = psycopg2.connect(
            'host = %s dbname = %s user = %s password = %s' % (
                settings.DATABASES['default']['HOST'],
                settings.DATABASES['default']['NAME'],
                settings.DATABASES['default']['USER'],
                settings.DATABASES['default']['PASSWORD']))
    cursor = conn.cursor()


    tables = File.objects.filter(filename=filename).first().tables.split(',')
    for table_name in tables:
        cursor.execute('DELETE FROM '+table_name+' WHERE filename=%s;',(filename, ))
    Template().check_tables()
    conn.commit()
    cursor.close()
    conn.close()
    delete_file(filename)
