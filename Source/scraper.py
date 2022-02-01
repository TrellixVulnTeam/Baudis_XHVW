import re
from requests import get
from bs4 import BeautifulSoup
import urllib3
from threading import Thread
from kivy.clock import Clock
import subprocess
import sys
import queue
import errno

runProc = True
downloadUtil = None
baudisBooksList = None
def runDownloadProcess():
    global downloadUtil
    global runProc
    with subprocess.Popen([sys.executable, 'BookDownloader.py'], stdin=subprocess.PIPE,  #Freeze
                          stdout=subprocess.PIPE, encoding='utf-8') as dUtil:
        downloadUtil = dUtil
        thread = Thread(target=getFromSubproc, args=(), daemon=True)
        thread.start()
        dUtil.wait()
        print('here')

def getFromSubproc():
    while True:
        message = downloadUtil.stdout.readline()

        title = re.search(r'Title: .* EndTitle', message)
        if title != None:
            title = title.group(0)
            title = title.removeprefix('Title: ')
            title = title.removesuffix(' EndTitle')
        if message != '':
            message = message.strip()
            if 'Load' in message:
                percent = re.search(r'Load: .*%',message).group(0)
                percent = percent.removeprefix('Load: ')
                percent = percent.removesuffix('%')

                baudisBooksList[title]['button'].on_progress(percent)
        if 'Filepath: ' in message:
            filepath = re.search(r'Filepath: .*;',message).group(0)
            filepath = filepath.removeprefix('Filepath: ')
            filepath = filepath.removesuffix(';')
            baudisBooksList[title]['button'].filepath = filepath
            baudisBooksList[title]['button'].on_loaded()


def sendToSubproc():
    try:  # Check if new book sended to load
       newLoad = loadQueue.get(block=False)
    except queue.Empty as e:
       return

    try:
        global downloadUtil
        linkTitle = '-d {link} ||| {title}'.format(link=newLoad['link'], title=newLoad['button'].title)
        downloadUtil.stdin.write(linkTitle + ' \n')
        downloadUtil.stdin.flush()
        loadQueue.task_done()
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

# Run daemon-thread for book downloading
loadQueue = queue.Queue()

thread = Thread(target=runDownloadProcess,args=(),daemon=True)
thread.start()

