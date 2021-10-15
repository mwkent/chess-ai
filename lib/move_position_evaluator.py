import chess
from board import Board
import position_evaluator
import chess_util


class MovePositionEvaluator(object):
    """Evaluates positions on a move by move basis.
    Keeps track of the evaluation for each piece on the board.
    """

    def __init__(self, board: Board, turn: chess.Color):
        """Evaluates every piece on the board.
        Pieces for turn have positive evaluations.
        Pieces for not turn have negative evaluations.
        """
        self.pieces_to_values = {}
        self.pieces_evaluation = 0
        self.final_evaluation = 0
        self.board = board
        self.turn = turn
        # Updates to pieces_to_values when a move is popped from the board
        self.undo_updates = []
        self.undo_pieces_evaluation = []
        self.undo_final_evaluation = []
        
        for piece in board.get_all_pieces():
            piece_evaluation = self._get_piece_evaluation(piece)
            self.pieces_evaluation += piece_evaluation
            self.pieces_to_values[piece] = piece_evaluation

        self._set_final_evaluation()
        
    def get_pieces_to_reevaluate(self) -> chess.SquareSet:
        """Which pieces need to be reevaluated after a move? The piece that was moved,
        all of the pieces that attacked the piece before the move and after the move,
        and all of the pieces the piece attacked before and after the move.
        """
        # Todo: Add kings
        move = self.board.peek()
        attacked_pieces_from_from_square = chess.SquareSet([square for square in self.board.attacks(move.from_square)
                                                            if self.board.piece_at(square) is not None])
        attacked_pieces_from_to_square = chess.SquareSet([square for square in self.board.attacks(move.to_square)
                                                          if self.board.piece_at(square) is not None])
        pieces_to_reevaluate = chess.SquareSet.from_square(move.to_square).union(
            attacked_pieces_from_from_square).union(attacked_pieces_from_to_square).union(
                self.board.attackers(chess.WHITE, move.from_square)).union(
                    self.board.attackers(chess.BLACK, move.from_square)).union(
                        self.board.attackers(chess.WHITE, move.to_square)).union(self.board.attackers(chess.BLACK, move.to_square))
        return pieces_to_reevaluate

    def evaluate_after_move(self) -> float:
        """Evaluates only pieces affected by the move
        Returns the evaluation of the position
        """
        # Todo: add attacking higher pieces eval
        # Todo: Handle endgames
        
        self.undo_pieces_evaluation.append(self.pieces_evaluation)
        
        undo_updates = {}
        move_from_square = self.board.peek().from_square
        undo_updates[move_from_square] = self.pieces_to_values.get(move_from_square, 0)
        pieces_to_reevaluate = self.get_pieces_to_reevaluate()
        for piece in pieces_to_reevaluate:
            undo_updates[piece] = self.pieces_to_values.get(piece, 0)
            self._reevaluate_piece(piece)
        self.undo_updates.append(undo_updates)

        self.undo_final_evaluation.append(self.final_evaluation)
        self._set_final_evaluation()

        return self.final_evaluation
    
    def undo_move(self) -> None:
        """Undoes move, modifying pieces_to_values, pieces_evaluation, and final_evaluation
        """
        self.pieces_to_values.update(self.undo_updates.pop())
        self.pieces_evaluation = self.undo_pieces_evaluation.pop()
        self.final_evaluation = self.undo_final_evaluation.pop()
    
    def _set_final_evaluation(self):
        """Sets the final_evaluation, the evaluation considering checkmate, draws, and repetition
        Assumes pieces_evaluation has already been set
        """
        game_over_eval = position_evaluator.get_game_over_eval(self.board, self.turn)
        if game_over_eval is not None:
            self.final_evaluation = game_over_eval
        else:
            self.final_evaluation = position_evaluator.get_repetition_eval(self.board, self.turn, self.pieces_evaluation)

    
    def _reevaluate_piece(self, piece: chess.Square) -> None:
        """Updates the evaluation for the specified piece
        """
        move = self.board.peek()
        piece_evaluation = self._get_piece_evaluation(piece)
        # Reevaluate the piece that was moved
        if piece == move.to_square:
            self._clear_en_passant_square()
            self.pieces_evaluation -= self.pieces_to_values[move.from_square]
            self.pieces_to_values.pop(move.from_square)
            # Subtracts the value of the captured piece if the move was a capture
            self.pieces_evaluation -= self.pieces_to_values.get(move.to_square, 0)
        else:
            self.pieces_evaluation -= self.pieces_to_values[piece]
        self.pieces_evaluation += piece_evaluation
        self.pieces_to_values[piece] = piece_evaluation

    def _clear_en_passant_square(self) -> None:
        """Clears the value for the pawn that was taken en passant.
        This assumes the move was already made on the board,
        and the to_square for the move was not already cleared.
        """
        move = self.board.peek()
        # Is this a pawn capture and is there no piece in the to_square being captured?
        if self.board.piece_type_at(move.to_square) == chess.PAWN and \
        chess.square_file(move.from_square) != chess.square_file(move.to_square) and \
        move.to_square not in self.pieces_to_values:
            # Square where pawn was captured en passant
            en_passant_square = chess_util.get_prior_pawn_square(move.to_square, self.board.color_at(move.to_square))
            self.pieces_evaluation -= self.pieces_to_values.get(en_passant_square, 0)
            self.pieces_to_values.pop(en_passant_square, None)
    
    def _get_piece_evaluation(self, piece: chess.Square):
        piece_evaluation = position_evaluator.evaluate_piece(self.board, self.board.color_at(piece), piece)
        if self.board.color_at(piece) != self.turn:
            piece_evaluation *= -1
        return piece_evaluation
    
    def get_evaluation(self):
        return self.final_evaluation
    
    def print_pieces_to_values(self):
        print(dict((chess.square_name(piece), value) for piece, value in self.pieces_to_values.items()))
