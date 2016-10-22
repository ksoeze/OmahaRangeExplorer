#!/usr/bin/env python3
# board.py --- 
# 
# Filename: board.py
# Description: 
# Author: Johann Ertl
# Maintainer: 
# Created: Don Mar 17 10:47:22 2016 (+0100)
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
# Ignores 2nd 2 pair on paired board: Q5 is not in list on AQ544 board 
# 
# 

# Change Log:
# 

# Code:

from utils import *
from itertools import combinations
import random

def parse_board(board=''):
    current_board=[]
    parsing_board=board

    #check if valid length and known chars
    if len(parsing_board)==0 or len(parsing_board)>10:
        return current_board
    for x in parsing_board:
        if x in RANKS or x in SUITS or x in RANDOM_RANKS or x in RANDOM_SUITS:
            continue
        else:
            return current_board
    #parse board
    for x in RANDOM_BOARD:
        if len(parsing_board) == 0:
            current_board.append(x)
            continue
        if parsing_board[0] in RANKS or parsing_board[0] in RANDOM_RANKS:
            x = x.replace(RANDOM_CARD[0],parsing_board[0])
            parsing_board=parsing_board[1:]
        if len(parsing_board) == 0:
            current_board.append(x)
            continue           
        if parsing_board[0] in SUITS or parsing_board[0] in RANDOM_SUITS:
            x = x.replace(RANDOM_CARD[1],parsing_board[0])
            parsing_board=parsing_board[1:]
        current_board.append(x)
    return current_board

def return_string(board,street="river"):
    board_str=''
    for i in range (0,3):
        for j in range(0,2):
            if board[i][j] in RANKS or board[i][j] in SUITS:
                board_str=board_str+board[i][j]
    if street == "turn" or street == "river":
        for j in range (0,2):
            if board[3][j] in RANKS or board[3][j] in SUITS:
                board_str=board_str+board[3][j]
    if street == "river":
        for j in range (0,2):
            if board[4][j] in RANKS or board[4][j] in SUITS:
                board_str=board_str+board[4][j]          
    return board_str

def return_next_cards(board,all_cards=True):
    # returns a list of cards for possible next street card
    # if all_cards = False it only returns 1 of every rank + random suit  
    board = parse_board(board)
    if all_cards:
        return_cards=[card for card in CARDS if card not in board]
        return return_cards
    else:
        return_cards=[rank + random.choice(SUITS) for rank in RANKS]
        return_cards=[card for card in return_cards if card not in board]
        return return_cards

def return_ranks(board=[]):
    ranks=[r for r,s in board if r in RANKS]
    return sorted(ranks, key=lambda x:RANK_ORDER[x],reverse=True)

def return_suits(board=[]):
    suits=[s for r,s in board if s in SUITS]
    suits=[(suits.count(x),x) for x in SUITS if suits.count(x) != 0]
    return sorted(suits, key=lambda tup: tup[0],reverse=True)

def possible_flush_or_fd_ranks(board, suit):
    flush_ranks=[r for r,s in board if (s==suit and r in RANKS)]
    possible_flush_ranks=[r for r in RANKS if not r in flush_ranks]
    return possible_flush_ranks[0:-1]

def return_flushes(board):
    flush_suit=[s for c,s in return_suits(board) if c>2]
    if not flush_suit:
        return []
    return [r+flush_suit[0]*2 for r in possible_flush_or_fd_ranks(board,flush_suit[0])]

def return_flush_blocker(board):
    flushes=return_flushes(board)
    if not flushes:
        return []
    return [x[0:-1] for x in flushes]

def return_kicker(ranks):
    return [r for r in RANKS if r not in ranks]

def return_flushdraws(board,suit):
    fd_suits=[s for c,s in return_suits(board) if c == 2]
    if suit not in fd_suits:
        return []
    return [r+suit*2 for r in possible_flush_or_fd_ranks(board,suit)]

def rank_count(ranks):
    rank_count = [[],[],[],[]]
    for i in range(0,4):
        rank_count[i]= list(set( r for r in ranks if ranks.count(r) == (i+1) ))
    for i in rank_count:
        i.sort(key=lambda x:RANK_ORDER[x],reverse=True)
    return rank_count

