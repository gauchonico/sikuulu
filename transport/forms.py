from django import forms
from .models import (
    Driver, Vehicle, Route, StudentTransportAssignment,
    MaintenanceRecord, TransportExpenditure, TransportFee
)


class DriverForm(forms.ModelForm):
    class Meta:
        model = Driver
        fields = ['name', 'license_number', 'contact_info']
        
class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = ['license_plate', 'capacity', 'driver', 'route', 'last_maintenance_date']
        widgets = {
            'license_plate': forms.TextInput(attrs={'class': 'form-control'}),
            'capacity': forms.NumberInput(attrs={'class': 'form-control'}),
            'driver': forms.Select(attrs={'class': 'form-control'}),
            'route': forms.Select(attrs={'class': 'form-control'}),
            'last_maintenance_date': forms.DateInput(attrs={'type': 'date'})
        }

class RouteForm(forms.ModelForm):
    # Add a help text for stops field
    stops = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Enter stops separated by commas (e.g., Stop 1, Stop 2, Stop 3)'
        }),
        help_text='Enter multiple stops separated by commas'
    )
    class Meta:
        model = Route
        fields = ['name', 'start_point', 'end_point', 'stops']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter route name'
            }),
            'start_point': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter start point'
            }),
            'end_point': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter end point'
            }),
            
        }
        
    def clean_stops(self):
        stops = self.cleaned_data['stops']
        # Split by comma and strip whitespace from each stop
        stop_list = [stop.strip() for stop in stops.split(',') if stop.strip()]
        # Join back with commas for storage
        return ', '.join(stop_list)

class StudentTransportAssignmentForm(forms.ModelForm):
    class Meta:
        model = StudentTransportAssignment
        fields = ['student', 'route', 'pickup_point', 'status', 'notes']
        widgets = {
            'student': forms.Select(attrs={'class': 'form-control'}),
            'route': forms.Select(attrs={'class': 'form-control'}),
            'pickup_point': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter pickup point'
            }),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter any additional notes'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make some fields optional
        self.fields['notes'].required = False
        
        # Add help texts
        self.fields['pickup_point'].help_text = 'Specify the exact location where the student will be picked up'
        self.fields['status'].help_text = 'Set to inactive to end the transport assignment'

class MaintenanceRecordForm(forms.ModelForm):
    class Meta:
        model = MaintenanceRecord
        fields = [
            'vehicle', 'service_date', 'maintenance_type', 'mechanic_name',
            'mechanic_contact', 'workshop_name', 'description', 'cost',
            'next_service_date', 'odometer_reading'
        ]
        widgets = {
            'service_date': forms.DateInput(attrs={'type': 'date'}),
            'next_service_date': forms.DateInput(attrs={'type': 'date'})
        }

class TransportExpenditureForm(forms.ModelForm):
    class Meta:
        model = TransportExpenditure
        fields = [
            'date', 'category', 'amount', 'vehicle', 'description',
            'receipt_number', 'paid_by', 'approved_by'
        ]
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'})
        }