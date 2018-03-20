from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter, XMLConverter, HTMLConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
import os


def convert_pdf(path, outp, format='txt', codec='utf-8', password=''):
    rsrcmgr = PDFResourceManager()
    laparams = LAParams()
    outf = open(outp + '.' + format, 'wb')
    if format == 'txt':
        device = TextConverter(rsrcmgr, outf, codec=codec, laparams=laparams)
    elif format == 'html':
        device = HTMLConverter(rsrcmgr, outf, codec=codec, laparams=laparams)
    elif format == 'xml':
        device = XMLConverter(rsrcmgr, outf, codec=codec, laparams=laparams)
    else:
        raise ValueError('provide format, either text, html or xml!')
    fp = open(path, 'rb')
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    maxpages = 0
    caching = True
    pagenos = set()
    for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password, caching=caching, check_extractable=True):
        interpreter.process_page(page)

    fp.close()
    device.close()
    outf.close()


for fp in os.listdir('.'):
    if fp.endswith(".pdf"):
        convert_pdf(fp, fp[:-4], 'html')
