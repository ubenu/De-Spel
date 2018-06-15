'''
Created on 29 May 2018

@author: SchilsM
'''
import webbrowser

from kivy.app import App
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.properties import ObjectProperty


from despel.words import Words
        
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
            self.ids.kivy_screen_manager.get_screen("game_screen").on_draw()
            
               
    def onEscBtn(self):
        # Check if there are any screens to go back to
        if self.screen_list:
            # If there are screens we can go back to, do it
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
    ui_articles, ui_stakes, ui_heaps = ObjectProperty(), ObjectProperty(), ObjectProperty()
    ui_word, ui_heap_current, ui_total = ObjectProperty(), ObjectProperty(), ObjectProperty()
    ui_draw, ui_go = ObjectProperty(), ObjectProperty()

    def __init__(self, *args, **kwargs):
        super(Words, self).__init__()
        super(GameScreen, self).__init__(*args, **kwargs)
        self.result_popup = ResultPopup()        
        
    def on_state_changed(self):
        self.ui_go.disabled = True
        article, stake = '', ''
        current_word = self.ui_word.text
        for btn in self.ui_articles.children:
            if btn.state == 'down':
                article = btn.name.lower()
        for btn in self.ui_stakes.children:
            if btn.state == 'down':
                stake = btn.name.lower()
        if article and stake and current_word:
            self.ui_go.disabled = False
        
    def on_go(self):
        article, stake = '', ''
        for btn in self.ui_articles.children:
            if btn.state == 'down':
                article = btn.name.lower()
        for btn in self.ui_stakes.children:
            if btn.state == 'down':
                stake = btn.name.lower()
        if article and stake:
            self.set_result(article, stake)
            corr_art = self.current_word_pack.Lidwoord.iloc[0]
            word = self.current_word_pack.Woord.iloc[0].lower()
            correct = corr_art.lower() == article.lower()             
            self.ui_total.text = "Totaal: {}".format(self.get_total())
            dist = self.get_heap_distribution()
            self.ui_heaps.text = dist.to_string(index=False, justify="left")
            self.result_popup.open(correct, word, corr_art)
            self.on_draw()
                   
    def on_draw(self):
        self.draw_word()
        try:
            word = self.current_word_pack.Woord.to_string(index=False)
            heap = self.current_word_pack.Stapel.to_string(index=False)
            self.ui_word.text = word
            self.ui_heap_current.text = "({})".format(heap)
            for btn in self.ui_articles.children:
                btn.state = 'normal'
            for btn in self.ui_stakes.children:
                btn.state = 'normal'
                btn.disabled = False 
                stake = btn.name.lower()
                scoring_for_heap = self.scoring[self.scoring.Stapel.str.lower() == heap.lower()]
                if scoring_for_heap.Inzet.str.lower().isin([stake,]).any():
                    scoring_for_stake = scoring_for_heap[scoring_for_heap.Inzet.str.lower() == stake]
                    corr = scoring_for_stake[scoring_for_stake.Antwoord.str.lower() == 'goed']
                    if corr.Advies.iloc[0] == 'Kies':
                        btn.state = 'down'  
                    incorr = scoring_for_stake[scoring_for_stake.Antwoord.str.lower() == 'fout']
                    pnts_corr = corr.Punten.iloc[0]
                    pnts_incorr = incorr.Punten.iloc[0]
                    btn.text = "{}\nGoed: +{:d}\nFout: {:d}".format(btn.name, pnts_corr, pnts_incorr)
                else:
                    btn.text = btn.name
                    btn.disabled = True
            self.on_state_changed()

        except Exception as e:
            print(e)
            print("Fout opgetreden bij trekken van nieuw woord")
            
    def on_save(self):
        print(self.player)
        
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
                "[sub]* [i]Toep[/i], kort voor [i]Toepassing[/i], is Nederlands voor [i]App[/i].[/sub] "

                
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

        
###########################################################################################################################################    
if __name__ == '__main__':
    DeSpelApp().run()
    
    