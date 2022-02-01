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
import asyncio

def runAsyncio():
    loop.run_forever()

def downloadBook(link, title, *largs):
    session = HTMLSession()
    response = session.get(link)
    response.html.render()
    response.close()
    downloadLink = findDownloadLink(response)
    task = asyncio.ensure_future(loading(downloadLink, title))

def findDownloadLink(html):
    data_bid = html.html.find('div.bookpage--chapters.player--chapters', first = True).attrs['data-bid']
    jplPlayers = html.html.find('div.jpl')

    for jpl in jplPlayers:
        if('data-bid' in jpl.attrs and jpl.attrs['data-bid'] == data_bid):
            downloadLink = jpl.find('audio',first= True).attrs['src']

    return downloadLink

async def loading(link,filename, path = os.path.expanduser('~/Baudis/SavedBooks')):

    response = poolM.request('GET',link,preload_content = False)#Get file link
    Path(path ).mkdir(parents=True, exist_ok=True)#Create directory for books if not exist
    contentLength = response.getheader('Content-Length')
    chunkSize = 1024
    filePercent = int(contentLength) / 100
    loadPercent = 0;
    inCompletePercent = 0;
    filename = filename.replace(' ','_')

    #Create file and write in
    with open(R'{path}/{filename}.mp3'.format(path=path, filename=filename),'wb') as out_file:
        for chunk in await response.stream(chunkSize):
            if chunk:
                inCompletePercent += chunkSize
                if inCompletePercent >= filePercent:
                    loadPercent += 1
                    inCompletePercent -= filePercent
                    print('Load: {percent}%'.format(percent = loadPercent))
                await out_file.write(chunk)
    print(f' Download end: \n Link: {link} \n Filename: {filename} \n Filepath: {path}/{filename}.mp3')
    print('Close downloader')

poolM = urllib3.PoolManager()
loop = asyncio.get_event_loop()
thread = Thread(target=runAsyncio, args=(), daemon=True)
thread.start()

while True:
    # Listening and executing commands from main process
    LinkTitle = sys.stdin.readline()
    if(LinkTitle.strip() == 'close'):
        session.close()
        thread.close()
        loop.stop()
        print('Closed')
    elif '-d' in LinkTitle:
        LinkTitle = LinkTitle.removeprefix('-d')
        LinkTitle = LinkTitle.split(' ||| ')
        downloadBook(LinkTitle[0],LinkTitle[1])
    else: print('Unknown command {LinkTitle}'.format(LinkTitle = LinkTitle))

