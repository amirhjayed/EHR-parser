from json import dumps
from .segmenter import Segmenter
from .ie_modules import get_name, get_email, get_phone, get_address, label_from


class Extracter:
    def __init__(self, fpath, lang):
        self.lang = lang
        self.seg = Segmenter(fpath, lang)
        self.seg.layout_pdf()

        # Dictionaries to store extracted informations
        self.contact_dict = {"name": "", "email": "", "address": "", "title": "", "phone": ""}
        self.skill_dict = {}
        self.educ_dict = {}
        self.career_dict = {}
        self.interest_dict = {}
        self.references_dict = {}

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

        index, address, endof_addr = get_address(contact_seg)
        self.contact_dict["address"] += address
        del(contact_seg[index])
        if not endof_addr:
            index, address, endof_addr = get_address(contact_seg)
            self.contact_dict["address"] += ", " + address
            del(contact_seg[index])

        # Title is everything else
        for item in contact_seg:
            self.contact_dict["title"] += item + " "

    def extract_skill(self):
        # Use what found before the : as label
        skill_seg = self.seg.get_skill()
        for item in skill_seg:
            pos = item.find(":")
            if pos != -1:
                label = label_from(item[0:pos])
                if label:
                    label_list = [w.strip(" •:") for w in item[pos:].split(",")]
                    label_list = [w for w in label_list if w]
                    self.skill_dict[label] = label_list

    def extract_educ(self):
        pass

    def extract_career(self):
        pass

    def extract_interest(self):
        pass

    def extract_references(self):
        pass

    # Getters
    def get_json(self, arg="all"):  # use kwargs
        if arg == "contact":
            _json = dumps(self.contact_dict, indent=2, ensure_ascii=False)
        elif arg == "skill":
            _json = dumps(self.skill_dict, indent=2, ensure_ascii=False)

        return _json

    def get_dict(self, arg="all"):
        if arg == "contact":
            return self.contact_dict
        if arg == "skill":
            return self.skill_dict
