from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.students.models import Student
from apps.corecode.models import AcademicSession, AcademicTerm

from apps.finance.models import Invoice, InvoiceItem, Receipt
import random

class Command(BaseCommand):
    help = 'Generates fake invoices with transport fees'

    def add_arguments(self, parser):
        parser.add_argument('count', type=int, help='Number of invoices to generate')

    def handle(self, *args, **kwargs):
        count = kwargs['count']
        
        # Get required related objects
        students = Student.objects.filter(current_status='active')
        if not students:
            self.stdout.write(self.style.ERROR('No active students found'))
            return

        session = AcademicSession.objects.filter(current=True).first()
        if not session:
            self.stdout.write(self.style.ERROR('No current academic session found'))
            return

        term = AcademicTerm.objects.filter(current=True).first()
        if not term:
            self.stdout.write(self.style.ERROR('No current academic term found'))
            return

        for i in range(count):
            student = random.choice(students)
            
            # Create invoice
            invoice = Invoice.objects.create(
                student=student,
                session=session,
                term=term,
                class_for=student.current_class,
                status='active'
            )

            # Create invoice items including transport fee
            items = [
                ('Tuition Fee', random.randint(50000, 100000)),
                ('Transport Fee', random.randint(10000, 20000)),
                ('Books', random.randint(5000, 15000))
            ]

            for desc, amount in items:
                InvoiceItem.objects.create(
                    invoice=invoice,
                    description=desc,
                    amount=amount
                )

            # Randomly mark some invoices as fully paid
            if random.choice([True, False]):
                
                total = sum(item.amount for item in invoice.invoiceitem_set.all())
                Receipt.objects.create(
                    invoice=invoice,
                    amount_paid=total,
                    date_paid=timezone.now(),
                    comment='Full payment'
                )

            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully created invoice for: {student.surname} {student.firstname}'
                )
            )

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully generated {count} invoices'
            )
        ) 