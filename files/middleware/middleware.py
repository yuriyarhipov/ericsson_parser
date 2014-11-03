from files.models import Files


class ActiveFiles(object):

    def process_request(self, request):
        project = request.project
        wcdma_filename = request.COOKIES.get('wcdma')
        lte_filename = request.COOKIES.get('lte')
        cna_filename = request.COOKIES.get('cna')

        if Files.objects.filter(filename=wcdma_filename, project=project).exists():
            wcdma_file = Files.objects.get(filename=wcdma_filename, project=project)
        else:
            wcdma_file = Files.objects.filter(project=project, file_type='xml', network='3g').first()
        if wcdma_file:
            request.wcdma = wcdma_file

        if Files.objects.filter(filename=lte_filename, project=project).exists():
            lte_file = Files.objects.get(filename=lte_filename, project=project)
        else:
            lte_file = Files.objects.filter(project=project, file_type='xml', network='4g').first()
        if lte_file:
            request.lte = lte_file

        if Files.objects.filter(filename=cna_filename, project=project).exists():
            cna_file = Files.objects.get(filename=cna_filename, project=project)
        else:
            cna_file = Files.objects.filter(project=project, file_type='xml', network='2g').first()
        if cna_file:
            request.cna = cna_file
