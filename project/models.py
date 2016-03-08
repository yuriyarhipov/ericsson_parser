from django.db import models



class Project(models.Model):
    project_name = models.TextField()
    created = models.DateField(auto_now=True)

    def get_list_files(self, network, file_type, vendor):
        from files.models import Files
        from files.models import SuperFile
        files = [f.filename for f in Files.objects.filter(project=self, network=network, file_type=file_type, vendor=vendor)]
        superfiles = [f.filename for f in SuperFile.objects.filter(project=self, network=network, file_type=file_type, vendor=vendor)]
        return files + superfiles

    def get_vendor_tree(self, network, vendor):
        data = []
        if (network == 'WCDMA') and (vendor == 'Ericsson'):
            wcdma_measurements = self.get_tree(network, 'WNCS OSS FILE', vendor)
            if wcdma_measurements:
                wcdma_measurements.extend(self.get_tree(network, 'WMRR OSS FILE', vendor))
            else:
                wcdma_measurements = self.get_tree(network, 'WMRR OSS FILE', vendor)

            wcdma_licenses_hardware_info = self.get_tree(network, 'WCDMA LICENSE FILE OSS XML', vendor)
            if wcdma_licenses_hardware_info:
                wcdma_licenses_hardware_info.extend(self.get_tree(network, 'WCDMA HARDWARE FILE OSS XML', vendor))
            else:
                wcdma_licenses_hardware_info = self.get_tree(network, 'WCDMA HARDWARE FILE OSS XML', vendor)

            data.extend([
                {'id': 'RNC',
                'label': 'Radio Network Configuration',
                'children': self.get_tree(network, 'WCDMA RADIO OSS BULK CM XML FILE', vendor)},
                {'id': 'TNC',
                'label': 'Transport Network Configuration',
                'children': self.get_tree(network, 'WCDMA TRANSPORT OSS BULK CM XML FILE', vendor)},
                {'id': 'WCDMA_Measurements',
                'label': 'Network Measurements',
                'children': wcdma_measurements},
                {'id': 'LHI',
                'label': 'Licenses & Hardware Info',
                'children': wcdma_licenses_hardware_info},
                {'id': 'Performance',
                'label': 'Performance',
                'children': self.get_tree(network, 'HISTOGRAM FORMAT COUNTER', vendor)},
            ])
        elif (network == 'WCDMA') and (vendor == 'Nokia'):
            data.extend([
                {'id': 'RNC',
                'label': 'Radio Network Configuration',
                'link': '/explore/nokia/'
                },
            ])

        elif network == 'GSM':
            gsm_measurements = self.get_tree(network, 'GSM NCS OSS FILE', vendor)
            if gsm_measurements:
                gsm_measurements.extend(self.get_tree(network, 'GSM MRR OSS FILE', vendor))
            else:
                gsm_measurements = self.get_tree(network, 'GSM MRR OSS FILE', vendor)

            data.extend([
                {'id': 'gsm_measurements',
                'label': 'Network Measurements',
                'children': gsm_measurements},
                {'id': 'RNC',
                'label': 'Radio Network Configuration',
                'children': self.get_tree(network, 'GSM BSS CNA  OSS FILE', vendor)},
            ])

        elif network == 'LTE':
            lte_licenses_hardware_info = self.get_tree(network, 'LTE LICENSE FILE OSS XML', vendor)
            if lte_licenses_hardware_info:
                lte_licenses_hardware_info.extend(self.get_tree(network, 'LTE HARDWARE FILE OSS XML', vendor))
            else:
                lte_licenses_hardware_info = self.get_tree(network, 'LTE HARDWARE FILE OSS XML', vendor)

            data.extend([
                {'id': 'RNC',
                'label': 'Radio Network Configuration',
                'children': self.get_tree(network, 'LTE RADIO eNodeB BULK CM XML FILE', vendor)},
                {'id': 'TNC',
                'label': 'Transport Network Configuration',
                'children': self.get_tree(network, 'LTE TRANSPORT eNodeB BULK CM XML FILE', vendor)},
                {'id': 'lteLHI',
                'label': 'Licenses & Hardware Info',
                'children': lte_licenses_hardware_info},
            ])
        return data

    def get_network_tree(self, network):
        from files.models import Files
        data = []
        for vendor in [f.vendor for f in Files.objects.filter(project=self, network=network).distinct('vendor')]:
            data.append({
                'id': vendor,
                'label': vendor,
                'type': vendor,
                'network': network,
                'children': self.get_vendor_tree(network, vendor)
            })
        if not data:
            return {}
        return data


    def get_tree(self, network, file_type, vendor):
        data = []
        for f in self.get_list_files(network, file_type, vendor):
            data.append({'id': f, 'label': f, 'children': '', 'type': file_type, 'network': network, 'menu': 'file'})
        if not data:
            return {}
        return data

    def get_drive_test(self):
        from files.models import Files
        data = []
        for f in Files.objects.filter(project=self, file_type='Drive Test'):
            data.append({
                'id': f.id,
                'label': f.filename,
                'children': '',
                'type': f.file_type,
                'show_check': True})
        if not data:
            data = {}
        return data

    def get_rnd_items(self, network):
        from files.models import Files
        data = []
        for f in Files.objects.filter(project=self, file_type='RND', network=network):
            data.append({
                'id': f.id,
                'label': f.description,
                'children': '',
                'type': f.file_type,
                'radio_input_name': '%s_rnd' % network.lower(),
                'link': '/rnd/%s/' % network,
                'show_check': True})
        if not data:
            data = {}
        return data

    def get_rnd_tree(self):
        data = [
            {
                'id': 'rnd_gsm',
                'label': 'GSM',
                'children': self.get_rnd_items('GSM'),
                'show_check': False},
            {
                'id': 'rnd_wcdma',
                'label': 'WCDMA',
                'children': self.get_rnd_items('WCDMA'),
                'show_check': False},
            {
                'id': 'rnd_lte',
                'label': 'LTE',
                'children': self.get_rnd_items('LTE'),
                'show_check': False}
        ]
        return data


class UserSettings(models.Model):
    current_project = models.ForeignKey(Project)
    user = models.TextField()

    #xml_files
    gsm_file = models.TextField()
    wcdma_file = models.TextField()
    lte_file = models.TextField()

    #rnd_files
    rnd_gsm_file = models.TextField()
    rnd_wcdma_file = models.TextField()
    rnd_lte_file = models.TextField()

    #map
    gsm_color = models.TextField()
    wcdma_color = models.TextField()
    lte_color = models.TextField()
    gsm_radius = models.TextField()
    wcdma_radius = models.TextField()
    lte_radius = models.TextField()
    map_center = models.TextField()
    map_zoom = models.TextField()
