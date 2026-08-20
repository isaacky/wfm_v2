from django.core.management.base import BaseCommand
from revenue.models import Debtlist
import csv

class Command(BaseCommand):
    help = 'Update debt values'
    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path to file with debt values')
    def handle(self, *args, **kwargs):
        file_path = kwargs['file_path']
        with open(file_path, 'r',encoding='latin1') as f:
            reader= csv.DictReader(f)
            for row in reader:
                Debtlist.objects.create(
                    meterno=row['meterno'], accountno=row['accountno'], sector=row['sector'], zone=row['zone'], totalbalance=row['totalbalance'], overdue_amount=row['overdue_amount'], systemreading=row['systemreading'],
                    phonenumber=row['phonenumber'], location=row['location'], name=row['name'], dtadd='2024-08-08', dtupdate='2024-08-08', status=False, itin=row['itin'], xcood=row['xcood'], ycood=row['ycood'], county_id=row['county_id'],
                    region_id=row['region_id'], last_bill=row['last_bill'], amount_paid=row['amount_paid'], asigned_by_id=row['asigned_by_id'], asigned_to_id=row['asigned_to_id'], dt_asigned='2024-08-08',
                    totalbalance_new=row['totalbalance_new'], target_acc=True, classification=row['classification']
                )
        self.stdout.write(self.style.SUCCESS('debt Updated Successfully!'))

