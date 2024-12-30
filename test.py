import sys
import trax_bindings
import io
import contextlib

def list_enum(enum_class):
    """
    Returns a list of members in the given enum_class.
    It filters out private or special attributes.
    """
    return [getattr(enum_class, name) for name in dir(enum_class)
            if not name.startswith("_") and isinstance(getattr(enum_class, name), enum_class)]

def test_globals():
    """Test global constants and arrays."""
    print("Testing global constants and arrays...")
    print("kInf:", trax_bindings.kInf)
    print("kDx:", trax_bindings.kDx)
    print("kDy:", trax_bindings.kDy)
    print("kPieceColors:", trax_bindings.kPieceColors)
    print("kPieceNotations:", trax_bindings.kPieceNotations)
    print("kLargePieceNotations:", trax_bindings.kLargePieceNotations)
    print("kPositionHashPrime:", trax_bindings.kPositionHashPrime)
    print()

def test_global_functions():
    """Test global functions."""
    print("Testing global functions...")
    random_val = trax_bindings.Random()
    print("Random() ->", random_val)

    trax_bindings.GeneratePossiblePiecesTable()
    print("GeneratePossiblePiecesTable() called.")

    trax_bindings.GenerateTrackDirectionTable()
    print("GenerateTrackDirectionTable() called.")

    trax_bindings.GenerateForcedPlayTable()
    print("GenerateForcedPlayTable() called.")
    print()

def test_enums():
    """Test enums (Piece, WinningReason)."""
    print("Testing enums...")

    from trax_bindings import Piece, WinningReason

    piece_values = list_enum(Piece)
    print("All Piece values:")
    for p in piece_values:
        print(" ", p)

    winning_reason_values = list_enum(WinningReason)
    print("All WinningReason values:")
    for w in winning_reason_values:
        print(" ", w)
    print()

def test_move():
    """Test the Move struct basic functionality."""
    print("Testing Move struct...")

    from trax_bindings import Move, Piece, Position

    pos = Position()

    # Default constructor
    move_default = Move()
    print("Default Move:", move_default.x, move_default.y, move_default.piece)

    # Constructor with (x, y, piece)
    move_init = Move(1, -1, Piece.PIECE_RWRW)
    print("Initialized Move:", move_init.x, move_init.y, move_init.piece)

    # Attempt to parse a valid notation like "A2+" or "@1/"
    try:
        move_parsed = Move("A2+", pos)
        print("Parsed Move (A2+):", move_parsed.x, move_parsed.y, move_parsed.piece)
        print("Notation of move_parsed:", move_parsed.notation())
    except Exception as e:
        print("Exception in Move constructor with 'A2+':", e)

    # Parse method
    try:
        success, next_pos = pos.DoMove(move_init)
        print("DoMove success:", success)
        if success:
            pos = next_pos  # Assign next_pos to pos
            print("After DoMove, pos finished?:", pos.finished())
            print("After DoMove, pos winner?:", pos.winner())
    except Exception as e:
        print("Exception in pos.DoMove(move_init):", e)

    print()

def test_move_custom_strings():
    """
    Test Move struct with the specific notation strings:
    @0+, A2+, B1+, @2\, A3/, etc.
    """
    print("Testing Move struct with custom notation strings...")

    from trax_bindings import Move, Position

    # These are the valid Trax notation strings provided
    notation_examples = [
        "@0+",
        "A2+",
        "B1+",
        "@2\\",
        "A3/",
        "@2\\",
        "@1/",
        "F1\\",
        "E2\\",
        "F2+",
        "D3+",
        "F3+",
        "A3/",
        "@3/",
        "G0/",
        "H1/",
        "B1\\",
        "A2+",
        "A1+",
        "@2/",
        "@4/",
        "A5/",
        "@3\\",
        "A2\\",
        "A1\\",
        "G5\\",
        "A6/",
        "@6\\",
    ]

    pos = Position()
    for notation_str in notation_examples:
        try:
            mv = Move(notation_str, pos)
            print(f"Parsed '{notation_str}': x={mv.x}, y={mv.y}, piece={mv.piece}")
            # Also check if re-notation matches (it might differ if parse changes x/y)
            print("  Re-notation:", mv.notation())
            # Optionally, perform DoMove and update pos
            success, next_pos = pos.DoMove(mv)
            if success:
                pos = next_pos
        except SystemExit:
            print(f"Failed to parse '{notation_str}' -> SystemExit")
        except Exception as e:
            print(f"Failed to parse '{notation_str}' -> Exception: {e}")

    print()

def test_scored_move():
    """Test the ScoredMove struct."""
    print("Testing ScoredMove struct...")

    from trax_bindings import ScoredMove, Move, Piece, Position

    dummy_move = Move("A2+", Position())
    sm = ScoredMove(100, dummy_move)
    print("ScoredMove score:", sm.score)
    print("ScoredMove move:", sm.move.x, sm.move.y, sm.move.piece)

    sm2 = ScoredMove(50, dummy_move)
    print("Is sm2 < sm?", sm2 < sm)
    print()

def test_line():
    """Test the Line struct."""
    print("Testing Line struct...")

    from trax_bindings import Line, Position

    pos = Position()
    try:
        line_obj = Line((0, 0), (1, 1), True, pos, {}, 0)
        print("Line created with is_red:", line_obj.is_red)
        line_obj.Dump()
        print("Line is_mate:", line_obj.is_mate)
        print("line_obj.edge_distances:", line_obj.edge_distances)
        line_obj.edge_distances = [5, 7]
        print("line_obj.edge_distances after setting:", line_obj.edge_distances)
        print("line_obj.loop_distances:", line_obj.loop_distances)
        line_obj.loop_distances = [10, 12]
        print("line_obj.loop_distances after setting:", line_obj.loop_distances)
        line_obj.endpoint_distance = 3
        line_obj.manhattan_distance = 6
        line_obj.is_inner = True
        print("Line endpoint_distance:", line_obj.endpoint_distance)
        print("Line manhattan_distance:", line_obj.manhattan_distance)
        print("Line is_inner:", line_obj.is_inner)
    except Exception as e:
        print("Line Exception:", e)
    print()

