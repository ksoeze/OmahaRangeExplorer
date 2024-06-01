#!/usr/bin/env python3
# main_gui.py --- 
# 
# Filename: main_gui.py
# Description: 
# Author: Johann 
# Maintainer: 
# Created: Die Apr  5 14:16:51 2016 (+0200)
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

from tkinter import *
from tkinter import ttk
from tkinter import scrolledtext
from tkinter import messagebox
from tkinter import filedialog

from utils import *
from gui_elements import *
from ppt import OddsOracleServer
from board import parse_board
from board import return_string
from hand import parse_hand

from queue import Queue
import threading
import time
import pickle
import logging

import matplotlib
matplotlib.use('TkAgg')

from numpy import arange, sin, pi
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

###
# Range Builder Functions 
###

def update_ranges():
    # updates all start ranges
    # updates general inputs (board, game, dead, num_sim etc)
    rb_p1_flop.set_start_range(rb_p1_pre.get_range())
    rb_p2_flop.set_start_range(rb_p2_pre.get_range())

    rb_p1_turn.set_start_range(expand_range(rb_p1_flop.get_selected_range(),"flop"))
    rb_p2_turn.set_start_range(expand_range(rb_p2_flop.get_selected_range(),"flop"))

    rb_p1_river.set_start_range(expand_range(rb_p1_turn.get_selected_range(),"turn"))
    rb_p2_river.set_start_range(expand_range(rb_p2_turn.get_selected_range(),"turn"))

    ev_hero.post.set_start_range(ev_hero.pre.get_range())
    ev_villain1.post.set_start_range(ev_villain1.pre.get_range())
    ev_villain2.post.set_start_range(ev_villain2.pre.get_range())

    # set game dead etc
    ppt_client.game=gi_game.get()
    ppt_client.dead=gi_dead.get()
    return

def calc_ppt_set_value(range_1, range_2):

    if isinstance(range_2,Range):
        villain_range=range_2.get_start_range()
        villain_selected_range=range_2.get_selected_range()
    else:
        villain_range=range_2
        villain_selected_range=range_2
    
    hero_range=range_1.get_start_range()
    hero_selected_range=range_1.get_selected_range()
    hero_subrange_0=range_1.get_range(0,start_range=True)
    hero_subrange_1=range_1.get_range(1,start_range=True)
    hero_subrange_2=range_1.get_range(2,start_range=True)
    hero_subrange_3=range_1.get_range(3,start_range=True)

    logging.info(DOTS)
    logging.info("Start Calculation for Board: {0}".format(ppt_client.board))
    logging.info("Game= {0}, Dead= {1}, Trials= {2}".format(ppt_client.game, ppt_client.dead, ppt_client.trial))
    logging.info("Hero start range: {0}".format(hero_range))
    logging.info("Villain start range: {0}".format(villain_range))
    logging.info("Villain selected range: {0}".format(villain_selected_range))
    
    if hero_range:
        equity=ppt_client.equity_query(hero_range,villain_range)
        range_1.set_range_equity(equity)
        logging.info("Equity is {0:.1f} for hero overall range: {1}".format(equity,hero_range))
    else: range_1.set_range_equity(0)
    if hero_subrange_0:
        frequency=ppt_client.in_range_query(hero_range,villain_selected_range,hero_subrange_0)
        range_1.set_freq(0,frequency)
        equity=ppt_client.equity_query(hero_subrange_0,villain_selected_range)
        range_1.set_equity(0,equity)
        logging.info("Hero sub-range 1: {0} (Eq: {1:.3f}; Freq: {2:.3f})".format(hero_subrange_0,equity,frequency))
    else:
        range_1.set_freq(0,0)
        range_1.set_equity(0,0)
    if hero_subrange_1:
        frequency=ppt_client.in_range_query(hero_range,villain_selected_range,hero_subrange_1)
        range_1.set_freq(1,frequency)
        equity=ppt_client.equity_query(hero_subrange_1,villain_selected_range)
        range_1.set_equity(1,equity)
        logging.info("Hero sub-range 2: {0} (Eq: {1:.3f}; Freq: {2:.3f})".format(hero_subrange_1,equity,frequency))
    else:
        range_1.set_freq(1,0)
        range_1.set_equity(1,0)        
    if hero_subrange_2:
        frequency=ppt_client.in_range_query(hero_range,villain_selected_range,hero_subrange_2)
        range_1.set_freq(2,frequency)
        equity=ppt_client.equity_query(hero_subrange_2,villain_selected_range)
        range_1.set_equity(2,equity)
        logging.info("Hero sub-range 3: {0} (Eq: {1:.3f}; Freq: {2:.3f})".format(hero_subrange_2,equity,frequency))
    else:
        range_1.set_freq(2,0)
        range_1.set_equity(2,0)        
    if hero_subrange_3:
        frequency=ppt_client.in_range_query(hero_range,villain_selected_range,hero_subrange_3)
        range_1.set_freq(3,frequency)
        equity=ppt_client.equity_query(hero_subrange_3,villain_selected_range)
        range_1.set_equity(3,equity)
        logging.info("Hero sub-range 4: {0} (Eq: {1:.3f}; Freq: {2:.3f})".format(hero_subrange_3,equity,frequency))
    else:
        range_1.set_freq(3,0)
        range_1.set_equity(3,0)       
    if hero_selected_range:
        frequency=ppt_client.in_range_query(hero_range,villain_selected_range,hero_selected_range)
        range_1.set_summary_freq(frequency)        
        equity=ppt_client.equity_query(hero_selected_range,villain_selected_range)
        logging.info("Hero selected range: {0} (Eq: {1:.3f}; Freq: {2:.3f})".format(hero_selected_range,equity,frequency))
        range_1.set_summary_equity(equity)
    else:
        range_1.set_summary_freq(0)
        range_1.set_summary_equity(0)
    logging.info("Finished Calculation: {0}".format(ppt_client.board))
    logging.info(DOTS+"\n")
    
def eval_range(range_1, range_2, street):
    # takes 2 Range elements and sets all frequency and equities for range_1 vs selected range 2
    update_ranges()
    ppt_queue.put((set_ppt_board,street)) # set start board...push to ppt queue for right timing
    ppt_queue.put((calc_ppt_set_value,range_1,range_2))
    return


def calc_ppt_set_value_3way(range_1, range_2, range_3):
    villain1_range=range_2.get_start_range()
    villain1_selected_range=range_2.get_selected_range()

    villain2_range=range_3.get_start_range()
    villain2_selected_range=range_3.get_selected_range()    
    
    hero_range=range_1.get_start_range()
    hero_selected_range=range_1.get_selected_range()
    hero_subrange_0=range_1.get_range(0,start_range=True)
    hero_subrange_1=range_1.get_range(1,start_range=True)
    hero_subrange_2=range_1.get_range(2,start_range=True)
    hero_subrange_3=range_1.get_range(3,start_range=True)

    logging.info(DOTS)
    logging.info("Start 3way calculation for board: {0}".format(ppt_client.board))
    logging.info("Game= {0}, Dead= {1}, Trials= {2}".format(ppt_client.game, ppt_client.dead, ppt_client.trial))
    logging.info("Hero start range: {0}".format(hero_range))
    logging.info("Villain1 start range: {0} \n".format(villain1_range))
    logging.info("Villain2 start range: {0} \n".format(villain2_range))
    logging.info("Villain1 selected range: {0} \n".format(villain1_selected_range))
    logging.info("Villain2 selected range: {0} \n".format(villain2_selected_range))    
    
    if hero_range:
        equity=ppt_client.equity_query_3way(hero_range,villain1_range,villain2_range)
        range_1.set_range_equity(equity)
        logging.info("Equity is {0:.3f} for hero overall range: {1} \n".format(equity,hero_range))
    else: range_1.set_range_equity(0)
    if hero_subrange_0:
        frequency=ppt_client.in_range_query_3way(hero_range,villain1_selected_range,villain2_selected_range,hero_subrange_0)
        range_1.set_freq(0,frequency)
        equity=ppt_client.equity_query_3way(hero_subrange_0,villain1_selected_range,villain2_selected_range)
        range_1.set_equity(0,equity)
        logging.info("Hero sub-range 1: {0} (Eq: {1:.3f}; Freq: {2:.3f})".format(hero_subrange_0,equity,frequency))
    else:
        range_1.set_freq(0,0)
        range_1.set_equity(0,0)
    if hero_subrange_1:
        frequency=ppt_client.in_range_query_3way(hero_range,villain1_selected_range,villain2_selected_range,hero_subrange_1)
        range_1.set_freq(1,frequency)
        equity=ppt_client.equity_query_3way(hero_subrange_1,villain1_selected_range,villain2_selected_range)
        range_1.set_equity(1,equity)
        logging.info("Hero sub-range 2: {0} (Eq: {1:.3f}; Freq: {2:.3f})".format(hero_subrange_1,equity,frequency))        
    else:
        range_1.set_freq(1,0)
        range_1.set_equity(1,0)        
    if hero_subrange_2:
        frequency=ppt_client.in_range_query_3way(hero_range,villain1_selected_range,villain2_selected_range,hero_subrange_2)
        range_1.set_freq(2,frequency)
        equity=ppt_client.equity_query_3way(hero_subrange_2,villain1_selected_range,villain2_selected_range)
        range_1.set_equity(2,equity)
        logging.info("Hero sub-range 3: {0} (Eq: {1:.3f}; Freq: {2:.3f})".format(hero_subrange_2,equity,frequency))
    else:
        range_1.set_freq(2,0)
        range_1.set_equity(2,0)        
    if hero_subrange_3:
        frequency=ppt_client.in_range_query_3way(hero_range,villain1_selected_range,villain2_selected_range,hero_subrange_3)
        range_1.set_freq(3,frequency)
        equity=ppt_client.equity_query_3way(hero_subrange_3,villain1_selected_range,villain2_selected_range)
        range_1.set_equity(3,equity)
        logging.info("Hero sub-range 4: {0} (Eq: {1:.3f}; Freq: {2:.3f})".format(hero_subrange_3,equity,frequency))        
    else:
        range_1.set_freq(3,0)
        range_1.set_equity(3,0)       
    if hero_selected_range:
        frequency=ppt_client.in_range_query_3way(hero_range,villain1_selected_range,villain2_selected_range,hero_selected_range)
        range_1.set_summary_freq(frequency)        
        equity=ppt_client.equity_query_3way(hero_selected_range,villain1_selected_range,villain2_selected_range)
        range_1.set_summary_equity(equity)
        logging.info("Hero selected range: {0} (Eq: {1:.3f}; Freq: {2:.3f})".format(hero_selected_range,equity,frequency))        
    else:
        range_1.set_summary_freq(0)
        range_1.set_summary_equity(0)
    logging.info("Finished Calculation: {0}".format(ppt_client.board))
    logging.info(DOTS)

