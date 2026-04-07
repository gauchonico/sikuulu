from django.urls import path
from . import views

app_name = 'transport'

urlpatterns = [
    
    # Dashboard URL
    path('', views.TransportDashboardView.as_view(), name='dashboard'),
    # Driver URLs
    path('drivers/', views.DriverListView.as_view(), name='driver-list'),
    path('driver/add/', views.DriverCreateView.as_view(), name='driver-add'),
    path('driver/<int:pk>/edit/', views.DriverUpdateView.as_view(), name='driver-edit'),

    # Vehicle URLs
    path('vehicles/', views.VehicleListView.as_view(), name='vehicle-list'),
    path('vehicle/add/', views.VehicleCreateView.as_view(), name='vehicle-add'),
    path('vehicle/<int:pk>/edit/', views.VehicleUpdateView.as_view(), name='vehicle-edit'),

    # Route URLs
    path('routes/', views.RoutesView.as_view(), name='route-list'),
    path('route/add/', views.RouteCreateView.as_view(), name='route-add'),
    path('route/<int:pk>/edit/', views.RouteUpdateView.as_view(), name='route-edit'),

    # Student Transport Assignment URLs
    path('assignments/', views.StudentTransportListView.as_view(), name='student-transport-list'),
    path('student/<int:student_id>/assign/', views.StudentTransportCreateView.as_view(), name='student-transport-add'),
    path('students/eligible/', views.EligibleStudentListView.as_view(), name='eligible-students-list'),

    # Maintenance Record URLs
    path('maintenance/', views.MaintenanceRecordListView.as_view(), name='maintenance-list'),
    path('maintenance/add/', views.MaintenanceRecordCreateView.as_view(), name='maintenance-add'),
    path('vehicle/<int:vehicle_id>/maintenance/', views.MaintenanceRecordListView.as_view(), name='vehicle-maintenance-list'),

    # Transport Expenditure URLs
    path('expenditures/', views.TransportExpenditureListView.as_view(), name='expenditure-list'),
    path('expenditure/add/', views.TransportExpenditureCreateView.as_view(), name='expenditure-add'),

    
]
