from django.urls import path
from . import views

urlpatterns = [
    path('submit/', views.submit_reset_request, name='submit_reset'),
    path('my-requests/', views.user_request_status, name='user_request_status'),
    path('director/review/', views.director_review_list, name='director_review_list'),
    path('director/review/<int:request_id>/', views.recommend_request, name='recommend_request'),
    path('director/requests/', views.director_review_list, name='director_review_list'),
    path('director/recommend/<int:request_id>/', views.recommend_request, name='recommend_request'),
]
