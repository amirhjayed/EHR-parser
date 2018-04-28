
# THIS MODULE ISN'T PART OF THE PROJECT
# Used it to scrape CS jobs from an article+_

from bs4 import BeautifulSoup
import requests

url = 'https://www.computersciencezone.org/50-highest-paying-jobs-computer-science/'

page = requests.get(url)
data = page.text
soup = BeautifulSoup(data)
a = soup.find_all('h2')
jobs = ''
for i in a:
    b = i.contents[0]
    result = ''.join([i for i in b if not i.isdigit()])
    print(result)
    jobs += result[2:] + '\n'


jobs = jobs.split('\n')
jobs = [w.upper() for w in jobs]
print(jobs)


# A = [1, 3, 5]
# B = [2, 4, 6]

# C = zip(A, B)
# for c in C:
#     print(c)
