from nltk.corpus import wordnet as wn
from nltk.stem import WordNetLemmatizer
wn_lemmatizer = WordNetLemmatizer()


def calculate_score(offer, candidate):
    # Calculate score :
    len_offer = len(offer)
    len_candidate = len(candidate)

    if len_offer > len_candidate:
        score = 0
        for w1 in offer:
            for w2 in candidate:
                score += w1.path_similarity(w2)
        score = score * (len_candidate / len_offer)
    else:
        score = 0
        for w1 in offer:
            for w2 in candidate:
                score = max(score, w1.path_similarity(w2))
    return score


def lemmatize_title(title):
    # split title pairs by space
    domain = title[0].split(' ')
    function = title[1].split(' ')

    # lemmatize title pairs
    domain = [wn_lemmatizer.lemmatize(w) for w in domain]
    function = [wn_lemmatizer.lemmatize(w) for w in function]

    return domain, function


def get_similarity(offer_title, candidate_title):
    # Split titles into (domain, function pairs)
    offer_title = offer_title.split(',')
    candidate_title = candidate_title.split(',')

    # lemmatize :
    offer_domain, offer_funct = lemmatize_title(offer_title)
    candidate_domain, candidate_funct = lemmatize_title(candidate_title)

    # get wordnet synonyme sets
    offer_domain = [wn.synset(w + '.n.01') for w in offer_domain]
    offer_funct = [wn.synset(w + '.n.01') for w in offer_funct]
    candidate_domain = [wn.synset(w + '.n.01') for w in candidate_domain]
    candidate_funct = [wn.synset(w + '.n.01') for w in candidate_funct]

    # get score by calculating similarity and returning it
    # the 3/4 and 1/4 factors are to highlight the importance of domain over function
    score = 0.75 * calculate_score(offer_domain, candidate_domain) + 0.25 * calculate_score(offer_funct, candidate_funct)
    return score


def intersection_ratio(a, b):
    # a, b : string of items separated by ','
    if a and b:
        a = a.split(',')
        b = b.split(',')
        return len(set(a) & set(b)) / len(set(b))
    else:
        return 0


def get_score(offer, candidate):
    score = 0

    # Degree and experience equally important.
    score += 10000 * get_similarity(offer.title, candidate.title)
    if offer.degree == candidate.degree:
        score += 1000
    if offer.experience != 0:
        score += 1000 * min((candidate.experience / offer.experience), 1)
    else:
        score += 100 * candidate.experience

    score += 100 * intersection_ratio(offer.programming, candidate.programming)
    score += 10 * intersection_ratio(offer.frameworks, candidate.frameworks)
    score += intersection_ratio(offer.languages, candidate.languages)

    print('offer : ', offer.title, 'candidate name :', candidate.name, 'score : ', score)
    return score
