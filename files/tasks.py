from djcelery import celery
from celery import current_task

from django.conf import settings
from celery.task.control import revoke
from os.path import basename
from ericsson.wcdma import EricssonWcdma
from archive import XmlPack


@celery.task
def create_parameters_table(f, network, template_name):
    from files.cna import CNA
    from parameters.template import Template

    if network == 'GSM':
        CNA().create_template(template_name)
    elif network == 'WCDMA':
        Template().create_template_table(template_name)
    elif network == 'LTE':
        Template().create_template_table(template_name)


def upload_file(project_id, description, vendor, file_type, network, filename):
    xml_types = [
        'WCDMA RADIO OSS BULK CM XML FILE',
        'WCDMA TRANSPORT OSS BULK CM XML FILE',
        'LTE RADIO eNodeB BULK CM XML FILE',
        'LTE TRANSPORT eNodeB BULK CM XML FILE'
    ]

    work_file = XmlPack(filename).get_files()[0]
    if (vendor == 'Ericsson') and (network == 'WCDMA'):
        if file_type in xml_types:
            ew = EricssonWcdma()
            ew.from_xml(work_file, basename(filename))
            ew.save_to_database(
                project_id,
                vendor,
                network,
                file_type,
                basename(filename))


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
    from files.distance import Distance
    from files.models import Files
    from files.nokia import Nokia

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

    distance_files = [
        'HISTOGRAM FILE COUNTER - Access Distance',
    ]

    nokia_xml = [
        'Configuration Management XML File',
    ]

    work_file = XmlPack(filename).get_files()[0]
    task = current_task
    task.update_state(state="PROGRESS", meta={"current": 1})

    if (vendor == 'Ericsson') and (network == 'WCDMA'):
        if file_type in xml_types:
            ew = EricssonWcdma()
            ew.from_xml(work_file, task)
            ew.save_to_database(project.id, vendor, network, file_type, task)

    task.update_state(state='PROGRESS', meta={
        'current': 100,
        'message': 'processing'})
    revoke(worker.request.id, terminate=True)


@celery.task
def superfile(filename, files):
    from files.models import Files
    from files.cna import CNA
    from files.wcdma import WCDMA

    root_file = Files.objects.filter(filename=files[0]).first()
    Files.objects.filter(filename=filename, project=root_file.project).delete()
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
        cursor.execute('DELETE FROM ' + table_name + ' WHERE filename=%s;',
        (filename, ))
    Template().check_tables()
    conn.commit()
    cursor.close()
    conn.close()
    delete_file(filename)


@celery.task
def create_table(table, rows, network, filename, parent_task_id, project):
    from xml_processing.xml import Tables
    from celery.result import AsyncResult
    from files.models import FileTasks
    from files.excel import ExcelFile

    Tables().write_data(table, rows, network, filename)
    ft = FileTasks.objects.get(task_id=parent_task_id)
    tasks = ft.tasks.split(',')
    status = True
    for task_id in tasks:
        if (not AsyncResult(task_id).ready()) and (task_id != create_table.request.id):
            status = False
            break

    if status:
        additional_tables.delay(network);
    revoke(create_table.request.id, terminate=True)


@celery.task
def additional_tables(network):
    from xml_processing.xml import Tables
    Tables().create_additional_tables(network)


@celery.task
def write_distance_file(project_id, filename, rows):
    from files.distance import Distance
    Distance().write_rows(project_id, filename, rows)

