from djcelery import celery
from celery import current_task

from django.conf import settings


@celery.task
def worker(filename, project,  description, vendor, file_type, network):
    if not project:
        return

    from archive import XmlPack
    from xml_processing.xml import Xml
    from files.cna import CNA
    from files.measurements import Measurements
    from files.lic import License
    from files.hw import HardWare
    from files.models import UploadedFiles

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
            meta={"current": 0, "total": 100})
    interval_per_file = float(100)/float(1)

    current = 0

    if network in ['WCDMA', 'LTE']:
        if file_type in xml_types:
            Xml().save_xml(work_file, project, description, vendor, file_type, network, current_task, current, interval_per_file)

    if network == 'GSM':
        if file_type in cna_types:
            CNA().save_cna(work_file, project, description, vendor, file_type, network, current_task, current, interval_per_file)

    if file_type in measurements_types:
        Measurements().save_file(work_file, project, description, vendor, file_type, network, current_task, current, interval_per_file)

    if file_type in license_types:
        lic = License(work_file)
        lic.parse_data(project, description, vendor, file_type, network, current_task, current, interval_per_file)

    if file_type in hardware_types:
        hw = HardWare(work_file)
        hw.parse_data(project, description, vendor, file_type, network, current_task, current, interval_per_file)

    task.update_state(state='PROGRESS', meta={"current": 100, "total": 100})
    UploadedFiles.objects.filter(filename=filename).delete()

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
