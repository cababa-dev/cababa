from django.urls import path

from . import views

app_name = 'staff'

urlpatterns = [
    path('', views.StaffTopView.as_view(), name='top'),
    path('login/', views.StaffLoginView.as_view(), name='login'),
    path('logout/', views.StaffLogoutView.as_view(), name='logout'),
    path('signup/', views.StaffSignupView.as_view(), name='signup'),
    path('confirm/', views.SignupConfirmView.as_view(), name='signup_confirm'),
    path('me/edit/', views.StaffEditMeView.as_view(), name='edit_me'),

    path('staff/', views.StaffListView.as_view(), name='staff_list'),
    path('staff/new', views.StaffCreateView.as_view(), name='staff_create'),
    path('staff/<str:staff_id>/', views.StaffDetailView.as_view(), name='staff_detail'),
    path('staff/<str:staff_id>/edit', views.StaffEditView.as_view(), name='staff_edit'),
    path('staff/<str:staff_id>/delete', views.StaffDeleteView.as_view(), name='staff_delete'),

    path('hostess/', views.HostessListView.as_view(), name='hostess_list'),
    path('hostess/new', views.HostessCreateView.as_view(), name='hostess_create'),
    path('hostess/invite', views.HostessInviteView.as_view(), name='hostess_invite'),
    path('hostess/<str:hostess_id>/', views.HostessDetailView.as_view(), name='hostess_detail'),
    path('hostess/<str:hostess_id>/edit', views.HostessEditView.as_view(), name='hostess_edit'),
]