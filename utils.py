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
LOW_RANK_ORDER = {'K':12, 'Q':11, 'J':10, 'T':9, '9':8, '8':7, '7':6, '6':5, '5':4, '4':3, '3':2, '2':1,'A':0}
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

PPT_TRIAL=100000 # omaha ranger: 300000 and 50000 for evaluation
PPT_RANK_QUERY_TRIAL=10000
PPT_IN_RANGE_TRIAL=50000
PPT_NEXT_CARD_EQ_TRIAL=100000
PPT_MAX_SEC=10
PPT_THREAD_CNT=8
PPT_LOCATION="/home/johann/usr/PPTOddsOracle/ui_jar/"
PPT_NUM_DIGETS=4 # whole length including decimal point (minimal length = 0.00)
PPT_GAME="omahahi" # std game
PPT_SYNTAX='Generic'

# ev calcs defaults

STACKSIZE=97.0
POTSIZE=6.5
BETSIZE=4
RAISESIZE=14
RERAISESIZE=35
STREET="flop"

BET4_STACK=100
BET4_OPEN=3
BET4_3BET=10
BET4_POT=14

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
EV_PLAYER_FRAME_PADDING="10 10 3 3"
GENERAL_SETTING_PADDING="10 10 10 10"
FONT_SIZE=9 # std font size
FONT_FAM='Helvetica'
FONT_FAM_MONO='monospace'
TITLE="OMAHA RANGE CRUSHER"
MAIN_GEOMETRY="2200x2000"
TEXT_OUTPUT_HEIGHT=60
TEXT_OUTPUT_WIDTH=140
DOTS="-----------------------------------------------------------"

BET_VS_1_INFO=("Hero subranges are ignored for EV calcs...only Hero Prerange + Hand and Villain Ranges\n"
               "Enter at least valid ranges for:\n"
               "Hero Pre, Villain Pre, Villain Subrange 1,2,4, Hero Hand\n"
               "Villain Range 1 is his value raise range; Range 2: call; Range 3: bluffraise; Range 4: fold (enter *)\n"
               "Selections are ignored for EV calcs...but freq and eq results next to ranges works as in range builder\n"
               "Betsizes are not checked for validity...\n"
               "For AI spots just enter bet or raise or reraisesize == stacksize")

BET_VS_1_RESULT_STR=("Some guidelines:\n"
                     "Perfect polarised range when betting pot:\n"
                     "Value:Bluff flop ~ 1:2.37 \n"
                     "Value:Bluff turn ~ 1:1.25\n"
                     "Value:Bluff river ~ 2:1 \n"
                     "Alpha is % a bluff has to work for EV = 0 with 0% equity\n"
                     "1-Alpha is % a player should defend vs perfectly polarised range\n"
                     "Realisation factors are hard to estimate...\n"
                     "Would guess R_vs_raise < R_vs_range < R_vs_call against most players in many situations\n"
                     "Nutty draws...fd/gs etc can often realise more than their equity\n"
                     "Weak made hands often realise a lot less than their equity\n"
                     "Arguments for bet: \n"
                     "- dont get raised off equity often (low raise feq + low equity vs raise range)\n"
                     "- equity vs call is not much lower than equity vs range\n"
                     "- equity vs folding range is low\n"
                     "Defend vs Raise asumes villain plays on range 1 and folds range 3"
                     "...")

BET_VS_2_INFO=("Hero subranges are ignored for EV calcs...only Hero Prerange + Hand and Villain Ranges\n"
               "Enter at least valid ranges for:\n"
               "Hero Pre, Villain1/2 Pre, Villain1 Subrange 1,2,4, Villain2 Subrange 1,2,4,  Hero Hand\n"
               "Villain Range 1 is the value raise range; Range 2: call; Range 3: bluffraise; Range 4: fold (enter *)\n"
               "Villain 2 acts after villain 1...Villain 2 ships range 1 4 value also when villain 1 calls/raises (unrealistic but 3 way ai are rare)\n"
               "Selections are ignored for EV calcs...but freq and eq results next to ranges works as in range builder\n"
               "(eq and freq are calculated vs selection of both other players)\n"
               "Betsizes are not checked for validity...\n")

BET_VS_2_RESULT_STR=("Some guidelines:\n"
                     "\n"
                     "\n"
                     "\n"
                     "\n"
                     "\n"
                     "\n"
                     "\n"
                     "\n"
                     "\n"
                     "\n"
                     "\n"
                     "\n"
                     "\n"
                     "\n"
                     "...")
BET4_INFO=("Enter Hand in question\n\n"
           "If thinking about 4bet:\n"
           "Enter your starting stack with V1; your open/dead amount; V1 3bet size; total potsize after 3bet\n"
           "Takes V1 pre range as start (=3bet range); 5bet subrange 1; call rest and stacks off if equity > pot odds vs your hand\n"
           "(not accurate in real game but vs AA is very slow calc)\n\n"
           "If thinking about call 4bet:\n"
           "Enter your starting stack with V1; your 3bet size; total potsize after 3bet\n"
           "Takes V1 pre range as start (=4bet range); asumes perfect play from us vs V1 on the flop\n\n"
           "Betsizes are not checked for validity...\n")

BET4_RESULT=("\n"
             "...see logging output\n")
