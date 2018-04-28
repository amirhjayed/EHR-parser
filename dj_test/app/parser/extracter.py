from django.conf import settings
from json import dumps
from .segmenter import Segmenter
from .ie_modules import expand_list, get_name, get_email, get_phone, get_address, get_title, tokz, get_degree, itemize_seg, get_duration, get_title_career

import pandas as pd


class Extracter:
    def __init__(self, fpath, lang):
        self.lang = lang
        self.seg = Segmenter(fpath, lang)
        self.seg.layout_pdf()

        # Load job titles and degrees
        if lang == 'Fr':
            csvfile1 = open(settings.BASE_DIR + '/app/parser/data/fr_it_jobs.csv', 'r')
            csvfile2 = open(settings.BASE_DIR + '/app/parser/data/degree_fr.csv', 'r')
        else:
            csvfile1 = open(settings.BASE_DIR + '/app/parser/data/en_it_jobs.csv', 'r')
            csvfile2 = open(settings.BASE_DIR + '/app/parser/data/degree_en.csv', 'r')
        titles = pd.read_csv(csvfile1)
        domains = expand_list(list(titles.domain))
        functions = expand_list(list(titles.function))
        self.title_dict = {
            **dict.fromkeys(domains, 'domain'),
            **dict.fromkeys(functions, 'function')
        }
        degree_data = pd.read_csv(csvfile2)
        self.degree_dict = degree_data.melt().set_index('value').to_dict()['variable']

        # LOAD SKILLS DATA :
        csvfile1 = open(settings.BASE_DIR + '/app/parser/data/programming.csv', 'r')
        csvfile2 = open(settings.BASE_DIR + '/app/parser/data/technologies.csv', 'r')
        csvfile3 = open(settings.BASE_DIR + '/app/parser/data/languages.csv', 'r')
        prog_skills = pd.read_csv(csvfile1)
        tech_skills = pd.read_csv(csvfile2)
        lang_skills = pd.read_csv(csvfile3)
        # Convert df into dicts
        self.prog_dict = prog_skills.melt().set_index('value').to_dict()['variable']
        self.tech_dict = tech_skills.melt().set_index('value').to_dict()['variable']
        if self.lang == 'Fr':
            self.lang_dict = {**dict.fromkeys(list(lang_skills.fr), 'languages')}
        else:
            self.lang_dict = {**dict.fromkeys(list(lang_skills.en), 'languages')}

        # Dictionaries to store extracted informations
        self.contact_dict = {"name": "", "email": "", "address": "", "title": "", "phone": ""}
        self.skill_dict = {"programming_languages": "", "programming_frameworks": "", "technologies": "", "languages": ""}
        self.career_list = []

        # DO EXTRACTION
        self.extract()

    # CONTACT
    def extract_contact(self):
        contact_seg = self.seg.get_contact()
        if contact_seg[0].title() == 'Curriculum Vitae':
            del(contact_seg[0])
        index, self.contact_dict["name"] = get_name(contact_seg)
        del(contact_seg[index])

        index, self.contact_dict["email"] = get_email(contact_seg)
        del(contact_seg[index])

        index, self.contact_dict["phone"] = get_phone(contact_seg)
        del(contact_seg[index])

        # Addresses can be split over multiple lines,
        index, address, endof_addr = get_address(contact_seg)
        self.contact_dict["address"] += address
        del(contact_seg[index])
        if not endof_addr:
            index, address, endof_addr = get_address(contact_seg)
            self.contact_dict["address"] += ", " + address
            del(contact_seg[index])

        # title as (domain, function) pair
        self.contact_dict["title"] = get_title(contact_seg, self.title_dict)

    # SKILL
    def extract_skill(self):
        skill_seg = self.seg.get_skill()
        for item in skill_seg:

            tokenz = tokz(item)  # tokenize item
            for tok in tokenz:
                tok = tok.upper()  # upper for normalization purposes
                key = ''

                # This block searches tok in skill dicts
                if self.prog_dict.get(tok):
                    key = self.prog_dict.get(tok)
                elif self.tech_dict.get(tok):
                    key = self.tech_dict.get(tok)
                elif self.lang_dict.get(tok):
                    key = self.lang_dict.get(tok)

                if key:
                    self.skill_dict[key] += ',' + tok

        # maybe a better way
        for key in self.skill_dict:
            if self.skill_dict[key]:
                self.skill_dict[key] = self.skill_dict[key][1:]

    def extract_degree(self):
        self.degree = ''
        education_seg = self.seg.get_education()
        self.degree = get_degree(education_seg, self.degree_dict)

    # Career : as (title, duration)
    def extract_career(self):
        experience = 0
        career_seg = self.seg.get_career()
        career_items_dict = itemize_seg(career_seg, self.lang)
        for time in career_items_dict:
            months_duration = get_duration(time)
            experience += months_duration  # This if sum of exp
            career_item = {
                "title": "",
                "duration": months_duration
            }
            career_item["title"] = get_title_career(career_items_dict[time], self.title_dict)
            self.career_list.append(career_item)

        self.experience = experience

    def extract(self):
        self.extract_contact()
        self.extract_skill()
        self.extract_degree()
        self.extract_career()

    # Getters
    def get_json(self, arg="all"):
        if arg == "contact":
            _json = dumps(self.contact_dict, indent=2, ensure_ascii=False)
            return _json
        elif arg == "skill":
            _json = dumps(self.skill_dict, indent=2, ensure_ascii=False)
            return _json
        elif arg == "career":
            _json = dumps(self.career_list, indent=2, ensure_ascii=False)
            return _json

    def get_dict(self, arg="candidate"):
        if arg == "contact":
            return self.contact_dict
        elif arg == "skill":
            return self.skill_dict
        elif arg == "career":
            return self.career_list
        elif arg == "candidate":
            r = {**self.contact_dict, **self.skill_dict}
            return r
