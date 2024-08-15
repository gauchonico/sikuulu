from django.contrib import admin

from apps.staffs.models import *

# Register your models here.

admin.site.register(Staff)
admin.site.register(SalaryScale)
admin.site.register(MonthlySalary)
