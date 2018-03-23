from django.urls import path

from . import views

app_name = 'app'
urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('joboffer/', views.JobOfferView.as_view(), name='joboffer'),
    path('candidate/', views.CandidateView.as_view(), name='candidate'),
    path('database/', views.databaseView.as_view(), name='database'),
    path('candidate/submit/', views.submit, name='submit')
]
