from django.core.management.base import BaseCommand
from django.apps import apps
from faker import Faker
import random

class Command(BaseCommand):
    help = 'Bulk assign eligible students to routes'

    def add_arguments(self, parser):
        parser.add_argument('count', type=int, help='Number of assignments to generate')

    def handle(self, *args, **kwargs):
        fake = Faker()
        count = kwargs['count']

        # Get models using apps to avoid circular imports
        Student = apps.get_model('students', 'Student')
        Invoice = apps.get_model('finance', 'Invoice')
        InvoiceItem = apps.get_model('finance', 'InvoiceItem')
        Route = apps.get_model('transport', 'Route')
        StudentTransportAssignment = apps.get_model('transport', 'StudentTransportAssignment')

        # Get all routes
        routes = list(Route.objects.all())
        if not routes:
            self.stdout.write(self.style.ERROR('No routes found. Please create routes first.'))
            return

        # Get eligible students (those who have paid transport fees)
        eligible_students = []
        for student in Student.objects.filter(current_status='active'):
            try:
                current_invoice = Invoice.objects.filter(
                    student=student,
                    status='active'
                ).latest('id')
                
                transport_item = InvoiceItem.objects.filter(
                    invoice=current_invoice,
                    description__icontains='transport'
                ).exists()
                
                if transport_item and current_invoice.total_amount_paid() >= current_invoice.total_amount_payable():
                    eligible_students.append(student)
                    
            except Invoice.DoesNotExist:
                continue

        if not eligible_students:
            self.stdout.write(self.style.ERROR('No eligible students found'))
            return

        # Create assignments
        assignments_created = 0
        for _ in range(count):
            if not eligible_students:  # Stop if we run out of eligible students
                break
                
            student = random.choice(eligible_students)
            route = random.choice(routes)
            
            # Remove student from eligible list to avoid duplicate assignments
            eligible_students.remove(student)
            
            try:
                assignment = StudentTransportAssignment.objects.create(
                    student=student,
                    route=route,
                    pickup_point=random.choice(route.stops.split(',')).strip(),
                    status='active'
                )
                assignments_created += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Assigned {student.surname} {student.firstname} to route {route.name}'
                    )
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f'Failed to assign {student.surname} {student.firstname}: {str(e)}'
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {assignments_created} transport assignments'
            )
        ) 