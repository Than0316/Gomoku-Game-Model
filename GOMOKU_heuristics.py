def gen(self, role, only_threes, star_spread):
    if self.count <= 0:
        return [(7, 7)]

    fives = []
    comfours = []
    humfours = []
    comblockedfours = []
    humblockedfours = []
    comtwothrees = []
    humtwothrees = []
    comthrees = []
    humthrees = []
    comtwos = []
    humtwos = []
    neighbors = []

    board = self.board
    reverse_role = R.reverse(role)

    for i in range(len(board)):
        for j in range(len(board)):
            if board[i][j] == R.empty:
                neighbor = (2, 2)
                if len(self.all_steps) < 6:
                    neighbor = (1, 1)
                if self.has_neighbor((i, j), neighbor[0], neighbor[1]):  # must have neighbor

                    score_hum = self.hum_score[i][j]
                    score_com = self.com_score[i][j]
                    max_score = max(score_com, score_hum)

                    p = {
                        'pos': (i, j),
                        'scoreHum': score_hum,
                        'scoreCom': score_com,
                        'score': max_score,
                        'role': role
                    }

                    if score_com >= S.FIVE:  # computer can win
                        fives.append(p)
                    elif score_hum >= S.FIVE:  # player can win
                        fives.append(p)
                    elif score_com >= S.FOUR:
                        comfours.append(p)
                    elif score_hum >= S.FOUR:
                        humfours.append(p)
                    elif score_com >= S.BLOCKED_FOUR:
                        comblockedfours.append(p)
                    elif score_hum >= S.BLOCKED_FOUR:
                        humblockedfours.append(p)
                    elif score_com >= 2 * S.THREE:
                        comtwothrees.append(p)
                    elif score_hum >= 2 * S.THREE:
                        humtwothrees.append(p)
                    elif score_com >= S.THREE:
                        comthrees.append(p)
                    elif score_hum >= S.THREE:
                        humthrees.append(p)
                    elif score_com >= S.TWO:
                        comtwos.insert(0, p)
                    elif score_hum >= S.TWO:
                        humtwos.insert(0, p)
                    else:
                        neighbors.append(p)

    # If a five-in-a-row, must play it
    if len(fives):
        return fives

    # Go for your own live four if possible
    if role == R.com and comfours:
        return comfours
    if role == R.hum and humfours:
        return humfours

    # If opponent has live four, but you can't block, return only opponent's live four
    if role == R.com and humfours and not comblockedfours:
        return humfours
    if role == R.hum and comfours and not humblockedfours:
        return comfours

    # Both sides have live four/block four, consider them all
    if role == R.com:
        fours = comfours + humfours
        blockedfours = comblockedfours + humblockedfours
    else:
        fours = humfours + comfours
        blockedfours = humblockedfours + comblockedfours

    if fours:
        return fours + blockedfours

    if role == R.com:
        result = comtwothrees + humtwothrees + comblockedfours + humblockedfours + comthrees + humthrees
    else:
        result = humtwothrees + comtwothrees + humblockedfours + comblockedfours + humthrees + comthrees

    # Double-threes are special
    if comtwothrees or humtwothrees:
        return result

    # Only return >= live-three moves
    if only_threes:
        return result

    # Twos and neighbors
    if role == R.com:
        twos = comtwos + humtwos
    else:
        twos = humtwos + comtwos

    twos.sort(key=lambda x: x['score'], reverse=True)
    result += twos if twos else neighbors

    # Don't return too many weak choices
    if len(result) > config.count_limit:
        return result[:config.count_limit]

    return result