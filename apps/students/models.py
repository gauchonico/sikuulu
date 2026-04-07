from django.core.validators import RegexValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone

from django.apps import apps
  # Assuming you have this model

from apps.corecode.models import AcademicTerm, StudentClass


class Student(models.Model):
    STATUS_CHOICES = [("active", "Active"), ("inactive", "Inactive")]

    GENDER_CHOICES = [("male", "Male"), ("female", "Female")]

    current_status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default="active"
    )
    registration_number = models.CharField(max_length=200, unique=True)
    surname = models.CharField(max_length=200)
    firstname = models.CharField(max_length=200)
    other_name = models.CharField(max_length=200, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default="male")
    date_of_birth = models.DateField(default=timezone.now)
    current_class = models.ForeignKey(
        StudentClass, on_delete=models.SET_NULL, blank=True, null=True
    )
    date_of_admission = models.DateField(default=timezone.now)

    mobile_num_regex = RegexValidator(
        regex="^[0-9]{10,15}$", message="Entered mobile number isn't in a right format!"
    )
    parent_mobile_number = models.CharField(
        validators=[mobile_num_regex], max_length=13, blank=True
    )

    address = models.TextField(blank=True)
    others = models.TextField(blank=True)
    passport = models.ImageField(blank=True, upload_to="students/passports/")
    
    
    def is_eligible_for_transport(self):
        # Get the models only when needed
        Invoice = apps.get_model('finance', 'Invoice')
        InvoiceItem = apps.get_model('finance', 'InvoiceItem')
        """Check if student has paid for transport services in current term"""
        
        # Get current term's invoice
        current_term = AcademicTerm.objects.filter(current=True).first()
        if not current_term:
            return False
            
        try:
            current_invoice = Invoice.objects.get(
                student=self,
                term=current_term,
                status='active'
            )
            
            # Check if transport fee exists in invoice items
            transport_item = InvoiceItem.objects.filter(
                invoice=current_invoice,
                description__icontains='transport'  # Case-insensitive search for 'transport'
            ).first()
            
            if not transport_item:
                return False
                
            # Check if the transport fee has been paid
            total_paid = current_invoice.total_amount_paid()
            total_payable = current_invoice.total_amount_payable()
            
            # Student is eligible if they've paid in full
            return total_paid >= total_payable
            
        except Invoice.DoesNotExist:
            return False

    class Meta:
        ordering = ["surname", "firstname", "other_name"]

    def __str__(self):
        return f"{self.surname} {self.firstname} {self.other_name} ({self.registration_number})"

    def get_absolute_url(self):
        return reverse("student-detail", kwargs={"pk": self.pk})
    
    


class StudentBulkUpload(models.Model):
    date_uploaded = models.DateTimeField(auto_now=True)
    csv_file = models.FileField(upload_to="students/bulkupload/")
