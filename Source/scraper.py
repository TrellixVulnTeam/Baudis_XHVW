import atexit
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
prevTitle = None
currentPage = 0;

def runDownloadProcess():
    global downloadUtil
    global runProc
    with subprocess.Popen([sys.executable, 'BookDownloader.py'], stdin=subprocess.PIPE,  #Freeze
                          stdout=subprocess.PIPE, encoding='utf-8') as dUtil:
        atexit.register(kill_subprocess)
        downloadUtil = dUtil
        thread = Thread(target=getFromSubprocess, args=(), daemon=True)
        thread.start()
        downloadUtil.wait()

def kill_subprocess():
    downloadUtil.terminate()

def getFromSubprocess():
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
            elif 'Filepath: ' in message:
                filepath = re.search(r'Filepath: .*;',message).group(0)
                filepath = filepath.removeprefix('Filepath: ')
                filepath = filepath.removesuffix(';')
                baudisBooksList[title]['button'].filepath = filepath
                baudisBooksList[title]['button'].on_loaded()
            elif 'Error' in message:
                print(message)
                baudisBooksList[title]['button'].on_error()

            else:
                print(message)


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


def search(title = None):
    global prevTitle
    global currentPage
    if title != None:
        currentPage = 1
        prevTitle = title
    else:
        currentPage += 1
        title = prevTitle
    response = get('https://akniga.org/search/books/page{currentPage}/?q={title}'.format(currentPage=currentPage,title=title))
    books = parseBookList(response.text)
    return books

def parseBookList(html):
    soup = BeautifulSoup(html, 'lxml')

    if soup.find('div',_class="ls-blankslate-text") != None :
        return
    enters = soup.find_all('div', class_='content__main__articles--item')
    entersDict = {}

    for enter in enters:
        paidBook = enter.find('a', {'href': 'https://akniga.org/paid/'})
        if paidBook != None: continue  # Its paid book, don't show in list

        bookTitle = enter.find('h2', class_='caption__article-main')
        bookTitle = bookTitle.text.strip()
        bookLink = enter.find('a', class_='content__article-main-link tap-link')['href']
        entersDict[bookTitle] = bookLink
    return entersDict

# Run daemon-thread for book downloading
loadQueue = queue.Queue()

thread = Thread(target=runDownloadProcess,args=(),daemon=True)
thread.start()

