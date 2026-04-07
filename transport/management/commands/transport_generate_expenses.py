from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker
from django.db import models
import random
from datetime import timedelta

class Command(BaseCommand):
    help = 'Generate fake transport expenditures'

    def add_arguments(self, parser):
        parser.add_argument('count', type=int, help='Number of expenditures to generate')
        parser.add_argument(
            '--months',
            type=int,
            default=6,
            help='Generate expenses for the last n months (default: 6)'
        )

    def handle(self, *args, **kwargs):
        fake = Faker()
        count = kwargs['count']
        months = kwargs['months']

        # Import here to avoid circular imports
        from transport.models import Vehicle, TransportExpenditure

        # Get all vehicles
        vehicles = list(Vehicle.objects.all())
        if not vehicles:
            self.stdout.write(self.style.ERROR('No vehicles found. Please create vehicles first.'))
            return

        # Common expense types with their categories and amount ranges
        expense_types = [
            ('FUEL', 'Fuel purchase for vehicle', (5000, 20000)),
            ('FUEL', 'Emergency refueling', (2000, 5000)),
            ('INSURANCE', 'Annual vehicle insurance', (50000, 200000)),
            ('INSURANCE', 'Third-party insurance renewal', (30000, 80000)),
            ('SALARY', 'Driver monthly salary', (30000, 70000)),
            ('SALARY', 'Transport staff allowance', (10000, 30000)),
            ('PERMIT', 'Vehicle registration renewal', (20000, 40000)),
            ('PERMIT', 'Route permit fee', (15000, 35000)),
            ('PARTS', 'Tire replacement', (15000, 60000)),
            ('PARTS', 'Brake system repair', (10000, 40000)),
            ('PARTS', 'Engine oil change', (5000, 15000)),
            ('TOOLS', 'Vehicle maintenance tools', (5000, 25000)),
            ('TOOLS', 'Safety equipment', (3000, 10000)),
            ('MISC', 'Vehicle cleaning service', (2000, 5000)),
            ('MISC', 'Emergency repairs', (5000, 25000))
        ]

        # Staff members for approval and payment
        staff_members = [
            'John Smith', 'Mary Johnson', 'Robert Wilson', 
            'Sarah Brown', 'Michael Davis', 'Elizabeth Taylor'
        ]

        # Generate expenditures
        for i in range(count):
            # Select random vehicle and expense type
            vehicle = random.choice(vehicles)
            category, description_template, amount_range = random.choice(expense_types)
            
            # Generate a date within the specified months
            date = fake.date_between(
                start_date=timezone.now() - timedelta(days=30 * months),
                end_date=timezone.now()
            )

            # Generate description with vehicle details
            description = f"{description_template} - {vehicle.license_plate}"
            if category == 'FUEL':
                description += f" ({random.randint(20, 60)} liters)"
            
            # Create the expenditure record
            expenditure = TransportExpenditure.objects.create(
                vehicle=vehicle,
                category=category,
                amount=random.randint(*amount_range),
                date=date,
                description=description,
                receipt_number=f"RCP-{fake.unique.random_number(digits=6)}",
                paid_by=random.choice(staff_members),
                approved_by=random.choice(staff_members),
            )

            self.stdout.write(
                self.style.SUCCESS(
                    f'Created expenditure: {expenditure.expenditure_number} - '
                    f'{expenditure.category} - ₦{expenditure.amount:,.2f} for {vehicle}'
                )
            )

        total_amount = TransportExpenditure.objects.filter(
            date__gte=timezone.now() - timedelta(days=30 * months)
        ).aggregate(total=models.Sum('amount'))['total'] or 0

        self.stdout.write(
            self.style.SUCCESS(
                f'\nSuccessfully generated {count} transport expenditures\n'
                f'Total amount: ₦{total_amount:,.2f}\n'
                f'Period: Last {months} months'
            )
        )