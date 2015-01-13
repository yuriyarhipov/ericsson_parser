from files.models import Files


class ActiveFiles(object):

    def process_request(self, request):
        project = request.project
        wcdma_filename = request.COOKIES.get('wcdma')
        lte_filename = request.COOKIES.get('lte')
        gsm_filename = request.COOKIES.get('gsm')

        request.lte = None
        request.cna = None
        request.wcdma = None

        request.wcdma = Files().get_active_file(project, 'WCDMA', wcdma_filename)
        request.lte = Files().get_active_file(project, 'LTE', lte_filename)
        request.gsm = Files().get_active_file(project, 'GSM', gsm_filename)


