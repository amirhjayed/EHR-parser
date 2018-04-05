# Trying spacy
import spacy
import numpy as np
nlp = spacy.load("fr")


def get_phone(item):
    n = ''
    for c in item:
        if c.isdigit() or c == '+':
            n += c
        if len(n) > 7:
            if n[0] == '+':
                n = '+(' + n[1:4] + ')' + n[4:]
            return n


def ie_contact(contact_list, contact_found):
    # (name, email, address, title, phone)
    contact_output = ["", "", "", "", ""]
    for item in contact_list:
        label = contact_classifier(item, contact_found)
        contact_output[label] += " " + item
    return contact_output


xx = [u'Houssem ROUIS', u': Résidence Les Rives de l’Yvette', u'91440 Bures-sur-Yvette', u': houssemeddine.rouis92@gmail.com', u': 06 13 04 49 05', u'Étudiant en M2 Systèmes Embarqués', u'et Traitement de l’Information']

print(ie_contact(xx))

# doc_text = ''
# score.fill(0)
# doc = nlp(item)
# if len(doc) <= 4:
#     score[0] = 0.3
# else:
#     score[2] = 0.3
#     score[3] = 0.3

# for token in doc:
#     if token.like_email:
#         score[1] = 10.0
#         break
#     elif token.is_upper:
#         score[0] += 0.2
#     elif token.is_digit:
#         score[0] -= 1.0
#         score[2] += 0.2
#         if not contact_found[4]:
#             print(doc.text)
#             cell = get_phone(doc.text)
#             if cell:
#                 score[4] = 10.0
#                 doc_text = cell
#                 break

#         score[4] += 0.2
#     elif token.tag_ == 'PROPN':
#         score[0] += 0.1
