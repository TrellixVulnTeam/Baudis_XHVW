import io
import threading

from requests import get
from bs4 import BeautifulSoup
import urllib3
from threading import Thread
from requests_html import HTMLSession
from kivy.clock import Clock
from functools import partial
import subprocess
import sys
import errno
import codecs

SEARCH_PARSE = 'String for identification of parsed html page'
BOOKPAGE_PARSE = 'String for identification of parsed book page'

def search(str):
    response = get('https://akniga.org/search/books/?q={title}'.format(title=str))
    books = parseBookList(response.text)
    return books

def parseBookList(html):
    soup = BeautifulSoup(html, 'lxml')
    bookTitlesUnparsed = soup.find_all('h2', class_='caption__article-main')
    bookTitlesParsed = []

    for unparsedTitle in bookTitlesUnparsed: # Transfer unparsed objects into parsed
        bookTitlesParsed.append(unparsedTitle.text.strip())

    bookLinksUnparsed = soup.find_all('a', class_='content__article-main-link tap-link')
    bookLinksParsed = []

    for unparsedLink in bookLinksUnparsed: # Transfer unparsed objects into parsed
        bookLinksParsed.append(unparsedLink['href'])

    return dict(zip(bookTitlesParsed,bookLinksParsed))

def downloadBook(link,title):
    thread = threading.Thread(target=runDownload,args=(link,title))
    thread.start()
    return None

def runDownload(link,title):
    downloadUtil = subprocess.Popen(
        [sys.executable, 'BookDownloader.py'],stdin=subprocess.PIPE, stdout=subprocess.PIPE,encoding='utf-8')
    try:
        linkTitle = '-d {link} ||| {title}'.format(link = link,title = title)
        #print(linkTitle)
        #downloadUtil.stdin.write("f")
        #print(linkTitle)
        #expLink = 'ААААFФФ'
        #print('before send: ' + str(expLink)) codecs.encode()
        print(linkTitle)
        answer = downloadUtil.communicate(linkTitle)
        print(answer[0])

    except IOError as e:
        print("error")
        if e.errno == errno.EPIPE or e.errno == errno.EINVAL:
            # Stop loop on "Invalid pipe" or "Invalid argument".
            # No sense in continuing with broken pipe.
            print(e.errno)
        else:
            print(e)
            # Raise any other error.
            raise

    #stdout_data = downloadUtil.communicate(input='data_to_write')[0]

    #downloadUtil.stdin.write('exit')
    #downloadUtil.stdin.flush()