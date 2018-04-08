from json import dumps
from django.shortcuts import render, redirect
from django.views import View, generic
from .parser.extracter import Extracter
from .models import Candidate, JobOffer, Recruter
from django.core.files.storage import FileSystemStorage
from .forms import JobOfferForm, RecruterForm, UserForm
from django.contrib.auth import logout
from django.contrib.auth.models import User


def submit_cv(request):
    if request.method == 'POST' and request.FILES['cv_file']:
        myfile = request.FILES['cv_file']
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)

        uploaded_file_url = fs.location + "/" + filename
        extracter = Extracter(uploaded_file_url)
        extracter.extract_contact()
        contact_dict = extracter.get_dict("contact")
        contact_json = extracter.get_json("contact")
        candidate = Candidate(contact_dict, cv_ref=uploaded_file_url)
        candidate.save()

        return render(request, 'app/submit.html', {
            'uploaded_file_url': uploaded_file_url,
            'contact_json': contact_json
        })
    return render(request, 'app/submit_cv.html')


def submit_jo(request):
    if request.method == 'POST':
        form = JobOfferForm(request.POST)
        valid = form.is_valid()
        cleaned_data = form.cleaned_data
        req_keys = {"technologies", "languages", "qualities"}
        req_dict = {key: cleaned_data[key] for key in req_keys}
        req_json = dumps(req_dict, ensure_ascii=False)
        user_id = User.objects.get(id=request.user.id)
        recruter = Recruter.objects.get(user_id=user_id)
        jo = JobOffer(title=cleaned_data['title'],
                      working_schedule=cleaned_data['schedule'],
                      niv_etude=cleaned_data['degree'],
                      salary=cleaned_data['salary'],
                      experience=cleaned_data['experience'],
                      requirements=req_json,
                      description=cleaned_data["description"],
                      recruter=recruter
                      )
        jo.save()
        return render(request, 'app/submit_jo.html', {"cleaned_data": cleaned_data, "valid": valid, "req_json": req_json})


class HomeView(generic.TemplateView):
    template_name = 'app/home.html'


class RecruterView(generic.TemplateView):
    template_name = 'app/recruter.html'


class OfferView(generic.TemplateView):
    template_name = 'app/viewoffer.html'


class ParserView(generic.TemplateView):
    template_name = 'app/batch_parse.html'


class JobOfferView(View):
    form = JobOfferForm()
    template_name = 'app/joboffer.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {'form': self.form})


class CandidateView(generic.TemplateView):
    template_name = 'app/candidate.html'


def signup(request):
    if request.method == "POST":
        uform = UserForm(data=request.POST)
        pform = RecruterForm(data=request.POST)
        if uform.is_valid() and pform.is_valid():
            user = uform.save()
            profile = pform.save(commit=False)
            profile.user = user
            profile.save()
    else:
        uform = UserForm()
        pform = RecruterForm()
    return render(request, 'app/signup.html', {'uform': uform, "pform": pform})


def logout_view(request):
    logout(request)
    return redirect('/recruter/')
