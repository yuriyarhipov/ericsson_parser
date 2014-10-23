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
    #from measurements.measurements import Measurements


    work_file = XmlPack(filename).get_files()[0]



    task = current_task
    task.update_state(state="PROGRESS",
            meta={"current": 0, "total": 100})
    interval_per_file = float(100)/float(1)

    current = 0

    if network.lower() in ['3g', '4g']:
       if file_type.lower() == 'xml':
           Xml().save_xml(work_file, project, description, vendor, file_type, network, current_task, current, interval_per_file)

    if network.lower() == '2g':
        if file_type.lower() == 'txt':
            CNA().save_cna(work_file, project, description, vendor, file_type, network, current_task, current, interval_per_file)

    #    elif '.xml' in f:
    #        Xml().save_xml(f, project, current_task, current, interval_per_file)
    #    elif '.msmt' in f:
    #        Measurements().save_file(f, project, '', current_task, current, interval_per_file)


    #    current += interval_per_file
    #task.update_state(state='PROGRESS', meta={"current": 100, "total": 100})


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
