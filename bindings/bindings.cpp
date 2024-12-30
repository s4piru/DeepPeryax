// bindings.cpp
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>               // For std::vector, std::string, etc.
#include <memory>                       // For std::shared_ptr
#include "trax.h"

namespace py = pybind11;

// ヘルパー関数：kLargePieceNotations を Python のリストに変換
static py::list convertLargePieceNotations() {
    py::list outer_list;
    for (int i = 0; i < NUM_PIECES; ++i) {
        py::list middle_list;
        for (int row = 0; row < 3; ++row) {
            middle_list.append(std::string(kLargePieceNotations[i][row]));
        }
        outer_list.append(middle_list);
    }
    return outer_list;
}

PYBIND11_MODULE(trax_bindings, m) {
    m.doc() = "Python bindings for TRAX game engine (excluding Searcher)";

    //
    // 1) グローバル定数・変数・配列
    //
    m.attr("kInf") = kInf;

    m.attr("kDx") = py::cast(std::vector<int>{kDx[0], kDx[1], kDx[2], kDx[3]});
    m.attr("kDy") = py::cast(std::vector<int>{kDy[0], kDy[1], kDy[2], kDy[3]});

    // kPieceColors をリストとして公開
    {
        py::list py_piece_colors;
        for (int i = 0; i < NUM_PIECES; ++i) {
            py_piece_colors.append(std::string(kPieceColors[i]));
        }
        m.attr("kPieceColors") = py_piece_colors;
    }

    // kPieceNotations を文字列として公開
    {
        m.attr("kPieceNotations") = std::string(kPieceNotations);
    }

    // kLargePieceNotations をリストのリストとして公開
    m.attr("kLargePieceNotations") = convertLargePieceNotations();

    m.attr("kPositionHashPrime") = kPositionHashPrime;

    //
    // 2) グローバル関数
    //
    m.def("Random", &Random, "Generate a random number using Xorshift128.");
    m.def("GeneratePossiblePiecesTable", &GeneratePossiblePiecesTable, "Generate a lookup table for possible pieces.");
    m.def("GenerateTrackDirectionTable", &GenerateTrackDirectionTable, "Generate direction table for track lines.");
    m.def("GenerateForcedPlayTable", &GenerateForcedPlayTable, "Generate forced-play table.");

    //
    // 3) 列挙型
    //

    // enum Piece
    py::enum_<Piece>(m, "Piece")
        .value("PIECE_EMPTY",    PIECE_EMPTY)
        .value("PIECE_RWRW",     PIECE_RWRW)
        .value("PIECE_WRWR",     PIECE_WRWR)
        .value("PIECE_RWWR",     PIECE_RWWR)
        .value("PIECE_RRWW",     PIECE_RRWW)
        .value("PIECE_WRRW",     PIECE_WRRW)
        .value("PIECE_WWRR",     PIECE_WWRR)
        .value("NUM_PIECES",     NUM_PIECES)
        .export_values();

    // enum WinningReason
    py::enum_<WinningReason>(m, "WinningReason")
        .value("WINNING_REASON_UNKNOWN", WINNING_REASON_UNKNOWN)
        .value("WINNING_REASON_LOOP",    WINNING_REASON_LOOP)
        .value("WINNING_REASON_LINE",    WINNING_REASON_LINE)
        .value("WINNING_REASON_FULL",    WINNING_REASON_FULL)
        .value("WINNING_REASON_RESIGN",  WINNING_REASON_RESIGN)
        .export_values();

    //
    // 4) Struct Move
    //
    py::class_<Move>(m, "Move")
        .def(py::init<>(), "Default constructor.")
        .def(py::init<const std::string&, const Position&>(),
             py::arg("trax_notation"), py::arg("previous_position"),
             "Construct a Move by parsing trax_notation with reference to previous_position.")
        .def(py::init<int, int, Piece>(),
             py::arg("x"), py::arg("y"), py::arg("piece"),
             "Construct a Move from coordinate (x, y) and piece.")
        .def("Parse", &Move::Parse,
             py::arg("trax_notation"), py::arg("previous_position"),
             "Parse a trax notation string based on previous_position.")
        .def("notation", &Move::notation,
             "Return the Trax notation of the move.")
        // ビットフィールドに対して def_property を使用
        .def_property("x",
            [](const Move &m) -> int { return m.x; },
            [](Move &m, int value) { m.x = value; },
            "X coordinate.")
        .def_property("y",
            [](const Move &m) -> int { return m.y; },
            [](Move &m, int value) { m.y = value; },
            "Y coordinate.")
        .def_property("piece",
            [](const Move &m) -> Piece { return m.piece; },
            [](Move &m, Piece value) { m.piece = value; },
            "Piece kind.");

    //
    // 5) Struct ScoredMove
    //
    py::class_<ScoredMove>(m, "ScoredMove")
        .def(py::init<int, Move>(),
             py::arg("score"), py::arg("move"),
             "Constructor for ScoredMove with score and move.")
        .def_readwrite("score", &ScoredMove::score, "Score of the move.")
        .def_readwrite("move", &ScoredMove::move, "The Move itself.")
        .def("__lt__",
             [](const ScoredMove &self, const ScoredMove &rhs) {
                 return self < rhs;
             },
             "Comparison operator for sorting.");

    //
    // 6) Struct Line
    //
    py::class_<Line>(m, "Line")
        .def(py::init<>(), "Default constructor for Line.")
        .def(py::init<const std::pair<int, int>&,
                      const std::pair<int, int>&,
                      bool,
                      const Position&,
                      const std::map<std::pair<int, int>, int>&,
                      int>(),
             py::arg("endpoint_a"),
             py::arg("endpoint_b"),
             py::arg("is_red"),
             py::arg("position"),
             py::arg("indexed_edges"),
             py::arg("total_index"),
             "Construct a Line with detailed parameters.")
        .def("Dump", &Line::Dump, "Debug print information of the line.")
        .def("is_mate", &Line::is_mate, "Return true if line is mate.")
        .def_readwrite("is_red", &Line::is_red, "True if the line is red.")
        // 配列メンバーをプロパティとして公開
        .def_property("edge_distances",
            [](const Line &l) -> std::vector<int> {
                return std::vector<int>(l.edge_distances, l.edge_distances + 2);
            },
            [](Line &l, const std::vector<int> &v) {
                for (size_t i = 0; i < 2 && i < v.size(); ++i) { // size_t に変更
                    l.edge_distances[i] = v[i];
                }
            },
            "Distances to edges.")
        .def_readwrite("endpoint_distance", &Line::endpoint_distance, "Endpoint distance.")
        .def_readwrite("manhattan_distance", &Line::manhattan_distance, "Manhattan distance.")
        .def_readwrite("is_inner", &Line::is_inner, "True if it is inner line.")
        .def_property("loop_distances",
            [](const Line &l) -> std::vector<int> {
                return std::vector<int>(l.loop_distances, l.loop_distances + 2);
            },
            [](Line &l, const std::vector<int> &v) {
                for (size_t i = 0; i < 2 && i < v.size(); ++i) { // size_t に変更
                    l.loop_distances[i] = v[i];
                }
            },
            "Loop distances for inner lines.")
        .def_readwrite("endpoint_index_a", &Line::endpoint_index_a, "Endpoint A index.")
        .def_readwrite("endpoint_index_b", &Line::endpoint_index_b, "Endpoint B index.");

    //
    // 7) Class Position
    //
    py::class_<Position, std::shared_ptr<Position>>(m, "Position")
        .def(py::init<>(), "Construct an empty Trax board.")
        .def("GenerateMoves", &Position::GenerateMoves, "Return a list of possible moves from current position.")
        .def("DoMove",
             [](const std::shared_ptr<Position> &self, const Move &move) -> std::pair<bool, std::shared_ptr<Position>> {
                 std::shared_ptr<Position> next_position = std::make_shared<Position>();
                 bool success = self->DoMove(move, next_position.get());
                 return std::make_pair(success, next_position);
             },
             py::arg("move"),
             "Apply a move to the current position, return (success, next_position).")
        .def("GetPossiblePieces", &Position::GetPossiblePieces, py::arg("x"), py::arg("y"),
             "Return a set of pieces that can be placed at (x, y).")
        .def("Hash", &Position::Hash, "Compute a rolling hash of the position.")
        .def("EnumerateLines",
             [](const std::shared_ptr<Position> &self) {
                 std::vector<Line> lines;
                 self->EnumerateLines(&lines);
                 return lines;
             },
             "Enumerate lines in the position and return them.")
        .def("Swap", &Position::Swap, py::arg("to"), "Swap internal data with another Position object.")
        .def("Clear", &Position::Clear, "Clear the board to an empty Trax board.")
        .def("Dump", &Position::Dump, "Print debug info of the position to stderr.")
        .def("ToString64x64", &Position::ToString64x64, "Convert the position to a 64x64 map string.")
        // 'at' メソッドのバインディングを修正
        .def("at",
             [](const std::shared_ptr<Position> &self, int x, int y) -> Piece {
                 return static_cast<const Position&>(*self).at(x, y); // const Position& を明示的に使用
             },
             py::arg("x"), py::arg("y"),
             "Get the piece at (x, y).")
        .def_property_readonly("max_x", &Position::max_x, "Maximum x range of the board.")
        .def_property_readonly("max_y", &Position::max_y, "Maximum y range of the board.")
        .def_property_readonly("red_to_move", &Position::red_to_move, "True if red is the side to move for the NEXT turn.")
        .def("finished", &Position::finished, "Return True if the game is finished in this position.")
        .def("winner", &Position::winner, "Return 1 if red is the winner, -1 if white is the winner, or 0 if draw.")
        .def("winning_reason", &Position::winning_reason, "Return the reason of winning if finished() == True; otherwise UNKNOWN.");

    //
    // 8) struct Game
    //
    py::class_<Game>(m, "Game")
        .def(py::init<>(), "Default constructor for Game.")
        .def_readwrite("moves", &Game::moves, "List of moves in this game.")
        .def_readwrite("comments", &Game::comments, "List of comments (one for each move).")
        .def_readwrite("winner", &Game::winner, "1 if red is the winner, -1 if white is the winner, 0 if draw.")
        .def_readwrite("winning_reason", &Game::winning_reason, "Winning reason such as loop or line.")
        // 配列メンバーをプロパティとして公開
        .def_property("average_search_depths",
            [](const Game &g) -> std::vector<double> {
                return std::vector<double>(g.average_search_depths, g.average_search_depths + 2);
            },
            [](Game &g, const std::vector<double> &v) {
                for (size_t i = 0; i < 2 && i < v.size(); ++i) { // size_t に変更
                    g.average_search_depths[i] = v[i];
                }
            },
            "Average search depth array: [white, red].")
        .def_property("average_nps",
            [](const Game &g) -> std::vector<double> {
                return std::vector<double>(g.average_nps, g.average_nps + 2);
            },
            [](Game &g, const std::vector<double> &v) {
                for (size_t i = 0; i < 2 && i < v.size(); ++i) { // size_t に変更
                    g.average_nps[i] = v[i];
                }
            },
            "Average NPS array: [white, red].")
        .def("Clear", &Game::Clear, "Clear the game record.")
        .def("num_moves", &Game::num_moves, "Return the number of moves in this game.");

    //
    // 9) ParseCommentedGames
    //
    m.def("ParseCommentedGames", &ParseCommentedGames,
          py::arg("filename"), py::arg("games"),
          "Parse commented games from a file into the provided games vector.");

    //
    // 10) Class Book
    //
    py::class_<Book>(m, "Book")
        .def(py::init<>(), "Default constructor for Book.")
        .def("Init", &Book::Init, py::arg("games"), py::arg("max_steps") = 3,
             "Generate book data from the given games with optional max_steps.")
        .def("Select",
             [](Book &self, const std::shared_ptr<Position> &position) -> std::pair<bool, Move> {
                 Move next_move;
                 bool found = self.Select(*position, &next_move);
                 return std::make_pair(found, next_move);
             },
             py::arg("position"),
             "Select a move from the book for the given position. Returns (found, move).");

    //
    // 11) ShowPosition
    //
    m.def("ShowPosition", &ShowPosition, "Show the current position (reads from flags?).");
}
