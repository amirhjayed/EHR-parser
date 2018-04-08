import re
from nltk import word_tokenize
from nltk import pos_tag
from geotext import GeoText


def get_name(contact_list):
    for index, i in enumerate(contact_list):
        name_flag = True
        tokz = word_tokenize(i)
        tags = pos_tag(tokz)
        for item in tags:
            if item[1] != 'NNP':
                name_flag = False
            if not name_flag:
                break
        else:
            return index, i


def get_email(contact_list):
    for index, item in enumerate(contact_list):
        if item.find('@') != -1:
            match = re.search(r'[\w\.-]+@[\w\.-]+', item)
            match = match.group(0)
            return index, match,


def get_address(contact_list):
    """ Check for cities --> Checks for postal code (CD + NN) --> checks keyword"""
    for index, item in enumerate(contact_list):
        # Cities
        places = GeoText(item)
        if places.cities:
            return index, item, True
        # Postal code
        tokz = word_tokenize(item)
        tags = pos_tag(tokz)
        for idx, tag in enumerate(tags):
            if tag[1] == 'CD':
                if tags[idx + 1][1][0:2] == 'NN':
                    return index, item, False
                break
        # keywords
        loc_kw = ['RÉSIDENCE', 'APPARTEMENT', 'RUE', 'ARRONDISSEMNT']  # Need another way to store and use data

        for word in tokz:
            if word.upper() in loc_kw:
                return index, item, False


def get_phone(contact_list):
    for index, i in enumerate(contact_list):
        n = ''
        for c in i:
            if c.isdigit() or c == '+':
                n += c
        if len(n) > 7:
            return index, n


def label_from(item):
    # Probably like isHeader, Need some kind of benchmark
    # Discuss This
    """ Implement this """
    item = item.strip(" •:")
    return item
