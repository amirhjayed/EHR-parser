from django.views import generic
from .models import Candidate, JobOffer
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage


class HomeView(generic.TemplateView):
    template_name = 'app/home.html'


class JobOfferView(generic.TemplateView):
    template_name = 'app/joboffer.html'
    model = JobOffer


class CandidateView(generic.TemplateView):
    model = Candidate
    template_name = 'app/candidate.html'


class databaseView(generic.TemplateView):
    model = Candidate
    template_name = 'app/database.html'


def submit(request):
    if request.method == 'POST' and request.FILES['cv_file']:
        myfile = request.FILES['cv_file']
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        uploaded_file_url = fs.url(filename)
        return render(request, 'app/submit.html', {
            'uploaded_file_url': uploaded_file_url
        })
    return render(request, 'app/submit.html')
