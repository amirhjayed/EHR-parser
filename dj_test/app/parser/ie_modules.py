import re
from nltk import word_tokenize
from nltk import pos_tag
from geotext import GeoText


def tokz(i):
    # just to avoid importing nltk in extracter
    return(word_tokenize(i))


def expand_list(l):
    l_ex = []
    for i in l:
        if isinstance(i, str):
            i = word_tokenize(i)
            l_ex += i
    return l_ex


#  CONTACT EXTRACTION #
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
        # keywords -->  CSV, and Fr,En
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


def get_title(contact_list, title_dict):
    domain, function = '', ''
    for item in contact_list:
        tokz = word_tokenize(item)

        for tok in tokz:
            tok = tok.lower()
            if title_dict.get(tok) == 'domain':
                domain += ' ' + tok
            elif title_dict.get(tok) == 'function':
                function += ' ' + tok
    return '{},{}'.format(domain[1:], function[1:])


# Career extraction:

# Regex for month matching
months_fr = "((j|J)an|(f|F)év|(M|m)ar|(A|a)vr|(M|m)ai|(J|j)uin|(J|j)uil|(A|a)oû|(S|s)ep|(O|o)ct|(N|n)ov|(D|d)éc)"
months_en = "((J|j)an|(F|f)eb|(M|m)ar|(A|a)pr|(M|m)ay|(J|j)un|(J|j)ul|(A|a)ug|(S|s)ep|(O|o)ct|(N|n)ov|(D|d)ec)"

m_ord_fr = {
    "JAN": "0", "FÉV": "1", "MAR": "2", "AVR": "3", "MAI": "4", "JUIN": "5", "JUIL": "6", "AOÛ": "7", "SEP": "8", "OCT": "9", "NOV": "10", "DÉC": "11"
}
m_ord_en = {
    "JAN": "0", "FEB": "1", "MAR": "2", "APR": "3", "MAY": "4", "JUN": "5", "JUL": "6", "AUG": "7", "SEP": "8", "OCT": "9", "NOV": "10", "DEC": "11"
}


def isdate(i, lg):
    if i.isdigit():
        if len(i) == 4:
            return i + ' year'
    else:
        if lg == 'Fr':
            m = re.search(months_fr, i)
            if m:
                m_ord = m_ord_fr[m.group(0).upper()]
                return m_ord + ' month'
        else:
            m = re.search(months_en, i)
            if m:
                m_ord = m_ord_en[m.group(0).upper()]
                return m_ord, + ' month'
            else:
                return False


def find_date(career_seg, lg):

    # We assume there is always a year in date
    date = ''  # as (month,year)-(month,year)
    st_m, st_y, en_m, en_y = 'x', 'x', 'x', 'x'
    date_start = False

    for item in career_seg:
        tokenz = []
        for i in word_tokenize(item):
            tokenz.extend(i.split('-'))
        for tok in tokenz:
            d = isdate(tok, lg)
            if d:
                d, t = d.split(' ')
                date_start = True

                if t == 'month':
                    if st_m == 'x':
                        st_m = d
                    else:
                        en_m = d

                else:
                    if st_y == 'x':
                        st_y = d
                    else:
                        en_y = d
            else:
                if date_start:
                    date = '({} {})-({} {})'.format(st_m, st_y, en_m, en_y)
                    return date
        else:  # end of the loop
            date = '({} {})-({} {})'.format(st_m, st_y, en_m, en_y)
            return date


def itemize_seg(_seg, lg):
    items_dict = dict()
    date = find_date(_seg, lg)
    items_dict[date] = ''
    for idx, item in enumerate(_seg):
        item = word_tokenize(item)
        for i in item:
            if not isdate(i, lg):
                items_dict[date] += ' ' + i
            else:
                date = find_date(_seg[idx:], lg)
                items_dict[date] = ''
    return items_dict


def get_duration(item):
    st, en = item.split('-')
    st_m, st_y = st[1:-1].split(' ')
    en_m, en_y = en[1:-1].split(' ')

    if st_y != 'x':
        if en_y == 'x':
            if st_m != 'x':
                if en_m != 'x':
                    return int(en_m) - int(st_m) + 1
                else:
                    return 1
            else:
                return 12
        else:
            if st_m != 'x':
                y = int(en_y) - int(st_y) - 1
                m = 12 - int(st_m)
                m += int(en_m) + 1
                m += 12 * y
                return m
            else:
                return 12 * (int(en_y) - int(st_y) + 1)
    else:
        if st_m != 'x' and en_m != 'x':
            return int(en_m) - int(st_m) + 1
        else:
            return 0


def get_title_career(career_item, title_dict):
    domain, function = '', ''
    tokz = word_tokenize(career_item)
    for tok in tokz:
        tok = tok.lower()
        if title_dict.get(tok) == 'domain':
            domain += ' ' + tok
        elif title_dict.get(tok) == 'function':
            function += ' ' + tok
    return '{},{}'.format(domain[1:], function[1:])


def get_degree(seg, data):
    for line in seg:
        words = word_tokenize(line)
        for w in words:
            w = w.lower()
            deg = data.get(w)
            if deg:
                return deg
    else:
        return 'Bac'
