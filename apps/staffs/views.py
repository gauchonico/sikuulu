import csv
from django.contrib.messages.views import SuccessMessageMixin
from django.forms import widgets
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views import View
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from apps.staffs.forms import BulkUploadForm, MonthlySalaryForm

from .models import MonthlySalary, Staff


class StaffListView(ListView):
    model = Staff


class StaffDetailView(DetailView):
    model = Staff
    template_name = "staffs/staff_detail.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        staff = self.object

        # Get all monthly salary records for this staff member
        monthly_salaries = MonthlySalary.objects.filter(staff=staff).order_by('-year', '-month')

        # Calculate summary information
        salary_summary = {
            'total_paid': sum(s.amount_paid for s in monthly_salaries),
            'total_deductions': sum(s.deductions for s in monthly_salaries),
            'total_balance_due': sum(s.balance_due for s in monthly_salaries),
            'salary_records': monthly_salaries
        }

        context['salary_summary'] = salary_summary
        return context


class StaffCreateView(SuccessMessageMixin, CreateView):
    model = Staff
    fields = "__all__"
    success_message = "New staff successfully added"

    def get_form(self):
        """add date picker in forms"""
        form = super(StaffCreateView, self).get_form()
        form.fields["date_of_birth"].widget = widgets.DateInput(attrs={"type": "date"})
        form.fields["date_of_admission"].widget = widgets.DateInput(
            attrs={"type": "date"}
        )
        form.fields["address"].widget = widgets.Textarea(attrs={"rows": 1})
        form.fields["others"].widget = widgets.Textarea(attrs={"rows": 1})
        return form


class StaffUpdateView(SuccessMessageMixin, UpdateView):
    model = Staff
    fields = "__all__"
    success_message = "Record successfully updated."

    def get_form(self):
        """add date picker in forms"""
        form = super(StaffUpdateView, self).get_form()
        form.fields["date_of_birth"].widget = widgets.DateInput(attrs={"type": "date"})
        form.fields["date_of_admission"].widget = widgets.DateInput(
            attrs={"type": "date"}
        )
        form.fields["address"].widget = widgets.Textarea(attrs={"rows": 1})
        form.fields["others"].widget = widgets.Textarea(attrs={"rows": 1})
        return form


class StaffDeleteView(DeleteView):
    model = Staff
    success_url = reverse_lazy("staff-list")
    
    
class MonthlySalaryListView(ListView):
    model = MonthlySalary
    template_name = "staffs/monthly_salary_list.html"
    context_object_name = "salaries"
    paginate_by = 10
    
    def get_queryset(self):
        return MonthlySalary.objects.all().select_related('staff')
    
    
class MothlySalaryDetailsView(DetailView):
    model = MonthlySalary
    template_name = "staffs/monthly_salary_detail.html"
    context_object_name =  "salary"
    
class MonthlySalaryCreateView(CreateView):
    model = MonthlySalary
    form_class = MonthlySalaryForm
    
    template = "staff/monthlysalary_form.html"
    success_url = reverse_lazy('salaries-list')
    success_message = "Monthly salary record successfully created."
    
    def form_valid(self, form):
        salary_record = form.save(commit=False)
        # Calculate the balance_due based on the base salary from the SalaryScale
        salary_record.calculate_balance_due()
        salary_record.save()
        return super(MonthlySalaryCreateView, self).form_valid(form)

class MonthSalaryUpdateView(UpdateView):
    model = MonthlySalary
    fields = ['staff','session', 'year', 'month', 'amount_paid', 'deductions', 'comments']
    template = "staff/monthlysalary_form.html"
    success_url = reverse_lazy('salaries-list')
    success_message = "Monthly salary record successfully updated."
    
    def form_valid(self, form):
        salary_record = form.save(commit=False)
        # Calculate the balance_due based on the base salary from the SalaryScale
        salary_record.calculate_balance_due()
        salary_record.save()
        return super().form_valid(form)
    
# class BulkUploadView(View):
#     form_class = BulkUploadForm
#     template_name = 'staff/bulk_upload.html'

#     def get(self, request):
#         form = self.form_class()
#         return render(request, self.template_name, {'form': form})

#     def post(self, request):
#         form = self.form_class(request.POST, request.FILES)
#         if form.is_valid():
#             file = request.FILES['file']
#             data = file.read().decode('utf-8').splitlines()
#             reader = csv.DictReader(data)

#             # Validate and process each row in the CSV
#             for row in reader:
#                 try:
#                     staff = Staff.objects.get(id=row['staff_id'])  # Adjust field name as necessary
#                     session = AcademicSession.objects.get(year=row['year'])
#                     term = AcademicTerm.objects.get(name=row['term'])  # Adjust field name as necessary

#                     MonthlySalary.objects.update_or_create(
#                         staff=staff,
#                         year=row['year'],
#                         month=row['month'],
#                         defaults={
#                             'amount_paid': row['amount_paid'],
#                             'deductions': row['deductions'],
#                             'comments': row.get('comments', '')
#                         }
#                     )
#                 except Staff.DoesNotExist:
#                     messages.error(request, f"Staff with ID {row['staff_id']} does not exist.")
#                 except AcademicSession.DoesNotExist:
#                     messages.error(request, f"Academic session {row['year']} does not exist.")
#                 except AcademicTerm.DoesNotExist:
#                     messages.error(request, f"Academic term {row['term']} does not exist.")
#                 except Exception as e:
#                     messages.error(request, f"Error processing row: {e}")

#             messages.success(request, "Bulk upload successful.")
#             return redirect('monthlysalary-list')

#         return render(request, self.template_name, {'form': form})
