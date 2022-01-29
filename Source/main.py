
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

import scraper

Config.set('graphics', 'width', '400')
Config.set('graphics', 'height', '370')

class ScrollContainer(ScrollView):
    pass

class AudioButton(RelativeLayout):
    pass

class ListLayout(GridLayout):
    pass

class SearchTabs(BoxLayout):
    pass

class MainMenu(BoxLayout):
    pass

class FilterTab(Button):
    pass



class BaudisApp(App):

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

        return self.root

    def playBook(self, value):
        link = scraper.downloadBook(self.booksList[value.text],value.text) #Load & parse web-page of book
        #scraper.createDownloadThread(link,'{fileName}.mp3'.format(fileName = value.text))

    def showBooks(self, value):
        self.booksList = scraper.search(value.text)

        for title in self.booksList.keys():
            btn = AudioButton()
            for child in btn.children:
                if (isinstance(child, Button)):
                    child.text = title
                    child.bind(on_press=self.playBook)
            self.listLayout.add_widget(btn)

if __name__ == '__main__':
    BaudisApp().run()


