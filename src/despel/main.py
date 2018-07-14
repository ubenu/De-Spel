'''
Created on 29 May 2018

@author: SchilsM
'''
import webbrowser

from kivy.app import App
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.properties import ObjectProperty
from kivy.properties import StringProperty

from despel.words import Words
from despel.json_settings import json_settings
        
###########################################################################################################################################    
class DeSpelRoot(BoxLayout):
    """
    Root  of all widgets
    """
    def __init__(self, **kwargs):
        super(DeSpelRoot, self).__init__(**kwargs)
        self.screen_list = []
        self.user_name = "gast"
        
        
    def changeScreen(self, next_screen): 
        # If next_screen is not in the list of screens, add it
        current_screen = self.ids.kivy_screen_manager.current
        if current_screen == "start_screen" or current_screen == "game_screen":
            self.user_name = self.ids.kivy_screen_manager.get_screen(current_screen).ui_user_name.text
        if self.ids.kivy_screen_manager.current not in self.screen_list:
            self.screen_list.append(self.ids.kivy_screen_manager.current)
        
        if next_screen == "over deze toep":
            self.ids.kivy_screen_manager.current = "about_screen"
        elif next_screen == "spelen":
            self.ids.kivy_screen_manager.current = "game_screen"
            game_screen = self.ids.kivy_screen_manager.get_screen("game_screen")
            game_screen.ui_user_name.text = self.user_name
            game_screen.setup_player(self.user_name)
            self.ids.kivy_screen_manager.get_screen("game_screen").on_draw()
        else:
            pass
            
               
    def onEscBtn(self):
        current_screen = self.ids.kivy_screen_manager.current
        if current_screen == "game_screen":
            self.user_name = self.ids.kivy_screen_manager.get_screen(current_screen).ui_user_name.text
        # Check if there are any screens to go back to
        if self.screen_list:
            # If there are screens we can go back to, do it
            previous_screen = self.screen_list.pop()
            if previous_screen == "start_screen":
                self.ids.kivy_screen_manager.get_screen(previous_screen).ui_user_name.text = self.user_name
            self.ids.kivy_screen_manager.current = previous_screen
            # We don't want to close
            return True
        # No more screens to go back to, but we still do not want to close
        return True

###########################################################################################################################################    
class StartScreen(Screen):
    ui_user_name: StringProperty()  
    
    def __init__(self, *args, **kwargs):  
        super(StartScreen, self).__init__(*args, **kwargs)

    
###########################################################################################################################################    
class GameScreen(Screen, Words):
    """
    The game screen
    """
    ui_articles, ui_stakes, ui_heaps = ObjectProperty(), ObjectProperty(), ObjectProperty()
    ui_word, ui_heap_current, ui_total = ObjectProperty(), ObjectProperty(), ObjectProperty()
    ui_draw, ui_go, ui_save = ObjectProperty(), ObjectProperty(), ObjectProperty()
    ui_user_name = ObjectProperty()
    
    def __init__(self, *args, **kwargs):
        super(GameScreen, self).__init__(*args, **kwargs)
        self.result_popup = ResultPopup() 
        
    def on_state_changed(self):
        self.ui_go.disabled = True
        self.ui_save.disabled = True
        if (self.player.Geschiedenis != "").all():
            self.ui_save.disabled = False
        article, stake = '', ''
        for btn in self.ui_articles.children:
            if btn.state == 'down':
                article = btn.name
        for btn in self.ui_stakes.children:
            if btn.state == 'down':
                stake = btn.name
        if article and stake:
            self.ui_go.disabled = False
        
    def on_go(self):
        article, stake = '', ''
        for btn in self.ui_articles.children:
            if btn.state == 'down':
                article = btn.name
        for btn in self.ui_stakes.children:
            if btn.state == 'down':
                stake = btn.name
        if article and stake:
            self.set_result(article, stake)
            corr_art = self.current_word_pack.Lidwoord[0]
            word = self.current_word_pack.index[0].lower()
            correct = corr_art.lower() == article.lower()             
            self.result_popup.open(correct, word, corr_art)
            self.on_draw()
                   
    def on_draw(self):
        self.draw_word()
        try:
            word = self.current_word_pack.index[0] #.to_string(index=False)
            heap = self.current_word_pack.Stapel[0] #.to_string(index=False)
            self.ui_word.text = word
            self.ui_heap_current.text = "Uit:\n{}".format(heap)
            for btn in self.ui_articles.children:
                btn.state = 'normal'
            for btn in self.ui_stakes.children:
                btn.state = 'normal'
                btn.disabled = False
                if self.scoring.loc[heap].index.isin([btn.name,]).any():
                    pts0, pts1 = self.scoring.loc[(heap, btn.name),][['Fout','Goed']]   
                    btn.text = "{}\nGoed: +{:d}\nFout: {:d}".format(btn.name, int(pts1), int(pts0))                         
                else:
                    btn.text = btn.name
                    btn.disabled = True                
                if self.heap_data.Advies.loc[heap] == btn.name:
                    btn.state = 'down'
            self.on_state_changed()
            dist = self.get_heap_distribution()
            dist_str = ""
            for s, n in dist.iterrows():
                dist_str += s[0] + "  " + n[0] * '|' + '\n'
            self.ui_total.text = "{}".format(self.get_total())                
            self.ui_heaps.text = dist_str 
        except Exception as e:
            print(e)
            
    def on_save(self):
        if not self.ui_user_name.text == "":
            name = self.ui_user_name.text
        self.save_player(name)
            


