from django.urls import path

from .views import (
    MonthSalaryUpdateView,
    MonthlySalaryCreateView,
    MonthlySalaryListView,
    MothlySalaryDetailsView,
    StaffCreateView,
    StaffDeleteView,
    StaffDetailView,
    StaffListView,
    StaffUpdateView,
)

urlpatterns = [
    path("list/", StaffListView.as_view(), name="staff-list"),
    path("<int:pk>/", StaffDetailView.as_view(), name="staff-detail"),
    path("create/", StaffCreateView.as_view(), name="staff-create"),
    path("<int:pk>/update/", StaffUpdateView.as_view(), name="staff-update"),
    path("<int:pk>/delete/", StaffDeleteView.as_view(), name="staff-delete"),
    # Salaries Urls 
    path("salaries/", MonthlySalaryListView.as_view(), name="salaries-list"),
    path("salary-detail/<int:pk>/",MothlySalaryDetailsView.as_view(), name="salary-detail"),
    path("salary-update/<int:pk>/", MonthSalaryUpdateView.as_view(), name="salary-update" ),
    path("salary-add/", MonthlySalaryCreateView.as_view(), name="new-salary"),
]
