from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker

import random
from apps.students.models import Student, StudentClass
from apps.corecode.models import AcademicTerm


class Command(BaseCommand):
    help = 'Generates fake student data'

    def add_arguments(self, parser):
        parser.add_argument('count', type=int, help='Number of students to generate')

    def handle(self, *args, **kwargs):
        fake = Faker()
        count = kwargs['count']
        
        # Get all available classes
        classes = list(StudentClass.objects.all())
        if not classes:
            self.stdout.write(self.style.ERROR('No student classes found. Please create some classes first.'))
            return

        for i in range(count):
            # Generate a unique registration number
            while True:
                reg_number = f"STD{fake.unique.random_number(digits=4)}"
                if not Student.objects.filter(registration_number=reg_number).exists():
                    break

            # Create student
            student = Student.objects.create(
                current_status=random.choice(['active', 'inactive']),
                registration_number=reg_number,
                surname=fake.last_name(),
                firstname=fake.first_name(),
                other_name=fake.first_name() if random.choice([True, False]) else '',
                gender=random.choice(['male', 'female']),
                date_of_birth=fake.date_of_birth(minimum_age=5, maximum_age=18),
                current_class=random.choice(classes),
                date_of_admission=fake.date_between(start_date='-3y', end_date='today'),
                parent_mobile_number=f"0{fake.random_number(digits=10)}",
                address=fake.address(),
                others=fake.text(max_nb_chars=100) if random.choice([True, False]) else ''
            )

            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully created student: {student.surname} {student.firstname} ({student.registration_number})'
                )
            )

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully generated {count} students'
            )
        ) 