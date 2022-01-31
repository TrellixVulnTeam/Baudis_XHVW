import re

from requests import get
from bs4 import BeautifulSoup
import urllib3
from threading import Thread
from kivy.clock import Clock
import subprocess
import sys
import errno

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

def downloadBook(title, bookDict):
    thread = Thread(target=runDownload,args=(title, bookDict))
    thread.start()
    return None

def runDownload(title, bookDict):
    with subprocess.Popen([sys.executable, 'BookDownloader.py'],stdin=subprocess.PIPE,
                          stdout=subprocess.PIPE,encoding='utf-8') as downloadUtil:
        try:
            linkTitle = '-d {link} ||| {title}'.format(link = bookDict['link'],title = title)
            downloadUtil.stdin.write(linkTitle)
            downloadUtil.stdin.flush()
            downloadUtil.stdin.close()
            while True:
                while True:
                    message = downloadUtil.stdout.readline()
                    if message != '':
                        message = message.strip()
                        print(message)
                        if 'Load' in message:
                            percent = message.removeprefix('Load: ')
                            percent = percent.removesuffix('%')
                            bookDict['button'].on_progress(percent)
                    if('Filepath: ' in message):
                        message = message.removeprefix('Filepath: ')
                        bookDict['button'].filepath = message
                    if 'Close downloader' in message:
                        bookDict['button'].on_loaded()
                        downloadUtil.kill()
                        return
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