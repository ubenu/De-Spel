'''
Created on 31 May 2018

@author: SchilsM
'''

import sqlite3
import csv
import random

import numpy
import pandas

class DeSpelDBController(object):
    """
    For storing in and retrieving from memory all available words in the game.
    """
    def create_db(self):
        """
        Creates the database for De Spel
        """
        db = sqlite3.connect('despel.db') # (':memory:')        # to create db in memory only
        cursor = db.cursor()
        cursor.execute('''  PRAGMA foreign_keys = ON; ''')
        # Create the all_words table
        cursor.execute(''' 
            CREATE TABLE IF NOT EXISTS all_words 
            (
                word_id INTEGER PRIMARY KEY, 
                word TEXT,
                article TEXT 
            ); 
        ''')
        # Create the heap_characteristics table
        cursor.execute(''' 
            CREATE TABLE IF NOT EXISTS heap_characteristics 
            (
                heap_name TEXT UNIQUE PRIMARY KEY, 
                suggested_stake TEXT REFERENCES heap_name, 
                drawing_weight REAL
            ); 
        ''')
        # Create the all_players table
        cursor.execute(''' 
            CREATE TABLE IF NOT EXISTS all_players 
            (
                player_id INTEGER PRIMARY KEY, 
                player_name TEXT,
                player_password TEXT,
                player_info BLOB
            );
        ''')
        # Create the scoring_patterns table
        cursor.execute(''' 
            CREATE TABLE IF NOT EXISTS scoring_pattern 
            (
                heap_name TEXT REFERENCES heap_characteristics(heap_name), 
                stake TEXT REFERENCES heap_characteristics(heap_name), 
                score_correct REAL,
                score_incorrect REAL
            );
        ''')
        # Create the all_sessions table
        cursor.execute(''' 
            CREATE TABLE IF NOT EXISTS all_sessions 
            (
                session_id INTEGER PRIMARY KEY, 
                player_id INTEGER REFERENCES all_players(player_id),
                session_date TEXT
            ); 
        ''')
        # Create the session_entries table
        cursor.execute(''' 
            CREATE TABLE IF NOT EXISTS session_entries 
            (
                session_id INTEGER REFERENCES all_sessions(session_id), 
                word_id INTEGER REFERENCES players(player_id),
                current_heap TEXT REFERENCES heap_characteristics(heap_name),
                score REAL,
                history TEXT
            ); 
        ''')
        db.close()
        
    def set_words(self, all_words_path=""):
        db = sqlite3.connect('despel.db')
        cursor = db.cursor()
        if all_words_path == "":
            all_words_path=".//master_wordlist.csv"
        with open(all_words_path) as all_words_csv:
            data = csv.reader(all_words_csv)
            next(data) # to skip first row in the csv file, which has column names
            for tup in data: # tuple consists of [word, article, meaning, translation]
                cursor.execute('''
                    INSERT INTO all_words(word, article) 
                    VALUES(?, ?);
                ''', tup[0:2] )
            db.commit()
        db.close()
                
    def set_heap_characteristics(self, heap_characteristics_path=""):
        db = sqlite3.connect('despel.db')
        cursor = db.cursor()
        if heap_characteristics_path == "":
            heap_characteristics_path=".//heap_data.csv"
        with open(heap_characteristics_path) as heaps_csv:
            data = csv.reader(heaps_csv)
            next(data)
            for tup in data:
                cursor.execute(""" 
                    INSERT INTO heap_characteristics(heap_name, suggested_stake, drawing_weight)
                    VALUES(?, ?, ?);
                """, tup[0:3] ) 
        db.close()
    
    def set_scoring(self, scoring_path=""): 
        db = sqlite3.connect('despel.db')
        cursor = db.cursor()
        if scoring_path == "":
            scoring_path=".//scoring.csv"
        with open(scoring_path) as scoring_csv:
            data = csv.reader(scoring_csv)
            next(data)
            for tup in data:
                cursor.execute(""" 
                    INSERT INTO scoring_pattern(heap_name, stake, score_correct, score_incorrect)
                    VALUES(?, ?, ?, ?);
                """, tup[0:4])
            
        db.close()
    
    def add_player(self, name, password, info={}):
        pass
    
    def add_new_session(self, player_id, word_ids):
        pass
        
        