def test_position():
    """Test the Position class."""
    print("Testing Position class...")

    from trax_bindings import Position, Move, Piece

    try:
        pos = Position()
        print("Position finished?:", pos.finished())
        moves = pos.GenerateMoves()
        print("Generated moves:", moves)
        if moves:
            move_test = moves[0]  # Take the first generated move
            success, next_pos = pos.DoMove(move_test)
            print("DoMove success:", success)

            if success:
                pos = next_pos  # Assign next_pos to pos
                print("After DoMove, pos finished?:", pos.finished())
                print("After DoMove, pos winner?:", pos.winner())

        piece_set = pos.GetPossiblePieces(0, 0)
        print("GetPossiblePieces(0,0):", piece_set)
        print("Position Hash:", pos.Hash())
        lines = pos.EnumerateLines()
        print("EnumerateLines:", lines)

        pos2 = Position()
        pos.Swap(pos2)
        print("Swapped pos with pos2. pos2 finished?:", pos2.finished())

        pos2.Clear()
        print("pos2 finished after Clear?:", pos2.finished())

        pos.Dump()
        print("pos.ToString64x64():", pos.ToString64x64())

        try:
            p = pos.at(0, 0)
            print("pos.at(0,0) ->", p)
        except Exception as e:
            print("Position.at Exception:", e)

        print("pos.max_x:", pos.max_x)
        print("pos.max_y:", pos.max_y)
        print("pos.red_to_move:", pos.red_to_move)
        print("pos.finished():", pos.finished())
        print("pos.winner():", pos.winner())
        print("pos.winning_reason():", pos.winning_reason())
    except Exception as e:
        print("Position Exception:", e)
    print()

def test_game():
    """Test the Game struct."""
    print("Testing Game struct...")

    from trax_bindings import Game, Move, Piece, Position

    try:
        g = Game()
        print("Game initial winner:", g.winner)
        print("Game initial winning_reason:", g.winning_reason)
        print("Game initial moves:", g.moves)
        print("Game initial comments:", g.comments)
        print("Game initial average_search_depths:", g.average_search_depths)
        g.average_search_depths = [1.5, 2.7]
        print("Game updated average_search_depths:", g.average_search_depths)
        print("Game initial average_nps:", g.average_nps)
        g.average_nps = [1000.0, 2000.0]
        print("Game updated average_nps:", g.average_nps)

        # Create a move and add to game
        pos = Position()
        move = Move("A2+", pos)
        g.moves.append(move)
        print("Number of moves in Game after append:", g.num_moves())

        # Clear the game
        g.Clear()
        print("Game winner after Clear:", g.winner)
        print("Game num_moves after Clear:", g.num_moves())
    except Exception as e:
        print("Game Exception:", e)
    print()

def test_book():
    """Test the Book class."""
    print("Testing Book class...")

    from trax_bindings import Book, Game, Position, Piece

    try:
        book = Book()
        print("Book created.")
        empty_games = []
        book.Init(empty_games, max_steps=2)
        print("Book.Init called with empty_games.")
        pos = Position()
        found, move_sel = book.Select(pos)
        print("Book.Select:", found, move_sel)
        if found:
            print("Selected Move:", move_sel.x, move_sel.y, move_sel.piece)
    except Exception as e:
        print("Book Exception:", e)
    print()

def test_show_position():
    """Test the ShowPosition function by simulating user input and capturing output."""
    print("Testing ShowPosition...")

    from trax_bindings import ShowPosition

    # Define the number of moves and the move notations to simulate input
    num_moves = 3
    moves_notation = [ "@0+", "A2+", "B1+"]  # Example move notations

    # Create the input string as expected by ShowPosition()
    input_str = f"{num_moves}\n" + "\n".join(moves_notation) + "\n"

    # Create StringIO objects to simulate stdin and capture stdout
    original_stdin = sys.stdin
    original_stdout = sys.stdout
    sys.stdin = io.StringIO(input_str)
    sys.stdout = io.StringIO()

    try:
        ShowPosition()
        # Retrieve the output
        output = sys.stdout.getvalue()
    except SystemExit:
        output = "ShowPosition() exited due to invalid input.\n"
    except Exception as e:
        output = f"ShowPosition() raised an exception: {e}\n"
    finally:
        # Restore original stdin and stdout
        sys.stdin = original_stdin
        sys.stdout = original_stdout

    print("Captured ShowPosition output:")
    print(output)

def main():
    """Main test entry point."""
    print("========== TRAX BINDINGS TEST BEGIN ==========")

    # 1) Globals
    test_globals()

    # 2) Global functions
    test_global_functions()

    # 3) Enums
    test_enums()

    # 4) Move (basic)
    test_move()

    # 5) Move with custom strings
    test_move_custom_strings()

    # 6) ScoredMove
    test_scored_move()

    # 7) Line
    test_line()

    # 8) Position
    test_position()

    # 9) Game
    test_game()

    # 11) Book
    test_book()

    # 12) ShowPosition
    # test_show_position()

    print("========== TRAX BINDINGS TEST END ==========")

if __name__ == "__main__":
    main()
