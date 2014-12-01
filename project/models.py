from django.db import models



class Project(models.Model):
    project_name = models.TextField()
    created = models.DateField(auto_now=True)

    def get_list_files(self, network, file_type, vendor):
        from files.models import Files
        return [f.filename for f in Files.objects.filter(project=self, network=network, file_type=file_type, vendor=vendor)]

    def get_vendor_tree(self, network, vendor):
        data = []
        if network == 'WCDMA':
            wcdma_measurements = self.get_tree(network, 'WNCS OSS FILE', vendor)
            wcdma_measurements.extend(self.get_tree(network, 'WMRR OSS FILE', vendor))
            wcdma_licenses_hardware_info = self.get_tree(network, 'WCDMA LICENSE FILE OSS XML', vendor)
            wcdma_licenses_hardware_info.extend(self.get_tree(network, 'WCDMA HARDWARE FILE OSS XML', vendor))

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
        elif network == 'GSM':
            gsm_measurements = self.get_tree(network, 'GSM NCS OSS FILE', vendor)
            gsm_measurements.extend(self.get_tree(network, 'GSM MRR OSS FILE', vendor))
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
            lte_licenses_hardware_info.extend(self.get_tree(network, 'LTE HARDWARE FILE OSS XML', vendor))
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
        return data


    def     get_tree(self, network, file_type, vendor):
        data = []
        for f in self.get_list_files(network, file_type, vendor):
            data.append({'id': f, 'label': f, 'children': '', 'type': file_type, 'network': network})
        return data
