from django.shortcuts import render, redirect
from django.views import View, generic
from .parser.extracter import Extracter
from django.views.generic.edit import FormView
from .models import Candidate, JobOffer, Recruiter
from django.core.files.storage import FileSystemStorage
from .forms import JobOfferForm, RecruiterForm, UserForm, CandidateForm, ContactForm, FileFieldForm
from django.contrib.auth import logout
from django.contrib.auth.models import User, Group
from django.core import mail
from .matcher.get_score import get_score
from django.core.exceptions import ObjectDoesNotExist


class HomeView(View):
    template_name = 'app/home.html'

    def get(self, request):

        if request.user:
            if request.user.groups.filter(name='candidates').exists():
                return redirect('candidate/')
            elif request.user.groups.filter(name='recruiters').exists():
                return redirect('recruiter/')
            else:
                return render(request, self.template_name)
        else:
            return render(request, self.template_name)


# ~~~~~~~~~~~~~~~
# Recruiter space
# ~~~~~~~~~~~~~~~
class RecruiterView(generic.TemplateView):
    template_name = 'app/recruiter.html'


class OfferListView(View):
    template_name = 'app/viewoffer.html'

    def get(self, request):
        recruiter = Recruiter.objects.get(user=request.user.id)
        offers = list(JobOffer.objects.all().filter(recruiter_id=recruiter.id))
        offers = [(o.title.replace(',', ' '), o.id) for o in offers]
        return render(request, self.template_name, {'offers': offers, 'name': recruiter.name})


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
        return render(request, self.template_name, {'form': form, 'get': 'get', 'offer': offer.title.replace(',', ' ')})

    def post(self, request, offer_id):
        if request.POST.get('edit'):
            offer = JobOffer.objects.get(id=offer_id)
            form = JobOfferForm(request.POST, instance=offer)
            form.save()
            return render(request, self.template_name, {'form': form, 'post': 'post', 'offer': offer.title.replace(',', ' ')})
        if request.POST.get('delete'):
            JobOffer.objects.get(id=offer_id).delete()
            return redirect('/recruiter/offers/')


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
    def func(candidate):
        offer = JobOffer.objects.get(id=offer_id)
        score = get_score(offer, candidate)
        return score
    return func


class MatchView(View):
    template_name = 'app/match.html'

    def get(self, request, offer_id):
        offer = JobOffer.objects.get(id=offer_id)
        recruiter = Recruiter.objects.get(user_id=request.user.id)
        if request.GET.get('db') == 'yours':
            order_func = get_match_function(offer_id)
            candidates = list(Candidate.objects.all().filter(recruiter_id=recruiter.id))
            candidates.sort(key=order_func, reverse=True)
            return render(request, self.template_name, {'offer': offer.title.replace(',', ' '), 'candidates': candidates, 'name': recruiter.name})

        elif request.GET.get('db') == 'ours':
            order_func = get_match_function(offer_id)
            candidates = list(Candidate.objects.all().filter(recruiter_id=None))
            candidates.sort(key=order_func, reverse=True)
            return render(request, self.template_name, {'offer': offer.title.replace(',', ' '), 'candidates': candidates, 'name': recruiter.name})

        else:
            offer = JobOffer.objects.get(id=offer_id)
            return render(request, self.template_name, {'offer': offer.title.replace(',', ' '), 'name': recruiter.name})


class CandidateMatchView(View):
    template_name = 'app/candidate_match.html'

    def get(self, request, offer_id, cand_id):
        cand = Candidate.objects.get(id=cand_id)
        form = CandidateForm(instance=cand)
        return render(request, self.template_name, {'form': form})


class ContactCandidateView(View):
    template_name = 'app/contact.html'

    def get(self, request, offer_id, cand_id):
        offer = JobOffer.objects.get(id=offer_id)
        cand = Candidate.objects.get(id=cand_id)
        data = {'subject': 'Job Offer', 'sender': offer.recruiter.email, 'reciever': cand.email, 'message': 'Dear sir, do you want to work for us ?'}
        form = ContactForm(data)
        return render(request, self.template_name, {'form': form, 'get': 'get', 'space': 'Recruiter', 'name': cand.name, 'offer': offer.title.replace(',', ' ')})

    def post(self, request, offer_id, cand_id):
        form = ContactForm(request.POST)
        mail.send_mail(request.POST.get('subject'),
                       request.POST.get('message'),
                       'contact.ehr.services@gmail.com',
                       [request.POST.get('reciever')],
                       fail_silently=False
                       )
        return render(request, self.template_name, {'form': form, 'post': 'post', 'space': 'Recruiter'})


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
            return render(request, self.template_name, {'names': names})
        else:
            return self.form_invalid(form)


# ~~~~~~~~~~~~~~~ #
# Candidate space #
# ~~~~~~~~~~~~~~~ #
class CandidateView(View):
    template_name = 'app/candidate.html'

    def get(self, request):
        return render(request, self.template_name, {'get': 'yes'})


