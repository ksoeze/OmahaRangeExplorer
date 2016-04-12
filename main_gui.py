#!/usr/bin/env python3
# main_gui.py --- 
# 
# Filename: main_gui.py
# Description: 
# Author: Johann Ertl
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
# 
#

from tkinter import *
from tkinter import ttk
#from tkinter import font
from tkinter import scrolledtext
from tkinter import messagebox

from utils import *
from gui_elements import *
from ppt import OddsOracleServer
from board import parse_board
from board import return_string
from hand import parse_hand
#from hand import *

from queue import Queue
import threading
import time

import logging

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

    # set game dead etc
    ppt_client.game=gi_game.get()
    ppt_client.dead=gi_dead.get()
    return

def calc_ppt_set_value(range_1, range_2):
    villain_range=range_2.get_start_range()
    villain_selected_range=range_2.get_selected_range()

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
    logging.info("Villain start range: {0} \n".format(villain_range))
    
    if hero_range:
        equity=ppt_client.equity_query(hero_range,villain_range)
        range_1.set_range_equity(equity)
        logging.info("Equity is {0:.1f} for hero overall range: {1} \n".format(equity,hero_range))
    else: range_1.set_range_equity(0)
    if hero_subrange_0:
        frequency=ppt_client.in_range_query(hero_range,villain_range,hero_subrange_0)
        range_1.set_freq(0,frequency)
        logging.info("Frequency is {0:.1f} for hero sub range 1: {1}".format(frequency,hero_subrange_0))
        equity=ppt_client.equity_query(hero_subrange_0,villain_selected_range)
        range_1.set_equity(0,equity)
        logging.info("Equity is {0:.1f} for hero sub range 1: {1} \n".format(equity,hero_subrange_0))
    else:
        range_1.set_freq(0,0)
        range_1.set_equity(0,0)
    if hero_subrange_1:
        frequency=ppt_client.in_range_query(hero_range,villain_range,hero_subrange_1)
        logging.info("Frequency is {0:.1f} for hero sub range 2: {1}".format(frequency,hero_subrange_1))
        range_1.set_freq(1,frequency)
        equity=ppt_client.equity_query(hero_subrange_1,villain_selected_range)
        logging.info("Equity is {0:.1f} for hero sub range 2: {1}\n".format(equity,hero_subrange_1))
        range_1.set_equity(1,equity)
    else:
        range_1.set_freq(1,0)
        range_1.set_equity(1,0)        
    if hero_subrange_2:
        frequency=ppt_client.in_range_query(hero_range,villain_range,hero_subrange_2)
        logging.info("Frequency is {0:.1f} for hero sub range 3: {1}".format(frequency,hero_subrange_2))
        range_1.set_freq(2,frequency)
        equity=ppt_client.equity_query(hero_subrange_2,villain_selected_range)
        logging.info("Equity is {0:.1f} for hero sub range 3: {1}\n".format(equity,hero_subrange_2))
        range_1.set_equity(2,equity)
    else:
        range_1.set_freq(2,0)
        range_1.set_equity(2,0)        
    if hero_subrange_3:
        frequency=ppt_client.in_range_query(hero_range,villain_range,hero_subrange_3)
        logging.info("Frequency is {0:.1f} for hero sub range 4: {1}".format(frequency,hero_subrange_3))
        range_1.set_freq(3,frequency)
        equity=ppt_client.equity_query(hero_subrange_3,villain_selected_range)
        logging.info("Equity is {0:.1f} for hero sub range 4: {1}\n".format(equity,hero_subrange_3))
        range_1.set_equity(3,equity)
    else:
        range_1.set_freq(3,0)
        range_1.set_equity(3,0)       
    if hero_selected_range:
        frequency=ppt_client.in_range_query(hero_range,villain_range,hero_selected_range)
        logging.info("Frequency is {0:.1f} for hero selected range: {1}".format(frequency,hero_selected_range))
        range_1.set_summary_freq(frequency)        
        equity=ppt_client.equity_query(hero_selected_range,villain_selected_range)
        logging.info("Equity is {0:.1f} for hero selected range: {1}\n".format(equity,hero_selected_range))
        range_1.set_summary_equity(equity)
    else:
        range_1.set_summary_freq(0)
        range_1.set_summary_equity(0)

    logging.info("Finished Calculation: {0}".format(ppt_client.board))
    logging.info(DOTS)

    
def eval_range(range_1, range_2, street):
    # takes 2 Range elements and sets all frequency and equities for range_1 vs selected range 2
    update_ranges()

    ppt_queue.put((set_ppt_board,street)) # set start board...push to ppt queue for right timing

#    if parse_board(gi_board.get()): # ignore empty/non valid board
#        ppt_client.board=return_string(parse_board(gi_board.get()),street)
    
    ppt_queue.put((calc_ppt_set_value,range_1,range_2))
    return



def eval_player_1():
    eval_range(rb_p1_flop, rb_p2_flop, "flop")
    eval_range(rb_p1_turn, rb_p2_turn, "turn")
    eval_range(rb_p1_river, rb_p2_river, "river")
    
def eval_player_2():
    eval_range(rb_p2_flop, rb_p1_flop,"flop")
    eval_range(rb_p2_turn, rb_p1_turn, "turn")
    eval_range(rb_p2_river, rb_p1_river, "river")
    
###
# Equity Calcs Functions
###


###
# General Functions
###

def change_logging_status(checkbox_status):
    if checkbox_status:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
    return

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
    if parse_board(gi_board.get()): # ignore empty/non valid board
        ppt_client.board=return_string(parse_board(gi_board.get()),street)
        
def expand_range(range_string, street):
    board=return_string(parse_board(gi_board.get()),street) if parse_board(gi_board.get()) else []
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

text_output = scrolledtext.ScrolledText(textframe, height=TEXT_OUTPUT_HEIGHT, width=TEXT_OUTPUT_WIDTH, font=(FONT_FAM,FONT_SIZE))
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

range_distribution_frame=ttk.Frame(general_info_frame, padding=FRAME_PADDING)
range_distribution_frame.grid(column=1, row=0, sticky=(N, W, E, S))

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
gi_combo_box=ttk.Combobox(game_info_frame, textvariable=gi_game, values=('omahahi'),font=(FONT_FAM,FONT_SIZE),width=10,state='readonly').grid(column=3, row=1, sticky=W, padx=PADX, pady=PADY)


notebook_frame=ttk.Notebook(mainframe,padding=FRAME_PADDING)
notebook_frame.grid(column=0, row=1, sticky=(N, W, E, S))

range_builder_frame=ttk.Frame(notebook_frame,padding=FRAME_PADDING)
ev_calc_frame=ttk.Frame(notebook_frame,padding=FRAME_PADDING)

notebook_frame.add(range_builder_frame, text='Range Builder')
notebook_frame.add(ev_calc_frame, text='EV Calcs')

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
rb_p1_calc_bu=ttk.Button(rb_p1_calc_frame, text="EVAL ALL", command = lambda: eval_player_1()) # find good idea to call same function for player 1 and player 2

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
# PPT Worker Thread...push all tasks to ppt_queue
###

ppt_client=OddsOracleServer()
ppt_queue=Queue()
ppt_thread=threading.Thread(target=ppt_task_consumer, args=(ppt_queue,))
ppt_thread.setDaemon(True)
ppt_thread.start()

ppt_queue.put((ppt_client.start_ppt,)) # start PPT Server

#root.bind('<Return>', calculate)
#root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()

# 
# main_gui.py ends here
