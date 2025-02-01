# reviews/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('search/', views.search, name='search'),  # This is the search URL
    path('', views.Reviews_List, name='Reviews_List'),
    path('Review_created/', views.Review_created, name='Review_created'),
    path('<int:review_id>/delete/', views.Review_deleted, name='Review_deleted'),
    path('<int:review_id>/edit/', views.Review_edit, name='Review_edit'),
    path('<int:review_id>/details/', views.Review_detail, name='Review_detail')

]
