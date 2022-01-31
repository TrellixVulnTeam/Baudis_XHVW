
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
    loaded = False
    filepath = ''

    def on_progress(self,percent):
        for child in self.children:
            if (isinstance(child, Button)):
                percent = percent.strip()
                child.text = f'Loading: {percent}% {self.title}'
                child.color = (0, 1 / 100 * int(percent) ,0,1) #than close to complete than greener
                return
    def on_loaded(self):
        for child in self.children:
            if (isinstance(child, Button)):
                child.text = self.title
                child.color = (0, 0.9, 0, 1)  # than close to complete than greener
        self.loaded = True

class ListLayout(GridLayout):
    pass

class SearchTabs(BoxLayout):
    pass

class MainMenu(BoxLayout):
    pass

class FilterTab(Button):
    pass

class CloseButton(Button):
    title = ''
    audioButton = None



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
            self.booksList[filename] = {'button': btn}

            for child in btn.children:
                if (isinstance(child, Button)):
                    child.text = filename
                    child.bind(on_press=self.playBook)
                elif isinstance(child, RelativeLayout):
                    for relativeChild in child.children[0].children:
                        if isinstance(relativeChild, CloseButton):
                            relativeChild.title = filename
                            relativeChild.audioButton = btn
                            relativeChild.bind(on_press=self.deleteBook)
            self.listLayout.add_widget(btn)
            btn.on_loaded()

        return self.root

    def playBook(self, button):
        if self.booksList[button.text]['button'].loaded:
            os.system('start {filepath}'.format(filepath = self.booksList[button.text]['button'].filepath))
        else:
            link = scraper.downloadBook(button.text, self.booksList[button.text])  # Load & parse web-page of book

    def deleteBook(self, button):
        title = button.title
        path = os.path.expanduser('~\Baudis\SavedBooks\\')
        for filename in os.listdir(path):
            if title in filename:
                os.remove(path + filename)
                button.audioButton.parent.remove_widget(button.audioButton)


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
            self.booksList[title] = {'link': self.booksList[title],'button': btn}
            for child in btn.children:
                if isinstance(child, Button):
                    child.text = title
                    child.bind(on_press=self.playBook)
                elif isinstance(child, RelativeLayout):
                    for relativeChild in child.children[0].children:
                        if isinstance(relativeChild,CloseButton):
                            relativeChild.title = title
                            relativeChild.audioButton = btn
                            relativeChild.bind(on_press=self.deleteBook)

            self.listLayout.add_widget(btn)

if __name__ == '__main__':
    BaudisApp().run()