def eval_range_3way(range_1, range_2, range_3, street):
    # takes 2 Range elements and sets all frequency and equities for range_1 vs selected range 2
    update_ranges()
    ppt_queue.put((set_ppt_board,street)) # set start board...push to ppt queue for right timing
    ppt_queue.put((calc_ppt_set_value_3way,range_1,range_2,range_3))
    return

def eval_player_1():
    eval_range(rb_p1_flop, rb_p2_flop, "flop")
    eval_range(rb_p1_turn, rb_p2_turn, "turn")
    eval_range(rb_p1_river, rb_p2_river, "river")
    
def eval_player_2():
    eval_range(rb_p2_flop, rb_p1_flop,"flop")
    eval_range(rb_p2_turn, rb_p1_turn, "turn")
    eval_range(rb_p2_river, rb_p1_river, "river")
    

def eval_range_distribution():
    update_ranges()
    start_ranges=get_range_distribution_ranges()
    rd_range.set_start_range(start_ranges[0])
    eval_range(rd_range,start_ranges[1],"river")
    return

def get_range_distribution_ranges():
    hero_range_sel=rd_start_range.get()
    hero_range=""
    if hero_range_sel == 'Player 1 Flop':
        hero_range= expand_range(rb_p1_flop.get_selected_range(),"flop")
    elif  hero_range_sel == 'Player 2 Flop':
        hero_range=expand_range(rb_p2_flop.get_selected_range(),"flop")
    elif  hero_range_sel == 'Player 1 Turn':
        hero_range=expand_range(rb_p1_turn.get_selected_range(),"turn")
    elif  hero_range_sel == 'Player 2 Turn':
        hero_range=expand_range(rb_p2_turn.get_selected_range(),"turn")       
    elif  hero_range_sel == 'Player 1 River':
        hero_range=expand_range(rb_p1_river.get_selected_range(),"river")
    elif  hero_range_sel == 'Player 2 River':
        hero_range=expand_range(rb_p2_river.get_selected_range(),"river")
    elif hero_range_sel == 'Hero':
        hero_range=expand_range(ev_hero.post.get_selected_range(), "river")
    elif hero_range_sel == 'Villain 1':
        hero_range=expand_range(ev_villain1.post.get_selected_range(), "river")
    elif hero_range_sel == 'Villain 2':
        hero_range=expand_range(ev_villain2.post.get_selected_range(), "river")

    villain_range_sel=rd_vs_range.get()
    vil_range=""
    if villain_range_sel == 'Player 1 Flop':
        vil_range=expand_range(rb_p1_flop.get_selected_range(),"flop")
    elif  villain_range_sel == 'Player 2 Flop':
        vil_range=expand_range(rb_p2_flop.get_selected_range(),"flop")                      
    elif  villain_range_sel == 'Player 1 Turn':
        vil_range=expand_range(rb_p1_turn.get_selected_range(),"turn")                      
    elif  villain_range_sel == 'Player 2 Turn':
        vil_range=expand_range(rb_p2_turn.get_selected_range(),"turn")                      
    elif  villain_range_sel == 'Player 1 River':
        vil_range=expand_range(rb_p1_river.get_selected_range(),"river")                      
    elif  villain_range_sel == 'Player 2 River':
        vil_range=expand_range(rb_p2_river.get_selected_range(),"river")                      
    elif villain_range_sel == 'Hero':
        vil_range=expand_range(ev_hero.post.get_selected_range(),"river")                      
    elif villain_range_sel == 'Villain 1':
        vil_range=expand_range(ev_villain1.post.get_selected_range(),"river")                      
    elif villain_range_sel == 'Villain 2':
        vil_range=expand_range(ev_villain2.post.get_selected_range(),"river")                      
    return [hero_range,vil_range]


def turn_card_calc():
    update_ranges()
    ppt_client.board=return_string(parse_board(gi_board.get()),"flop") if parse_board(gi_board.get()) else ""
    start_ranges=get_range_distribution_ranges()
    ppt_queue.put((ppt_client.next_card_eval,start_ranges[0],start_ranges[1]))
    return
def river_card_calc():
    update_ranges()
    ppt_client.board=return_string(parse_board(gi_board.get()),"turn") if parse_board(gi_board.get()) else ""
    start_ranges=get_range_distribution_ranges()
    ppt_queue.put((ppt_client.next_card_eval,start_ranges[0],start_ranges[1]))    
    return
###
# Equity Calcs Functions
###

def bet_vs_1_calc():
    eval_range(ev_hero.post,ev_villain1.post,ev_bet_vs1_street.get())
    eval_range(ev_villain1.post,ev_hero.post,ev_bet_vs1_street.get())
    
    ppt_queue.put((ppt_client.bet_vs_1_calculations, ev_bet_vs1_result_str, ev_hero.post,ev_villain1.post,
                   ev_bet_vs1_hand.get(),
                   ev_bet_vs1_potsize.get(),ev_bet_vs1_stacksize.get(),ev_bet_vs1_betsize.get(),
                   ev_bet_vs1_raisesize.get(),ev_bet_vs1_reraisesize.get(),ev_bet_vs1_street.get()
                   ))
    return

def rank_hand():
    update_ranges()
    ppt_queue.put((ppt_client.rank_hand,
                   ev_bet_vs1_hand.get()))
    
def bet_vs_2_calc():
    eval_range_3way(ev_hero.post,ev_villain1.post,ev_villain2.post,ev_bet_vs2_street.get())
    eval_range_3way(ev_villain1.post,ev_villain2.post,ev_hero.post,ev_bet_vs2_street.get())
    eval_range_3way(ev_villain2.post,ev_villain1.post,ev_hero.post,ev_bet_vs2_street.get())
    
    ppt_queue.put((ppt_client.bet_vs_2_calculations, ev_bet_vs2_result_str, ev_hero.post, ev_villain1.post
                   ,ev_villain2.post, ev_bet_vs2_hand.get(), ev_bet_vs2_potsize.get()
                   ,ev_bet_vs2_stacksize1.get(),ev_bet_vs2_stacksize2.get(),
                   ev_bet_vs2_betsize.get(),ev_bet_vs2_raisesize.get(),ev_bet_vs2_reraisesize.get(),ev_bet_vs2_street.get() ))
    
    return

def do_4bet_calc():
    update_ranges()
    ppt_queue.put((ppt_client.do_4bet, ev_4bet_result_str, ev_4bet_hand.get(), ev_villain1.pre.get_range(),
                   ev_villain1.post.get_certain_range([0]),ev_4bet_stacksize.get(), ev_4bet_opensize.get(),
                   ev_4bet_3bsize.get(), ev_4bet_potsize.get()))
    return
    
def call_4bet_calc():
    update_ranges()
    ppt_queue.put((ppt_client.call_4bet, ev_4bet_result_str, ev_4bet_hand.get(), ev_villain1.pre.get_range(),
                  ev_4bet_stacksize.get(), ev_4bet_opensize.get(),
                   ev_4bet_3bsize.get(), ev_4bet_potsize.get()))    
    return

def hero_ship_plot():
    popup_window=Toplevel()
    popup_window.wm_title("Hero ships his stack in")

    figure = Figure(figsize=(15, 10), dpi=160)
    plot = figure.add_subplot(111)
    plot.grid(True)
    plot.set_xticks(arange(0,0.5,0.02))
    plot.set_yticks(arange(0,1,0.05))
    interval = arange(0.0, 0.5, 0.01)
    stack=ppt_client.str2float(ev_bet_vs1_stacksize.get())
    pot=ppt_client.str2float(ev_bet_vs1_potsize.get())
    function = (-interval*(pot + 2*stack) + stack)/(pot - interval*(pot+2*stack) + stack)

    plot.plot(interval,function)
    plot.set_title("Hero ships; Equity and corresponding FEQ for EV ship = 0")
    plot.set_xlabel("Equity")
    plot.set_ylabel("Villain Fold Frequency")

    canvas=FigureCanvasTkAgg(figure, master=popup_window)
    canvas.draw()
    canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)
    canvas._tkcanvas.pack(side=TOP, fill=BOTH, expand=1)

    popup_window.mainloop()
    return

