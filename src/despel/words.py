'''
Created on 31 May 2018

@author: SchilsM
'''

import pandas
import numpy



class Words(object):
    '''
    Used to draw random words from the master wordlist
    '''

    def __init__(self, 
                 player_path="",
                 master_path=".//master_wordlist.csv", 
                 scoring_path=".//scoring.csv",
                 heap_data_path=".//heap_data.csv",
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
        self.player_path = player_path
        self.heap_words = pandas.DataFrame(index=self.heaps)
        self.master_wordlist = None
        self.scoring = None
        self.player = None
        self.heap_data = None
        self.open_word_list(master_path)
        self.open_scoring(scoring_path)
        self.open_heap_data(heap_data_path)
        self.open_personal_score(player_path)
        if self.player is None:
            sample_index = numpy.random.choice(self.master_wordlist.index, n_words, replace=False)
            self.player = self.master_wordlist.loc[sample_index]
            self.player.columns.tolist().extend(['Stapel', 'Punten', 'Geschiedenis'])
            self.player.loc[:, 'Stapel'] = self.heaps[0]
            self.player.loc[:, 'Punten'] = 0
            self.player.loc[:, 'Geschiedenis'] = ""
        self.current_word_pack = None
        self.total_score = 0
            
    def set_result(self, article, stake):
        heap = self.current_word_pack.Stapel.to_string(index=False)
        correct = article.lower() == self.current_word_pack.Lidwoord.to_string(index=False).lower()
        score = self.scoring.loc[(heap, stake),]['Fout','Goed']
        destination = ("Gezien", stake)
        s = ('F', 'G')[correct]
#        score, destination = self._get_points_and_destination(hp, stake, correct)
        self.player.loc[self.current_word_pack.index[0],'Punten'] += score[correct]
        self.player.loc[self.current_word_pack.index[0],'Stapel'] = destination[correct]
        self.player.loc[self.current_word_pack.index[0],'Geschiedenis'] += s
                
#     def _get_points_and_destination(self, heap, stake, correct):
#         
#         hp = self.scoring[self.scoring.Stapel.str.lower() == heap.lower()]
#         hp_st = hp[hp.Inzet.str.lower() == stake.lower()]
#         entry = (hp_st[hp_st.Antwoord.str.lower() == 'fout'], 
#                  hp_st[hp_st.Antwoord.str.lower() == 'goed'])[correct]
#         return entry.Punten.iloc[0], entry.Bestemming.iloc[0]
            
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
        probs = []
        for index, row in self.player.iterrows():
            for index2, row2 in self.heap_data.iterrows():
                if row.Stapel == index2:
                    probs.extend(int(row2.Trekkans) * [index])
        sample_index = numpy.random.choice(probs, 1, replace=True)
        self.current_word_pack = self.player.loc[sample_index, :]

    def open_word_list(self, file_path):
        try:
            self.master_wordlist = pandas.read_csv(file_path).loc[:,['Woord', 'Lidwoord']]
        except Exception as e:
            print(e)
            print("No master wordlist")
            
    def open_personal_score(self, file_path):
        try:
            self.player = pandas.read_csv(file_path) 
        except Exception as e:
            print(e)
            print("No player data")
            
    def open_scoring(self, file_path):
        try:
            self.scoring = pandas.read_csv(file_path, index_col=(0, 1))  
        except Exception as e:
            print(e)
            print("No scoring info")
      
    def open_heap_data(self, file_path):
        try:
            self.heap_data = pandas.read_csv(file_path, index_col=0) 
        except Exception as e:
            print(e)
            print("No scoring info")
      