def hand_board_intersections(ranks): # not including full + 
    rank_count_list=rank_count(ranks)
    if len(rank_count_list[0]) == len(ranks):
        sets=[str(r)*2 for r in ranks]
        two_pair=[''.join(r) for r in combinations(ranks,2)]
        return sets + two_pair + ranks
    #if rank_count_list[3]:
    #    return rank_count_list[3]
    if rank_count_list[2]:
        # quads=[rank_count_list[2][0]]
        trips=[]
        if rank_count_list[1]:
          #  quads.append(rank_count_list[1][0]*2)
            if RANK_ORDER[rank_count_list[1][0]] > RANK_ORDER[rank_count_list[2][0]]:
                trips.append(rank_count_list[1][0])
        else:
            trips=[x*2 for x in rank_count_list[0] if RANK_ORDER[x] > RANK_ORDER[rank_count_list[2][0]]]
        return trips # sorted(quads, key=lambda x:RANK_ORDER[x[0]], reverse=True) + trips
    if rank_count_list[1]:
        # quads=[r*2 for r in rank_count_list[1]]
        # fulls=[''.join(r+r) for r in rank_count_list[0]]
        # fulls=fulls+[x+y for x in rank_count_list[0] for y in rank_count_list[1]]
        # if len(rank_count_list[1])==2:
        #     fulls=fulls+[''.join(rank_count_list[1][0])+''.join(rank_count_list[1][1])]
        # fulls=sort_fulls(ranks,fulls)
        trips=rank_count_list[1]
        two_pair=[]
        possible_2_pair_ranks=[rank for rank in rank_count_list[0] if RANK_ORDER[rank] > RANK_ORDER[rank_count_list[1][0]]]
        if len(possible_2_pair_ranks) >= 2: 
            two_pair=[''.join(possible_2_pair_ranks[0] + r) for r in possible_2_pair_ranks[1:]]
        pairs=rank_count_list[0]
        return trips+two_pair+pairs # quads+fulls+trips+two_pair+pairs
    return []

def return_fulls_or_better(ranks):
    rank_count_list=rank_count(ranks)
    if rank_count_list[3]:
        return rank_count_list[3]
    if rank_count_list[2]:
        quads=[rank_count_list[2][0]]
        if rank_count_list[1]:
            quads.append(rank_count_list[1][0]*2)
        return sorted(quads, key=lambda x:RANK_ORDER[x[0]], reverse=True)
    if rank_count_list[1]:
        quads=[r*2 for r in rank_count_list[1]]
        fulls=[''.join(r+r) for r in rank_count_list[0]]
        fulls=fulls+[x+y for x in rank_count_list[0] for y in rank_count_list[1]]
        if len(rank_count_list[1])==2:
            fulls=fulls+[''.join(rank_count_list[1][0])+''.join(rank_count_list[1][1])]
        fulls=sort_fulls(ranks,fulls)
        return quads+fulls
    return []   

def return_str_flush(board):
    ranks=return_ranks(board)
    straights=return_straights(ranks)
    flush_suit=[s for c,s in return_suits(board) if c>2]
    str_flush=[]
    
    if not (straights and flush_suit):
        return []

    for straight in STRAIGHTS:
        str_flush_cards=[c for c in straight if c+flush_suit[0] not in board]
        if len(str_flush_cards)==2:
            str_flush.append(str_flush_cards[0]+flush_suit[0]+str_flush_cards[1]+flush_suit[0])
    return str_flush
    
def return_straights(ranks):
    ranks=straight_ranks(ranks)
    straights=[]
    for s in STRAIGHTS:
        straight_combo=[]
        for r in combinations(ranks,3):
            stra=''.join([x for x in s if x not in r])
            if len(stra)==2 and stra not in straights:
                straight_combo.append(''.join(sorted(stra, key=lambda x:RANK_ORDER[x], reverse=True)))
        straight_combo.sort(key=lambda x:(RANK_ORDER[x[0]],RANK_ORDER[x[1]]),reverse=True)
        straights+=straight_combo
    return straights

def straight_ranks(ranks):
    ranks=rank_count(ranks)
    return ranks[0]+ranks[1]+ranks[2]

