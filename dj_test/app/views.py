from django.views import generic
from django.shortcuts import render
from .parser.extracter import Extracter
from .models import Candidate
from django.core.files.storage import FileSystemStorage


def submit(request):
    if request.method == 'POST' and request.FILES['cv_file']:
        myfile = request.FILES['cv_file']
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)

        uploaded_file_url = fs.location + "/" + filename
        extracter = Extracter(uploaded_file_url)
        extracter.extract_contact()
        contact_dict = extracter.get_dict("contact")
        contact_json = extracter.get_json("contact")
        candidate = Candidate(**contact_dict, cv_ref=uploaded_file_url)
        candidate.save()

        return render(request, 'app/submit.html', {
            'uploaded_file_url': uploaded_file_url,
            'contact_json': contact_json
        })
    return render(request, 'app/submit.html')


class HomeView(generic.TemplateView):
    template_name = 'app/home.html'


class JobOfferView(generic.TemplateView):
    template_name = 'app/joboffer.html'


class CandidateView(generic.TemplateView):
    template_name = 'app/candidate.html'


class databaseView(generic.TemplateView):
    template_name = 'app/database.html'
