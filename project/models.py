from django.db import models


class Project(models.Model):
    project_name = models.TextField()
    created = models.DateField(auto_now=True)

    def get_list_files(self, network, file_type):
        from files.models import Files
        return [f.filename for f in Files.objects.filter(project=self, network=network, file_type=file_type)]

    def get_tree(self, network, file_type):
        data = []
        for f in self.get_list_files(network, file_type):
            data.append({'id': f.lower(), 'label': f, 'children': '', 'type': file_type, 'network': network})

        lic_files = self.get_list_files(network, 'license')
        if lic_files:
            lic_menu = []
            for lic_file in lic_files:
                lic_menu.append({'id': lic_file.lower(), 'label': lic_file, 'children': '', 'type': 'license', 'network': network})
            data.append({'id': 'lic_%s' % network.lower(), 'label': 'License', 'children': lic_menu})

        hardware_files = self.get_list_files(network, 'hardware')
        if hardware_files:
            hardware_menu = []
            for hardware_file in hardware_files:
                hardware_menu.append({'id': hardware_file.lower(), 'label': hardware_file, 'children': '', 'type': 'hardware', 'network': network})
            data.append({'id': 'hw_%s' % network.lower(), 'label': 'Hardware', 'children': hardware_menu})

        wncs_files = self.get_list_files(network, 'wncs')
        ncs_files = self.get_list_files(network, 'ncs')
        wmrr_files = self.get_list_files(network, 'wmrr')
        mrr_files = self.get_list_files(network, 'mrr')

        meas_menu =[]

        wncs_menu = []
        for wncs_file in wncs_files:
            wncs_menu.append({'id': wncs_file.lower(), 'label': wncs_file, 'children': '', 'type': 'wncs', 'network': network})
        if wncs_menu:
            meas_menu.append({'id': 'wncs_%s' % network.lower(), 'label': 'WNCS', 'children': wncs_menu})

        ncs_menu = []
        for ncs_file in ncs_files:
            ncs_menu.append({'id': ncs_file.lower(), 'label': ncs_file, 'children': '', 'type': 'ncs', 'network': network})
        if ncs_menu:
            meas_menu.append({'id': 'ncs_%s' % network.lower(), 'label': 'NCS', 'children': ncs_menu})

        wmrr_menu = []
        for wmrr_file in wmrr_files:
            wmrr_menu.append({'id': wmrr_file.lower(), 'label': wmrr_file, 'children': '', 'type': 'wmrr', 'network': network})
        if wmrr_menu:
            meas_menu.append({'id': 'wmrr_%s' % network.lower(), 'label': 'WMRR', 'children': wmrr_menu})

        mrr_menu = []
        for mrr_file in mrr_files:
            mrr_menu.append({'id': mrr_file.lower(), 'label': mrr_file, 'children': '', 'type': 'mrr', 'network': network})
        if mrr_menu:
            meas_menu.append({'id': 'mrr_%s' % network.lower(), 'label': 'MRR', 'children': mrr_menu})

        if meas_menu:
            data.append({'id': 'meas_%s' % network.lower(), 'label': 'Measurements', 'children': meas_menu})

        return data
