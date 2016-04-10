#!/usr/bin/env python3
# ppt.py --- 
# 
# Filename: ppt.py
# Description: 
# Author: Johann Ertl
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
            self.run_query(TEST_QUERY)
            
    def run_query(self, query):
        try:
            result = self.ppt_client.PPTServer.executePQL(query, self.trial, self.max_time, self.thread_cnt)
            logging.info(result)
            return result
        except:
            logging.error("No Connection to PPT Server")

    def parse_ppt_answer(self, answer,keyword="EQUITY",num_digets=PPT_NUM_DIGETS):
        number=0.0
        for line in answer.splitlines():
            if keyword in line:
                numbers=re.search('\d+\.\d+',line)
                numbers=numbers.group(0)
                if len(numbers)>PPT_NUM_DIGETS and '.' in numbers:
                    number=float(numbers)
                else:
                    logging.error("Could not get resulting number from PPT answer")
                    return 0.0
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
        logging.debug("Running the following query:")
        logging.debug(query)
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
        logging.debug("Running the following query:")
        logging.debug(query)
        return self.parse_ppt_answer(self.run_query(query),"INRANGE")

    def format_range(self,hand_range):
        return parse_hand(hand_range,self.board)
    
def test():
    ppt_client=OddsOracleServer(trial=100000)
    ppt_client.start_ppt()
    ppt_client.board="Ks4h3c"
    for i in range(0,10):
        #result=ppt_client.run_query(TEST_QUERY)
        #equity=ppt_client.parse_ppt_answer(result,"EQUITY")
        #print(equity)
        #print("Equity: {0:2.2f}".format(equity*100))
        result=ppt_client.equity_query("AA","10%")
        equity=ppt_client.parse_ppt_answer(result,"EQUITY")
        # print(result)
        # if equity == 0:
        #   print(equity)
        print("Equity: {0:2.1f}".format(equity*100))
        result=ppt_client.in_range_query("AA","10%","As")
        in_range=ppt_client.parse_ppt_answer(result,"INRANGE")
        # print(result)
        # if equity == 0:
        #   print(equity)
        print("IN RANGE: {0:2.1f}".format(in_range))
if __name__ == '__main__':
    import timeit
    logger=logging.getLogger()
    logger.setLevel(logging.ERROR)
    
    if DEBUG:
        test()


# 
# ppt.py ends here