def villain_ship_plot():
    popup_window=Toplevel()
    popup_window.wm_title("Villain ships his stack in over Hero bet")

    figure = Figure(figsize=(15, 10), dpi=160)
    plot = figure.add_subplot(111)
    plot.grid(True)
    plot.set_xticks(arange(0,0.5,0.02))
    plot.set_yticks(arange(0,1,0.05))
    interval = arange(0.0, 0.5, 0.01)
    stack=ppt_client.str2float(ev_bet_vs1_stacksize.get())
    pot=ppt_client.str2float(ev_bet_vs1_potsize.get())
    bet=ppt_client.str2float(ev_bet_vs1_betsize.get())
    function = (-interval*(pot + 2*stack) + stack)/(pot+bet - interval*(pot+2*stack) + stack)

    plot.plot(interval,function)
    plot.set_title("Villain ships over Hero bet; Equity and corresponding FEQ for EV ship = 0")
    plot.set_xlabel("Equity")
    plot.set_ylabel("Villain Fold Frequency")

    canvas=FigureCanvasTkAgg(figure, master=popup_window)
    canvas.draw()
    canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)
    canvas._tkcanvas.pack(side=TOP, fill=BOTH, expand=1)

    popup_window.mainloop()
    return
###
# General Functions
###

def save_session():
    filename = filedialog.asksaveasfilename()
    logging.debug("Filename={}".format(filename))
    try:
        data = {
            "gi_board": gi_board.get(),
            "gi_dead": gi_dead.get(),
            "gi_game": gi_game.get(),
            "gi_debug": gi_debug.get(),
            "ev_bet_vs1_stacksize":ev_bet_vs1_stacksize.get(),
            "ev_bet_vs1_potsize":ev_bet_vs1_potsize.get(),
            "ev_bet_vs1_betsize":ev_bet_vs1_betsize.get(),
            "ev_bet_vs1_raisesize":ev_bet_vs1_raisesize.get(),
            "ev_bet_vs1_reraisesize":ev_bet_vs1_reraisesize.get(),
            "ev_bet_vs1_hand":ev_bet_vs1_hand.get(),
            "ev_bet_vs1_street":ev_bet_vs1_street.get(),

            "ev_bet_vs2_stacksize1":ev_bet_vs2_stacksize1.get(),
            "ev_bet_vs2_stacksize2":ev_bet_vs2_stacksize2.get(),
            "ev_bet_vs2_potsize":ev_bet_vs2_potsize.get(),
            "ev_bet_vs2_betsize":ev_bet_vs2_betsize.get(),
            "ev_bet_vs2_raisesize":ev_bet_vs2_raisesize.get(),
            "ev_bet_vs2_reraisesize":ev_bet_vs2_reraisesize.get(),
            "ev_bet_vs2_hand":ev_bet_vs2_hand.get(),
            "ev_bet_vs2_street":ev_bet_vs2_street.get(),

            "ev_4bet_stacksize":ev_4bet_stacksize.get(),
            "ev_4bet_potsize":ev_4bet_potsize.get(),
            "ev_4bet_opensize":ev_4bet_opensize.get(),
            "ev_4bet_3bsize":ev_4bet_3bsize.get(),
            "ev_4bet_hand":ev_4bet_hand.get(),
            
            "rb_p1_pre.include_range":rb_p1_pre.include_range.get(),
            "rb_p1_pre.exclude_range":rb_p1_pre.exclude_range.get(),
            "rb_p2_pre.include_range":rb_p2_pre.include_range.get(),
            "rb_p2_pre.exclude_range":rb_p2_pre.exclude_range.get(),

            "rd_range.sub_range_list[0].input_range":rd_range.sub_range_list[0].input_range.get(),
            "rd_range.sub_range_list[1].input_range":rd_range.sub_range_list[1].input_range.get(),
            "rd_range.sub_range_list[2].input_range":rd_range.sub_range_list[2].input_range.get(),
            "rd_range.sub_range_list[3].input_range":rd_range.sub_range_list[3].input_range.get(),

            "rd_start_range":rd_start_range.get(),
            "rd_vs_range":rd_vs_range.get(),

            "rb_p1_flop.sub_range_list[0].input_range":rb_p1_flop.sub_range_list[0].input_range.get(),
            "rb_p1_flop.sub_range_list[1].input_range":rb_p1_flop.sub_range_list[1].input_range.get(),
            "rb_p1_flop.sub_range_list[2].input_range":rb_p1_flop.sub_range_list[2].input_range.get(),
            "rb_p1_flop.sub_range_list[3].input_range":rb_p1_flop.sub_range_list[3].input_range.get(),
            "rb_p2_flop.sub_range_list[0].input_range":rb_p2_flop.sub_range_list[0].input_range.get(),
            "rb_p2_flop.sub_range_list[1].input_range":rb_p2_flop.sub_range_list[1].input_range.get(),
            "rb_p2_flop.sub_range_list[2].input_range":rb_p2_flop.sub_range_list[2].input_range.get(),
            "rb_p2_flop.sub_range_list[3].input_range":rb_p2_flop.sub_range_list[3].input_range.get(),

            "rb_p1_turn.sub_range_list[0].input_range":rb_p1_turn.sub_range_list[0].input_range.get(),
            "rb_p1_turn.sub_range_list[1].input_range":rb_p1_turn.sub_range_list[1].input_range.get(),
            "rb_p1_turn.sub_range_list[2].input_range":rb_p1_turn.sub_range_list[2].input_range.get(),
            "rb_p1_turn.sub_range_list[3].input_range":rb_p1_turn.sub_range_list[3].input_range.get(),
            "rb_p2_turn.sub_range_list[0].input_range":rb_p2_turn.sub_range_list[0].input_range.get(),
            "rb_p2_turn.sub_range_list[1].input_range":rb_p2_turn.sub_range_list[1].input_range.get(),
            "rb_p2_turn.sub_range_list[2].input_range":rb_p2_turn.sub_range_list[2].input_range.get(),
            "rb_p2_turn.sub_range_list[3].input_range":rb_p2_turn.sub_range_list[3].input_range.get(),

            "rb_p1_river.sub_range_list[0].input_range":rb_p1_river.sub_range_list[0].input_range.get(),
            "rb_p1_river.sub_range_list[1].input_range":rb_p1_river.sub_range_list[1].input_range.get(),
            "rb_p1_river.sub_range_list[2].input_range":rb_p1_river.sub_range_list[2].input_range.get(),
            "rb_p1_river.sub_range_list[3].input_range":rb_p1_river.sub_range_list[3].input_range.get(),
            "rb_p2_river.sub_range_list[0].input_range":rb_p2_river.sub_range_list[0].input_range.get(),
            "rb_p2_river.sub_range_list[1].input_range":rb_p2_river.sub_range_list[1].input_range.get(),
            "rb_p2_river.sub_range_list[2].input_range":rb_p2_river.sub_range_list[2].input_range.get(),
            "rb_p2_river.sub_range_list[3].input_range":rb_p2_river.sub_range_list[3].input_range.get(),

            "ev_hero.pre.include_range":ev_hero.pre.include_range.get(),
            "ev_hero.pre.exclude_range":ev_hero.pre.exclude_range.get(),
            "ev_villain1.pre.include_range":ev_villain1.pre.include_range.get(),
            "ev_villain1.pre.exclude_range":ev_villain1.pre.exclude_range.get(),
            "ev_villain2.pre.include_range":ev_villain2.pre.include_range.get(),
            "ev_villain2.pre.exclude_range":ev_villain2.pre.exclude_range.get(),

            "ev_hero.post.sub_range_list[0].input_range":ev_hero.post.sub_range_list[0].input_range.get(),
            "ev_hero.post.sub_range_list[1].input_range":ev_hero.post.sub_range_list[1].input_range.get(),
            "ev_hero.post.sub_range_list[2].input_range":ev_hero.post.sub_range_list[2].input_range.get(),
            "ev_hero.post.sub_range_list[3].input_range":ev_hero.post.sub_range_list[3].input_range.get(),

            "ev_villain1.post.sub_range_list[0].input_range":ev_villain1.post.sub_range_list[0].input_range.get(),
            "ev_villain1.post.sub_range_list[1].input_range":ev_villain1.post.sub_range_list[1].input_range.get(),
            "ev_villain1.post.sub_range_list[2].input_range":ev_villain1.post.sub_range_list[2].input_range.get(),
            "ev_villain1.post.sub_range_list[3].input_range":ev_villain1.post.sub_range_list[3].input_range.get(),
            
            "ev_villain2.post.sub_range_list[0].input_range":ev_villain2.post.sub_range_list[0].input_range.get(),
            "ev_villain2.post.sub_range_list[1].input_range":ev_villain2.post.sub_range_list[1].input_range.get(),
            "ev_villain2.post.sub_range_list[2].input_range":ev_villain2.post.sub_range_list[2].input_range.get(),
            "ev_villain2.post.sub_range_list[3].input_range":ev_villain2.post.sub_range_list[3].input_range.get()
        }
        with open(filename, "wb") as f:
            pickle.dump(data, f)
    except Exception as e:
            logging.error("Error saving session:\n" + str(e))            
    return

