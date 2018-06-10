'''
Created on 29 May 2018

@author: SchilsM
'''
import webbrowser

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen
from kivy.core.window import Window
from kivy.properties import ObjectProperty

from de_spel.words import Words
        
###########################################################################################################################################    
class DeSpelRoot(BoxLayout):
    """
    Root  of all widgets
    """
    def __init__(self, **kwargs):
        super(DeSpelRoot, self).__init__(**kwargs)
        self.screen_list = []
        
        
    def changeScreen(self, next_screen):
        
        # If next_screen is not in the list of screens, add it
        if self.ids.kivy_screen_manager.current not in self.screen_list:
            self.screen_list.append(self.ids.kivy_screen_manager.current)
            
        if next_screen == "over deze toep":
            self.ids.kivy_screen_manager.current = "about_screen"
        elif next_screen == "oefenen":
            self.ids.kivy_screen_manager.current = "add_location_screen"
        else:
            self.ids.kivy_screen_manager.current = "game_screen"
               
    def onEscBtn(self):
        # Check if there are any screens to go back to
        if self.screen_list:
            # If there are screens we can go back to. do it
            self.ids.kivy_screen_manager.current = self.screen_list.pop()
            # We don't want to close
            return True
        # No more screens to go back to, but we still do not want to close
        return True

    
    
###########################################################################################################################################    
class GameScreen(Screen, Words):
    """
    The game screen
    """
    articles = ObjectProperty()
    def __init__(self, *args, **kwargs):
        super(GameScreen, self).__init__(*args, **kwargs)
        
    def on_play(self):
        print(self.word.text)
        

###########################################################################################################################################    
class AddLocationScreen(Screen):
    """
    A tutorial screen
    """
    search_input = ObjectProperty()
    
    def __init__(self, *args, **kwargs):
        super(AddLocationScreen, self).__init__(*args, **kwargs)
        
    def search_location(self):
        print("Search location {}".format(self.search_input.text))
        
            
###########################################################################################################################################    
class DeSpelApp(App):
    """
    The App
    """
    def __init__(self, **kwargs):
        super(DeSpelApp, self).__init__(**kwargs)
        self.title = "De Spel"
        Window.bind(on_keyboard=self.onEscBtn)
        
    def build(self):
        return DeSpelRoot()
    
    def onEscBtn(self, window, key, *args):
    # User presses back button
        if key == 27:
            return self.root.onEscBtn()
        pass
        
    def getText(self):
        return ("Goedendag!"
                "\n\n"
                "    Het idee voor [i][b]De Spel[/b][/i] was van Wim Hardeman "
                "en zij heeft ook de spelregels bedacht."
                "\n"
                "    Marietje schilstra, onder de schuilnaam [i]ubenu[/i], heeft de Toep* voor [i]De Spel[/i] geschreven, "
                "in de geheimtaal [ref=python][u]python[/u][/ref]. Voor het ontwikkelen van " 
                "de gebruikersvensters heeft zij gebruik gemaakt van de "
                "[ref=kivy][u]kivy[/u][/ref]-bibliotheek.  " 
                "[ref=source][u]Hier[/u][/ref] vindt u het geheimschrift."
                "\n\n\n\n"
                "    * [i]Toep[/i], kort voor [i]Toepassing[/i], is Nederlands voor [i]App[/i]. "
                "\n\n"
                
#                "This App is under the [b][ref=mit]MIT Licence[/ref][/b]\n"
            )
         
    def on_ref_press(self, instance, ref):
        _dict = {
            "kivy": "http://kivy.org/#home",
            "python": "https://www.python.org/",
            "source": "https://github.com/ubenu/NieuweWoordenLeren",
#            "mit": "https://github.com/gopar/Kivy-Tutor/blob/master/LICENSE.md",
             }
        if ref in _dict:
            webbrowser.open(_dict[ref])

        
###########################################################################################################################################    
if __name__ == '__main__':
    DeSpelApp().run()
    
    