class Submit_cv_view(View):
    template_name = 'app/submit_cv.html'

    def get(self, request):
        try:
            Candidate.objects.get(user=request.user.id)
            message = 'You already uploaded a CV.\n Uploading again will override the old one.'
        except Candidate.DoesNotExist:
            message = ''

        return render(request, self.template_name, {'get': 'yes', 'message': message})

    def post(self, request):
        render_dict = {'post': 'yes'}
        if request.FILES.get('cv_file'):
            myfile = request.FILES['cv_file']
            if myfile.name.endswith('pdf'):
                lang = request.POST.get('language')

                # Extracter will take the uploaded CV and return a dictionnary containing extracted info
                extracter = Extracter(myfile, lang[0:2])

                # stuff
                extracter_message = extracter.is_valid()  # is_valid returns the cause of extraction failure.
                print(extracter_message)
                if not extracter_message:  # if message is empty extraction is valid
                    try:
                        candidate = Candidate.objects.get(user=request.user.id)
                    except Candidate.DoesNotExist:
                        candidate = False

                    # update existing candidate object
                    if candidate:
                        candidate.cv_file.delete(save=False)
                        candidate = Candidate(id=candidate.id, **extracter.get_dict(), cv_file=myfile, user=request.user)
                        candidate.save()

                        render_dict.update({
                            'success': True,
                            'message': 'Your profile was updated.\n File location : ' + candidate.cv_file.url,
                        })

                    # create new candidate object
                    else:
                        candidate = Candidate(**extracter.get_dict(), cv_file=myfile, user=request.user)
                        candidate.save()

                        render_dict.update({
                            'success': True,
                            'message': 'Candidate profile created.\nFile location : ' + candidate.cv_file.url,
                        })

                else:
                    message = 'Sorry, we were unable to parse your CV.'
                    if extracter_message == 'seg':

                        render_dict.update({
                            'message': message,
                            'message2': 'Segmentation failed. Please make sure you chose the right language.',
                            'message3': 'This also can happen if the template used to create the CV is complicated.'
                        })
                    elif extracter_message == 'name':

                        render_dict.update({
                            'message': message,
                            'message2': 'Extraction failed to extract your name.',
                            'message3': 'The name must start with a capitalized letter for us to be able to extract it.'
                        })
                    elif extracter_message == 'email':

                        render_dict.update({
                            'message': message,
                            'message2': 'Extraction failed to extract your email.',
                            'message3': 'Your CV must include an email so recruiters can contact you. ',
                        })
                    elif extracter_message == 'degree':

                        render_dict.update({
                            'message': message,
                            'message2': 'Extraction failed to extract your degree.',
                            'message3': 'Check if the education section contain the name of the degree for each school.',
                        })
                    elif extracter_message == 'title':
                        render_dict.update({
                            'message': message,
                            'message2': 'Extraction failed to extract your title.',
                            'message3': 'Please check if you mentioned your title in the contact section or in your career section.',
                        })

            else:
                render_dict = {
                    'message': 'Please upload a resume in PDF format'
                }

            return render(request, self.template_name, render_dict)


def get_match_function2(candidate_id):
    def func(offer):
        candidate = Candidate.objects.get(id=candidate_id)
        score = get_score(offer, candidate)
        return score
    return func


class ListOffersView(View):
    template_name = 'app/list_offers.html'

    def get(self, request):
        try:
            candidate = Candidate.objects.get(user=request.user.id)
            order_func = get_match_function2(candidate.id)
            offers = list(JobOffer.objects.all())
            offers.sort(key=order_func, reverse=True)
            offers = [(o.title.replace(',', ' '), o.id) for o in offers]
            return render(request, self.template_name, {'offers': offers})
        except ObjectDoesNotExist:
            return render(request, self.template_name, {'message': 'Please upload a CV before using this feature.'})


class ConsultOfferView(View):
    template_name = 'app/consult_offer.html'

    def get(self, request, offer_id):
        offer = JobOffer.objects.get(id=offer_id)
        form = JobOfferForm(instance=offer)
        return render(request, self.template_name, {'form': form, 'offer': offer.title.replace(',', ' '), 'recruiter': offer.recruiter.name})


class ContactRecruiterView(View):
    template_name = 'app/contact.html'

    def get(self, request, offer_id):
        offer = JobOffer.objects.get(id=offer_id)
        cand = Candidate.objects.get(user=request.user.id)
        data = {'subject': 'Job Offer', 'sender': cand.email, 'reciever': offer.recruiter.email, 'message': 'Dear sir, the attached fle is my CV. I want to work'}
        form = ContactForm(data)
        return render(request, self.template_name, {'form': form, 'get': 'get', 'space': 'Candidate', 'name': offer.recruiter.name, 'offer': offer.title.replace(',', ' ')})

    def post(self, request, offer_id):
        form = ContactForm(request.POST)
        cv_file = Candidate.objects.get(user=request.user.id).cv_file
        with mail.get_connection() as connection:
            mail.EmailMessage(
                request.POST.get('subject'),
                request.POST.get('message'),
                'contact.ehr.services@gmail.com',
                [request.POST.get('reciever')],
                attachments=[(cv_file.name, cv_file.read(), 'application/pdf')],
                connection=connection,
            ).send()
        return render(request, self.template_name, {'form': form, 'post': 'post', 'space': 'Candidate'})


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