def load_session():
    filename = filedialog.askopenfilename()
    logging.debug("Filename={}".format(filename))
    try:
        with open(filename,"rb") as f:
            data = pickle.load(f)
        gi_board.set(data["gi_board"])
        gi_dead.set(data["gi_dead"])
        gi_game.set(data["gi_game"])
        gi_debug.set(data["gi_debug"])

        ev_bet_vs1_stacksize.set(data["ev_bet_vs1_stacksize"])
        ev_bet_vs1_potsize.set(data["ev_bet_vs1_potsize"])
        ev_bet_vs1_betsize.set(data["ev_bet_vs1_betsize"])
        ev_bet_vs1_raisesize.set(data["ev_bet_vs1_raisesize"])
        ev_bet_vs1_reraisesize.set(data["ev_bet_vs1_reraisesize"])        
        ev_bet_vs1_hand.set(data["ev_bet_vs1_hand"])
        ev_bet_vs1_street.set(data["ev_bet_vs1_street"])

        ev_bet_vs2_stacksize1.set(data["ev_bet_vs2_stacksize1"])
        ev_bet_vs2_stacksize2.set(data["ev_bet_vs2_stacksize2"])        
        ev_bet_vs2_potsize.set(data["ev_bet_vs2_potsize"])
        ev_bet_vs2_betsize.set(data["ev_bet_vs2_betsize"])
        ev_bet_vs2_raisesize.set(data["ev_bet_vs2_raisesize"])
        ev_bet_vs2_reraisesize.set(data["ev_bet_vs2_reraisesize"])        
        ev_bet_vs2_hand.set(data["ev_bet_vs2_hand"])
        ev_bet_vs2_street.set(data["ev_bet_vs2_street"])

        ev_4bet_stacksize.set(data["ev_4bet_stacksize"])
        ev_4bet_potsize.set(data["ev_4bet_potsize"])
        ev_4bet_opensize.set(data["ev_4bet_opensize"])
        ev_4bet_3bsize.set(data["ev_4bet_3bsize"])
        ev_4bet_hand.set(data["ev_4bet_hand"])
        
        rb_p1_pre.include_range.set(data["rb_p1_pre.include_range"])
        rb_p1_pre.exclude_range.set(data["rb_p1_pre.exclude_range"])
        rb_p2_pre.include_range.set(data["rb_p2_pre.include_range"])
        rb_p2_pre.exclude_range.set(data["rb_p2_pre.exclude_range"])

        rd_range.sub_range_list[0].input_range.set(data["rd_range.sub_range_list[0].input_range"])
        rd_range.sub_range_list[1].input_range.set(data["rd_range.sub_range_list[1].input_range"])
        rd_range.sub_range_list[2].input_range.set(data["rd_range.sub_range_list[2].input_range"])
        rd_range.sub_range_list[3].input_range.set(data["rd_range.sub_range_list[3].input_range"])

        rd_start_range.set(data["rd_start_range"])
        rd_vs_range.set(data["rd_vs_range"])

        rb_p1_flop.sub_range_list[0].input_range.set(data["rb_p1_flop.sub_range_list[0].input_range"])
        rb_p1_flop.sub_range_list[1].input_range.set(data["rb_p1_flop.sub_range_list[1].input_range"])
        rb_p1_flop.sub_range_list[2].input_range.set(data["rb_p1_flop.sub_range_list[2].input_range"])
        rb_p1_flop.sub_range_list[3].input_range.set(data["rb_p1_flop.sub_range_list[3].input_range"])
        rb_p2_flop.sub_range_list[0].input_range.set(data["rb_p2_flop.sub_range_list[0].input_range"])
        rb_p2_flop.sub_range_list[1].input_range.set(data["rb_p2_flop.sub_range_list[1].input_range"])
        rb_p2_flop.sub_range_list[2].input_range.set(data["rb_p2_flop.sub_range_list[2].input_range"])
        rb_p2_flop.sub_range_list[3].input_range.set(data["rb_p2_flop.sub_range_list[3].input_range"])
        rb_p1_turn.sub_range_list[0].input_range.set(data["rb_p1_turn.sub_range_list[0].input_range"])
        rb_p1_turn.sub_range_list[1].input_range.set(data["rb_p1_turn.sub_range_list[1].input_range"])
        rb_p1_turn.sub_range_list[2].input_range.set(data["rb_p1_turn.sub_range_list[2].input_range"])
        rb_p1_turn.sub_range_list[3].input_range.set(data["rb_p1_turn.sub_range_list[3].input_range"])
        rb_p2_turn.sub_range_list[0].input_range.set(data["rb_p2_turn.sub_range_list[0].input_range"])
        rb_p2_turn.sub_range_list[1].input_range.set(data["rb_p2_turn.sub_range_list[1].input_range"])
        rb_p2_turn.sub_range_list[2].input_range.set(data["rb_p2_turn.sub_range_list[2].input_range"])
        rb_p2_turn.sub_range_list[3].input_range.set(data["rb_p2_turn.sub_range_list[3].input_range"])


        rb_p1_river.sub_range_list[0].input_range.set(data["rb_p1_river.sub_range_list[0].input_range"])
        rb_p1_river.sub_range_list[1].input_range.set(data["rb_p1_river.sub_range_list[1].input_range"])
        rb_p1_river.sub_range_list[2].input_range.set(data["rb_p1_river.sub_range_list[2].input_range"])
        rb_p1_river.sub_range_list[3].input_range.set(data["rb_p1_river.sub_range_list[3].input_range"])
        rb_p2_river.sub_range_list[0].input_range.set(data["rb_p2_river.sub_range_list[0].input_range"])
        rb_p2_river.sub_range_list[1].input_range.set(data["rb_p2_river.sub_range_list[1].input_range"])
        rb_p2_river.sub_range_list[2].input_range.set(data["rb_p2_river.sub_range_list[2].input_range"])
        rb_p2_river.sub_range_list[3].input_range.set(data["rb_p2_river.sub_range_list[3].input_range"])

        ev_hero.pre.include_range.set(data["ev_hero.pre.include_range"])
        ev_hero.pre.exclude_range.set(data["ev_hero.pre.exclude_range"])
        ev_villain1.pre.include_range.set(data["ev_villain1.pre.include_range"])
        ev_villain1.pre.exclude_range.set(data["ev_villain1.pre.exclude_range"])
        ev_villain2.pre.include_range.set(data["ev_villain2.pre.include_range"])
        ev_villain2.pre.exclude_range.set(data["ev_villain2.pre.exclude_range"])

        ev_hero.post.sub_range_list[0].input_range.set(data["ev_hero.post.sub_range_list[0].input_range"])
        ev_hero.post.sub_range_list[1].input_range.set(data["ev_hero.post.sub_range_list[1].input_range"])
        ev_hero.post.sub_range_list[2].input_range.set(data["ev_hero.post.sub_range_list[2].input_range"])
        ev_hero.post.sub_range_list[3].input_range.set(data["ev_hero.post.sub_range_list[3].input_range"])

        ev_villain1.post.sub_range_list[0].input_range.set(data["ev_villain1.post.sub_range_list[0].input_range"])
        ev_villain1.post.sub_range_list[1].input_range.set(data["ev_villain1.post.sub_range_list[1].input_range"])
        ev_villain1.post.sub_range_list[2].input_range.set(data["ev_villain1.post.sub_range_list[2].input_range"])
        ev_villain1.post.sub_range_list[3].input_range.set(data["ev_villain1.post.sub_range_list[3].input_range"])

        ev_villain2.post.sub_range_list[0].input_range.set(data["ev_villain2.post.sub_range_list[0].input_range"])
        ev_villain2.post.sub_range_list[1].input_range.set(data["ev_villain2.post.sub_range_list[1].input_range"])
        ev_villain2.post.sub_range_list[2].input_range.set(data["ev_villain2.post.sub_range_list[2].input_range"])
        ev_villain2.post.sub_range_list[3].input_range.set(data["ev_villain2.post.sub_range_list[3].input_range"])      
    except Exception as e:
            logging.error("Error loading session:\n" + str(e))            
    return

