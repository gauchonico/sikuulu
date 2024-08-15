from django.core.validators import RegexValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone

from apps.corecode.models import AcademicSession


class SalaryScale(models.Model):
    name = models.CharField(max_length=100)  # e.g., Senior Teacher, Cleaner, etc.
    base_salary = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name

class Staff(models.Model):
    STATUS = [("active", "Active"), ("inactive", "Inactive")]

    GENDER = [("male", "Male"), ("female", "Female")]

    current_status = models.CharField(max_length=10, choices=STATUS, default="active")
    surname = models.CharField(max_length=200)
    firstname = models.CharField(max_length=200)
    other_name = models.CharField(max_length=200, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER, default="male")
    date_of_birth = models.DateField(default=timezone.now)
    date_of_admission = models.DateField(default=timezone.now)
    salary_scale = models.ForeignKey(SalaryScale, on_delete=models.CASCADE, null=True, blank=True)

    mobile_num_regex = RegexValidator(
        regex="^[0-9]{10,15}$", message="Entered mobile number isn't in a right format!"
    )
    mobile_number = models.CharField(
        validators=[mobile_num_regex], max_length=13, blank=True
    )

    address = models.TextField(blank=True)
    others = models.TextField(blank=True)

    def __str__(self):
        return f"{self.surname} {self.firstname} {self.other_name}"

    def get_absolute_url(self):
        return reverse("staff-detail", kwargs={"pk": self.pk})
    
class MonthlySalary(models.Model):
    MONTHS = [
        (1, "January"),
        (2, "February"),
        (3, "March"),
        (4, "April"),
        (5, "May"),
        (6, "June"),
        (7, "July"),
        (8, "August"),
        (9, "September"),
        (10, "October"),
        (11, "November"),
        (12, "December"),
    ]
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    session = models.ForeignKey(AcademicSession, on_delete=models.CASCADE,null=True, blank=True)
    year = models.IntegerField(default=timezone.now().year)
    month = models.IntegerField(choices=MONTHS)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    balance_due = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    comments = models.TextField(blank=True)
    
    class Meta:
        unique_together = ('staff', 'year', 'month')
        ordering = ['-session','-year', '-month', 'staff']

    def __str__(self):
        return f"{self.staff} - {self.get_month_display()} {self.year} ({self.session})"

    @property
    def base_salary(self):
        return self.staff.salary_scale.base_salary
    
    def calculate_balance_due(self):
        self.balance_due = self.base_salary - self.amount_paid - self.deductions
        return self.balance_due
    
    def save(self, *args, **kwargs):
        self.calculate_balance_due()
        super(MonthlySalary, self).save(*args, **kwargs)


    

