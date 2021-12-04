import chess
import chess_util
from typing import List, Set
from constants import PIECE_TYPES_TO_ROUGH_VALUES
from pickle import NONE

PIECE_TYPES_TO_VALUES = {chess.PAWN: 100, chess.KNIGHT: 305, chess.BISHOP: 330, 
                         chess.ROOK: 500, chess.QUEEN: 900, chess.KING: 10_000}
NON_PAWN_PIECE_TYPES = [chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN]


class Board(chess.Board, object):

    def __init__(self, fen=chess.STARTING_FEN, chess960=False):
        self._phase = {}
        self._squares_to_attackers_and_defenders = {}
        super(Board, self).__init__(fen=fen, chess960=chess960)

    def copy(self):
        board = super().copy()
        board._phase = self._phase.copy()
        board._squares_to_attackers_and_defenders = self._squares_to_attackers_and_defenders.copy()
        return board

    # Todo: Update phase rather than reset it
    def push(self, move):
        self._phase.clear()
        self._squares_to_attackers_and_defenders.clear()
        return super().push(move)

    # Todo: Update phase rather than reset it
    def pop(self):
        self._phase.clear()
        self._squares_to_attackers_and_defenders.clear()
        return super().pop()
    
    def get_all_pieces(self) -> List[chess.Square]:
        return [square for square in chess.SQUARES if self.piece_type_at(square) is not None]

    def get_phase(self, color):
        if color not in self._phase:
            piece_value_total = 0
            for piece_type in NON_PAWN_PIECE_TYPES:
                pieces = self.pieces(piece_type, not color)
                piece_value_total = piece_value_total + len(pieces) * PIECE_TYPES_TO_VALUES[piece_type]
            # if piece value is greater than or equal to this, then opening
            min_opening_total = 2 * PIECE_TYPES_TO_VALUES[chess.QUEEN]
            # if piece value is less than or equal to this, then endgame
            max_endgame_total = PIECE_TYPES_TO_VALUES[chess.ROOK] + PIECE_TYPES_TO_VALUES[chess.BISHOP]
            scaled_piece_value_total = min(min_opening_total, max(piece_value_total, max_endgame_total)) - max_endgame_total
            scaled_min_opening_total = min_opening_total - max_endgame_total
            self._phase[color] = 1 - (scaled_piece_value_total * 1.0 / scaled_min_opening_total)
        return self._phase[color]

    def gives_checkmate(self, move: chess.Move) -> bool:
        """
        Probes if the given move would put the opponent in checkmate. The move
        must be at least pseudo-legal.
        """
        self.push(move)
        try:
            return self.is_checkmate()
        finally:
            self.pop()

    def get_castling_rook(self, move: chess.Move) -> (chess.Square, chess.Square):
        """Returns the from and to square of the rook that is being castled by `move`
        """
        rook_from_square = None
        rook_to_square = None

        if self.is_kingside_castling(move):
            if self.turn == chess.WHITE:
                rook_from_square = next(square for square in
                                        chess_util.BACKRANK_WHITE_SQUARES_REVERSED
                                        if self.color_at(square) == self.turn and
                                        self.piece_type_at(square) == chess.ROOK)
                rook_to_square = chess.F1
            else: #Black's turn
                rook_from_square = next(square for square in
                                        chess_util.BACKRANK_BLACK_SQUARES_REVERSED
                                        if self.color_at(square) == self.turn and
                                        self.piece_type_at(square) == chess.ROOK)
                rook_to_square = chess.F8
        elif self.is_queenside_castling(move):
            if self.turn == chess.WHITE:
                rook_from_square = next(square for square in
                                        chess_util.BACKRANK_WHITE_SQUARES
                                        if self.color_at(square) == self.turn and
                                        self.piece_type_at(square) == chess.ROOK)
                rook_to_square = chess.D1
            else: #Black's turn
                rook_from_square = next(square for square in
                                        chess_util.BACKRANK_BLACK_SQUARES
                                        if self.color_at(square) == self.turn and
                                        self.piece_type_at(square) == chess.ROOK)
                rook_to_square = chess.D8

        return rook_from_square, rook_to_square

    # Todo: Not considering battery attackers that are pinned?
    def get_pinned_attackers_and_defenders(self, piece, defend_color=None):
        if defend_color is None:
            defend_color = self.color_at(piece)
        pinned_attackers = []
        all_attackers = self.attackers(not defend_color, piece)
        all_defenders = self.attackers(defend_color, piece)
        for attacker in all_attackers:
            if (not chess_util.can_piece_capture(self, attacker, piece)) and \
                chess_util.get_pinner(self, attacker) in all_defenders:
                pinned_attackers.append(attacker)
        pinned_defenders = []
        for defender in all_defenders:
            if (not chess_util.can_piece_capture(self, defender, piece)) and \
                chess_util.get_pinner(self, defender) in all_attackers:
                pinned_defenders.append(defender)
        return pinned_attackers, pinned_defenders

    # Gets attackers of square that are part of a battery of attackers (param)
    def get_battery_attackers(self, square, color, attackers):
        # Todo: Consider batteries through other player's pieces
        battery_attackers = []
        for attacker in attackers:
            if self.piece_type_at(attacker) in [chess.PAWN, chess.BISHOP, chess.ROOK, chess.QUEEN]:
                # Pieces attacking the attacker; should not include existing attackers or attacked piece
                attacker_attackers = [attacker_attacker for attacker_attacker in self.attackers(color, attacker)
                    if attacker_attacker != square and attacker_attacker not in attackers]
                for attacker_attacker in attacker_attackers:
                    # A battery is formed attacking the square
                    if self.piece_type_at(attacker_attacker) in [chess.BISHOP, chess.ROOK, chess.QUEEN] \
                        and not self.is_pinned(color, attacker_attacker) \
                        and attacker_attacker in chess.SquareSet.ray(square, attacker):
                        battery_attackers.append(attacker_attacker)
        return battery_attackers

    # Get first attackers - the pieces of color that can move to square first
    # Batteries not included, kings currently included
    def get_first_attackers_and_defenders(self, square: chess.Square, defend_color: chess.Color=None) \
        -> (List[chess.Square], List[chess.Square]):
        if defend_color is None:
            defend_color = self.color_at(square)
        attackers = [attacker for attacker in self.attackers(not defend_color, square) if chess_util.can_piece_capture(self, attacker, square)]
        defenders = [attacker for attacker in self.attackers(defend_color, square) if chess_util.can_piece_capture(self, attacker, square)]
        return attackers, defenders
    
    # Get second attackers and defenders - the attackers and defenders who can't move to square first
    # i.e. pieces that may be in a battery or are pinned
    # Technically, pinned pieces could be first attackers or defenders
    def get_second_attackers_and_defenders(self, square: chess.Square, first_attackers, first_defenders, 
                                           defend_color: chess.Color=None):
        if defend_color is None:
            defend_color = self.color_at(square)
        first_attackers_and_defenders = first_attackers + first_defenders
        second_attackers = self.get_battery_attackers(square, not defend_color, first_attackers_and_defenders)
        second_defenders = self.get_battery_attackers(square, defend_color, first_attackers_and_defenders)

        pinned_attackers, pinned_defenders = self.get_pinned_attackers_and_defenders(square, defend_color)
        second_attackers += pinned_attackers
        second_defenders += pinned_defenders

        # Todo: Is there a better way to solve this?
        # Need to check if there are batteries being formed with pinned attackers and defenders as well
        second_attackers += self.get_battery_attackers(square, not defend_color, pinned_attackers)
        second_defenders += self.get_battery_attackers(square, defend_color, pinned_defenders)
        return second_attackers, second_defenders

    def get_attackers_and_defenders(self, piece: chess.Square, piece_color: chess.Color=None) -> \
        (List[chess.Square], List[chess.Square], List[chess.Square], List[chess.Square]):
        if piece not in self._squares_to_attackers_and_defenders:
            if piece_color is None:
                piece_color = self.color_at(piece)
            first_attackers, first_defenders = self.get_first_attackers_and_defenders(piece, piece_color)
            # Sort to know which are the least valued attackers and defenders
            first_attackers.sort(key=lambda piece:PIECE_TYPES_TO_VALUES[self.piece_type_at(piece)])
            first_defenders.sort(key=lambda piece:PIECE_TYPES_TO_VALUES[self.piece_type_at(piece)])
            second_attackers, second_defenders = self.get_second_attackers_and_defenders(
                piece, first_attackers, first_defenders, piece_color)
            self._squares_to_attackers_and_defenders[piece] = \
                first_attackers, second_attackers, first_defenders, second_defenders
        return self._squares_to_attackers_and_defenders[piece]
    
    def get_stronger_pieces_attacked_by(self, piece: chess.Square) -> Set[chess.Square]:
        """Returns a set of the pieces that have a higher value than `piece`
        and are being attacked by piece
        """
        piece_color = self.color_at(piece)
        piece_value = PIECE_TYPES_TO_ROUGH_VALUES[self.piece_type_at(piece)]
        return {attacked_square for attacked_square in self.attacks(piece)
                       if self.piece_at(attacked_square) is not None and
                       self.color_at(attacked_square) != piece_color and
                       piece_value < PIECE_TYPES_TO_ROUGH_VALUES[self.piece_type_at(attacked_square)]}

