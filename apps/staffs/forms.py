from django import forms

from apps.corecode.models import AcademicSession
from apps.staffs.models import MonthlySalary

class BulkUploadForm(forms.Form):
    file = forms.FileField()
    
class MonthlySalaryForm(forms.ModelForm):
    class Meta:
        model = MonthlySalary
        fields = ['staff','session', 'year', 'month', 'amount_paid', 'deductions', 'comments']

    def __init__(self, *args, **kwargs):
        # Initialize the form
        super(MonthlySalaryForm, self).__init__(*args, **kwargs)

        # Set the current session as the default value for the session field
        if not self.instance.pk:  # Check if the instance is being created, not updated
            current_session = AcademicSession.objects.get(current=True)
            self.fields['session'].initial = current_session