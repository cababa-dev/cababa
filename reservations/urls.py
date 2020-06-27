from django.urls import path

from . import views

app_name = 'reservations'

urlpatterns = [
    path('hostess/', views.HostessListView.as_view(), name='hostess_list'),
    path('hostess/search/', views.HostessSearchView.as_view(), name='hostess_search'),
    path('hostess/detail/', views.HostessDetailTestView.as_view(), name='hostess_detail_test'),
    path('hostess/<str:hostess_id>/', views.HostessDetailView.as_view(), name='hostess_detail'),
    path('<str:available_id>/new/', views.CreateReserveView.as_view(), name='create_reserve'),
    path('<str:reservation_id>/done/', views.DoneReserveView.as_view(), name='done_reserve'),
    path('<str:reservation_id>/pay/authorize/', views.ReserveAuthorizeView.as_view(), name='pay_authorize'),
    path('<str:reservation_id>/pay/cancel/', views.ReserveCancelView.as_view(), name='pay_cancel'),
]