def clear_session():
    gi_board.set("")
    gi_dead.set("")
    gi_game.set("omahahi")
    gi_debug.set(0)
    
    ev_bet_vs1_stacksize.set(STACKSIZE)
    ev_bet_vs1_potsize.set(POTSIZE)
    ev_bet_vs1_betsize.set(BETSIZE)
    ev_bet_vs1_raisesize.set(RAISESIZE)
    ev_bet_vs1_reraisesize.set(RERAISESIZE)
    ev_bet_vs1_street.set(STREET)     
    ev_bet_vs1_hand.set("")
   
    ev_bet_vs2_hand.set("")
    ev_bet_vs2_stacksize1.set(STACKSIZE)
    ev_bet_vs2_stacksize2.set(STACKSIZE)
    ev_bet_vs2_potsize.set(POTSIZE)
    ev_bet_vs2_betsize.set(BETSIZE)
    ev_bet_vs2_raisesize.set(RAISESIZE)
    ev_bet_vs2_reraisesize.set(RERAISESIZE)
    ev_bet_vs2_street.set(STREET)
    
    ev_4bet_stacksize.set(BET4_STACK)
    ev_4bet_potsize.set(BET4_POT)
    ev_4bet_opensize.set(BET4_OPEN)
    ev_4bet_3bsize.set(BET4_3BET)
        
    rb_p1_pre.include_range.set("")
    rb_p1_pre.exclude_range.set("")
    rb_p2_pre.include_range.set("")
    rb_p2_pre.exclude_range.set("")

    rd_range.sub_range_list[0].input_range.set("")
    rd_range.sub_range_list[1].input_range.set("")
    rd_range.sub_range_list[2].input_range.set("")
    rd_range.sub_range_list[3].input_range.set("")
    rd_range.sub_range_list[0].x_box_value.set(0)
    rd_range.sub_range_list[1].x_box_value.set(0)
    rd_range.sub_range_list[2].x_box_value.set(0)
    rd_range.sub_range_list[3].x_box_value.set(0)
    
    rd_start_range.set('Player 1 Flop')
    rd_vs_range.set('Player 2 Flop')

    rb_p1_flop.sub_range_list[0].input_range.set("")
    rb_p1_flop.sub_range_list[1].input_range.set("")
    rb_p1_flop.sub_range_list[2].input_range.set("")
    rb_p1_flop.sub_range_list[3].input_range.set("")
    rb_p2_flop.sub_range_list[0].input_range.set("")
    rb_p2_flop.sub_range_list[1].input_range.set("")
    rb_p2_flop.sub_range_list[2].input_range.set("")
    rb_p2_flop.sub_range_list[3].input_range.set("")
    rb_p1_turn.sub_range_list[0].input_range.set("")
    rb_p1_turn.sub_range_list[1].input_range.set("")
    rb_p1_turn.sub_range_list[2].input_range.set("")
    rb_p1_turn.sub_range_list[3].input_range.set("")
    rb_p2_turn.sub_range_list[0].input_range.set("")
    rb_p2_turn.sub_range_list[1].input_range.set("")
    rb_p2_turn.sub_range_list[2].input_range.set("")
    rb_p2_turn.sub_range_list[3].input_range.set("")

    rb_p1_flop.sub_range_list[0].x_box_value.set(0)
    rb_p1_flop.sub_range_list[1].x_box_value.set(0)
    rb_p1_flop.sub_range_list[2].x_box_value.set(0)
    rb_p1_flop.sub_range_list[3].x_box_value.set(0)
    rb_p2_flop.sub_range_list[0].x_box_value.set(0)
    rb_p2_flop.sub_range_list[1].x_box_value.set(0)
    rb_p2_flop.sub_range_list[2].x_box_value.set(0)
    rb_p2_flop.sub_range_list[3].x_box_value.set(0)
    rb_p1_turn.sub_range_list[0].x_box_value.set(0)
    rb_p1_turn.sub_range_list[1].x_box_value.set(0)
    rb_p1_turn.sub_range_list[2].x_box_value.set(0)
    rb_p1_turn.sub_range_list[3].x_box_value.set(0)
    rb_p2_turn.sub_range_list[0].x_box_value.set(0)
    rb_p2_turn.sub_range_list[1].x_box_value.set(0)
    rb_p2_turn.sub_range_list[2].x_box_value.set(0)
    rb_p2_turn.sub_range_list[3].x_box_value.set(0)
    rb_p1_river.sub_range_list[0].x_box_value.set(0)
    rb_p1_river.sub_range_list[1].x_box_value.set(0)
    rb_p1_river.sub_range_list[2].x_box_value.set(0)
    rb_p1_river.sub_range_list[3].x_box_value.set(0)
    rb_p2_river.sub_range_list[0].x_box_value.set(0)
    rb_p2_river.sub_range_list[1].x_box_value.set(0)
    rb_p2_river.sub_range_list[2].x_box_value.set(0)
    rb_p2_river.sub_range_list[3].x_box_value.set(0)


    rb_p1_river.sub_range_list[0].input_range.set("")
    rb_p1_river.sub_range_list[1].input_range.set("")
    rb_p1_river.sub_range_list[2].input_range.set("")
    rb_p1_river.sub_range_list[3].input_range.set("")
    rb_p2_river.sub_range_list[0].input_range.set("")
    rb_p2_river.sub_range_list[1].input_range.set("")
    rb_p2_river.sub_range_list[2].input_range.set("")
    rb_p2_river.sub_range_list[3].input_range.set("")

    ev_hero.pre.include_range.set("")
    ev_hero.pre.exclude_range.set("")
    ev_villain1.pre.include_range.set("")
    ev_villain1.pre.exclude_range.set("")
    ev_villain2.pre.include_range.set("")
    ev_villain2.pre.exclude_range.set("")

    ev_hero.post.sub_range_list[0].input_range.set("")
    ev_hero.post.sub_range_list[1].input_range.set("")
    ev_hero.post.sub_range_list[2].input_range.set("")
    ev_hero.post.sub_range_list[3].input_range.set("")

    ev_hero.post.sub_range_list[0].x_box_value.set(0)
    ev_hero.post.sub_range_list[1].x_box_value.set(0)
    ev_hero.post.sub_range_list[2].x_box_value.set(0)
    ev_hero.post.sub_range_list[3].x_box_value.set(0)
    
    ev_villain1.post.sub_range_list[0].input_range.set("")
    ev_villain1.post.sub_range_list[1].input_range.set("")
    ev_villain1.post.sub_range_list[2].input_range.set("")
    ev_villain1.post.sub_range_list[3].input_range.set("")

    ev_villain1.post.sub_range_list[0].x_box_value.set(0)
    ev_villain1.post.sub_range_list[1].x_box_value.set(0)
    ev_villain1.post.sub_range_list[2].x_box_value.set(0)
    ev_villain1.post.sub_range_list[3].x_box_value.set(0)
    
    ev_villain2.post.sub_range_list[0].input_range.set("")
    ev_villain2.post.sub_range_list[1].input_range.set("")
    ev_villain2.post.sub_range_list[2].input_range.set("")
    ev_villain2.post.sub_range_list[3].input_range.set("")

    ev_villain2.post.sub_range_list[0].x_box_value.set(0)
    ev_villain2.post.sub_range_list[1].x_box_value.set(0)
    ev_villain2.post.sub_range_list[2].x_box_value.set(0)
    ev_villain2.post.sub_range_list[3].x_box_value.set(0)

def paste_hand():
    logging.info("Clipboard:\n {}".format(root.clipboard_get()))
    
def change_logging_status(checkbox_status):
    if checkbox_status:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
    return

# def disable_widgets(parent):
#     for child in parent.winfo_children():
#         child.state(["disabled"])
#     return

def ppt_task_consumer(queue):
    while True:
        function, *args = queue.get()
        if function == "EXIT":
            logging.info("KILL PPT Thread")
            break
        if args:
            logging.debug("Trying to execute the following PPT task: {0}".format(function))
            function(*args)
            logging.debug("Finished PPT task")
        else:
            logging.debug("Trying to execute the following PPT task: {0}.".format(function))
            function()
            logging.debug("Finished PPT task")
            
def set_ppt_board(street):
    ppt_client.board=""
    if parse_board(gi_board.get()):
        ppt_client.board=return_string(parse_board(gi_board.get()),street)
        
def expand_range(range_string, street):
    board=return_string(parse_board(gi_board.get()),street) if parse_board(gi_board.get()) else ""
    return parse_hand(range_string,board)


###
# MAIN CODE STARTS HERE (no seperate class / main function)
###


root=Tk()
root.title(TITLE)
#root.geometry(MAIN_GEOMETRY)

style = ttk.Style()
style.configure('.', font=(FONT_FAM, FONT_SIZE))
# style.configure('TButton', borderwidth=2)

mainframe=ttk.Frame(root, padding=FRAME_PADDING) # main frame containing everything except textoutput window on the right
mainframe.grid(column=0, row=0, sticky=(N, W, E, S))

textframe = ttk.Frame(root, padding=FRAME_PADDING)
textframe.grid(column=1, row=0, sticky=(N, W, E, S))
textframe.columnconfigure(0, weight=1)
textframe.rowconfigure(0, weight=1)

text_output = scrolledtext.ScrolledText(textframe, height=TEXT_OUTPUT_HEIGHT, width=TEXT_OUTPUT_WIDTH, font=(FONT_FAM_MONO,FONT_SIZE))
text_output.grid(column=0, row=0, sticky=(N,W,E,S))

# redir = RedirectText(text_output)
# sys.stdout = redir

logger_widget_handler=ScrolledTextLogger(text_output)
formatter = logging.Formatter('%(levelname)s - %(message)s')
logger_widget_handler.setFormatter(formatter)
logger = logging.getLogger()
logger.addHandler(logger_widget_handler)
logger.setLevel(logging.INFO)


general_info_frame=ttk.Frame(mainframe, padding=FRAME_PADDING) # frame above notebook
general_info_frame.grid(column=0, row=0, sticky=(N, W, E, S))

game_info_frame=ttk.Labelframe(general_info_frame, padding=GENERAL_SETTING_PADDING, text="General Settings")
game_info_frame.grid(column=0, row=0, sticky=(N, W, E, S), padx=PADX, pady=PADY)

range_distribution_frame=ttk.Labelframe(general_info_frame, padding=GENERAL_SETTING_PADDING, text="Range Distribution")
range_distribution_frame.grid(column=1, row=0, sticky=(N, W, E, S))


###
# Menue Code
###

root.option_add('*tearOff', FALSE)


menubar = Menu(root,font=(FONT_FAM,FONT_SIZE))
root.config(menu=menubar)

menu_file = Menu(menubar,font=(FONT_FAM,FONT_SIZE))
menu_edit = Menu(menubar,font=(FONT_FAM,FONT_SIZE))
menubar.add_cascade(menu=menu_file, label='File')
menubar.add_cascade(menu=menu_edit, label='Edit')

menu_file.add_command(label='Open Session', command=load_session)
menu_file.add_command(label='Save Session', command=save_session)
menu_file.add_command(label='Clear Session', command=clear_session)
# menu_file.add_command(label='Close', command=closeFile)

menu_edit.add_command(label='Paste HH',command=paste_hand)

###
# Game Info Code
###

