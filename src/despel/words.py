'''
Created on 31 May 2018

@author: SchilsM
'''

import pandas
import numpy
from tables.table import Cols

class Words(object):
    '''
    Used to draw random words from the master wordlist
    '''


    def __init__(self, 
                 master_path=".//master_wordlist.csv", 
                 scoring_path=".//scoring.csv",
                 player_path=".//player.csv",
                 n_words=20,
                 ):
        '''
        Constructor
        @master_path: path to master word list (all possible words)
        @scoring_path: path to file with scoring system
        @player_path: path to data of individual player
        @n_words: maximum number of words not in Goud or Platina 
        '''
        self.heaps = "Nieuw Gezien Zilver Goud Platina".split()
        self.stakes = "Goud Zilver Platina".split()
        self.answer_qual = "Fout Goed".split()
        self.heap_words = pandas.DataFrame(index=self.heaps)
        self.master_wordlist = None
        self.scoring = None
        self.player = None
        self.open_word_list(master_path)
        self.open_scoring(scoring_path)
#        self.open_personal_score(player_path)
        if not (self.master_wordlist is None or self.scoring is None):
            if self.player is None:
                # No Player file, therefore, take n_words from the master_wordlist and assign all the status 'Nieuw'
                sample_index = numpy.random.choice(self.master_wordlist.index, n_words, replace=False)
                self.player = self.master_wordlist.loc[sample_index]
                self.player.columns.tolist().append('Stapel')
                self.player.loc[:, 'Stapel'] = self.heaps[0]
            
    def play(self, word, article, stake):
        print(word, article, stake)
            
    def draw_word(self):
        sample_index = numpy.random.choice(self.player.index, 1, replace=True)
        return self.player.loc[sample_index, :]

    def open_word_list(self, file_path):
        try:
            self.master_wordlist = pandas.read_csv(file_path).loc[:,['Woord', 'Lidwoord']]
            print(self.master_wordlist)
        except Exception as e:
            print(e)
            print("No master wordlist")
            
    def open_personal_score(self, file_path):
        try:
            self.player = pandas.read_csv(file_path) 
            print(self.player)
        except Exception as e:
            print(e)
            print("No player data")
            
    def open_scoring(self, file_path):
        try:
            self.scoring = pandas.read_csv(file_path)  
        except Exception as e:
            print(e)
            print("No scoring info")
      
