#!/usr/bin/env python


#poker constants

RANKS = list("AKQJT98765432")
SUITS = list("cdhs")
CARDS = list(rank + suit for suit in SUITS for rank in RANKS)
RANDOM_RANKS = list("RON")
RANDOM_SUITS = list("wxyz")
RANDOM_CARD = 'Bb'
RANDOM_CARDS = list(rank + suit for suit in RANDOM_SUITS for rank in RANDOM_RANKS)
RANDOM_BOARD = [RANDOM_CARD]*5
RANK_ORDER = {'A':12, 'K':11, 'Q':10, 'J':9, 'T':8, '9':7, '8':6, '7':5, '6':4, '5':3, '4':2, '3':1, '2':0}
LOW_CARDS = list("A2345678")
STRAIGHTS=[list("AKQJT"),list("KQJT9"),list("QJT98"),list("JT987"),list("T9876"),list("98765"),list("87654"),list("76543"),list("65432"),list("5432A")]
INVALID_CHAR='#'


# developement constants

DEBUG = True
MACRO_FILE_LOCATION="/home/johann/Documents/poker/oddsOracleMacros.csv"

PPT_SERVER_PORT="http://localhost:37890"
TEST_QUERY=("select avg(equity(hero, turn)) as EQUITY \n"
    "from game='omahahi', \n"
    "syntax='Generic', \n"
    "hero='AA', \n" 
    "villain='KdQsTcJd', \n" 
    "board='Kc8s5s' \n")

PPT_TRIAL=300000 # omaha ranger: 300000 and 50000 for evaluation
PPT_MAX_SEC=10
PPT_THREAD_CNT=8
PPT_LOCATION="/home/johann/usr/PPTOddsOracle/ui_jar/"
PPT_NUM_DIGETS=4 # whole length including decimal point (minimal length = 0.00)
PPT_GAME="omahahi" # std game
PPT_SYNTAX='Generic'


# gui constants

INPUT_LENGTH=50 # number of chars for standard range input line
PRE_INPUT_LENTH=40
START_RANGE_WIDTH=47 # number of chars reserved for start range...adjust if Freq and Equity Description arent alligned
SPACES_BEFORE_SUMMARY_LINE=42 
PADX=5 # std padding x
PADY=5 # std padding y
BUTTON_PADX=5
FRAME_PADDING="3 3 3 3" # std padding for small frames
RANGE_FRAME_PADDING="3 50 3 3"
PLAYER_FRAME_PADDING="3 3 180 3"
GENERAL_SETTING_PADDING="10 10 10 10"
FONT_SIZE=9 # std font size
FONT_FAM='Helvetica'
TITLE="OMAHA RANGE CRUSHER"
MAIN_GEOMETRY="2200x2000"
TEXT_OUTPUT_HEIGHT=60
TEXT_OUTPUT_WIDTH=150