# ttk.Label(game_info_frame,text="General Settings:").grid(column=0, row=0, columnspan=2, sticky=W, padx=PADX, pady=PADY)
ttk.Label(game_info_frame,text="Board: ").grid(column=0, row=1, sticky=W, padx=PADX, pady=PADY)
ttk.Label(game_info_frame,text="Dead: ").grid(column=0, row=2, sticky=W, padx=PADX, pady=PADY)
ttk.Label(game_info_frame,text="Debug: ").grid(column=0, row=3, sticky=W, padx=PADX, pady=PADY)
ttk.Label(game_info_frame,text="Game: ").grid(column=2, row=1, sticky=W, padx=PADX, pady=PADY)

# General Setting Variables

gi_board=StringVar()
gi_dead=StringVar()
gi_game=StringVar()
gi_debug=BooleanVar()

gi_game.set("omahahi")

ttk.Entry(game_info_frame,textvariable=gi_board,width=INPUT_LENGTH//3,font=(FONT_FAM,FONT_SIZE)).grid(column=1, row=1, sticky=W, padx=PADX, pady=PADY)
ttk.Entry(game_info_frame,textvariable=gi_dead,width=INPUT_LENGTH//3,font=(FONT_FAM,FONT_SIZE)).grid(column=1, row=2, sticky=W, padx=PADX, pady=PADY)
ttk.Checkbutton(game_info_frame, variable=gi_debug, onvalue=True, offvalue=False, command= lambda: change_logging_status(gi_debug.get())).grid(column=1, row=3, sticky=W, padx=PADX, pady=PADY)
gi_combo_box=ttk.Combobox(game_info_frame, textvariable=gi_game, values=('omahahi','omaha8', 'omahahi5', 'omaha85'),font=(FONT_FAM,FONT_SIZE),width=10,state='readonly').grid(column=3, row=1, sticky=W, padx=PADX, pady=PADY)


notebook_frame=ttk.Notebook(mainframe,padding=FRAME_PADDING)
notebook_frame.grid(column=0, row=1, sticky=(N, W, E, S))

range_builder_frame=ttk.Frame(notebook_frame,padding=FRAME_PADDING)
ev_calc_frame=ttk.Frame(notebook_frame,padding=FRAME_PADDING)

notebook_frame.add(range_builder_frame, text='Range Builder')
notebook_frame.add(ev_calc_frame, text='EV Calcs')


###
# Range Distribution Code
###

rd_start_range=StringVar()
rd_vs_range=StringVar()
rd_start_ranges_set=('Player 1 Flop','Player 2 Flop','Player 1 Turn','Player 2 Turn','Player 1 River','Player 2 River',
                     'Hero', 'Villain 1', 'Villain 2')
rd_start_range.set('Player 1 Flop')
rd_vs_range.set('Player 2 Flop')

ttk.Label(range_distribution_frame,text="Select Range: ").grid(column=0, row=0, sticky=W, padx=PADX, pady=PADY)
ttk.Label(range_distribution_frame,text=" vs: ").grid(column=2, row=0, sticky=W, padx=PADX, pady=PADY)
rd_range_combo_box=ttk.Combobox(range_distribution_frame, textvariable=rd_start_range, values=rd_start_ranges_set,font=(FONT_FAM,FONT_SIZE),width=15,state='readonly').grid(column=1, row=0, sticky=W, padx=PADX, pady=PADY)
rd_range_combo_box=ttk.Combobox(range_distribution_frame, textvariable=rd_vs_range, values=rd_start_ranges_set,font=(FONT_FAM,FONT_SIZE),width=15,state='readonly').grid(column=3, row=0, sticky=W, padx=PADX, pady=PADY)

rd_range_frame=ttk.Frame(range_distribution_frame,padding=FRAME_PADDING)
rd_range_frame.grid(column=0, columnspan=4, row=1, sticky=(N, W, E, S))

rd_range=Range(rd_range_frame,"Range",rd_start_range.get())
rd_eval_bu=ttk.Button(range_distribution_frame, text="EVAL RANGE", command = lambda: eval_range_distribution())
rd_eval_bu.grid(column=4, row=0, sticky=W,padx=BUTTON_PADX)
rd_eval_bu=ttk.Button(range_distribution_frame, text="TURN CARD", command = lambda: turn_card_calc())
rd_eval_bu.grid(column=5, row=0, sticky=W,padx=BUTTON_PADX)
rd_eval_bu=ttk.Button(range_distribution_frame, text="RIVER CARD", command = lambda: river_card_calc())
rd_eval_bu.grid(column=6, row=0, sticky=W,padx=BUTTON_PADX)
###
# Range Builder Code
###

# Frames

rb_player_1_frame=ttk.Frame(range_builder_frame,padding=PLAYER_FRAME_PADDING)
rb_player_1_frame.grid(column=0, row=0, sticky=(N, W, E, S))

rb_player_2_frame=ttk.Frame(range_builder_frame,padding=PLAYER_FRAME_PADDING)
rb_player_2_frame.grid(column=1, row=0, sticky=(N, W, E, S))

rb_p1_pre_frame=ttk.Frame(rb_player_1_frame,padding=FRAME_PADDING)
rb_p1_pre_frame.grid(column=0, row=0, sticky=(N, W, E, S))

rb_p1_flop_frame=ttk.Frame(rb_player_1_frame,padding=RANGE_FRAME_PADDING)
rb_p1_flop_frame.grid(column=0, row=1, sticky=(N, W, E, S))

rb_p1_turn_frame=ttk.Frame(rb_player_1_frame,padding=RANGE_FRAME_PADDING)
rb_p1_turn_frame.grid(column=0, row=2, sticky=(N, W, E, S))

rb_p1_river_frame=ttk.Frame(rb_player_1_frame,padding=RANGE_FRAME_PADDING)
rb_p1_river_frame.grid(column=0, row=3, sticky=(N, W, E, S))

rb_p1_calc_frame=ttk.Frame(rb_player_1_frame,padding=RANGE_FRAME_PADDING)
rb_p1_calc_frame.grid(column=0, row=4, sticky=(N, W, E, S))

rb_p2_pre_frame=ttk.Frame(rb_player_2_frame,padding=FRAME_PADDING)
rb_p2_pre_frame.grid(column=0, row=0, sticky=(N, W, E, S))

rb_p2_flop_frame=ttk.Frame(rb_player_2_frame,padding=RANGE_FRAME_PADDING)
rb_p2_flop_frame.grid(column=0, row=1, sticky=(N, W, E, S))

rb_p2_turn_frame=ttk.Frame(rb_player_2_frame,padding=RANGE_FRAME_PADDING)
rb_p2_turn_frame.grid(column=0, row=2, sticky=(N, W, E, S))

rb_p2_river_frame=ttk.Frame(rb_player_2_frame,padding=RANGE_FRAME_PADDING)
rb_p2_river_frame.grid(column=0, row=3, sticky=(N, W, E, S))

rb_p2_calc_frame=ttk.Frame(rb_player_2_frame,padding=RANGE_FRAME_PADDING)
rb_p2_calc_frame.grid(column=0, row=4, sticky=(N, W, E, S))


# Instances of range gui elements

rb_p1_pre=RangePreflop(rb_p1_pre_frame, "Player 1", PRE_INPUT_LENTH)
rb_p2_pre=RangePreflop(rb_p2_pre_frame, "Player 2", PRE_INPUT_LENTH)

rb_p1_flop=Range(rb_p1_flop_frame,"Flop")
rb_p2_flop=Range(rb_p2_flop_frame,"Flop")

rb_p1_turn=Range(rb_p1_turn_frame,"Turn")
rb_p2_turn=Range(rb_p2_turn_frame,"Turn")

rb_p1_river=Range(rb_p1_river_frame, "River")
rb_p2_river=Range(rb_p2_river_frame,"River")

# Calculate buttons in the last line

rb_p1_calc_flop_bu=ttk.Button(rb_p1_calc_frame, text="EVAL FLOP", command = lambda: eval_range(rb_p1_flop, rb_p2_flop, "flop"))
rb_p1_calc_turn_bu=ttk.Button(rb_p1_calc_frame, text="EVAL TURN", command = lambda: eval_range(rb_p1_turn, rb_p2_turn, "turn"))
rb_p1_calc_river_bu=ttk.Button(rb_p1_calc_frame, text="EVAL RIVER", command = lambda: eval_range(rb_p1_river, rb_p2_river, "river"))
rb_p1_calc_bu=ttk.Button(rb_p1_calc_frame, text="EVAL ALL", command = lambda: eval_player_1())

rb_p1_calc_flop_bu.grid(column=0, row=0, sticky=W,padx=BUTTON_PADX)
rb_p1_calc_turn_bu.grid(column=1, row=0, sticky=W,padx=BUTTON_PADX)
rb_p1_calc_river_bu.grid(column=2, row=0, sticky=W,padx=BUTTON_PADX)
rb_p1_calc_bu.grid(column=3, row=0, sticky=W,padx=BUTTON_PADX*5)

rb_p2_calc_flop_bu=ttk.Button(rb_p2_calc_frame, text="EVAL FLOP", command = lambda: eval_range(rb_p2_flop, rb_p1_flop,"flop"))
rb_p2_calc_turn_bu=ttk.Button(rb_p2_calc_frame, text="EVAL TURN", command = lambda: eval_range(rb_p2_turn, rb_p1_turn, "turn"))
rb_p2_calc_river_bu=ttk.Button(rb_p2_calc_frame, text="EVAL RIVER", command = lambda: eval_range(rb_p2_river, rb_p1_river, "river"))
rb_p2_calc_bu=ttk.Button(rb_p2_calc_frame, text="EVAL ALL", command = lambda: eval_player_2())

rb_p2_calc_flop_bu.grid(column=0, row=0, sticky=W,padx=BUTTON_PADX)
rb_p2_calc_turn_bu.grid(column=1, row=0, sticky=W,padx=BUTTON_PADX)
rb_p2_calc_river_bu.grid(column=2, row=0, sticky=W,padx=BUTTON_PADX)
rb_p2_calc_bu.grid(column=3, row=0, sticky=W,padx=BUTTON_PADX*5)

###
# EV Calc Code
###

ev_hero_frame=ttk.Frame(ev_calc_frame,padding=EV_PLAYER_FRAME_PADDING)
ev_hero_frame.grid(column=0, row=0, sticky=(N, W, E, S))
ev_villain1_frame=ttk.Frame(ev_calc_frame,padding=EV_PLAYER_FRAME_PADDING)
ev_villain1_frame.grid(column=0, row=1, sticky=(N, W, E, S))
ev_villain2_frame=ttk.Frame(ev_calc_frame,padding=EV_PLAYER_FRAME_PADDING)
ev_villain2_frame.grid(column=0, row=2, sticky=(N, W, E, S))

ev_hero=EvCalcPlayer(ev_hero_frame,"Hero")
ev_villain1=EvCalcPlayer(ev_villain1_frame,"Villain1")
ev_villain2=EvCalcPlayer(ev_villain2_frame,"Villain2")

ev_calc_notebook_frame=ttk.Notebook(ev_calc_frame,padding=FRAME_PADDING)
ev_calc_notebook_frame.grid(column=1, row=0, columnspan=2, rowspan=3, sticky=(N, W, E, S))

ev_bet_vs1_frame=ttk.Frame(ev_calc_notebook_frame,padding=FRAME_PADDING)
ev_bet_vs2_frame=ttk.Frame(ev_calc_notebook_frame,padding=FRAME_PADDING)
ev_4bet_frame=ttk.Frame(ev_calc_notebook_frame,padding=FRAME_PADDING)

ev_calc_notebook_frame.add(ev_bet_vs1_frame,text="BET vs 1")
ev_calc_notebook_frame.add(ev_bet_vs2_frame,text="BET vs 2")
ev_calc_notebook_frame.add(ev_4bet_frame,text="4 BET")

###
# Bet vs One Code
###

ev_bet_vs1_input_frame=ttk.Labelframe(ev_bet_vs1_frame, padding=GENERAL_SETTING_PADDING, text="Input Fields")
ev_bet_vs1_input_frame.grid(column=0, row=1, sticky=(N, W, E, S), padx=PADX, pady=PADY)

ev_bet_vs1_result_frame=ttk.Labelframe(ev_bet_vs1_frame, padding=GENERAL_SETTING_PADDING, text="Results")
ev_bet_vs1_result_frame.grid(column=0, row=2, sticky=(N, W, E, S), padx=PADX, pady=PADY)

ev_bet_vs1_info_frame=ttk.Labelframe(ev_bet_vs1_frame, padding=GENERAL_SETTING_PADDING, text="Infos")
ev_bet_vs1_info_frame.grid(column=0, row=0, sticky=(N, W, E, S), padx=PADX, pady=PADY)

ev_bet_vs1_result_str=StringVar()

ttk.Label(ev_bet_vs1_info_frame,text=BET_VS_1_INFO).grid(column=0, row=0, sticky=W, padx=PADX, pady=PADY)
ttk.Label(ev_bet_vs1_result_frame,textvariable=ev_bet_vs1_result_str).grid(column=0, row=0, sticky=W, padx=PADX, pady=PADY)

ev_bet_vs1_result_str.set(BET_VS_1_RESULT_STR)

ttk.Label(ev_bet_vs1_input_frame,text="Hero Hand: ").grid(column=0, row=0, sticky=W, padx=PADX, pady=PADY)
ttk.Label(ev_bet_vs1_input_frame,text="Potsize: ").grid(column=2, row=1, sticky=W, padx=PADX, pady=PADY)
ttk.Label(ev_bet_vs1_input_frame,text="Stacksize: ").grid(column=2, row=2, sticky=W, padx=PADX, pady=PADY)
ttk.Label(ev_bet_vs1_input_frame,text="Bet Size: ").grid(column=0, row=1, sticky=W, padx=PADX, pady=PADY)
ttk.Label(ev_bet_vs1_input_frame,text="Raise Size: ").grid(column=0, row=2, sticky=W, padx=PADX, pady=PADY)
ttk.Label(ev_bet_vs1_input_frame,text="Reraise Size: ").grid(column=0, row=3, sticky=W, padx=PADX, pady=PADY)
ttk.Label(ev_bet_vs1_input_frame,text="Street: ").grid(column=2, row=0, sticky=W, padx=PADX, pady=PADY)

ev_bet_vs1_stacksize=StringVar()
ev_bet_vs1_potsize=StringVar()
ev_bet_vs1_betsize=StringVar()
ev_bet_vs1_raisesize=StringVar()
ev_bet_vs1_reraisesize=StringVar()
ev_bet_vs1_hand=StringVar()
ev_bet_vs1_street=StringVar()

ev_bet_vs1_stacksize.set(STACKSIZE)
ev_bet_vs1_potsize.set(POTSIZE)
ev_bet_vs1_betsize.set(BETSIZE)
ev_bet_vs1_raisesize.set(RAISESIZE)
ev_bet_vs1_reraisesize.set(RERAISESIZE)
ev_bet_vs1_street.set(STREET)


ttk.Entry(ev_bet_vs1_input_frame,textvariable=ev_bet_vs1_hand,width=INPUT_LENGTH//3,font=(FONT_FAM,FONT_SIZE)).grid(column=1, row=0, sticky=W, padx=PADX, pady=PADY)
ttk.Entry(ev_bet_vs1_input_frame,textvariable=ev_bet_vs1_potsize,width=INPUT_LENGTH//3,font=(FONT_FAM,FONT_SIZE)).grid(column=3, row=1, sticky=W, padx=PADX, pady=PADY)
ttk.Entry(ev_bet_vs1_input_frame,textvariable=ev_bet_vs1_stacksize,width=INPUT_LENGTH//3,font=(FONT_FAM,FONT_SIZE)).grid(column=3, row=2, sticky=W, padx=PADX, pady=PADY)
ttk.Entry(ev_bet_vs1_input_frame,textvariable=ev_bet_vs1_betsize,width=INPUT_LENGTH//3,font=(FONT_FAM,FONT_SIZE)).grid(column=1, row=1, sticky=W, padx=PADX, pady=PADY)
ttk.Entry(ev_bet_vs1_input_frame,textvariable=ev_bet_vs1_raisesize,width=INPUT_LENGTH//3,font=(FONT_FAM,FONT_SIZE)).grid(column=1, row=2, sticky=W, padx=PADX, pady=PADY)
ttk.Entry(ev_bet_vs1_input_frame,textvariable=ev_bet_vs1_reraisesize,width=INPUT_LENGTH//3,font=(FONT_FAM,FONT_SIZE)).grid(column=1, row=3, sticky=W, padx=PADX, pady=PADY)
ttk.Combobox(ev_bet_vs1_input_frame, textvariable=ev_bet_vs1_street, values=('flop','turn','river'),font=(FONT_FAM,FONT_SIZE),width=10,state='readonly').grid(column=3, row=0, sticky=W, padx=PADX, pady=PADY)
ev_bet_vs_1_bu=ttk.Button(ev_bet_vs1_input_frame, text="GO!", command=bet_vs_1_calc)
ev_bet_vs_1_bu.grid(column=3, row=4, sticky=W,padx=BUTTON_PADX)
ev_rank_hand_bu=ttk.Button(ev_bet_vs1_input_frame, text="RANK Hand", command=rank_hand)
ev_rank_hand_bu.grid(column=5, row=3, sticky=W,padx=BUTTON_PADX)
ev_bet_vs_1_hero_plot_bu=ttk.Button(ev_bet_vs1_input_frame, text="Hero \'ships\'", command=hero_ship_plot)
ev_bet_vs_1_hero_plot_bu.grid(column=4, row=4, sticky=W,padx=BUTTON_PADX)
ev_bet_vs_1_villain_plot_bu=ttk.Button(ev_bet_vs1_input_frame, text="Villain \'ships\'", command=villain_ship_plot)
ev_bet_vs_1_villain_plot_bu.grid(column=5, row=4, sticky=W,padx=BUTTON_PADX)

###
# Bet vs two Code
###

ev_bet_vs2_input_frame=ttk.Labelframe(ev_bet_vs2_frame, padding=GENERAL_SETTING_PADDING, text="Input Fields")
ev_bet_vs2_input_frame.grid(column=0, row=1, sticky=(N, W, E, S), padx=PADX, pady=PADY)

ev_bet_vs2_result_frame=ttk.Labelframe(ev_bet_vs2_frame, padding=GENERAL_SETTING_PADDING, text="Results")
ev_bet_vs2_result_frame.grid(column=0, row=2, sticky=(N, W, E, S), padx=PADX, pady=PADY)

ev_bet_vs2_info_frame=ttk.Labelframe(ev_bet_vs2_frame, padding=GENERAL_SETTING_PADDING, text="Infos")
ev_bet_vs2_info_frame.grid(column=0, row=0, sticky=(N, W, E, S), padx=PADX, pady=PADY)

ev_bet_vs2_result_str=StringVar()

ttk.Label(ev_bet_vs2_info_frame,text=BET_VS_2_INFO).grid(column=0, row=0, sticky=W, padx=PADX, pady=PADY)
ttk.Label(ev_bet_vs2_result_frame,textvariable=ev_bet_vs2_result_str).grid(column=0, row=0, sticky=W, padx=PADX, pady=PADY)

ev_bet_vs2_result_str.set(BET_VS_2_RESULT_STR)

ttk.Label(ev_bet_vs2_input_frame,text="Hero Hand: ").grid(column=0, row=0, sticky=W, padx=PADX, pady=PADY)
ttk.Label(ev_bet_vs2_input_frame,text="Potsize: ").grid(column=2, row=1, sticky=W, padx=PADX, pady=PADY)
ttk.Label(ev_bet_vs2_input_frame,text="Stacksize vs 1: ").grid(column=2, row=2, sticky=W, padx=PADX, pady=PADY)
ttk.Label(ev_bet_vs2_input_frame,text="Stacksize vs 2: ").grid(column=2, row=3, sticky=W, padx=PADX, pady=PADY)
ttk.Label(ev_bet_vs2_input_frame,text="Bet Size: ").grid(column=0, row=1, sticky=W, padx=PADX, pady=PADY)
ttk.Label(ev_bet_vs2_input_frame,text="Raise Size: ").grid(column=0, row=2, sticky=W, padx=PADX, pady=PADY)
ttk.Label(ev_bet_vs2_input_frame,text="Reraise Size: ").grid(column=0, row=3, sticky=W, padx=PADX, pady=PADY)
ttk.Label(ev_bet_vs2_input_frame,text="Street: ").grid(column=2, row=0, sticky=W, padx=PADX, pady=PADY)

ev_bet_vs2_stacksize1=StringVar()
ev_bet_vs2_stacksize2=StringVar()
ev_bet_vs2_potsize=StringVar()
ev_bet_vs2_betsize=StringVar()
ev_bet_vs2_raisesize=StringVar()
ev_bet_vs2_reraisesize=StringVar()
ev_bet_vs2_hand=StringVar()
ev_bet_vs2_street=StringVar()

ev_bet_vs2_stacksize1.set(STACKSIZE)
ev_bet_vs2_stacksize2.set(STACKSIZE)
ev_bet_vs2_potsize.set(POTSIZE)
ev_bet_vs2_betsize.set(BETSIZE)
ev_bet_vs2_raisesize.set(RAISESIZE)
ev_bet_vs2_reraisesize.set(RERAISESIZE)
ev_bet_vs2_street.set(STREET)


ttk.Entry(ev_bet_vs2_input_frame,textvariable=ev_bet_vs2_hand,width=INPUT_LENGTH//3,font=(FONT_FAM,FONT_SIZE)).grid(column=1, row=0, sticky=W, padx=PADX, pady=PADY)
ttk.Entry(ev_bet_vs2_input_frame,textvariable=ev_bet_vs2_potsize,width=INPUT_LENGTH//3,font=(FONT_FAM,FONT_SIZE)).grid(column=3, row=1, sticky=W, padx=PADX, pady=PADY)
ttk.Entry(ev_bet_vs2_input_frame,textvariable=ev_bet_vs2_stacksize1,width=INPUT_LENGTH//3,font=(FONT_FAM,FONT_SIZE)).grid(column=3, row=2, sticky=W, padx=PADX, pady=PADY)
ttk.Entry(ev_bet_vs2_input_frame,textvariable=ev_bet_vs2_stacksize2,width=INPUT_LENGTH//3,font=(FONT_FAM,FONT_SIZE)).grid(column=3, row=3, sticky=W, padx=PADX, pady=PADY)
ttk.Entry(ev_bet_vs2_input_frame,textvariable=ev_bet_vs2_betsize,width=INPUT_LENGTH//3,font=(FONT_FAM,FONT_SIZE)).grid(column=1, row=1, sticky=W, padx=PADX, pady=PADY)
ttk.Entry(ev_bet_vs2_input_frame,textvariable=ev_bet_vs2_raisesize,width=INPUT_LENGTH//3,font=(FONT_FAM,FONT_SIZE)).grid(column=1, row=2, sticky=W, padx=PADX, pady=PADY)
ttk.Entry(ev_bet_vs2_input_frame,textvariable=ev_bet_vs2_reraisesize,width=INPUT_LENGTH//3,font=(FONT_FAM,FONT_SIZE)).grid(column=1, row=3, sticky=W, padx=PADX, pady=PADY)
ttk.Combobox(ev_bet_vs2_input_frame, textvariable=ev_bet_vs2_street, values=('flop','turn','river'),font=(FONT_FAM,FONT_SIZE),width=10,state='readonly').grid(column=3, row=0, sticky=W, padx=PADX, pady=PADY)
ev_bet_vs_2_bu=ttk.Button(ev_bet_vs2_input_frame, text="GO!", command=bet_vs_2_calc)
ev_bet_vs_2_bu.grid(column=3, row=4, sticky=W,padx=BUTTON_PADX)

###
# 4bet Code
###


ev_4bet_input_frame=ttk.Labelframe(ev_4bet_frame, padding=GENERAL_SETTING_PADDING, text="Input Fields")
ev_4bet_input_frame.grid(column=0, row=1, sticky=(N, W, E, S), padx=PADX, pady=PADY)

ev_4bet_result_frame=ttk.Labelframe(ev_4bet_frame, padding=GENERAL_SETTING_PADDING, text="Results")
ev_4bet_result_frame.grid(column=0, row=2, sticky=(N, W, E, S), padx=PADX, pady=PADY)

ev_4bet_info_frame=ttk.Labelframe(ev_4bet_frame, padding=GENERAL_SETTING_PADDING, text="Infos")
ev_4bet_info_frame.grid(column=0, row=0, sticky=(N, W, E, S), padx=PADX, pady=PADY)

ev_4bet_result_str=StringVar()

ttk.Label(ev_4bet_info_frame,text=BET4_INFO).grid(column=0, row=0, sticky=W, padx=PADX, pady=PADY)
ttk.Label(ev_4bet_result_frame,textvariable=ev_4bet_result_str).grid(column=0, row=0, sticky=W, padx=PADX, pady=PADY)

ev_4bet_result_str.set(BET4_RESULT)

ttk.Label(ev_4bet_input_frame,text="Hero Hand: ").grid(column=0, row=0, sticky=W, padx=PADX, pady=PADY)
ttk.Label(ev_4bet_input_frame,text="Open: ").grid(column=0, row=1, sticky=W, padx=PADX, pady=PADY)
ttk.Label(ev_4bet_input_frame,text="3-bet size: ").grid(column=0, row=2, sticky=W, padx=PADX, pady=PADY)
ttk.Label(ev_4bet_input_frame,text="Potsize (before 4b): ").grid(column=2, row=1, sticky=W, padx=PADX, pady=PADY)
ttk.Label(ev_4bet_input_frame,text="Overall stacksize: ").grid(column=2, row=2, sticky=W, padx=PADX, pady=PADY)


ev_4bet_stacksize=StringVar()
ev_4bet_potsize=StringVar()
ev_4bet_opensize=StringVar()
ev_4bet_3bsize=StringVar()
ev_4bet_hand=StringVar()


ev_4bet_stacksize.set(BET4_STACK)
ev_4bet_potsize.set(BET4_POT)
ev_4bet_opensize.set(BET4_OPEN)
ev_4bet_3bsize.set(BET4_3BET)


ttk.Entry(ev_4bet_input_frame,textvariable=ev_4bet_hand,width=INPUT_LENGTH//3,font=(FONT_FAM,FONT_SIZE)).grid(column=1, row=0, sticky=W, padx=PADX, pady=PADY)
ttk.Entry(ev_4bet_input_frame,textvariable=ev_4bet_opensize,width=INPUT_LENGTH//3,font=(FONT_FAM,FONT_SIZE)).grid(column=1, row=1, sticky=W, padx=PADX, pady=PADY)
ttk.Entry(ev_4bet_input_frame,textvariable=ev_4bet_3bsize,width=INPUT_LENGTH//3,font=(FONT_FAM,FONT_SIZE)).grid(column=1, row=2, sticky=W, padx=PADX, pady=PADY)
ttk.Entry(ev_4bet_input_frame,textvariable=ev_4bet_potsize,width=INPUT_LENGTH//3,font=(FONT_FAM,FONT_SIZE)).grid(column=3, row=1, sticky=W, padx=PADX, pady=PADY)
ttk.Entry(ev_4bet_input_frame,textvariable=ev_4bet_stacksize,width=INPUT_LENGTH//3,font=(FONT_FAM,FONT_SIZE)).grid(column=3, row=2, sticky=W, padx=PADX, pady=PADY)
ev_4bet_bu=ttk.Button(ev_4bet_input_frame, text="4-bet this nice hand!", command=do_4bet_calc)
ev_4bet_bu.grid(column=1, row=4, sticky=W,padx=BUTTON_PADX)
ev_call_4bet_bu=ttk.Button(ev_4bet_input_frame, text="Call 4-bet and suck Aces!", command=call_4bet_calc)
ev_call_4bet_bu.grid(column=3, row=4, sticky=W,padx=BUTTON_PADX)


###
# PPT Worker Thread...push all tasks to ppt_queue
###

ppt_client=OddsOracleServer()
ppt_queue=Queue()
ppt_thread=threading.Thread(target=ppt_task_consumer, args=(ppt_queue,))
ppt_thread.setDaemon(True)
ppt_thread.start()

ppt_queue.put((ppt_client.start_ppt,)) # start PPT Server

root.mainloop()
# main_gui.py ends here