#                 n0 = 1
#                 n1 = int(cursor.lastrowid)
#                 x = random.randint(n0, n1)
#                 print(n0, n1, x)
#                 cursor.execute(
#                     '''SELECT word, article FROM all_words WHERE id=?''', (x, ) 
#                     )
#                 w = cursor.fetchone()
#                 print(w[0], w[1])
                       
            
    

class Words(object):
    '''
    Used to draw random words from the all_words wordlist
    '''

    def __init__(self):
        '''
        Constructor
        '''
        super(Words, self).__init__()
        all_words_path=".//master_wordlist.csv"
        self.dsdb = DeSpelDBController()
        self.dsdb.create_db()
        self.dsdb.set_words()
        self.dsdb.set_scoring()
        self.dsdb.set_heap_characteristics()
        scoring_path=".//scoring.csv"
        heap_data_path=".//heap_data.csv"
        n_words=5
        self.n_words = n_words 
        self.heaps = "Nieuw Bekeken Zilver Goud Platina".split()
        self.stakes = "Goud Zilver Platina".split()
        self.heap_words = pandas.DataFrame(index=self.heaps)
        self.all_words_wordlist = None
        self.scoring = None
        self.player = None
        self.heap_data = None
        self.open_word_list(all_words_path)
        self.open_scoring(scoring_path)
        self.open_heap_data(heap_data_path)
        self.current_word_pack = None
        self.previous_word_pack = None
        
        
    def setup_player(self, user_name):
        self.player = None
        player_path=""
        if user_name != "" and user_name.lower() != "gast":
            player_path = ".//{}.csv".format(user_name)
        self.open_player(player_path)
        if self.player is None:
            sample_index = random.sample(self.all_words_wordlist.index.tolist(), self.n_words) # numpy.random.choice(self.all_words_wordlist.index, self.n_words, replace=False)
            self.player = self.all_words_wordlist.loc[sample_index]
            self.player.loc[:, 'Stapel'] = self.heaps[0]
            self.player.loc[:, 'Aanvullen'] = 0
            self.player.loc[:, 'Punten'] = 0
            self.player.loc[:, 'Geschiedenis'] = ""  
        else:  
            n_pt = self.get_new_pt()
            if n_pt > 0:
                new_index = self.all_words_wordlist.index.drop(self.player.index)
                sample_index = numpy.random.choice(new_index, n_pt, replace=False)
                new_words = self.all_words_wordlist.loc[sample_index]
                new_words.loc[:, 'Stapel'] = self.heaps[0]
                new_words.loc[:, 'Punten'] = 0
                new_words.loc[:, 'Geschiedenis'] = "" 
                self.player = self.player.append(new_words)
                self.player.loc[:, 'Aanvullen'] = 0
            
    def set_result(self, article, stake):
        heap = self.current_word_pack.Stapel[0] #.to_string(index=False)
        correct = article.lower() == self.current_word_pack.Lidwoord[0].lower()
        score = self.scoring.loc[(heap, stake),][['Fout','Goed']]
        destination = ("Bekeken", stake)
        new_pt = (0, int(heap != "Platina" and stake == "Platina"))
        s = ('F', 'G')[correct]
        self.player.loc[self.current_word_pack.index[0],'Punten'] += int(score[correct])
        self.player.loc[self.current_word_pack.index[0], 'Aanvullen'] = new_pt[correct]
        self.player.loc[self.current_word_pack.index[0],'Stapel'] = destination[correct]
        self.player.loc[self.current_word_pack.index[0],'Geschiedenis'] += s
                
    def get_total(self):
        return self.player.Punten.sum()
    
    def get_new_pt(self):
        return self.player.Aanvullen.sum()
    
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
                        probs.extend(int(row_heap.Kans) * [p_word])
        sample = numpy.random.choice(probs, 1, replace=True)
        self.current_word_pack = self.player.loc[sample, :]

    def open_word_list(self, file_path):
        try:
            self.all_words_wordlist = pandas.read_csv(file_path, index_col=0).loc[:,['Lidwoord']]
        except Exception as e:
            print(e)
            print("No all_words wordlist")
            
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

    def open_player(self, file_path):
        try:
            self.player = pandas.read_csv(file_path, index_col=0) 
        except Exception:
            pass
#             print(e)
#             print("No player data")
            
    def save_player(self, user_name):
        fname = ".//{}.csv".format(user_name)
        self.player.to_csv(fname)
        
        
      
