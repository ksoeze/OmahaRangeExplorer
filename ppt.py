#!/usr/bin/env python3
# ppt.py --- 
# 
# Filename: ppt.py
# Description: 
# Author: Johann 
# Maintainer: 
# Created: Die Mar 15 17:44:58 2016 (+0100)
# Version: 
# Last-Updated: 
#           By: 
#     Update #: 0
# URL: 
# Keywords: 
# Compatibility: 
# 
# 

# Commentary: 
# 
# 
# 
# 

# Change Log:
# 
# 
# 

# Code:

import xmlrpc.client
import subprocess
import time
from utils import *
import re
from hand import parse_hand
from board import return_next_cards

import logging

class OddsOracleServer():
    def __init__(self,ppt_location=PPT_LOCATION,ppt_port=PPT_SERVER_PORT, trial=PPT_TRIAL, max_time=PPT_MAX_SEC, thread_cnt=PPT_THREAD_CNT,game=PPT_GAME, syntax=PPT_SYNTAX):
        self.ppt_client = xmlrpc.client.ServerProxy(ppt_port)
        self.ppt_location=ppt_location
        self.trial=trial
        self.max_time=max_time
        self.thread_cnt=thread_cnt
        self.game=game
        self.dead=""
        self.syntax=syntax
        self.board=""

    def start_ppt(self): # test if ppt is running and otherwise try to start it and return client objekt
        logging.info("Check / Start PPT Server")
        logging.info("Try to Run TEST QUERY")
        try:
            logging.info(self.ppt_client.PPTServer.executePQL(TEST_QUERY, self.trial, self.max_time, self.thread_cnt))
        except:
            logging.error("No connection to PPT server...try to open it & wait 2 sec")
            self.ppt_server = subprocess.Popen(['java', '-cp', 'p2.jar', 'propokertools.cli.XMLRPCServer'], cwd=self.ppt_location, stdout=subprocess.PIPE)
            time.sleep(2)
            logging.info("Try executing first sample again")
            logging.info(self.run_query(TEST_QUERY))
            
    def log_ppt_answer(self,answer):
        if "ERROR" in answer:
            logging.error(answer)
        elif "EQUITY" in answer or "INRANGE" in answer or "NUM_BETTER_HANDS" in answer or "GET5BETPERCENT" in answer or "EV4BET" in answer or "EVCALL4BET" in answer or "RANK" in answer:
            logging.debug("PPT answer is: \n {}".format(answer))
        else:
            logging.warning("Unexpected PPT Answer...CHECK Result:\n".format(answer))
        return

    def run_query(self, query):
        trial = self.trial if "5" not in self.game else self.trial//4 # cut trials with 5card games
        try:
            result = self.ppt_client.PPTServer.executePQL(query, trial, self.max_time, self.thread_cnt)
        except:
            logging.error("No Connection to PPT Server")
            return ""
        self.log_ppt_answer(result)
        return result

    def parse_ppt_answer(self, answer,keyword="EQUITY",num_digets=PPT_NUM_DIGETS):
        number=0.0
        if not answer:
            logging.error("Could not get resulting number from PPT answer")
            return number           
        for line in answer.splitlines():
            if keyword in line:
                numbers=re.search('\d+\.\d+',line)
                numbers=numbers.group(0)
                if numbers=="0.0": return 0.0
                if numbers=="1.0": return 1.0
                if len(numbers)>=PPT_NUM_DIGETS and '.' in numbers:
                    number=float(numbers)
                else:
                    logging.error("Could not get resulting number from PPT answer")
                    return number
        return number

    def equity_query(self, hero_range, villain_range):
        hero_range=self.format_range(hero_range)
        villain_range=self.format_range(villain_range)

        query=("select avg(riverEquity(hero)) as EQUITY \n"
               "from game='{0}', \n"
               "syntax='{1}', \n"
               "hero='{2}', \n" 
               "villain='{3}', \n" 
               "board='{4}', \n"
               "dead='{5}'\n").format(self.game, self.syntax, hero_range, villain_range, self.board, self.dead)
        logging.debug("Running an Equity Query with:")
        logging.debug("Game: {0}, Syntax: {1}, Board: {2}, Dead: {3}".format(self.game,self.syntax,self.board,self.dead))
        logging.debug("Hero Range: {}".format(hero_range))
        logging.debug("Villain Range: {}".format(villain_range))

        return (self.parse_ppt_answer(self.run_query(query),"EQUITY"))*100

    def equity_query_3way(self, hero_range, villain1_range, villain2_range):
        hero_range=self.format_range(hero_range)
        villain1_range=self.format_range(villain1_range)
        villain2_range=self.format_range(villain2_range)

        query=("select avg(riverEquity(hero)) as EQUITY \n"
               "from game='{0}', \n"
               "syntax='{1}', \n"
               "hero='{2}', \n" 
               "villain1='{3}', \n"
               "villain2='{6}', \n" 
               "board='{4}', \n"
               "dead='{5}'\n").format(self.game, self.syntax, hero_range, villain1_range, self.board, self.dead, villain2_range)
        logging.debug("Running an Equity Query 3way with:")
        logging.debug("Game: {0}, Syntax: {1}, Board: {2}, Dead: {3}".format(self.game,self.syntax,self.board,self.dead))
        logging.debug("Hero Range: {}".format(hero_range))
        logging.debug("Villain1 Range: {}".format(villain1_range))
        logging.debug("Villain2 Range: {}".format(villain2_range))

        return (self.parse_ppt_answer(self.run_query(query),"EQUITY"))*100
        
    
    def in_range_query(self, hero_range, villain_range, sub_range):
        hero_range=self.format_range(hero_range)
        villain_range=self.format_range(villain_range)
        sub_range=self.format_range(sub_range)
        
        query=("select count(inRange(hero,'{1}')) as INRANGE \n"
               "from game='{2}', \n"
               "syntax='{3}', \n"
               "hero='{0}', \n" 
               "villain='{4}', \n" 
               "board='{5}', \n"
               "dead='{6}'\n").format(hero_range, sub_range, self.game, self.syntax, villain_range, self.board, self.dead)
        logging.debug("Running an InRange/Frequency Query with:")
        logging.debug("Game: {0}, Syntax: {1}, Board: {2}, Dead: {3}".format(self.game,self.syntax,self.board,self.dead))
        logging.debug("Hero Range: {}".format(hero_range))
        logging.debug("Hero SubRange: {}".format(sub_range))       
        logging.debug("Villain Range: {}".format(villain_range))

        trial=self.trial
        self.trial=PPT_IN_RANGE_TRIAL
        answer = self.parse_ppt_answer(self.run_query(query),"INRANGE")
        self.trial=trial
        return answer
    
    def in_range_query_3way(self, hero_range, villain1_range, villain2_range, sub_range):
        hero_range=self.format_range(hero_range)
        villain1_range=self.format_range(villain1_range)
        villain2_range=self.format_range(villain2_range)        
        sub_range=self.format_range(sub_range)
        
        query=("select count(inRange(hero,'{1}')) as INRANGE \n"
               "from game='{2}', \n"
               "syntax='{3}', \n"
               "hero='{0}', \n" 
               "villain1='{4}', \n"
               "villain2='{7}', \n"                
               "board='{5}', \n"
               "dead='{6}'\n").format(hero_range, sub_range, self.game, self.syntax, villain1_range, self.board, self.dead, villain2_range)
        logging.debug("Running an InRange/Frequency Query 3 way with:")
        logging.debug("Game: {0}, Syntax: {1}, Board: {2}, Dead: {3}".format(self.game,self.syntax,self.board,self.dead))
        logging.debug("Hero Range: {}".format(hero_range))
        logging.debug("Hero SubRange: {}".format(sub_range))       
        logging.debug("Villain1 Range: {}".format(villain1_range))
        logging.debug("Villain2 Range: {}".format(villain2_range))        

        trial=self.trial
        self.trial=PPT_IN_RANGE_TRIAL
        answer = self.parse_ppt_answer(self.run_query(query),"INRANGE")
        self.trial=trial
        return answer
    
    def str2float(self,string):
        try:
            return float(string)
        except ValueError:
            logging.error("Could not convert entry to a valid number (Entry Text: {})".format(string))
            return 0.0

    def rank_query(self, equity, hero_range, villain_range, street):
        hero_range=self.format_range(hero_range)
        villain_range=self.format_range(villain_range)

        query=("select count(minEquity(hero,{0},{1:.4f})) as NUM_BETTER_HANDS \n"
               "from game='{2}', \n"
               "syntax='{3}', \n"
               "hero='{4}', \n" 
               "villain='{5}', \n" 
               "board='{6}', \n"
               "dead='{7}'\n").format(street, equity/100, self.game, self.syntax, hero_range, villain_range, self.board, self.dead)

        logging.debug(query + "\n\n")
        
        logging.debug("Running an Rank Query with:")
        logging.debug("Game: {0}, Syntax: {1}, Board: {2}, Dead: {3}".format(self.game,self.syntax,self.board,self.dead))
        logging.debug("Hero Range: {}".format(hero_range))
        logging.debug("Villain Range: {}".format(villain_range))
        logging.debug("Calc how often Hero has more than {0:.1f} equity".format(equity))

        trial=self.trial
        self.trial=PPT_RANK_QUERY_TRIAL
        answer=self.parse_ppt_answer(self.run_query(query),"NUM_BETTER_HANDS")       
        self.trial=trial
        return answer
    
    def bet_vs_1_calculations(self, result_label_var, hero_range, villain_range, hero_hand, pot_size=0, stack_size=0, bet_size=0, raise_size=0, rraise_size=0, street="flop"): #hero / villain_range are gui_element_objects
        hero_start_range=hero_range.get_start_range()
        hero_bet_range=hero_range.get_certain_range([0,2]) # hero bets range 1 and 3
        hero_bluff_range=hero_range.get_certain_range([2]) # hero bluffs range 3
        hero_value_range=hero_range.get_certain_range([0]) # hero vbets/goes broke? range 1
        hero_xb_range=hero_range.get_certain_range([1]) # range 2 is middle range

        villain_start_range=villain_range.get_start_range()
        villain_call_range=villain_range.get_certain_range([1])
        villain_raise_range=villain_range.get_certain_range([0,2])
        villain_fold_range=villain_range.get_certain_range([3])
        villain_value_range=villain_range.get_certain_range([0])

        result_str=""
        if not all([pot_size,stack_size,bet_size,raise_size,rraise_size]):
            result_str+="One or more numbers are empty/zero/invalid ->\n"
            result_str+="Please enter valid amouts or leave default values.\n"
            result_label_var.set(result_str)
            return

        if not all([villain_start_range,villain_call_range,villain_raise_range,villain_fold_range,villain_value_range]):
            result_str+="One or more Villain ranges are empty ->\n"
            result_str+="Please enter valid subranges...for fold range (subrange 4) put at least *\n"
            result_label_var.set(result_str)
            return

        if not all([hero_start_range,hero_hand]):
            result_str+="Missing Hero range/hand ->\n"
            result_str+="Please enter at least startrange and example hand for Hero \n"
            result_label_var.set(result_str)
            return           

        ## run equity/frequency queries

        logging.info(DOTS)
        logging.info("START EV CALCS")

        hand_eq_vs_range=self.equity_query(hero_hand,villain_start_range)

        hand_eq_vs_raise_range=self.equity_query(hero_hand,villain_raise_range)
        hand_eq_vs_call_range=self.equity_query(hero_hand,villain_call_range)
        hand_eq_vs_fold_range=self.equity_query(hero_hand,villain_fold_range)
        hand_eq_vs_value_raise_range=self.equity_query(hero_hand,villain_value_range)
        hand_ranking=self.rank_query(hand_eq_vs_range,hero_start_range,villain_start_range,street)
        
        villain_raise_freq=self.in_range_query(villain_start_range,hero_hand,villain_raise_range)
        villain_value_raise_freq=self.in_range_query(villain_start_range,hero_hand,villain_value_range)
        villain_call_freq=self.in_range_query(villain_start_range,hero_hand,villain_call_range)
        villain_fold_freq=self.in_range_query(villain_start_range,hero_hand,villain_fold_range)

        
        
        ## convert string variables to float values

        pot_size=self.str2float(pot_size)
        stack_size=self.str2float(stack_size)
        bet_size=self.str2float(bet_size)
        raise_size=self.str2float(raise_size)
        rraise_size=self.str2float(rraise_size)

      
        result_str+="General Infos:\n"
        result_str+="Stacksizes: {0}; Pot: {1} -> SPR = {2:.1f}\n".format(stack_size,pot_size,stack_size/pot_size)
        result_str+="Betsize: {0} ({1:.1f}% pot); Alpha: {2:.1f}%; 1-Alpha: {3:.1f}%\n".format(bet_size,bet_size/pot_size*100,(bet_size/(bet_size+pot_size))*100,(1-bet_size/(bet_size+pot_size))*100)
        result_str+="Raisesize: {0}; Alpha: {1:.1f}%; 1-Alpha: {2:.1f}%\n".format(raise_size,100*raise_size/(raise_size+pot_size+bet_size),100*(1-raise_size/(raise_size+pot_size+bet_size)))
        result_str+="Reraisesize: {0}; Alpha: {1:.1f}%; 1-Alpha: {2:.1f}%\n".format(rraise_size,100*(rraise_size-bet_size)/(rraise_size+pot_size+raise_size),100*(1-(rraise_size-bet_size)/(rraise_size+pot_size+raise_size)))
        result_str+="Stackoff Equity: {0:.1f}% ({1:.1f}% after bet; {2:.1f}% after raise; {3:.1f}% after reraise).\n".format(stack_size/(pot_size+2*stack_size)*100,(stack_size-bet_size)/(pot_size+2*stack_size)*100,(stack_size-raise_size)/(pot_size+2*stack_size)*100,(stack_size-rraise_size)/(pot_size+2*stack_size)*100)


        result_str+="\nEquities and Frequencies:\n"
        result_str+="Hero startrange equity: {}% vs villain startrange\n".format(hero_range.range_eq.get())
        result_str+="{0} equity: {1:.1f}% ({2:.1f}% of hero startrange has more equity)\n".format(hero_hand, hand_eq_vs_range, hand_ranking)
        try:
            villain_r_f_freq=1-villain_value_raise_freq/villain_raise_freq
            result_str+="Villain raises: {0:.1f}%; calls: {1:.1f}%; folds: {2:.1f}%; folds vs reraise: {3:.1f}%\n".format(
                villain_raise_freq,villain_call_freq, villain_fold_freq, villain_r_f_freq*100)
        except ZeroDivisionError:
            logging.error("Some Frequencies are off...Division by zero error")
            return
        result_str+="{0} equity vs raise {1:.1f}% ({4:.1f}% vs value); {2:.1f}% vs call; {3:.1f}% vs fold-range\n".format(
            hero_hand, hand_eq_vs_raise_range, hand_eq_vs_call_range, hand_eq_vs_fold_range, hand_eq_vs_value_raise_range)

        result_str+="\nEV for low SPR situations (asume equity realisation 100%):\n"
        result_str+="Ev BF = {:.2f}\n".format(villain_fold_freq/100*pot_size + villain_raise_freq/100*(-bet_size) +
                                          villain_call_freq/100*(hand_eq_vs_call_range/100*(pot_size+2*bet_size) - bet_size))
        result_str+="Ev BC = {:.2f}\n".format(villain_fold_freq/100*pot_size + villain_raise_freq/100*(hand_eq_vs_raise_range/100*(2*raise_size+pot_size) - raise_size) +
                                          villain_call_freq/100*(hand_eq_vs_call_range/100*(pot_size+2*bet_size) - bet_size))
        result_str+="Ev XB = {:.2f}\n".format(hand_eq_vs_range*pot_size/100)

        result_str+="\nEV for high SPR situations (EV as expression of realisation factors R_vs_range, R_vs_call, R_vs_raise):\n"

        result_str+="Ev BF = {0:.2f}".format(villain_fold_freq/100*pot_size-villain_raise_freq/100*bet_size-villain_call_freq/100*bet_size)
        result_str+=" + {0:.2f}*R_vs_call\n".format(villain_call_freq/100*hand_eq_vs_call_range/100*(pot_size+2*bet_size))       

        result_str+="Ev BC = {0:.2f}".format(villain_fold_freq/100*pot_size-villain_raise_freq/100*raise_size-villain_call_freq/100*bet_size)
        result_str+=" + {0:.2f}*R_vs_raise".format(villain_raise_freq/100*hand_eq_vs_raise_range/100*(2*raise_size+pot_size))
        result_str+=" + {0:.2f}*R_vs_call\n".format(villain_call_freq/100*hand_eq_vs_call_range/100*(pot_size+2*bet_size))
        result_str+="Ev XB = {:.2f} * R_vs_range \n".format(hand_eq_vs_range*pot_size/100)
        result_str+="Ev BF = EV XB if R_vs_range = {0:.2f} + {1:.2f}*R_vs_call\n".format((villain_fold_freq/100*pot_size-villain_raise_freq/100*bet_size-villain_call_freq/100*bet_size)/(hand_eq_vs_range*pot_size/100)
                                                                                       ,(villain_call_freq/100*hand_eq_vs_call_range/100*(pot_size+2*bet_size))/(hand_eq_vs_range*pot_size/100))


        result_str+="\nDefend vs Raise:\n"
        result_str+="Reraise Bluff no Equity: Villain folds {0:.1f}% ({1:.1f}% needed)\n".format(villain_r_f_freq*100,100*(rraise_size-bet_size)/(rraise_size+pot_size+raise_size))
        result_str+="Semibluff reraise needs {:.1f}% equity\n".format(100*(-villain_r_f_freq*(pot_size+bet_size+raise_size) + (1-villain_r_f_freq)*(rraise_size-bet_size))/((1-villain_r_f_freq)*(pot_size+2*rraise_size)))

        result_label_var.set(result_str)
        logging.info("DOONNEEE!!")
        logging.info(DOTS)
        return
        

    def bet_vs_2_calculations(self, result_label_var, hero_range, villain1_range, villain2_range, hero_hand, pot_size=0, stack_size1=0, stack_size2=0, bet_size=0, raise_size=0, rraise_size=0, street="flop"): #hero / villain_range are gui_element_objects

        hero_start_range=hero_range.get_start_range()
        hero_bet_range=hero_range.get_certain_range([0,2]) # hero bets range 1 and 3
        hero_bluff_range=hero_range.get_certain_range([2]) # hero bluffs range 3
        hero_value_range=hero_range.get_certain_range([0]) # hero vbets/goes broke? range 1
        hero_xb_range=hero_range.get_certain_range([1]) # range 2 is middle range

        villain1_start_range=villain1_range.get_start_range()
        villain1_call_range=villain1_range.get_certain_range([1])
        villain1_raise_range=villain1_range.get_certain_range([0,2])
        villain1_fold_range=villain1_range.get_certain_range([3])
        villain1_value_range=villain1_range.get_certain_range([0])

        villain2_start_range=villain2_range.get_start_range()
        villain2_call_range=villain2_range.get_certain_range([1])
        villain2_raise_range=villain2_range.get_certain_range([0,2])
        villain2_fold_range=villain2_range.get_certain_range([3])
        villain2_value_range=villain2_range.get_certain_range([0])

        villain1_raise_range_low_spr=villain1_range.get_certain_range([0,1])
        villain2_raise_range_low_spr=villain2_range.get_certain_range([0,1])
        villain1_fold_range_low_spr=villain1_range.get_certain_range([2,3])
        villain2_fold_range_low_spr=villain2_range.get_certain_range([2,3])       
        
        result_str=""
        if not all([pot_size,stack_size1,stack_size2,bet_size,raise_size,rraise_size]):
            result_str+="One or more numbers are empty/zero/invalid ->\n"
            result_str+="Please enter valid amouts or leave default values.\n"
            result_label_var.set(result_str)
            return

        if not all([villain1_start_range,villain1_call_range,villain1_raise_range,villain1_fold_range,villain1_value_range]):
            result_str+="One or more Villain1 ranges are empty ->\n"
            result_str+="Please enter valid subranges...for fold range (subrange 4) put at least *\n"
            result_label_var.set(result_str)
            return
 
        if not all([villain2_start_range,villain2_call_range,villain2_raise_range,villain2_fold_range,villain2_value_range]):
            result_str+="One or more Villain2 ranges are empty ->\n"
            result_str+="Please enter valid subranges...for fold range (subrange 4) put at least *\n"
            result_label_var.set(result_str)
            return       

        if not all([hero_start_range,hero_hand]):
            result_str+="Missing Hero range/hand ->\n"
            result_str+="Please enter at least startrange and example hand for Hero \n"
            result_label_var.set(result_str)
            return           

        ## run equity/frequency queries
        logging.info(DOTS)
        logging.info("START EV CALCS")

        hand_eq_vs_ranges=self.equity_query_3way(hero_hand,villain1_start_range,villain2_start_range)

        # results for low spr situations:
        hand_eq_vs_ship1_range=self.equity_query(hero_hand,villain1_raise_range_low_spr)
        hand_eq_vs_ship2_range=self.equity_query(hero_hand,villain2_raise_range_low_spr)
        hand_eq_vs_ship12_range=self.equity_query_3way(hero_hand,villain1_raise_range_low_spr,villain2_value_range)
        
        villain1_ship_freq=self.in_range_query_3way(villain1_start_range,hero_hand,villain2_fold_range_low_spr,villain1_raise_range_low_spr)
        villain2_ship_freq=self.in_range_query_3way(villain2_start_range,hero_hand,villain1_fold_range_low_spr,villain2_raise_range_low_spr)
        villain2_overship_freq=self.in_range_query_3way(villain2_start_range,hero_hand,villain1_raise_range_low_spr,villain2_value_range)

        # general frequencies (raise range 1+3, call range 2):
        
        hand_eq_vs_v1_1=self.equity_query(hero_hand,villain1_value_range)
        hand_eq_vs_v2_1=self.equity_query(hero_hand,villain2_value_range)
        hand_eq_vs_v12_1=self.equity_query_3way(hero_hand,villain1_value_range,villain2_value_range)

        
        villain1_raise_freq=self.in_range_query_3way(villain1_start_range,hero_hand,villain2_start_range,villain1_raise_range)
        villain2_raise_freq=self.in_range_query_3way(villain2_start_range,hero_hand,villain2_fold_range,villain2_raise_range)
        villain1_calls_freq=self.in_range_query_3way(villain1_start_range,hero_hand,villain2_start_range,villain1_call_range)
        villain2_calls_freq=self.in_range_query_3way(villain2_start_range,hero_hand,villain1_fold_range,villain2_call_range)
        villain1_folds_freq=self.in_range_query_3way(villain1_start_range,hero_hand,villain2_start_range,villain1_fold_range)
        villain2_folds_freq=self.in_range_query_3way(villain2_start_range,hero_hand,villain1_fold_range,villain2_fold_range)

        hand_eq_vs_v1_2=self.equity_query(hero_hand,villain1_call_range)
        hand_eq_vs_v2_2=self.equity_query(hero_hand,villain2_call_range)
        hand_eq_vs_v12_2=self.equity_query_3way(hero_hand,villain1_call_range,villain2_call_range)
        
        ## convert string variables to float values

        pot_size=self.str2float(pot_size)
        stack_size1=self.str2float(stack_size1)
        stack_size2=self.str2float(stack_size2)
        bet_size=self.str2float(bet_size)
        raise_size=self.str2float(raise_size)
        rraise_size=self.str2float(rraise_size)

        result_str+="Stacksize vs V1: {0}; vs V2: {1} Pot: {2}\n".format(stack_size1,stack_size2,pot_size)
        if stack_size1-stack_size2 > 0:
            sidepot=(stack_size1-stack_size2)*2
            sideplayer=1
        else:
            sidepot=(stack_size2-stack_size1)*2
            sideplayer=2
        result_str+="Potentional sidepot with V{0} is {1}\n".format(sideplayer,sidepot)
        result_str+="Betsize: {0} ({1:.1f}% pot); Alpha: {2:.1f}%; 1-Alpha: {3:.1f}%\n".format(bet_size,bet_size/pot_size*100,(bet_size/(bet_size+pot_size))*100,(1-bet_size/(bet_size+pot_size))*100)
        result_str+="Raisesize: {0}; Alpha: {1:.1f}%; 1-Alpha: {2:.1f}%\n".format(raise_size,100*raise_size/(raise_size+pot_size+bet_size),100*(1-raise_size/(raise_size+pot_size+bet_size)))
        result_str+="Stackoff Equity vs V1: {0:.1f}% , vs V2: {1:.1f}%, vs V12 (only main pot): {2:.1f}%.\n".format(stack_size1/(pot_size+2*stack_size1)*100,stack_size2/(pot_size+2*stack_size2)*100,
                                                                                                                                         min(stack_size1,stack_size2)/(pot_size+3*min(stack_size1,stack_size2))*100)
        
        result_str+="Stackoff Equity after bet vs V1: {0:.1f}% , vs V2: {1:.1f}%, vs V12 (only main pot): {2:.1f}%.\n".format((stack_size1-bet_size)/(pot_size+2*stack_size1)*100,(stack_size2-bet_size)/(pot_size+2*stack_size2)*100,
                                                                                                                                         (min(stack_size1,stack_size2)-bet_size)/(pot_size+3*min(stack_size1,stack_size2))*100)

        result_str+="\nHero startrange equity: {}% vs V1 and V2 startrange\n".format(hero_range.range_eq.get())
        result_str+="{0} equity: {1:.1f}% \n".format(hero_hand, hand_eq_vs_ranges)
        result_str+="Hand equity vs V1 range 1: {0:.1f}%; V2 range 1: {1:.1f}%; V12 range 1: {2:.1f}%\n".format(
            hand_eq_vs_v1_1,hand_eq_vs_v2_1,hand_eq_vs_v12_1)
        result_str+="Cbet gets raised (V1 raises range 1+3, calls 2; V2 raises 1+3 when V1 folds 4)~: {:.1f}\n".format(villain1_raise_freq + (1-villain1_raise_freq/100)*villain2_raise_freq)
        result_str+="Both fold: {:.1f}; ".format((villain1_folds_freq/100)*(villain2_folds_freq/100)*100)
        result_str+="bet get called ~:{:.1f} \n".format(villain1_calls_freq+(1-villain1_calls_freq/100)*villain2_calls_freq)
        result_str+="Equity vs call V1: {0:.1f}%; vs call V2: {1:.1f}%; vs call both: {2:.1f}%\n".format(
        hand_eq_vs_v1_2,hand_eq_vs_v2_2,hand_eq_vs_v12_2)

        v1_ship_v2_fold=(villain1_ship_freq/100)*(1-villain2_overship_freq/100)
        v1_fold_v2_ship=(1-villain1_ship_freq/100)*(villain2_ship_freq/100)
        v1_fold_v2_fold=(1-villain1_ship_freq/100)*(1-villain2_ship_freq/100)
        v1_ship_v2_ship=(villain1_ship_freq/100)*(villain2_overship_freq/100)            

        result_str+="\nLow SPR spot (3bet pot...only bet/ship left):\n"
        result_str+="V1 ships range 1 + 2 and V2 folds: {0:.1f}%\n".format(v1_ship_v2_fold*100)
        result_str+="V2 folds and V2 ships range 1 + 2: {0:.1f}%\n".format(v1_fold_v2_ship*100)
        result_str+="V1 folds and V2 folds 3 + 4: {0:.1f}%\n".format(v1_fold_v2_fold*100)
        result_str+="V1 ships range 1 + 2 and V2 ships range 1: {0:.1f}%\n".format(v1_ship_v2_ship*100)

        ev_both_fold=v1_fold_v2_fold*pot_size
        ev_v1_ship_v2_fold=v1_ship_v2_fold*(hand_eq_vs_ship1_range/100*(pot_size+stack_size1*2)-stack_size1)
        ev_v1_fold_v2_ships=v1_fold_v2_ship*(hand_eq_vs_ship2_range/100*(pot_size+stack_size2*2)-stack_size2)
        if sideplayer == 1:
            ev_v1_ship_v2_ships=v1_ship_v2_ship*(hand_eq_vs_ship12_range/100*(pot_size+stack_size2*3)-stack_size2+
                                                 hand_eq_vs_ship1_range/100*(sidepot)-sidepot/2)
        else:
            ev_v1_ship_v2_ships=v1_ship_v2_ship*(hand_eq_vs_ship12_range/100*(pot_size+stack_size1*3)-stack_size1+
                                                 hand_eq_vs_ship2_range/100*(sidepot)-sidepot/2)
        
        result_str+="Equity vs V1: {0:.1f}%; vs V2: {1:.1f}%; 3way: {2:.1f}%\n".format(
            hand_eq_vs_ship1_range,hand_eq_vs_ship2_range,hand_eq_vs_ship12_range)
        result_str+="Relative EVs of bet/call...Both fold: {0:.2f}; vs V1: {1:.2f}; vs V2: {2:.2f}; vs V12: {3:.2f}; OVERALL:{4:.2f}\n".format(
            ev_both_fold,ev_v1_ship_v2_fold,ev_v1_fold_v2_ships,ev_v1_ship_v2_ships,
            ev_both_fold+ev_v1_ship_v2_fold+ev_v1_fold_v2_ships+ev_v1_ship_v2_ships)

        
        result_label_var.set(result_str)
        logging.info("DOONNEEE!!")
        logging.info(DOTS)
        return
    


    def do_4bet(self,result_str,hand,villain_3brange,villain_5brange,stack_size,open_size,bet3_size,pot_size):
        logging.info(DOTS)
        logging.info("4BET CALC")
        logging.info("4-bet {0} vs V1 range: {1}".format(hand,villain_3brange))
        stack_size=self.str2float(stack_size)
        open_size=self.str2float(open_size)
        bet3_size=self.str2float(bet3_size)
        pot_size=self.str2float(pot_size)
        
        pot_call_3bet=pot_size+bet3_size-open_size
        pot_flop=pot_call_3bet*3
        invest_pre=bet3_size-open_size+pot_call_3bet
        invest_post=stack_size-pot_call_3bet-bet3_size

        logging.info("We invest {0} pre (total 4bet size: {1}) wiht pot otf: {2} and stacks left: {3}".format(
            invest_pre,invest_pre+open_size,pot_flop,invest_post))

        query=("select count(inRange(villain, '{0}')) as GET5BETPERCENT,\n"
               "avg(riverEquity(hero)) as EQUITY,"
               "avg( \n"  
               "case \n"      
               "when inRange(villain, '{1}')\n"
               "then riverEquity(hero)*{2} - {3} \n"
             "else\n" 
	       "case\n"
               "when minEquity(villain,flop,{4:.4f})\n"
               # "when minHvPerceivedRangeEquity(villain,flop,'AA',{4:.4f})\n" 
                "then {5}*riverEquity(hero) - {6}\n"
                 "else {7}\n"
               "end\n" 
             "end\n"                    
               ") as EV4BET\n"
               "from game='{8}',\n" 
               "syntax='{9}',\n" 
               "hero='{10}',\n" 
               "villain='{11}'").format(
                   villain_5brange,villain_5brange,pot_flop+invest_post*2,
                   invest_pre+invest_post,
                   invest_post/(pot_flop+2*invest_post),
                   pot_flop+invest_post*2,
                   invest_pre+invest_post,
                   pot_flop,
                   self.game,
                   self.syntax,
                   hand, villain_3brange
               )
        logging.info("Run the following 4bet query:\n" + query)
        logging.info("\n")
        logging.info(self.run_query(query))      
        return

        
    def call_4bet(self,result_str,hand,villain_4brange,stack_size,open_size,bet3_size,pot_size):
        logging.info(DOTS)
        logging.info("CALL 4BET CALC")
        logging.info("Call 4-bet {0} vs V1 range: {1}".format(hand,villain_4brange))
        stack_size=self.str2float(stack_size)
        open_size=self.str2float(open_size)
        bet3_size=self.str2float(bet3_size)
        pot_size=self.str2float(pot_size)
        
        pot_call_3bet=pot_size+bet3_size-open_size
        pot_flop=pot_call_3bet*3
        invest_pre=pot_call_3bet
        invest_post=stack_size-pot_call_3bet-bet3_size

        logging.info("We invest {0:.2f} pre (total 4bet size: {1:.2f}) wiht pot otf: {2:.2f} and stacks left: {3:.2f}".format(
            invest_pre,invest_pre+bet3_size,pot_flop,invest_post))

        query=("select avg(riverEquity(hero)) as EQUITY,\n"
               "avg( \n"  
               "case\n"
               "when minEquity(hero,flop,{0:.4f})\n"
                "then {1}*riverEquity(hero) - {2}\n"
                 "else {3}\n"
               "end) as EVCALL4BET\n"
               "from game='{4}',\n" 
               "syntax='{5}',\n" 
               "hero='{6}',\n" 
               "villain='{7}'").format(
                   invest_post/(invest_post*2+pot_flop),
                   pot_flop+2*invest_post,
                   invest_pre+invest_post,
                   -invest_pre,
                   self.game,
                   self.syntax,
                   hand,
                   villain_4brange
               )
        logging.info("Run the following call 4bet query:\n" + query)
        logging.info("\n")
        logging.info(self.run_query(query))    
        return

    def next_card_eval(self, hero_range, villain_range):
        next_cards=return_next_cards(self.board,False)
        board_original=self.board
        result=[]
        overall_equity=self.equity_query(hero_range,villain_range)
        logging.info(DOTS)
        logging.info("Hero Range: {}".format(hero_range))
        logging.info("Villain Range: {}".format(villain_range))
        logging.info("For board {0}, Hero equity is {1:.2f}% \n".format(self.board,overall_equity))
        result.append((self.board,overall_equity,0.0))
        self.trial=PPT_NEXT_CARD_EQ_TRIAL
        for card in next_cards:
            self.board+=card
            equity=self.equity_query(hero_range,villain_range)
            logging.info("For board {0}, Hero equity is {1:.2f}% (Difference: {2:.2f}%)".format(self.board,equity,equity-overall_equity))
            result.append((self.board,equity,equity-overall_equity))
            self.board=board_original
        logging.info("\n")
        logging.info("Sorted results for next Card:")
        result.sort(key=lambda x:x[1],reverse=True)
        for x in result:
            logging.info("For board {0}, Hero equity is {1:.2f}% (Difference: {2:.2f}%)".format(x[0],x[1],x[2]))
        logging.info("DONE")
        logging.info(DOTS)
        self.trial=PPT_TRIAL
        return
        
    def format_range(self,hand_range):
        return parse_hand(hand_range,self.board)

    def table_item(self,string,size):
        if len(string)>size:
            return string
        spaces=size-len(string)
        spaces_before=spaces//2
        return(spaces_before*" "+string+(spaces-spaces_before)*" ")

    def rank_hand_query(self,hand,num_plr):
        query=("select avg(handRankingFor(hero,'{0}')) as RANK \n"
               "from game='{1}',\n"
               "syntax='{2}',\n"
               "hero='{3}',\n"
               "dead='{4}'\n".format(num_plr,self.game,self.syntax,hand,self.dead))
        trial=self.trial
        self.trial=PPT_RANK_QUERY_TRIAL
        answer=self.run_query(query)
        answer=self.parse_ppt_answer(answer,"RANK")
        self.trial=trial
        return answer
        
    def rank_hand(self,hand):
        horizontal_line=80*"-"
        width=8

        logging.info(horizontal_line)
        logging.info("Rankings:")
        logging.info("|"+self.table_item("VR",width)+"|"+self.table_item("3H",width)+"|"+self.table_item("6H",width)+"|"+self.table_item("10H",width)+"|")
        rank_vr=self.table_item(str(round(self.rank_hand_query(hand,"vr"),1)),width)
        rank_3h=self.table_item(str(round(self.rank_hand_query(hand,"3h"),1)),width) if "5" not in self.game else  self.table_item("--",width)
        rank_6h=self.table_item(str(round(self.rank_hand_query(hand,"6h"),1)),width)
        rank_10h=self.table_item(str(round(self.rank_hand_query(hand,"10h"),1)),width) if "5" not in self.game else self.table_item(str(round(self.rank_hand_query(hand,"9h"),1)),width)
        logging.info("|"+rank_vr+"|"+rank_3h+"|"+rank_6h+"|"+rank_10h+"|\n")

        logging.info("vs PPT 6h Ranking HU:")
        logging.info("|"+self.table_item("2%",width)+"|"+self.table_item("4%",width)+"|"+self.table_item("6%",width)+"|"+self.table_item("10%",width)+"|"
                     +self.table_item("15%",width)+"|"+self.table_item("20%",width)+"|"+self.table_item("25%",width)+"|"+self.table_item("30%",width)+"|"
                     +self.table_item("40%",width)+"|"+self.table_item("50%",width)+"|"+self.table_item("75%",width)+"|"+self.table_item("100%",width)+"|")

        vs_2=self.table_item(str(round(self.equity_query(hand,"2%6h"),1)),width)
        vs_4=self.table_item(str(round(self.equity_query(hand,"4%6h"),1)),width)
        vs_6=self.table_item(str(round(self.equity_query(hand,"6%6h"),1)),width)
        vs_10=self.table_item(str(round(self.equity_query(hand,"10%6h"),1)),width)
        vs_15=self.table_item(str(round(self.equity_query(hand,"15%6h"),1)),width)
        vs_20=self.table_item(str(round(self.equity_query(hand,"20%6h"),1)),width)
        vs_25=self.table_item(str(round(self.equity_query(hand,"25%6h"),1)),width)
        vs_30=self.table_item(str(round(self.equity_query(hand,"30%6h"),1)),width)
        vs_40=self.table_item(str(round(self.equity_query(hand,"40%6h"),1)),width)
        vs_50=self.table_item(str(round(self.equity_query(hand,"50%6h"),1)),width)
        vs_75=self.table_item(str(round(self.equity_query(hand,"75%6h"),1)),width)
        vs_100=self.table_item(str(round(self.equity_query(hand,"100%6h"),1)),width)

        logging.info("|"+vs_2+"|"+vs_4+"|"+vs_6+"|"+vs_10+"|"+vs_15+"|"+vs_20+"|"+vs_25+"|"+vs_30+"|"+vs_40+"|"+vs_50+"|"+vs_75+"|"+vs_100+"|\n")
        logging.info("vs PPT 6h Ranking 3WAY:")
        logging.info("|"+self.table_item("15%",width)+"|"+self.table_item("15%",width)+"|"+self.table_item("15%",width)+"|"+self.table_item("25%",width)+"|"
                     +self.table_item("25%",width)+"|"+self.table_item("25%",width)+"|"+self.table_item("35%",width)+"|"+self.table_item("35%",width)+"|"
                     +self.table_item("35%",width)+"|"+self.table_item("50%",width)+"|"+self.table_item("50%",width)+"|"+self.table_item("50%",width)+"|")
        logging.info("|"+self.table_item("4%",width)+"|"+self.table_item("30%!4%",width)+"|"+self.table_item("30%",width)+"|"+self.table_item("6%",width)+"|"
                     +self.table_item("40%",width)+"|"+self.table_item("40%!6%",width)+"|"+self.table_item("8%",width)+"|"+self.table_item("50%",width)+"|"
                     +self.table_item("50%!8%",width)+"|"+self.table_item("12%",width)+"|"+self.table_item("60%",width)+"|"+self.table_item("60%!%12",width)+"|")
                     
        vs_15_4=self.table_item(str(round(self.equity_query_3way(hand,"15%6h","4%6h"),1)),width)
        vs_15_30=self.table_item(str(round(self.equity_query_3way(hand,"15%6h","30%6h"),1)),width)
        vs_15_30n4=self.table_item(str(round(self.equity_query_3way(hand,"15%6h","30%6h!4%6h"),1)),width)
        vs_25_6=self.table_item(str(round(self.equity_query_3way(hand,"25%6h","6%6h"),1)),width)
        vs_25_40=self.table_item(str(round(self.equity_query_3way(hand,"25%6h","40%6h"),1)),width)
        vs_25_40n6=self.table_item(str(round(self.equity_query_3way(hand,"25%6h","40%6h!6%6h"),1)),width)
        vs_35_8=self.table_item(str(round(self.equity_query_3way(hand,"35%6h","8%6h"),1)),width)
        vs_35_50=self.table_item(str(round(self.equity_query_3way(hand,"35%6h","50%6h"),1)),width)
        vs_35_50n8=self.table_item(str(round(self.equity_query_3way(hand,"35%6h","50%6h!8%6h"),1)),width)
        vs_50_12=self.table_item(str(round(self.equity_query_3way(hand,"50%6h","12%6h"),1)),width)
        vs_50_60=self.table_item(str(round(self.equity_query_3way(hand,"50%6h","60%6h"),1)),width)
        vs_50_60n12=self.table_item(str(round(self.equity_query_3way(hand,"50%6h","60%6h!12%6h"),1)),width)

                     
        logging.info("|"+vs_15_4+"|"+vs_15_30+"|"+vs_15_30n4+"|"+vs_25_6+"|"+vs_25_40+"|"+vs_25_40n6+"|"+vs_35_8+"|"+vs_35_50+"|"+vs_35_50n8+"|"+vs_50_12+"|"+vs_50_60+"|"+vs_50_60n12+"|\n")

        width=15
        if self.game=="omahahi":
            logging.info("some equities for omahahi common situations")
            logging.info("MP:")
            logging.info("|"+self.table_item("$3b4o%",width)+"|"+self.table_item("$3b6i%",width)+"|"+self.table_item("$FI20!$3b6i",width)+"|"+self.table_item("$FI30!3b4o",width)+"|"
                     +self.table_item("$FI40!3b4o",width)+"|"+self.table_item("$FI20!$3b6i",width)+"|"+self.table_item("$FI30!$3b6i",width)+"|")
            logging.info("|"+self.table_item("",width)+"|"+self.table_item("",width)+"|"+self.table_item("",width)+"|"+self.table_item("",width)+"|"
                     +self.table_item("",width)+"|"+self.table_item("$FI40!$3b4o",width)+"|"+self.table_item("$FI50!$3b4o",width)+"|")

            vs_3b4=self.table_item(str(round(self.equity_query(hand,"$3b4o"),1)),width)
            vs_3b6=self.table_item(str(round(self.equity_query(hand,"$3b6i"),1)),width)
            vs_fi20n6=self.table_item(str(round(self.equity_query(hand,"$FI20!$3b6i"),1)),width)
            vs_fi30n4=self.table_item(str(round(self.equity_query(hand,"$FI30!$3b4o"),1)),width)
            vs_fi40n4=self.table_item(str(round(self.equity_query(hand,"$FI40!$3b4o"),1)),width)
            vs_fi20n6fi40n4=self.table_item(str(round(self.equity_query_3way(hand,"$FI20!$3b6i","$FI40!$3b4o"),1)),width)
            vs_fi30n6fi50n4=self.table_item(str(round(self.equity_query_3way(hand,"$FI30!$3b6i","$FI50!$3b4o"),1)),width)

            logging.info("|"+vs_3b4+"|"+vs_3b6+"|"+vs_fi20n6+"|"+vs_fi30n4+"|"+vs_fi40n4+"|"+vs_fi20n6fi40n4+"|"+vs_fi30n6fi50n4+"|\n")

            logging.info("CO:")
            logging.info("|"+self.table_item("$FI15",width)+"|"+self.table_item("$3b6o",width)+"|"+self.table_item("$3b8i",width)+"|"+self.table_item("$FI25!$3b8i",width)+"|"+self.table_item("$FI50!3b6o",width)+"|"
                     +self.table_item("60!3b6o",width)+"|"+self.table_item("$FI25!$3b8i",width)+"|"+self.table_item("$FI25!$3b8i",width)+"|")
            logging.info("|"+self.table_item("",width)+"|"+self.table_item("",width)+"|"+self.table_item("",width)+"|"+self.table_item("",width)+"|"+self.table_item("",width)+"|"
                     +self.table_item("",width)+"|"+self.table_item("$FI50!$3b6o",width)+"|"+self.table_item("$FI60!$3b6o",width)+"|")

            vs_fi15=self.table_item(str(round(self.equity_query(hand,"$FI15"),1)),width)
            vs_3b6=self.table_item(str(round(self.equity_query(hand,"$3b6o"),1)),width)
            vs_3b8=self.table_item(str(round(self.equity_query(hand,"$3b8i"),1)),width)
            vs_fi25n8=self.table_item(str(round(self.equity_query(hand,"$FI25!$3b8i"),1)),width)
            vs_fi50n6=self.table_item(str(round(self.equity_query(hand,"$FI50!$3b6o"),1)),width)
            vs_60n6=self.table_item(str(round(self.equity_query(hand,"60%6h!$3b6o"),1)),width)
            vs_fi25n8fi50n6=self.table_item(str(round(self.equity_query_3way(hand,"$FI25!$3b8i","$FI50!$3b6o"),1)),width)
            vs_fi25n860n6=self.table_item(str(round(self.equity_query_3way(hand,"$FI25!$3b8i","60%6h!$3b6o"),1)),width)

            logging.info("|"+vs_fi15+"|"+vs_3b6+"|"+vs_3b8+"|"+vs_fi25n8+"|"+vs_fi50n6+"|"+vs_60n6+"|"+vs_fi25n8fi50n6+"|"+vs_fi25n860n6+"|\n")
            

            logging.info("BU:")
            
            logging.info("|"+self.table_item("$FI25",width)+"|"+self.table_item("$3b8o",width)+"|"+self.table_item("$3b10o",width)+"|"+self.table_item("$3b15o",width)+"|"+self.table_item("$FI50!3b8o",width)+"|"
                     +self.table_item("60%!3b10o",width)+"|"+self.table_item("$FI25!$3b10o",width)+"|"+self.table_item("$FI25!$3b10o",width)+"|")
            logging.info("|"+self.table_item("",width)+"|"+self.table_item("",width)+"|"+self.table_item("",width)+"|"+self.table_item("",width)+"|"+self.table_item("",width)+"|"
                     +self.table_item("",width)+"|"+self.table_item("60%!$3b8o",width)+"|"+self.table_item("$3b10o",width)+"|")

            vs_fi25=self.table_item(str(round(self.equity_query(hand,"$FI25"),1)),width)
            vs_3b8=self.table_item(str(round(self.equity_query(hand,"$3b8o"),1)),width)
            vs_3b10=self.table_item(str(round(self.equity_query(hand,"$3b10o"),1)),width)
            vs_3b15=self.table_item(str(round(self.equity_query(hand,"$3b15o"),1)),width)
            vs_fi50n8=self.table_item(str(round(self.equity_query(hand,"$FI50!$3b8o"),1)),width)
            vs_60n10=self.table_item(str(round(self.equity_query(hand,"60%6h!$3b10o"),1)),width)
            vs_fi25n10fi60n8=self.table_item(str(round(self.equity_query_3way(hand,"$FI25!$3b10o","60%!3b8o"),1)),width)
            vs_fi25n103b10=self.table_item(str(round(self.equity_query_3way(hand,"$FI25!$3b10o","$3b10o"),1)),width)

            logging.info("|"+vs_fi25+"|"+vs_3b8+"|"+vs_3b10+"|"+vs_3b15+"|"+vs_fi50n8+"|"+vs_60n10+"|"+vs_fi25n10fi60n8+"|"+vs_fi25n103b10+"|\n")
            
            logging.info("SB:")

            logging.info("|"+self.table_item("$FI40",width)+"|"+self.table_item("$FI50",width)+"|"+self.table_item("65%",width)+"|"+self.table_item("$3b15i",width)+"|"+self.table_item("$4b3",width)+"|"
                     +self.table_item("$FI50",width)+"|"+self.table_item("$FI50!AA",width)+"|"+self.table_item("$FI50!$4b4",width)+"|")
            logging.info("|"+self.table_item("",width)+"|"+self.table_item("",width)+"|"+self.table_item("",width)+"|"+self.table_item("",width)+"|"+self.table_item("",width)+"|"
                     +self.table_item("60%!$3b10o",width)+"|"+self.table_item("$3b10o",width)+"|"+self.table_item("$3b15o",width)+"|")

            vs_fi40=self.table_item(str(round(self.equity_query(hand,"$FI40"),1)),width)
            vs_fi50=self.table_item(str(round(self.equity_query(hand,"$FI50"),1)),width)
            vs_65=self.table_item(str(round(self.equity_query(hand,"65%"),1)),width)
            vs_3b15=self.table_item(str(round(self.equity_query(hand,"$3b15o"),1)),width)
            vs_4b3=self.table_item(str(round(self.equity_query(hand,"$4b3"),1)),width)
            vs_5060n10=self.table_item(str(round(self.equity_query_3way(hand,"$FI50","60%6h!$3b10o"),1)),width)
            vs_50nAA3b10=self.table_item(str(round(self.equity_query_3way(hand,"$FI50!AA","$3b10o"),1)),width)
            vs_50n4b43b15=self.table_item(str(round(self.equity_query_3way(hand,"$FI50!$4b4","$3b15o"),1)),width)

            logging.info("|"+vs_fi40+"|"+vs_fi50+"|"+vs_65+"|"+vs_3b15+"|"+vs_4b3+"|"+vs_5060n10+"|"+vs_50nAA3b10+"|"+vs_50n4b43b15+"|\n")           

            logging.info("BB:")

            logging.info("|"+self.table_item("70%",width)+"|"+self.table_item("$FI50",width)+"|"+self.table_item("$FI50",width)+"|"+self.table_item("$FI50",width)+"|"+self.table_item("$FI50",width)+"|")
            logging.info("|"+self.table_item("",width)+"|"+self.table_item("$FI25!$3b10o",width)+"|"+self.table_item("$FI35!$3b15o",width)+"|"+self.table_item("$3b10o",width)+"|"+self.table_item("$3b15o",width)+"|")

            vs_70=self.table_item(str(round(self.equity_query(hand,"70%6h"),1)),width)
            vs_fi50fi25n3b10=self.table_item(str(round(self.equity_query_3way(hand,"$FI50","$FI25!$3b10o"),1)),width)
            vs_fi50fi35n3b15=self.table_item(str(round(self.equity_query_3way(hand,"$FI50","$FI25!$3b15o"),1)),width)
            vs_fi503b10=self.table_item(str(round(self.equity_query_3way(hand,"$FI50","$3b10o"),1)),width)
            vs_fi503b15=self.table_item(str(round(self.equity_query_3way(hand,"$FI50","$3b15o"),1)),width)

            logging.info("|"+vs_70+"|"+vs_fi50fi25n3b10+"|"+vs_fi50fi35n3b15+"|"+vs_fi503b10+"|"+vs_fi503b15+"|\n")
        logging.info(horizontal_line)
        return
    
def test():
    ppt_client=OddsOracleServer(trial=100000)
    ppt_client.start_ppt()
    ppt_client.board="Ks4h3c"
    for i in range(0,10):
        #result=ppt_client.run_query(TEST_QUERY)
        #equity=ppt_client.parse_ppt_answer(result,"EQUITY")
        #print(equity)
        #print("Equity: {0:2.2f}".format(equity*100))
        # result=ppt_client.equity_query("AA","10%")
        # equity=ppt_client.parse_ppt_answer(result,"EQUITY")
        rank=ppt_client.rank_query(25,"10%","50%","flop")
        # print(result)
        # if equity == 0:
        #   print(equity)
        print("RANK: {0:2.1f}".format(rank))
        result=ppt_client.in_range_query("AA","10%","As")
        # in_range=ppt_client.parse_ppt_answer(result,"INRANGE")
        # print(result)
        # if equity == 0:
        #   print(equity)
        print("IN RANGE: {0:2.1f}".format(result))
if __name__ == '__main__':
    import timeit
    logger=logging.getLogger()
    logger.setLevel(logging.ERROR)
    
    if DEBUG:
        test()


# 
# ppt.py ends here
