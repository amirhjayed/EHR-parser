from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'app'
urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),

    # RECRUITER URLS:
    # ~~~~~~~~~~~~~~
    path('recruiter/', views.RecruiterView.as_view(), name='recruiter'),
    path('recruiter/signup/', views.signup, name="signup"),
    path('recruiter/login/', auth_views.LoginView.as_view(template_name='app/login.html'), name="signin"),
    path('recruiter/logout/', views.logout_view),

    # Submit Job offer
    path('recruiter/job_offer/', views.JobOfferView.as_view(), name='Job offer'),

    # Offers
    path('recruiter/offers/', views.OfferListView.as_view(), name='View offers'),
    path('recruiter/offers/<int:offer_id>/', views.OfferFormView.as_view()),
    path('recruiter/offers/<int:offer_id>/match/', views.MatchView.as_view()),
    path('recruiter/offers/<int:offer_id>/match/<int:cand_id>/', views.CandidateMatchView.as_view()),
    path('recruiter/offers/<int:offer_id>/match/<int:cand_id>/contact/', views.ContactCandidateView.as_view()),

    # batch
    path('recruiter/batch/', views.BatchParserView.as_view(), name='Batch parser'),
    # ~~~~~~~~~~~~~


    # CANDIDATE URLS:
    # ~~~~~~~~~~~~~~~
    path('candidate/', views.CandidateView.as_view(), name='candidate'),
    path('candidate/submit-cv/', views.Submit_cv_view.as_view()),
    path('media/resumes/<str:cv_file>', views.pdf_view),
    path('candidate/consult-offers/', views.ListOffersView.as_view()),
    path('candidate/consult-offers/<int:offer_id>/', views.ConsultOfferView.as_view()),
    path('candidate/consult-offers/<int:offer_id>/contact/', views.ContactRecruiterView.as_view()),

    path('candidate/signup/', views.signup_candidate, name="signup"),
    path('candidate/login/', auth_views.LoginView.as_view(template_name='app/login.html'), name="signin")
]
