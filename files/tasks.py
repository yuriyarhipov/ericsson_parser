from djcelery import celery
from celery import current_task

from django.conf import settings
from celery.task.control import revoke
from os.path import basename, splitext


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


@celery.task
def worker(file_ids):
    from os.path import basename
    from archive import XmlPack
    from xml_processing.xml import Xml, Table, WcdmaXML, Diff
    from files.cna import CNA
    from files.measurements import Measurements
    from files.lic import License
    from files.hw import HardWare
    from files.distance import Distance
    from files.drive_test import DriveTest
    from files.models import Files, UploadedFiles
    from rnd import Rnd

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

    task = current_task
    task.update_state(state="PROGRESS", meta={"current": 1})

    for f in UploadedFiles.objects.filter(id__in=file_ids):
        work_files = []
        filename = f.filename
        vendor = f.vendor
        file_type = f.file_type
        description = f.description

        ext = splitext(f)[1]
        if ext in ['rar', 'zip', 'gz', '.rar', '.zip', '.gz']:
            work_files.extend(XmlPack(filename).get_files())
        else:
            work_files.append(filename)

        if network in ['WCDMA', 'LTE']:
            if file_type in distance_files:
                Distance().write_file(
                    project,
                    description,
                    vendor,
                    work_file,
                    task)

            if (file_type in xml_types) and (network == 'LTE'):
                Files.objects.filter(
                    filename=basename(work_file),
                    project=project).delete()
                Xml().save_xml(
                    work_file,
                    project,
                    description,
                    vendor,
                    file_type,
                    network,
                    task)
            if (file_type in xml_types) and (network == 'WCDMA'):
                percent_per_file = 90 / len(work_files)
                i = 0
                available_percent = percent_per_file / 2
                tables = set()
                for f in work_files:
                    wx = WcdmaXML(f, project, task, i, available_percent)
                    table = Table(1, 'localhost', 'xml2', 'postgres', '1297536')
                    table_count = len(wx.data)
                    table_index = 0.0
                    for table_name, data in wx.data.iteritems():
                        tables.add(table_name)
                        table_index += 1
                        percent = int(table_index / table_count * 100)
                        task.update_state(state="PROGRESS", meta={"current": i + available_percent + int(float(available_percent) * float(percent) / 100)})
                        table.write_table(table_name, data)
                    i += percent_per_file
                    Files.objects.filter(filename=basename(f), project=project).delete()
                    Files.objects.create(
                        filename=basename(f),
                        file_type=file_type,
                        project=project,
                        tables=','.join(list(wx.data.keys())),
                        description=description,
                        vendor=vendor,
                        network=network)
                    task.update_state(state="PROGRESS", meta={"current": percent_per_file})
                diff = Diff(1, 'localhost', 'xml2', 'postgres', '1297536')
                i = 0.0
                l = float(len(tables))
                for table in tables:
                    i += 1
                    percent = int(i / l * 10)
                    task.update_state(state="PROGRESS", meta={"current": 90 + percent})
                    diff.diff(table)

                task.update_state(state="PROGRESS", meta={"current": 100})

        if network == 'GSM':
            if file_type in cna_types:
                CNA().save_cna(
                    work_file,
                    project,
                    description,
                    vendor,
                    file_type,
                    network,
                    task)

        if file_type in measurements_types:
            Measurements().save_file(
                work_file,
                project,
                description,
                vendor,
                file_type,
                network,
                current_task)

        if file_type in license_types:
            lic = License(work_file)
            lic.parse_data(
                project,
                description,
                vendor,
                file_type,
                network,
                current_task)

        if file_type in hardware_types:
            hw = HardWare(work_file)
            hw.parse_data(
                project,
                description,
                vendor,
                file_type,
                network,
                current_task)

        if file_type == 'Drive Test':
            dt = DriveTest()
            dt.upload_file(work_file, project.id, current_task)
            Files.objects.filter(filename=basename(work_file), project=project).delete()
            Files.objects.create(
                filename=basename(work_file),
                file_type=file_type,
                project=project,
                tables='',
                description=description,
                vendor=vendor,
                network=network)

        if file_type == 'RND':
            Rnd(project.id, network).write_file(work_file, description)
            Files.objects.filter(project=project, description=description).delete()
            Files.objects.create(
                filename=basename(work_file),
                file_type=file_type,
                project=project,
                tables='',
                description=description,
                vendor=vendor,
                network=network)

    task.update_state(state='PROGRESS', meta={"current": 100, })
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