###########################################################################################################################################    
class ResultPopup(Popup):
    """
    Widget that pops up to inform users whether they got the answer right or wrong
    """
    message = ObjectProperty()
    close_button = ObjectProperty()
    
    def __init__(self, *args, **kwargs):
        super(ResultPopup, self).__init__(*args, **kwargs)
        
    def open(self, correct, word, article):
        # If answer is correct, take off button if it's visible
        if correct:
            self.title = "Inderdaad"
            self.message.text = "[i]{}[/i] {}.".format(article, word)
            if self.close_button in self.content.children:
                self.content.remove_widget(self.close_button)
        # If answer is not correct, display button if it's hidden
        else:
            self.title = "Helaas..."
            self.message.text = "Het is [b]{}[/b] {}.".format(article, word)
            if self.close_button not in self.content.children:
                self.content.add_widget(self.close_button)
                
        # Display popup
        super(ResultPopup, self).open()
        if correct:
            Clock.schedule_once(self.dismiss, 1)
                            
            
###########################################################################################################################################    
class DeSpelApp(App):
    """
    The App
    """
    def __init__(self, **kwargs):
        super(DeSpelApp, self).__init__(**kwargs)
        self.title = "De Spel"
        Window.bind(on_keyboard=self.onEscBtn)
        self.use_kivy_settings = False
        
    def build(self):
        return DeSpelRoot()
    
    def onEscBtn(self, window, key, *args):
        if key == 27: # Escape button on keyboard
            return self.root.onEscBtn()
        pass
        
    def getText(self):
        return (
            "Het idee voor [i][b]De Spel[/b][/i] was van Wim Hardeman "
            "en zij heeft ook de spelregels bedacht."
            "\n"
            "Onder de schuilnaam [i]ubenu[/i] heeft Marietje Schilstra de Toep* voor [i]De Spel[/i] geschreven, "
            "in de codeertaal [ref=python][u]python[/u][/ref]. Voor het ontwikkelen van "                 
            "de gebruikersvensters heeft zij gebruik gemaakt van de "
            "[ref=kivy][u]kivy[/u][/ref]-bibliotheek.  " 
            "[ref=source][u]Hier[/u][/ref] vindt u de codering."
            "\n\n"
            "Deze Toep is uitgebracht onder de [u][i][ref=gnu_gpl]GNU General Public License v3.0[/ref][i][/u]\n"
            "\n\n"
            "* [i]Toep[/i], kort voor [i]Toepassing[/i], is Nederlands voor [i]App[/i].[/sub] "     
            )
         
    def on_ref_press(self, instance, ref):
        _dict = {
            "kivy": "http://kivy.org/#home",
            "python": "https://www.python.org/",
            "source": "https://github.com/ubenu/DeSpel",
            "gnu_gpl": "https://github.com/ubenu/DeSpel/blob/master/src/despel/LICENSE",
             }
        if ref in _dict:
            webbrowser.open(_dict[ref])

    def build_config(self, config):
        config.setdefaults("General", {"n_words": 20, })
        
    def build_settings(self, settings):
        settings.add_json_panel("De Spel", self.config, data=json_settings)
        
if __name__ == '__main__':
    DeSpelApp().run()
    
    