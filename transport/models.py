from django.db import models
from django.utils import timezone

from apps.students.models import Student

# Create your models here.

class Vehicle(models.Model):
    license_plate = models.CharField(max_length=10, unique=True)
    capacity = models.PositiveIntegerField()
    driver = models.ForeignKey('Driver', on_delete=models.SET_NULL, null=True)
    route = models.ForeignKey('Route', on_delete=models.SET_NULL, null=True)
    last_maintenance_date = models.DateField()
    
    def __str__(self):
        return self.license_plate
    
    def get_next_maintenance_date(self):
        """Returns the nearest upcoming maintenance date"""
        upcoming_maintenance = self.maintenance_records.filter(
            next_service_date__gt=timezone.now().date()
        ).order_by('next_service_date').first()
        return upcoming_maintenance.next_service_date if upcoming_maintenance else None
    
    def get_total_maintenance_cost(self, start_date=None, end_date=None):
        """Calculate total maintenance costs for a given period"""
        records = self.maintenance_records.all()
        if start_date:
            records = records.filter(service_date__gte=start_date)
        if end_date:
            records = records.filter(service_date__lte=end_date)
        return records.aggregate(total_cost=models.Sum('cost'))['total_cost'] or 0

class Driver(models.Model):
    name = models.CharField(max_length=100)
    license_number = models.CharField(max_length=10, unique=True)
    contact_info = models.TextField()
    
    def __str__(self):
        # Fix: Return a single string instead of a tuple
        return f"{self.name} ({self.license_number})"
    
    
class Route(models.Model):
    name = models.CharField(max_length=100)
    start_point = models.CharField(max_length=100)
    end_point = models.CharField(max_length=100)
    stops = models.TextField()  # Consider using JSONField for structured stops data
    
    def __str__(self):
        # Fix: Return a single string instead of a tuple
        return f"{self.name}: {self.start_point} to {self.end_point}"

# Add new TransportFee model
class TransportFee(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    fee_amount = models.DecimalField(max_digits=10, decimal_places=2)
    term = models.CharField(max_length=20)  # e.g., 'Term 1 2024', 'Monthly', etc.
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.route.name} - {self.fee_amount} ({self.term})"
    
    
class StudentTransportAssignment(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive')
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    route = models.ForeignKey(Route, on_delete=models.CASCADE, null=True, blank=True)
    pickup_point = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['route', 'student']
        # Ensure a student can only be assigned to one active route at a time
        constraints = [
            models.UniqueConstraint(
                fields=['student'],
                condition=models.Q(status='active'),
                name='unique_active_student_assignment'
            )
        ]

    def __str__(self):
        return f"{self.student} - Route: {self.route.name} ({self.pickup_point})"

    def save(self, *args, **kwargs):
        # If status is being changed to inactive, set end_date
        if self.pk:
            old_instance = StudentTransportAssignment.objects.get(pk=self.pk)
            if old_instance.status == 'active' and self.status == 'inactive':
                self.end_date = timezone.now().date()
        super().save(*args, **kwargs)
    

class TransportPayment(models.Model):
    assignment = models.ForeignKey(StudentTransportAssignment, on_delete=models.CASCADE)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField()
    payment_method = models.CharField(max_length=50)  # e.g., 'Cash', 'Bank Transfer', etc.
    reference_number = models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        return f"Payment for {self.assignment.student} - {self.amount_paid}"

class MaintenanceRecord(models.Model):
    MAINTENANCE_TYPES = [
        ('ROUTINE', 'Routine Service'),
        ('REPAIR', 'Repair Work'),
        ('INSPECTION', 'Vehicle Inspection'),
        ('TIRE', 'Tire Service'),
        ('OTHER', 'Other Maintenance')
    ]
    
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='maintenance_records')
    service_date = models.DateField()
    maintenance_type = models.CharField(max_length=20, choices=MAINTENANCE_TYPES)
    mechanic_name = models.CharField(max_length=100)
    mechanic_contact = models.CharField(max_length=100, blank=True)
    workshop_name = models.CharField(max_length=100)
    description = models.TextField()
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    next_service_date = models.DateField(null=True, blank=True)
    odometer_reading = models.PositiveIntegerField(help_text="Vehicle mileage at service time")
    
    def __str__(self):
        return f"{self.vehicle.license_plate} - {self.maintenance_type} on {self.service_date}"


class TransportExpenditure(models.Model):
    EXPENSE_CATEGORIES = [
        ('FUEL', 'Fuel Cost'),
        ('INSURANCE', 'Vehicle Insurance'),
        ('SALARY', 'Staff Salary'),
        ('PERMIT', 'Vehicle Permits/Licenses'),
        ('PARTS', 'Spare Parts'),
        ('TOOLS', 'Tools and Equipment'),
        ('MISC', 'Miscellaneous')
    ]
    
    expenditure_number = models.CharField(max_length=20, unique=True, editable=False, null=True, blank=True)
    date = models.DateField(default=timezone.now)
    category = models.CharField(max_length=20, choices=EXPENSE_CATEGORIES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    vehicle = models.ForeignKey(
        Vehicle, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        help_text="Leave blank if expense is not vehicle-specific"
    )
    description = models.TextField()
    receipt_number = models.CharField(max_length=50, blank=True)
    paid_by = models.CharField(max_length=100)
    approved_by = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.expenditure_number:
            # Get the current year and month
            year = timezone.now().strftime('%Y')
            month = timezone.now().strftime('%m')
            
            # Get the last expenditure number for this year/month
            last_expenditure = TransportExpenditure.objects.filter(
                expenditure_number__startswith=f'EXP-{year}{month}'
            ).order_by('-expenditure_number').first()
            
            if last_expenditure:
                # Extract the last sequence number and increment it
                last_sequence = int(last_expenditure.expenditure_number[-4:])
                new_sequence = str(last_sequence + 1).zfill(4)
            else:
                # Start with 0001 if no previous expenditure exists
                new_sequence = '0001'
            
            # Generate the new expenditure number
            self.expenditure_number = f'EXP-{year}{month}-{new_sequence}'
        
        super().save(*args, **kwargs)

    def __str__(self):
        vehicle_info = f" - {self.vehicle.license_plate}" if self.vehicle else ""
        return f"{self.expenditure_number} - {self.category} - {self.date}{vehicle_info}"

    class Meta:
        ordering = ['-date', '-expenditure_number']
        verbose_name = 'Transport Expenditure'
        verbose_name_plural = 'Transport Expenditures'
        
    @property
    def formatted_amount(self):
        """Returns the amount formatted with currency symbol"""
        return f"UGX{self.amount:,.2f}"