from json import dumps
from .segmenter import Segmenter
from .ie_modules import get_name, get_email, get_phone, get_address


class Extracter:
    def __init__(self, fpath):
        self.seg = Segmenter(fpath)
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
        pass

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
            json_contact = dumps(self.contact_dict, indent=2, ensure_ascii=False)
            return json_contact

    def get_dict(self, arg="all"):
        if arg == "contact":
            return self.contact_dict

# extracter = Extracter('CV-FR.pdf')
# extracter.extract_contact()
# print(extracter.get_json("contact"))
