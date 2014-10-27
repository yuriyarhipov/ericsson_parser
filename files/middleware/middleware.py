from files.models import Files


class ActiveFiles(object):

    def process_request(self, request):
        project = request.project
        wcdma_filename = request.COOKIES.get('wcdma')

        if Files.objects.filter(filename=wcdma_filename, project=project).exists():
            wcdma_file = Files.objects.get(filename=wcdma_filename, project=project)
        else:
            wcdma_file = Files.objects.filter(project=project, file_type='xml', network='3g').first()
        if wcdma_file:
            request.wcdma = wcdma_file