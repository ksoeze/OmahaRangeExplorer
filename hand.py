#!/usr/bin/env python3
# hand.py --- 
# 
# Filename: hand.py
# Description: 
# Author: Johann Ertl
# Maintainer: 
# Created: Mon Mar 14 17:50:36 2016 
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
# FIXME: Straight flush not included yet
# FIXME: Hand board Intersections returns are not sorted...2Q instead of Q2...problem with compare?
# 

# Change Log:
# 
# 
# 
# 

# Code:

from board import *
import re
import logging

def replace_macros(hand,macro_file):
    if '$' not in hand:
        return hand
    macro_file.readline() # ignore first line
    for line in macro_file:
        macro='$'+line[0:line.index(",")]
        line=line[line.index("\"")+1:]
        replace_range=line[0:line.index("\"")]
#        if macro in hand:
#            print(macro + "       " + replace_range)
        hand=hand.replace(macro,'('+replace_range+')')
#    if '$' in hand:
#        logging.error("Could not resolve all macros in hand:\n {0}".format(hand))
    return hand

def parse_hand(hand,board_string):
    board = parse_board(board_string)

    # macros working with ppt server??
    # try:
    #     macro_file=open(MACRO_FILE_LOCATION)
    # except:
    #     logging.error("Cannot open MACRO file")
    # else:
    #     hand = replace_macros(hand,macro_file)
    #     macro_file.close()

    hand = replace_strings(hand,board)
    return hand

def replace_strings(hand,board):
    """
    returns string with all + expressions replaced
    """
    ranks=return_ranks(board)
    ranks_no_count=set(ranks)
    suits=return_suits(board)
    flushes=return_flushes(board)
    straights=return_straights(ranks)
    fulls_or_better=return_fulls_or_better(ranks)
    hand_board_int=hand_board_intersections(ranks)
    str_draws=return_straight_draws(ranks)
    kickers=return_kicker(ranks)
    flush_suit=[]
    if flushes:
        flush_suit= flush_suit + [flushes[0][1:]]

    match_expr=re.compile('['+''.join(RANKS)+']'+'{3,4}'+'\+') #start with longest possible expressions == 3, 4 card wraps
    hand_sections=match_expr.findall(hand)

    if hand_sections:
        str_draws=return_straight_draws(ranks)
        for x in hand_sections:
            compare_x = ''.join(sorted(x[:-1], key=lambda x:RANK_ORDER[x], reverse=True))
            if compare_x in str_draws:
                replace_hands=str_draws[0:str_draws.index(compare_x)+1] # all better draws including written hand
                hand=hand.replace(x,range_string(replace_hands))
    
    match_expr=re.compile('['+''.join(RANKS)+']'+'['+''.join(SUITS)+']'+'{1,2}'+'\+') #flush flushdraw or blocker
    hand_sections=match_expr.findall(hand)

    if hand_sections:
       for x in hand_sections:
           compare_x=x[0:-1]
           if len(compare_x) == 2: # can only be blocker...todo exclude flushes? add !suit suit
               flush_blocker=return_flush_blocker(board)    
               if compare_x in flush_blocker:
                   replace_hands=flush_blocker[0:flush_blocker.index(compare_x)+1]
                   hand=hand.replace(x,range_string(replace_hands))
           else: # flush or flushdraw
               if flushes:
                   flushes=return_flushes(board)
                   if compare_x in flushes:
                     replace_hands=fulls_or_better + flushes[0:flushes.index(compare_x)+1]
                     hand=hand.replace(x,range_string(replace_hands))                     
                   else:
                       flush_drw=return_flushdraws(board,compare_x[-1])
                       if flush_drw:
                           replace_hands=flush_drw[0:flush_drw.index(compare_x)+1]
                           hand=hand.replace(x,range_string(replace_hands))                            

    match_expr=re.compile('['+''.join(RANKS)+']'+'{2}'+'\+') #straights, str draws or hand board intersections
    hand_sections=match_expr.findall(hand)
    
    if hand_sections:
        for x in hand_sections:
            compare_x=''.join(sorted(x[:-1], key=lambda x:RANK_ORDER[x], reverse=True))
            
            if compare_x in fulls_or_better:
                replace_hands=fulls_or_better[0:fulls_or_better.index(compare_x)+1]
                hand=hand.replace(x,range_string(replace_hands))
            elif compare_x in straights:
                replace_hands=fulls_or_better+flush_suit+straights[0:straights(compare_x)+1]
                hand=hand.replace(x,range_string(replace_hands))
            elif compare_x in str_draws:
                replace_hands=str_draws[0:str_draws.index(compare_x)+1]
                hand=hand.replace(x,range_string(replace_hands))
            elif compare_x in hand_board_int:
                replace_hands=flush_suit+straights+hand_board_int[0:hand_board_int.index(compare_x)+1]
                hand=hand.replace(x,range_string(replace_hands))
            elif x[1] in hand_board_int: # pair + kicker? 
                replace_hands=hand_board_int[0:hand_board_int.index(x[1])]
                better_kickers=kickers[0:kickers.index(x[0])+1]
                replace_hands=flush_suit+straights+replace_hands+[k+x[1] for k in better_kickers]
                hand=hand.replace(x,range_string(replace_hands))               

    match_expr=re.compile('['+''.join(RANKS)+']'+'{1}'+'\+') #one pair or better   
    hand_sections=match_expr.findall(hand)

    if hand_sections:
        for x in hand_sections:
            compare_x=x[:-1]
            if compare_x in hand_board_int:
                replace_hands=hand_board_int[0:hand_board_int.index(compare_x)+1]
                hand=hand.replace(x,range_string(replace_hands))

    if '+' in hand:
       logging.error("Could not resolve one or more + expressions in hand:\n{0}".format(hand))

    return hand

def range_string(hand_range):
    """
    takes list of hands and returns string in form of (hand1, hand2, hand3 ...)
    delets useless hands from hand range list ( for example KK if K is also in the range)
    """
    hand_range_compact=[]
    for x in hand_range:
        if not any([r in x for r in hand_range if r!=x]):
            hand_range_compact.append(x)

    hand_string='('
    for x in hand_range_compact:
        hand_string=hand_string+x+', '
    hand_string=hand_string[0:-2] + ')'
    
    return hand_string

# def find_ppt_hand(string,board):
#     """
#      takes string before a + sign in order to expand it and returns full range as list
#     """
#     hand= INVALID_CHAR*5+string # in order to not index empty string 
#     ranks=return_ranks(board)
#     suits=return_suits(board)
    
#     if hand[-1] == INVALID_CHAR: return []

def test():
    hand_string="$4B2:(A4+,Jss+)"
    board_string="Kh2s3s"
    sample_board=parse_board(board_string)
    print(hand_string)
    print(parse_hand(hand_string,board_string))

if __name__ == '__main__':
    import timeit
    if DEBUG:
        test()



# 
# hand.py ends here
