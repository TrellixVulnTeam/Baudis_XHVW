import codecs
import os.path

from requests import get
from bs4 import BeautifulSoup
import urllib3
from threading import Thread
import threading
from requests_html import HTMLSession
import sys
import codecs
from pathlib import Path

def downloadBook(link, title, *largs):
    with HTMLSession() as session:
        response = session.get(link)
        response.html.render()
        response.close()
        downloadLink = findDownloadLink(response)
        thread = Thread(target=loading, args=(downloadLink, title), daemon=True)
        thread.start()

def findDownloadLink(html):
    data_bid = html.html.find('div.bookpage--chapters.player--chapters', first = True).attrs['data-bid']
    jplPlayers = html.html.find('div.jpl')

    for jpl in jplPlayers:
        if('data-bid' in jpl.attrs and jpl.attrs['data-bid'] == data_bid):
            downloadLink = jpl.find('audio',first= True).attrs['src']

    return downloadLink

def loading(link,title, path = os.path.expanduser('~/Baudis/SavedBooks')):

    response = poolM.request('GET',link,preload_content = False)#Get file link
    Path(path ).mkdir(parents=True, exist_ok=True)#Create directory for books if not exist
    contentLength = response.getheader('Content-Length')
    chunkSize = 1024
    filePercent = int(contentLength) / 100
    loadPercent = 0;
    inCompletePercent = 0;
    filename = title.replace(' ','_')

    #Create file and write in
    with open(R'{path}/{filename}.mp3'.format(path=path, filename=filename),'wb') as out_file:
        for chunk in response.stream(chunkSize):
            if chunk:
                inCompletePercent += chunkSize
                if inCompletePercent >= filePercent:
                    loadPercent += 1
                    inCompletePercent -= filePercent
                    print('Title: {title} EndTitle Load: {percent}%'.format(percent = loadPercent,title = title))
                out_file.write(chunk)
    print(f'Title: {title} EndTitle Download end: Link: {link} Filename: {filename} Filepath: {path}/{filename}.mp3;')

poolM = urllib3.PoolManager()

while True:
    # Listening and executing commands from main process
    LinkTitle = sys.stdin.readline().strip()
    if(LinkTitle.strip() == 'close'):
        session.close()
        thread.close()
        loop.stop()
        print('Closed')
    elif '-d' in LinkTitle:
        LinkTitle = LinkTitle.removeprefix('-d')
        LinkTitle = LinkTitle.split(' ||| ')
        downloadBook(LinkTitle[0],LinkTitle[1])
    elif LinkTitle == '': pass
    else: print('Unknown command {LinkTitle}'.format(LinkTitle = LinkTitle))

