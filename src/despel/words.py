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
                self.player.columns.tolist().extend(['Stapel', 'Punten'])
                self.player.loc[:, 'Stapel'] = self.heaps[0]
                self.player.loc[:, 'Punten'] = 0
        self.current_word_pack = None
        self.total_score = 0
            
    def set_result(self, article, stake):
        if self.current_word_pack is None:
            pass
        else:
            correct_article = self.current_word_pack.Lidwoord.to_string(index=False)
            heap = self.current_word_pack.Stapel.to_string(index=False)
            result = self.get_points_and_next_heap(heap, stake, article.lower() == correct_article.lower())
            self.total_score += result[0]
            self.player.loc[self.current_word_pack.index[0],'Punten'] += result[0]
            self.player.loc[self.current_word_pack.index[0],'Stapel'] = result[1]
                
    def get_points_and_next_heap(self, heap, stake, correct):
            scoring_for_heap = self.scoring[self.scoring.Stapel.str.lower() == heap.lower()]
            scoring_for_stake = scoring_for_heap[scoring_for_heap.Inzet.str.lower() == stake.lower()]
            entry = scoring_for_stake[scoring_for_stake.Antwoord.str.lower() == 'fout']
            if correct:
                entry = scoring_for_stake[scoring_for_stake.Antwoord.str.lower() == 'goed']
            return (
                entry.Punten.iloc[0],
                entry.Bestemming.iloc[0]
                )
            
    def get_total(self):
        return self.player.Punten.sum()
    
    def get_heap_distribution(self):
        dist = pandas.DataFrame(index=self.heaps, columns=["Stapel", "Aantal woorden"])
        for h in self.heaps:
            hps = self.player.loc[:, 'Stapel']
            dist.loc[h,"Stapel"] = h
            dist.loc[h,"Aantal woorden"] = hps.loc[hps==h].count()
        return dist

        
    def draw_word(self):
        sample_index = numpy.random.choice(self.player.index, 1, replace=True)
        self.current_word_pack = self.player.loc[sample_index, :]

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
      
