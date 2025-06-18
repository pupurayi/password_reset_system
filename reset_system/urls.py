from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_redirect, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('login/', views.custom_login, name='custom_login'),
    path('logout/', views.custom_logout, name='custom_logout'),
    path('submit/', views.submit_reset_request, name='submit_reset'),
    path('service-desk/', views.service_desk_dashboard, name='service_desk_dashboard'),
    path('my-requests/', views.user_request_status, name='user_request_status'),
    path('director/review/', views.director_review_list, name='director_review_list'),
    path('director/review/<int:request_id>/', views.recommend_request, name='recommend_request'),
    path('director/requests/', views.director_review_list, name='director_review_list'),
    path('director/recommend/<int:request_id>/', views.recommend_request, name='recommend_request'),
    path('ict/review/', views.ict_review_list, name='ict_review_list'),
    path('ict/review/<int:request_id>/', views.ict_review_detail, name='ict_review_detail'),
    path('ict-admin/dashboard/', views.ict_admin_dashboard, name='ict_admin_dashboard'),
    path('ict-admin/finalise/<int:request_id>/', views.finalise_request, name='finalise_request'),
]
