from django.shortcuts import render, redirect
from django.views import View, generic
from .parser.extracter import Extracter
from .models import Candidate, JobOffer, Recruiter
from django.core.files.storage import FileSystemStorage
from .forms import JobOfferForm, RecruiterForm, UserForm, CandidateForm, ContactForm
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.core.mail import send_mail


class HomeView(generic.TemplateView):
    template_name = 'app/home.html'


# ~~~~~~~~~~~~~~~
# Recruiter space
# ~~~~~~~~~~~~~~~
class RecruiterView(generic.TemplateView):
    template_name = 'app/recruiter.html'


class OfferListView(generic.ListView):
    model = JobOffer
    template_name = 'app/viewoffer.html'


class ParserView(generic.TemplateView):
    template_name = 'app/batch_parse.html'


class JobOfferView(View):
    form = JobOfferForm()
    template_name = 'app/joboffer.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {'form': self.form})


class OfferFormView(View):
    template_name = 'app/alter_offer.html'

    def get(self, request, offer_id):
        offer = JobOffer.objects.get(id=offer_id)
        form = JobOfferForm(instance=offer)
        return render(request, self.template_name, {'form': form, 'get': 'get'})

    def post(self, request, offer_id):
        if request.POST.get('update'):
            offer = JobOffer.objects.get(id=offer_id)
            form = JobOfferForm(request.POST, instance=offer)
            form.save()
            return render(request, self.template_name, {'form': form, 'post': 'post'})
        if request.POST.get('delete'):
            JobOffer.objects.get(id=offer_id).delete()
            return redirect('/recruiter/view_offer/')


def submit_jo(request):
    if request.method == 'POST':
        user_id = User.objects.get(id=request.user.id)
        recruiter = Recruiter.objects.get(user_id=user_id)
        form = JobOfferForm(request.POST)
        job_offer = form.save(commit=False)
        job_offer.recruiter = recruiter
        job_offer.save()
        return render(request, 'app/submit_jo.html')


def signup(request):
    if request.method == "POST":
        uform = UserForm(data=request.POST)
        pform = RecruiterForm(data=request.POST)
        if uform.is_valid() and pform.is_valid():
            user = uform.save()
            profile = pform.save(commit=False)
            profile.user = user
            profile.save()
            return redirect('/recruiter/')
    else:
        uform = UserForm()
        pform = RecruiterForm()
        return render(request, 'app/signup.html', {'uform': uform, "pform": pform})


def logout_view(request):
    logout(request)
    return redirect('/recruiter/')


# Match View and utilities:
def get_match_function(offer_id):
    # NOT IMPLEMENTED #
    def func(candidate):
        offer = JobOffer.objects.get(id=offer_id)
        score = offer.experience - candidate.id
        return score
    return func


class MatchView(View):
    template_name = 'app/match.html'

    def get(self, request, offer_id):
        order_func = get_match_function(offer_id)
        candidates = list(Candidate.objects.all())
        candidates.sort(key=order_func)
        return render(request, self.template_name, {'offer_id': offer_id, 'candidates': candidates})


class CandidateMatchView(View):
    template_name = 'app/candidate_match.html'

    def get(self, request, offer_id, cand_id):
        cand = Candidate.objects.get(id=cand_id)
        form = CandidateForm(instance=cand)
        return render(request, self.template_name, {'form': form})


class CandidateContactView(View):
    template_name = 'app/candidate_contact.html'

    def get(self, request, offer_id, cand_id):
        offer = JobOffer.objects.get(id=offer_id)
        cand = Candidate.objects.get(id=cand_id)
        data = {'subject': 'Job Offer', 'sender': offer.recruiter.email, 'reciever': cand.email, 'message': 'wanna work ?'}
        form = ContactForm(data)
        return render(request, self.template_name, {'form': form, 'get': 'get'})

    def post(self, request, offer_id, cand_id):
        form = ContactForm(request.POST)
        send_mail(request.POST.get('subject'),
                  request.POST.get('message'),
                  'contact.ehr.services@gmail.com',
                  [request.POST.get('reciever')],
                  fail_silently=False
                  )
        return render(request, self.template_name, {'form': form, 'post': 'post'})


# ~~~~~~~~~~~~~~~ #
# Candidate space #
# ~~~~~~~~~~~~~~~ #
class CandidateView(generic.TemplateView):
    template_name = 'app/candidate.html'


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
        candidate = Candidate(**contact_dict, cv_ref=uploaded_file_url)
        candidate.save()

        return render(request, 'app/submit_cv.html', {
            'uploaded_file_url': uploaded_file_url,
            'contact_json': contact_json
        })
