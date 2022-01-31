
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.config import Config
from kivy.core.window import Window
from kivy.uix.textinput import TextInput
from requests_html import HTMLSession
from multiprocessing import Process, freeze_support
from kivy.graphics import Color, Rectangle
import glob
import os
import scraper

Config.set('graphics', 'width', '400')
Config.set('graphics', 'height', '370')

class ScrollContainer(ScrollView):
    pass

class AudioButton(RelativeLayout):
    title = ''
    onLoad = False
    loaded = False
    filepath = ''
    runAfterLoad = False
    baudisApp = None

    def on_progress(self,percent):
        for child in self.children:
            if (isinstance(child, Button)):
                percent = percent.strip()
                child.text = f'Loading: {percent}% {self.title}'
                child.color = (0, 0.2 + 0.7 / 100 * int(percent) ,0,1) #than close to complete than greener
                return
    def on_loaded(self):
        #Change color of text to green and remove "Loading" prefix
        for child in self.children:
            if isinstance(child, Button):
                child.text = self.title
                child.color = (0, 0.9, 0, 1)  # than close to complete than greener
            elif isinstance(child, RelativeLayout):
                deleteButton = DeleteButton()
                deleteButton.audioButton = self
                deleteButton.bind(on_press=self.deleteBook)
                child.children[0].add_widget(deleteButton)
        self.loaded = True
        self.onLoad = False

        if self.runAfterLoad == True:
            self.playBook()

    def deleteBook(self, button):
        os.remove(self.filepath)
        self.parent.remove_widget(self)

    def playBook(self, button = None):
        if self.loaded:
            if self.runAfterLoad == True:
                self.runAfterLoad = False
            os.system('start {filepath}'.format(filepath = self.filepath))
        elif self.onLoad == False: #Loading book if it not in loading process yet, but now run it after load
            self.onLoad = True
            self.runAfterLoad = True
            link = scraper.downloadBook(self.title, self.baudisApp.booksList[self.title])  # Load & parse web-page of book


class ListLayout(GridLayout):
    pass

class SearchTabs(BoxLayout):
    pass

class MainMenu(BoxLayout):
    pass

class FilterTab(Button):
    pass

class DeleteButton(Button):
    audioButton = None

class SearchInput(TextInput):
    pass

class BaudisApp(App):
    booksList = {} #List with loaded and not loaded books

    def build(self):
        # create a default grid layout with custom width/height
        self.listLayout = ListLayout()

        # when we add children to the grid layout, its size doesn't change at
        # all. we need to ensure that the height will be the minimum required
        # to contain all the childs. (otherwise, we'll child outside the
        # bounding box of the childs)
        self.listLayout.bind(minimum_height=self.listLayout.setter('height'))

        # create a scroll view, with a size < size of the grid
        self.root = MainMenu()
        for child in self.root.children:
            if isinstance(child, ScrollContainer):
                child.add_widget(self.listLayout)

        for child in self.root.children:
            if(isinstance(child,TextInput)):
                searchInput = child
                searchInput.bind(on_text_validate=self.showBooks)

        # Load and option existed abooks
        for filename in os.listdir(os.path.expanduser('~\Baudis\SavedBooks\\')):
            btn = AudioButton()
            btn.filepath = os.path.expanduser('~\Baudis\SavedBooks\\') + filename
            filename = filename.removesuffix('.mp3').replace('_',' ')
            btn.title = filename
            btn.baudisApp = self
            self.booksList[filename] = {'button': btn}

            for child in btn.children:
                if (isinstance(child, Button)):
                    child.text = filename
                    child.bind(on_press=btn.playBook)
            self.listLayout.add_widget(btn)
            btn.on_loaded()

        return self.root

    def showBooks(self, value):

        #Removing not loaded books for show new search results
        notLoadedBooksKeys = list( filter( lambda book: self.booksList[book]['button'].loaded == False,self.booksList.keys()) )
        for bookKey in notLoadedBooksKeys:
            self.listLayout.remove_widget(self.booksList[bookKey]['button'])
            self.booksList.pop(bookKey)

        # Sorting books who's not icluded yet in book list
        parsedBookList = scraper.search(value.text)
        uniqueBookKeys = list( filter(lambda book: self.booksList.get(book) == None,parsedBookList.keys()) )

        for bookKey in uniqueBookKeys: #Adding unique books in bookList
            self.booksList[bookKey] = parsedBookList[bookKey]

        #Create buttons for new books
        for title in uniqueBookKeys:
            btn = AudioButton()
            btn.title = title
            btn.baudisApp = self
            self.booksList[title] = {'link': self.booksList[title],'button': btn}
            for child in btn.children:
                if isinstance(child, Button):
                    child.text = title
                    child.audioButton = btn
                    child.bind(on_press=btn.playBook)

            self.listLayout.add_widget(btn)

if __name__ == '__main__':
    BaudisApp().run()


