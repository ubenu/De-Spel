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

    def __init__(self):
        '''
        Constructor
        '''
        super(Words, self).__init__()
        master_path=".//master_wordlist.csv"
        scoring_path=".//scoring.csv"
        heap_data_path=".//heap_data.csv"
        n_words=5
        self.n_words = n_words, 
        self.heaps = "Nieuw Bekeken Zilver Goud Platina".split()
        self.stakes = "Goud Zilver Platina".split()
        self.heap_words = pandas.DataFrame(index=self.heaps)
        self.master_wordlist = None
        self.scoring = None
        self.player = None
        self.heap_data = None
        self.open_word_list(master_path)
        self.open_scoring(scoring_path)
        self.open_heap_data(heap_data_path)
        self.current_word_pack = None
        self.previous_word_pack = None
        
    def setup_player(self, user_name):
        self.player = None
        player_path=""
        if user_name != "" and user_name.lower() != "gast":
            player_path = ".//{}.csv".format(user_name)
        self.open_personal_score(player_path)
        if self.player is None:
            sample_index = numpy.random.choice(self.master_wordlist.index, self.n_words, replace=False)
            self.player = self.master_wordlist.loc[sample_index]
            self.player.columns.tolist().extend(['Stapel', 'Punten', 'Geschiedenis'])
            self.player.loc[:, 'Stapel'] = self.heaps[0]
            self.player.loc[:, 'Punten'] = 0
            self.player.loc[:, 'Geschiedenis'] = ""  
        else:  
            player_index = self.player.index
            print(player_index)
            distr = self.get_heap_distribution()
            print(distr.loc['Platina','n'])
            #sample_index = self.draw_sample(distr.loc['Platina','n'])
            
    def set_result(self, article, stake):
        heap = self.current_word_pack.Stapel.to_string(index=False)
        correct = article.lower() == self.current_word_pack.Lidwoord.to_string(index=False).lower()
        score = self.scoring.loc[(heap, stake),][['Fout','Goed']]
        destination = ("Bekeken", stake)
        s = ('F', 'G')[correct]
        self.player.loc[self.current_word_pack.index[0],'Punten'] += int(score[correct])
        self.player.loc[self.current_word_pack.index[0],'Stapel'] = destination[correct]
        self.player.loc[self.current_word_pack.index[0],'Geschiedenis'] += s
                
    def get_total(self):
        return self.player.Punten.sum()
    
    def get_heap_distribution(self):
        dist = pandas.DataFrame(index=self.heaps, columns=["n",])
        for h in self.heaps:
            hps = self.player.loc[:, 'Stapel']
            dist.loc[h,"n"] = hps.loc[hps==h].count()
        return dist

    def draw_word(self):
        probs = []
        word = ""
        if not self.current_word_pack is None:
            word = self.current_word_pack.index[0]
        for p_word, row in self.player.iterrows():
            if word != p_word: # So that a word is not drawn multiple times in a row
                for heap, row_heap in self.heap_data.iterrows():
                    if row.Stapel == heap:
                        probs.extend(int(row_heap.Trekkans) * [p_word])
        sample = numpy.random.choice(probs, 1, replace=True)
        self.current_word_pack = self.player.loc[sample, :]

    def open_word_list(self, file_path):
        try:
            self.master_wordlist = pandas.read_csv(file_path, index_col=0).loc[:,['Lidwoord']]
        except Exception as e:
            print(e)
            print("No master wordlist")
            
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
            print("No heap data")

    def open_personal_score(self, file_path):
        try:
            self.player = pandas.read_csv(file_path) 
        except Exception as e:
            print(e)
            print("No player data")
            
    def save_player(self, user_name):
        fname = ".//{}.csv".format(user_name)
        self.player.to_csv(fname)
      
