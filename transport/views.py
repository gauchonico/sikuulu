from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView, ListView, View, CreateView, DeleteView, UpdateView, TemplateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum, Count, Q
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.apps import apps
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied

from transport import models
from transport.forms import *
from transport.models import Driver, Route, StudentTransportAssignment, Vehicle

# Create your views here.

class TransportListView(LoginRequiredMixin, ListView):
    model = StudentTransportAssignment
    template_name = "transport/transport.html"
    
class TransportDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'transport/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.now().date()
        thirty_days_ago = today - timedelta(days=30)

        # Vehicle Statistics
        context['total_vehicles'] = Vehicle.objects.count()
        context['active_vehicles'] = Vehicle.objects.filter(driver__isnull=False).count()
        
        # Driver Statistics
        context['total_drivers'] = Driver.objects.count()
        
        # Student Transport Statistics
        context['total_students_assigned'] = StudentTransportAssignment.objects.filter(
            status='active'
        ).count()
        
        # Maintenance Statistics
        context['pending_maintenance'] = MaintenanceRecord.objects.filter(
            next_service_date__lte=today
        ).select_related('vehicle').order_by('next_service_date')[:5]
        
        # Recent Transport Assignments
        context['recent_assignments'] = StudentTransportAssignment.objects.filter(
            status='active'
        ).select_related('student', 'route').order_by('-start_date')[:2]
        
        # Recent Expenditures
        context['recent_expenditures'] = TransportExpenditure.objects.filter(
            date__gte=thirty_days_ago
        ).order_by('-date')[:5]
        
        # Monthly Expenditure Summary
        monthly_expenses = TransportExpenditure.objects.filter(
            date__gte=thirty_days_ago
        )
        context['monthly_expenses'] = {
            'total_amount': monthly_expenses.aggregate(total=Sum('amount'))['total'] or 0,
            'by_type': monthly_expenses.values('category').annotate(
                total=Sum('amount')
            ).order_by('-total'),
            'fuel_costs': monthly_expenses.filter(
                category='FUEL'
            ).aggregate(total=Sum('amount'))['total'] or 0,
            'maintenance_costs': monthly_expenses.filter(
                category='MAINTENANCE'
            ).aggregate(total=Sum('amount'))['total'] or 0
        }
        
        # Route Statistics
        context['routes'] = Route.objects.annotate(
            student_count=Count('studenttransportassignment', 
                            filter=Q(studenttransportassignment__status='active'))
        )
        
        # Vehicles Requiring Attention
        context['vehicles_attention'] = Vehicle.objects.filter(
            Q(last_maintenance_date__lte=today - timedelta(days=90)) |
            Q(maintenance_records__next_service_date__lte=today)
        ).distinct()

        return context
    
    
# Driver Views
class DriverListView(LoginRequiredMixin, ListView):
    model = Driver
    template_name = 'transport/driver_list.html'
    context_object_name = 'drivers'
    
class DriverCreateView(CreateView):
    model = Driver
    form_class = DriverForm
    template_name = 'transport/driver_form.html'
    success_url = reverse_lazy('transport:transport-list')  # Adjust to your URL name
    
    
    def form_valid(self, form):
        messages.success(self.request, 'Driver added successfully!')
        return super().form_valid(form)

class DriverUpdateView(LoginRequiredMixin, UpdateView):
    model = Driver
    form_class = DriverForm
    template_name = 'transport/driver_form.html'
    success_url = reverse_lazy('driver-list')
    
# Vehicle Views
class VehicleListView(LoginRequiredMixin, ListView):
    model = Vehicle
    template_name = 'transport/vehicle_list.html'
    context_object_name = 'vehicles'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = VehicleForm()  # Add this line
        return context
    
class VehicleCreateView(CreateView):
    model = Vehicle
    form_class = VehicleForm
    template_name = 'transport/vehicle_form.html'
    success_url = reverse_lazy('transport:vehicle-list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Vehicle added successfully!')
        return super().form_valid(form)

class VehicleUpdateView(LoginRequiredMixin, UpdateView):
    model = Vehicle
    form_class = VehicleForm
    template_name = 'transport/vehicle_form.html'
    success_url = reverse_lazy('vehicle-list')
    

# Route Views
class RoutesView(LoginRequiredMixin, ListView):
    model = Route
    template_name = "transport/route_list.html"
    context_object_name = 'routes'
    success_url = reverse_lazy('route-list')
    
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = RouteForm()  # Add this line
        return context
    
