from django.urls import path

from . import views

app_name = 'staff'

urlpatterns = [
    path('', views.StaffTopView.as_view(), name='top'),
    path('login/', views.StaffLoginView.as_view(), name='login'),
    path('logout/', views.StaffLogoutView.as_view(), name='logout'),
    path('signup/', views.StaffSignupView.as_view(), name='signup'),
    path('confirm/', views.SignupConfirmView.as_view(), name='signup_confirm'),
    path('staff/', views.StaffListView.as_view(), name='staff_list'),
    path('staff/new', views.StaffCreateView.as_view(), name='staff_create'),
    path('staff/<str:staff_id>/', views.StaffDetailView.as_view(), name='staff_detail'),
    path('staff/<str:staff_id>/edit', views.StaffEditView.as_view(), name='staff_edit'),
    path('staff/<str:staff_id>/delete', views.StaffDeleteView.as_view(), name='staff_delete'),
]