def return_straight_draws(ranks):
    if len(ranks)==5: return []
    next_card_straight_hands=possible_straights_on_next_card(ranks)
    straight_hands=return_straights(ranks)
    gs_or_oesd=[hand for card in next_card_straight_hands for hand in next_card_straight_hands[card] if hand not in straight_hands]
    any_4_card_straight_combo=[combo1+combo2 for combo1 in gs_or_oesd for combo2 in gs_or_oesd]
    any_4_card_straight_combo=[''.join(sorted(set(hand), key=lambda x:RANK_ORDER[x], reverse=True)) for hand in any_4_card_straight_combo]
    any_4_card_straight_combo=list(set(any_4_card_straight_combo))

    def is_straight(hand, straight_hands):
        for straight in straight_hands:
            if (straight[0] in hand) and (straight[1] in hand):
                return True
        return False    
    
    any_4_card_straight_combo = [draw for draw in any_4_card_straight_combo if not is_straight(draw, straight_hands)]

    hand_straight_outs={}
    hand_straight_nuttynes={}


    for hand in any_4_card_straight_combo:
        hand_straight_outs[hand]=[]
        hand_straight_nuttynes[hand]=[]        
        for hand_combo in combinations(hand, 2):
            combo=''.join(sorted(hand_combo, key=lambda x:RANK_ORDER[x], reverse=True))
            for r in RANKS:
                if combo in next_card_straight_hands[r]:
                    if r not in hand_straight_outs[hand]:
                        hand_straight_outs[hand].append(r)
                        hand_straight_nuttynes[hand].append(next_card_straight_hands[r].index(combo))

    any_4_card_straight_combo=sorted(any_4_card_straight_combo, key = lambda x: (len(hand_straight_outs[x]),(100-sum(hand_straight_nuttynes[x]),x)), reverse=True)                        
                            
    for combo in combinations(any_4_card_straight_combo,2):
        if hand_straight_outs[combo[0]] == hand_straight_outs[combo[1]]:
            if len(combo[0]) > len(combo[1]):
                if combo[1] in combo[0] and combo[0] in any_4_card_straight_combo:
                    any_4_card_straight_combo.remove(combo[0])
            else:
                if combo[0] in combo[1] and combo[1] in any_4_card_straight_combo:
                    any_4_card_straight_combo.remove(combo[1])
    return any_4_card_straight_combo
    

def possible_straights_on_next_card(ranks):
    next_card={x:[] for x in RANKS}
    for card in next_card:
        next_ranks=straight_ranks(ranks+[card])
        next_card[card]=return_straights(next_ranks)
    return next_card
        
def sort_fulls(ranks,fulls):
    sort_fulls=[]
    for i in fulls:
        if ranks.count(i[0])==2 or i[0] == i[1]:
            sort_fulls.append(i)
        else:
            sort_fulls.append(i[1]+i[0])   
    fulls=sorted(sort_fulls, key=lambda x:(RANK_ORDER[x[0]],RANK_ORDER[x[1]]),reverse=True)
    return [''.join(sorted(full, key=lambda x:RANK_ORDER[x], reverse=True)) for full in fulls]

def pairs(ranks):
    pairs=[]
    for r in RANKS:
        if r not in ranks:
            pairs.append(''.join(r+r))
    return pairs

def test():
    board_string="Ks3s3s6h7d"
    sample_board=parse_board(board_string)
    ranks=return_ranks(sample_board)
    
  #  print(sample_board)
  #  print(return_ranks(sample_board))
  #  print(return_suits(sample_board))
  #  print(return_flushes(sample_board))
  #  print(return_flushdraws(sample_board,'c'))
  #  print(rank_count(return_ranks(sample_board)))
    print(hand_board_intersections(return_ranks(sample_board)))
    print(return_string(sample_board,"river"))
    print(return_straights(ranks))
    print(return_straight_draws(ranks))
    print(return_str_flush(sample_board))
    print(return_next_cards("Ks4s3c",False))
 #   print(pairs(ranks))


if __name__ == '__main__':
    import timeit
    if DEBUG:
        test()
        #print((timeit.timeit("test()", setup="from __main__ import test",number=1000)))
            
    

# 
# board.py ends here