class RouteCreateView(LoginRequiredMixin, CreateView):
    model = Route
    form_class = RouteForm
    template_name = 'transport/route_form.html'
    success_url = reverse_lazy('route-list')

class RouteUpdateView(LoginRequiredMixin, UpdateView):
    model = Route
    form_class = RouteForm
    template_name = 'transport/route_form.html'
    success_url = reverse_lazy('transport:route-list')
    
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            form = self.get_form()
            form_html = render_to_string(
                'transport/route_form.html',  # Use the new template
                {'form': form},
                request=request
            )
            return JsonResponse({
                'form_html': form_html
            })
        return super().get(request, *args, **kwargs)
    
# Student Transport Assignment Views
class StudentTransportListView(LoginRequiredMixin, ListView):
    model = StudentTransportAssignment
    template_name = 'transport/student_transport_list.html'
    context_object_name = 'assignments'

class EligibleStudentListView(LoginRequiredMixin, ListView):
    template_name = 'transport/eligible_students_list.html'
    context_object_name = 'eligible_students'

    def get_queryset(self):
        Student = apps.get_model('students', 'Student')
        Invoice = apps.get_model('finance', 'Invoice')
        InvoiceItem = apps.get_model('finance', 'InvoiceItem')
        
        # Get all active students
        students = Student.objects.filter(current_status='active').prefetch_related('studenttransportassignment_set').order_by('surname', 'firstname')
        
        # Get students with paid transport fees
        eligible_students = []
        for student in students:
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
                
        return eligible_students

class StudentTransportCreateView(LoginRequiredMixin, CreateView):
    model = StudentTransportAssignment
    form_class = StudentTransportAssignmentForm
    template_name = 'transport/student_transport_form.html'
    success_url = reverse_lazy('student-transport-list')
    
    def dispatch(self, request, *args, **kwargs):
        # Get Student model using apps to avoid circular import
        Student = apps.get_model('students', 'Student')
        self.student = get_object_or_404(Student, pk=self.kwargs.get('student_id'))
        
        # Check if student has paid for transport
        if not self.check_transport_eligibility():
            raise PermissionDenied("Student has not paid for transport services")
        return super().dispatch(request, *args, **kwargs)

    def check_transport_eligibility(self):
        # Get models using apps to avoid circular import
        Invoice = apps.get_model('finance', 'Invoice')
        InvoiceItem = apps.get_model('finance', 'InvoiceItem')
        
        try:
            current_invoice = Invoice.objects.filter(
                student=self.student,
                status='active'
            ).latest('id')
            
            # Check if transport fee exists and is paid
            transport_item = InvoiceItem.objects.filter(
                invoice=current_invoice,
                description__icontains='transport'
            ).exists()
            
            if transport_item:
                return current_invoice.total_amount_paid() >= current_invoice.total_amount_payable()
            return False
            
        except Invoice.DoesNotExist:
            return False

    def form_valid(self, form):
        # Set the student before saving the form
        form.instance.student = self.student
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['student'] = self.student
        return context

# Maintenance Record Views
class MaintenanceRecordListView(LoginRequiredMixin, ListView):
    model = MaintenanceRecord
    template_name = 'transport/maintenance_list.html'
    context_object_name = 'maintenance_records'

    def get_queryset(self):
        vehicle_id = self.kwargs.get('vehicle_id')
        if vehicle_id:
            return MaintenanceRecord.objects.filter(vehicle_id=vehicle_id)
        return MaintenanceRecord.objects.all()

class MaintenanceRecordCreateView(LoginRequiredMixin, CreateView):
    model = MaintenanceRecord
    form_class = MaintenanceRecordForm
    template_name = 'transport/maintenance_form.html'
    success_url = reverse_lazy('maintenance-list')

# Transport Expenditure Views
class TransportExpenditureListView(LoginRequiredMixin, ListView):
    model = TransportExpenditure
    template_name = 'transport/expenditure_list.html'
    context_object_name = 'expenditures'

class TransportExpenditureCreateView(LoginRequiredMixin, CreateView):
    model = TransportExpenditure
    form_class = TransportExpenditureForm
    template_name = 'transport/expenditure_form.html'
    success_url = reverse_lazy('expenditure-list')
    
    