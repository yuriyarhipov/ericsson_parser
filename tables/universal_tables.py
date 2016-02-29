from files.models import GsmGsm, LteLte, WcdmaWcdma, LteGsm, GsmLte, WcdmaLte, GsmWcdma, WcdmaGsm

class UniversalTable:

    def __init__(self, relation):
        self.relation = relation

    def get_table(self):
        columns = []
        if self.relation == 'gsmgsm':
            columns = ['CellSource', 'CellTarget', 'Status']

        elif self.relation in ['ltelte', 'wcdmawcdma', 'wcdmalte', 'ltewcdma']:
            columns = [
                'RncSource',
                'UtrancellSource',
                'CarrierSource',
                'RncTarget',
                'UtrancellTarget',
                'CarrierTarget',
                'Status']

        elif self.relation == 'wcdmawcdma':
            columns = [
                'RncSource',
                'UtrancellSource',
                'CarrierSource',
                'RncTarget',
                'UtrancellTarget',
                'CarrierTarget',
                'Status']

        elif self.relation in ['gsmwcdma', 'gsmlte']:
            columns = [
                'CellSource',
                'RncTarget',
                'UtrancellTarget',
                'CarrierTarget',
                'Status']

        elif self.relation in ['wcdmagsm', 'ltegsm']:
            columns = [
                'RncSource',
                'UtrancellSource',
                'CarrierSource',
                'CellTarget',
                'Status']

        data = []

        return columns, data

