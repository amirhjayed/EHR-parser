from django.shortcuts import render, redirect
from django.views import View, generic
from .parser.extracter import Extracter
from django.views.generic.edit import FormView
from .models import Candidate, JobOffer, Recruiter
from django.core.files.storage import FileSystemStorage
from .forms import JobOfferForm, RecruiterForm, UserForm, CandidateForm, ContactForm, FileFieldForm
from django.contrib.auth import logout
from django.contrib.auth.models import User, Group
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
            group = Group.objects.get(name='recruiters')
            group.user_set.add(user)
            profile = pform.save(commit=False)
            profile.user = user
            profile.save()
            return redirect('/recruiter/')
    else:
        uform = UserForm()
        pform = RecruiterForm()
        return render(request, 'app/recruiter_signup.html', {'uform': uform, "pform": pform})


def logout_view(request):
    logout(request)
    return redirect('/')


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
        offer = JobOffer.objects.get(id=offer_id)
        if request.GET.get('db') == 'yours':
            order_func = get_match_function(offer_id)
            uid = User.objects.get(id=request.user.id)
            recruiter = Recruiter.objects.get(user_id=uid)
            candidates = list(Candidate.objects.all().filter(recruiter_id=recruiter.id))
            candidates.sort(key=order_func)
            return render(request, self.template_name, {'offer': offer.title, 'candidates': candidates})
        elif request.GET.get('db') == 'ours':
            order_func = get_match_function(offer_id)
            candidates = list(Candidate.objects.all().filter(recruiter_id=None))
            candidates.sort(key=order_func)
            return render(request, self.template_name, {'offer': offer.title, 'candidates': candidates})
        else:
            offer = JobOffer.objects.get(id=offer_id)
            return render(request, self.template_name, {'offer': offer.title})


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


# Batch parse
def handle_uploaded_file(f, fs, uid):
    filename = fs.save(f.name, f)
    uploaded_file_url = fs.location + "/" + filename
    extracter = Extracter(uploaded_file_url)
    extracter.extract_contact()

    recruiter = Recruiter.objects.get(user_id=uid)
    contact_dict = extracter.get_dict("contact")
    candidate = Candidate(**contact_dict, cv_ref=uploaded_file_url)
    candidate.recruiter = recruiter
    name = candidate.name
    candidate.save()
    return name


class BatchParserView(FormView):
    form_class = FileFieldForm
    template_name = 'app/batch_parse.html'
    success_url = './'

    def post(self, request, *args, **kwargs):
        names = []
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        files = request.FILES.getlist('file_field')
        if form.is_valid():
            fs = FileSystemStorage()
            for f in files:
                names.append(handle_uploaded_file(f, fs, request.user.id))
            print(names)
            return render(request, self.template_name, {'names': names})
        else:
            return self.form_invalid(form)


# ~~~~~~~~~~~~~~~ #
# Candidate space #
# ~~~~~~~~~~~~~~~ #
class CandidateView(generic.TemplateView):
    template_name = 'app/candidate.html'


def signup_candidate(request):
    if request.method == "POST":
        uform = UserForm(data=request.POST)
        if uform.is_valid:
            user = uform.save()
            group = Group.objects.get(name='candidates')
            group.user_set.add(user)
            return redirect('/candidate/')
    else:
        uform = UserForm()
        return render(request, 'app/candidate_signup.html', {'uform': uform})


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
