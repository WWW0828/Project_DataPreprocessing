import board as bd
game = []
game_flag = False
valid_players = set()
min_blitz, max_blitz = 700, 2600
min_rapid, max_rapid = 700, 2400
total_blitz_games, total_rapid_games = 0, 0
blitz_rating = [0 for i in range((max_blitz - min_blitz)//100)]
rapid_rating = [0 for i in range((max_rapid - min_rapid)//100)]
game_cnt = 0

def eloNotIn(min_elo, max_elo, elo):
    return elo < min_elo or elo > max_elo

def whiteID(move): 
    if 'O-O-O' in move:
        return bd.actLongCastle('w')
    if 'O-O' in move:
        return bd.actShortCastle('w')
    if move[0].islower():
        return bd.actPawn('P', move)
    if move[0] == 'N':
        bd.findPinnedPieces('W')
        return bd.actKnight('N', move)
    if move[0] == 'K':
        return bd.actKing('K', move)
    bd.findPinnedPieces('W')
    return bd.actBRQ(move[0], move)

def blackID(move):
    if 'O-O-O' in move:
        return bd.actLongCastle('b')
    if 'O-O' in move:
        return bd.actShortCastle('b')
    if move[0].islower():
        return bd.actPawn('p', move)
    if move[0] == 'N':
        bd.findPinnedPieces('B')
        return bd.actKnight('n', move)
    if move[0] == 'K':
        return bd.actKing('k', move)
    bd.findPinnedPieces('B')
    return bd.actBRQ(move[0].lower(), move)

def appendAGame(append_line):
    global game_flag
    line = append_line.replace('\n', '')
    if 'Event' in line:
        game.append(line)
    elif 'UTCDate' in line:
        game.append(line)
    elif '1.' in line:
        game.append(line)
        if '1-0' in line:
            game.append(1.0)
        elif '0-1' in line:
            game.append(-1.0)
        else:
            game.append(0.0)
        game_flag = True
    elif 'WhiteRatingDiff' not in line and 'BlackRatingDiff' not in line:
        if 'White' in line or 'Black' in line:
            game.append(line)

def convertGame(game):
    global total_blitz_games, total_rapid_games
    training_format = ''
    result = game[-1] 
    event = 'Blitz' 
    temp_wr, temp_br = -1, -1
    temp_pw, temp_pb = '', ''
    # print(game)
    for game_info in game[:-1]:
        if 'Event' in game_info:
            if 'Rapid' in game_info:
                event = 'Rapid'
                training_format = f'GM[chess]RE[{result}]EV[Rapid]'
            elif 'Blitz' in game_info:
                training_format = f'GM[chess]RE[{result}]EV[Blitz]'
            else:
                return 
        elif 'UTCDate' in game_info:
            date = game_info.split('"')[1]
            training_format += f'DT[{date}]'
        elif 'WhiteElo' in game_info or 'BlackElo' in game_info:
            rating = game_info.split('"')[1]
            if rating == '?':
                return
            else:
                if event == 'Blitz':
                    if eloNotIn(min_blitz, max_blitz, int(rating)):
                        return
                else:
                    if eloNotIn(min_rapid, max_rapid, int(rating)):
                        return
            if 'WhiteElo' in game_info:
                temp_wr = int(rating)
                training_format += f'WR[{rating}]'
            else:
                temp_br = int(rating)
                training_format += f'BR[{rating}]'
        elif 'White' in game_info or 'Black' in game_info:
            player = game_info.split('"')[1]
            if player == '?':
                return
            if 'White' in game_info:
                temp_pw = player
                training_format += f'PW[{player}]'
            else:
                temp_pb = player
                training_format += f'PB[{player}]'
        elif '1. ' in game_info:
            bd.resetBoard()
            moves = game_info.split(' ')
            turn = 'W'
            for i in range(len(moves[:-1])):
                action_id = -1
                move = moves[i]
                # remove accuracy annotation
                newmove = move.replace('?', '')
                newmove = newmove.replace('!', '')
                if not move[0].isalpha():
                    continue
                if turn == 'W':
                    action_id = whiteID(newmove)
                    training_format += f'W[{action_id}]'
                    turn = 'B'
                else:
                    action_id = blackID(newmove)
                    training_format += f'B[{action_id}]'
                    turn = 'W'
    print(training_format)
    if event == 'Blitz':
        total_blitz_games += 1
        blitz_rating[(temp_wr - min_blitz)//100] += 1
        blitz_rating[(temp_br - min_blitz)//100] += 1
    else:
        total_rapid_games += 1
        rapid_rating[(temp_wr - min_rapid)//100] += 1
        rapid_rating[(temp_br - min_rapid)//100] += 1
    valid_players.add(temp_pw)
    valid_players.add(temp_pb)

with open('lichess_db_standard_rated_2013-01.pgn', 'r') as pgn:
    lines = pgn.readlines()
    for line in lines:
        appendAGame(line)
        if game_flag:
            convertGame(game)
            game_cnt += 1
            game_flag = False
            game.clear()     

print('# players:', len(valid_players))
print('# blitz games:', total_blitz_games)
s = str(blitz_rating[0])
for i in blitz_rating[1:]:
    s += ' ' + str(i)
print('rating distribution: 700-2600')
print(s)

print('# rapid games:', total_rapid_games)
s = str(rapid_rating[0])
for i in rapid_rating[1:]:
    s += ' ' + str(i)
print('rating distribution: 700-2400')
print(s)