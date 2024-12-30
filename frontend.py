from flask import Flask
import subprocess
from flask import render_template
from collections import namedtuple

# http://trax.peryaudo.org/W_at0p_A2p_B1p_at2b_A3s_at2b_at1s_F1b_E2b_F2p_D3p_F3p_A3s_at3s_G0s_H1s_B1b_A2p_A1p_at2s_at4s_A5s_at3b_A2b_A1b_G5b_A6s_at6b_FIN
# White is computer, and red (human) won. White plays first.

def unescape_move(move):
    move = move.replace("at", "@")
    move = move.replace("p", "+")
    move = move.replace("s", "/")
    move = move.replace("b", "\\")
    return move

def unescape_state(state):
    moves = state.split("_")
    com_first = (moves[0] == "W")
    moves = moves[1:]
    if len(moves) > 0 and moves[-1] == "FIN":
        moves = moves[:-1]
    moves = [unescape_move(move) for move in moves]
    return com_first, moves

def show_position(moves):
    process = subprocess.Popen(
        ["./trax", "--show_position"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
    )
    input_str = "\n".join([str(len(moves))] + moves)
    stdout, _ = process.communicate(input=input_str.encode("utf-8"))
    if process.returncode != 0:
        raise RuntimeError("Subprocess failed with return code {}".format(process.returncode))
    board = [line.split(b" ") for line in stdout.split(b"\n")]
    winner = board[0][0].decode('utf-8')
    if winner == "1": winner = "red"
    elif winner == "-1": winner = "white"
    board = board[1:-1]
    board = [[int.from_bytes(b, 'little') for b in line] for line in board]
    return winner, board

Cell = namedtuple('Cell', ['kind', 'x', 'y'])

def convert_board_to_cells(board):
    cells = []
    for y, row in enumerate(board):
        cells.append([Cell(kind=kind, x=x, y=y) for x, kind in enumerate(row)])
    return cells

app = Flask(__name__)

@app.route('/<path:state>', methods=['GET'])
def root(state):
    com_first, moves = unescape_state(state)
    try:
        winner, board = show_position(moves)
    except RuntimeError:
        return "invalid move! select a correct move", 400
    return render_template('index.html', board=convert_board_to_cells(board), winner=winner)

if __name__ == '__main__':
    app.run(debug=True)