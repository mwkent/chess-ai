import chess
import chess_util
from typing import List

PIECE_TYPES_TO_VALUES = {chess.PAWN: 100, chess.KNIGHT: 305, chess.BISHOP: 330, chess.ROOK: 500, chess.QUEEN: 900, chess.KING: 10_000}
NON_PAWN_PIECE_TYPES = [chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN]


class Board(chess.Board, object):

    def __init__(self, fen=chess.STARTING_FEN, chess960=False):
        self._phase = {}
        self._squares_to_attackers_and_defenders = {}
        super(Board, self).__init__(fen=fen, chess960=chess960)

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

    # Todo: Not considering battery attackers that are pinned?
    def get_pinned_attackers_and_defenders(self, piece):
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
    def get_first_attackers_and_defenders(self, square: chess.Square) -> (List[chess.Square], List[chess.Square]):
        defend_color = self.color_at(square)
        attackers = [attacker for attacker in self.attackers(not defend_color, square) if chess_util.can_piece_capture(self, attacker, square)]
        defenders = [attacker for attacker in self.attackers(defend_color, square) if chess_util.can_piece_capture(self, attacker, square)]
        return attackers, defenders
    
    # Get second attackers and defenders - the attackers and defenders who can't move to square first
    # i.e. pieces that may be in a battery or are pinned
    # Technically, pinned pieces could be first attackers or defenders
    def get_second_attackers_and_defenders(self, square, first_attackers, first_defenders):
        defend_color = self.color_at(square)
        second_attackers = chess_util.get_battery_attackers(self, square, not defend_color, first_attackers)
        second_defenders = chess_util.get_battery_attackers(self, square, defend_color, first_defenders)

        pinned_attackers, pinned_defenders = self.get_pinned_attackers_and_defenders(square)
        second_attackers += pinned_attackers
        second_defenders += pinned_defenders

        # Todo: Is there a better way to solve this?
        # Need to check if there are batteries being formed with pinned attackers and defenders as well
        second_attackers += self.get_battery_attackers(square, not defend_color, pinned_attackers)
        second_defenders += self.get_battery_attackers(square, defend_color, pinned_defenders)
        return second_attackers, second_defenders

    def get_attackers_and_defenders(self, piece: chess.Square) -> \
        (List[chess.Square], List[chess.Square], List[chess.Square], List[chess.Square]):
        if piece not in self._squares_to_attackers_and_defenders:
            first_attackers, first_defenders = self.get_first_attackers_and_defenders(piece)
            first_attackers.sort(key=lambda piece:PIECE_TYPES_TO_VALUES[self.piece_type_at(piece)])
            first_defenders.sort(key=lambda piece:PIECE_TYPES_TO_VALUES[self.piece_type_at(piece)])
            second_attackers, second_defenders = chess_util.get_second_attackers_and_defenders(self, piece, first_attackers, first_defenders)
            self._squares_to_attackers_and_defenders[piece] = first_attackers, second_attackers, first_defenders, second_defenders
        return self._squares_to_attackers_and_defenders[piece]
