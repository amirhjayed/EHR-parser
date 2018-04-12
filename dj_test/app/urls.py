from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'app'
urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('recruter/', views.RecruterView.as_view(), name='recruter'),
    path('candidate/', views.CandidateView.as_view(), name='candidate'),
    path('candidate/submit/', views.submit_cv, name='submit_cv'),
    path('recruter/signup/', views.signup, name="signup"),
    path('recruter/login/', auth_views.LoginView.as_view(template_name='app/login.html', redirect_field_name='recruter/'), name="signin"),
    path('recruter/logout/', views.logout_view),

    path('recruter/job_offer/', views.JobOfferView.as_view(), name='Job offer'),
    path('recruter/view_offer/', views.OfferListView.as_view(), name='View offers'),
    path('recruter/view_offer/<int:offer_id>/', views.OfferFormView.as_view()),
    path('recruter/parse_cvs/', views.ParserView.as_view(), name='Batch parser'),

    path('recruter/job_offer/submit/', views.submit_jo, name='submit_jo'),
]
