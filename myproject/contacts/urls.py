# contacts/urls.py
from django.urls import path
from . import views

app_name = 'contacts'
urlpatterns = [
    path('', views.contact_list, name='list'),
    path('create/', views.contact_create, name='create'),
    path('ajax/search/', views.ajax_search_contacts, name='ajax_search'),
    path('ajax/delete/<int:pk>/', views.ajax_delete_contact, name='ajax_delete'),
    path('ajax/update/<int:pk>/', views.ajax_update_contact, name='ajax_update'),
]
