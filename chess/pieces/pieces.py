import pygame

pygame.init()


class Check:
    def __init__(self, king, pieces):
        self.king = king
        self.pieces = pieces

    def double_check(self):
        return len(self.pieces) == 2

    @classmethod
    def in_path(cls, king_square, piece_square, move):
        if move == king_square:
            return False
        if king_square.row == piece_square.row:
            # horizontal
            if move.row == king_square.row:
                return max(king_square.column, piece_square.column) >= move.column >= min(king_square.column,
                                                                                          piece_square.column)
        elif king_square.column == piece_square.column:
            # vertical
            if move.column == king_square.column:
                return max(king_square.row, piece_square.row) >= move.row >= min(king_square.row, piece_square.row)
        else:
            # diagonal
            m = (king_square.row - piece_square.row) // (king_square.column - piece_square.column)
            c = - m * king_square.column + king_square.row
            if move.row == m * move.column + c:
                h_row, l_row = max(king_square.row, piece_square.row), min(king_square.row, piece_square.row)
                h_col, l_col = max(king_square.column, piece_square.column), min(king_square.column,
                                                                                 piece_square.column)
                return h_row >= move.row >= l_row and h_col >= move.column >= l_col
            else:
                return False

    def restricted(self, move):
        if isinstance(self.pieces[0], Knight):
            if move == self.pieces[0].square:
                return False
            else:
                return True
        if move == self.pieces[0].square:
            return False
        return not self.in_path(self.king.square, self.pieces[0].square, move)


class Pin:
    def __init__(self, king, pinned, pinning):
        self.king = king
        self.pinned = pinned
        self.pinning = pinning
        self.check = Check(king, [pinning])

    @classmethod
    def in_path(cls, pin_square, pinning_square, king_square):
        if pin_square.row == pinning_square.row:
            # horizontal
            return king_square.row == pin_square.row
        elif pin_square.column == pinning_square.column:
            # vertical
            return king_square.column == pin_square.column
        else:
            # diagonal
            m = (pin_square.row - pinning_square.row) // (pin_square.column - pinning_square.column)
            c = - m * pin_square.column + pin_square.row
            return king_square.row == m * king_square.column + c

    def restricted(self, move):
        return self.check.restricted(move)


class Piece:
    images = {
        'Pawn': [pygame.image.load(r'chess_pieces/black_pawn.jpg'), pygame.image.load(r'chess_pieces/white_pawn.jpg')],
        'Knight': [pygame.image.load(r'chess_pieces/black_knight.jpg'), pygame.image.load(
            r'chess_pieces/white_knight.JPG')],
        'Bishop': [pygame.image.load(r'chess_pieces/black_bishop.png'), pygame.image.load(
            r'chess_pieces/white_bishop.jpg')],
        'Rook': [pygame.image.load(r'chess_pieces/black_rook.jpg'), pygame.image.load(r'chess_pieces/white_rook.jpg')],
        'Queen': [pygame.image.load(r'chess_pieces/black_queen.png.jpg'), pygame.image.load(
            r'chess_pieces/white_queen.jpg')],
        'King': [pygame.image.load(r'chess_pieces/black_king.jpg'), pygame.image.load(r'chess_pieces/white_king.jpg')]
    }
    colors = {'Black': 0, 'White': 1}

    def __init__(self, board, color, square):
        self.board = board
        self.color = color
        self.square = square
        self.img = None

    def __repr__(self):
        return f'{self.color} {self.__class__} {self.square}'

    def pinned(self):
        """
        This method will determine whether a piece is pinned and find the path of the pin
        Path {}
        :return: The path on which the piece is restricted
        """
        king = self.board.kings[self.color]
        dummy_king = DummyKing(self.board, self.color, self.square)
        check = dummy_king.in_check(self.square)
        if check is None:
            return None

        for piece in check.pieces:
            if isinstance(piece, Knight):
                continue
            if Pin.in_path(self.square, piece.square, king.square):
                return Pin(king, self, piece)

    def move(self, square):
        self.square.piece = None
        self.square = square
        square.piece = self

    def possible_moves(self, check, check_pin=True):
        """
        This methods finds the legal moves for a piece
        :param check:
        :param check_pin:
        :return: a list of legal moves
        """
        return []

    def add_if_legal(self, moves, move, check, pin):
        if move is None:
            return False
        if check is not None and check.restricted(move):
            return True
        if pin is not None and pin.restricted(move):
            return True

        flag = True
        if move.piece is None:
            moves.append(move)
        elif move.piece.color != self.color:
            moves.append(move)
            flag = False
        else:
            flag = False

        return flag


# TODO: implement en passant and promotion
class Pawn(Piece):
    def __init__(self, board, color, square):
        super().__init__(board, color, square)
        self.img = self.images['Pawn'][Piece.colors[color]]

    def possible_moves(self, check, check_pin=True):
        pin = self.pinned() if check_pin else None

        moves = []
        i, j = self.square.row, self.square.column
        front_square = left_diagonal = right_diagonal = extra_square = None

        if self.color == 'White':
            front_square = self.board.get_square(i + 1, j)
            left_diagonal = self.board.get_square(i + 1, j - 1)
            right_diagonal = self.board.get_square(i + 1, j + 1)
            if i == 2:
                extra_square = self.board.get_square(i + 2, j)
        elif self.color == 'Black':
            front_square = self.board.get_square(i - 1, j)
            left_diagonal = self.board.get_square(i - 1, j + 1)
            right_diagonal = self.board.get_square(i - 1, j - 1)
            if i == 7:
                extra_square = self.board.get_square(i - 2, j)

        if front_square is not None and front_square.piece is None:
            if check is None or not check.restricted(front_square):
                if pin is None or not pin.restricted(front_square):
                    moves.append(front_square)
        if left_diagonal is not None and left_diagonal.piece is not None:
            if left_diagonal.piece.color != self.color:
                if check is None or not check.restricted(left_diagonal):
                    if pin is None or not pin.restricted(left_diagonal):
                        moves.append(left_diagonal)
        if right_diagonal is not None and right_diagonal.piece is not None:
            if right_diagonal.piece.color != self.color:
                if check is None or not check.restricted(right_diagonal):
                    if pin is None or not pin.restricted(right_diagonal):
                        moves.append(right_diagonal)
        if extra_square is not None and extra_square.piece is None:
            if check is None or not check.restricted(extra_square):
                if pin is None or not pin.restricted(extra_square):
                    moves.append(extra_square)

        return moves


class Knight(Piece):
    def __init__(self, board, color, square):
        super().__init__(board, color, square)
        self.img = self.images['Knight'][Piece.colors[color]]

    def possible_moves(self, check, check_pin=True):
        pin = self.pinned() if check_pin else None

        moves = []

        i, j = self.square.row, self.square.column

        squares = [(i - 2, j - 1), (i - 2, j + 1), (i + 2, j + 1), (i + 2, j - 1), (i + 1, j + 2), (i - 1, j + 2),
                   (i + 1, j - 2), (i - 1, j - 2)]

        for r, c in squares:
            move = self.board.get_square(r, c)
            self.add_if_legal(moves, move, check, pin)

        return moves


class Bishop(Piece):
    def __init__(self, board, color, square):
        super().__init__(board, color, square)
        self.img = self.images['Bishop'][Piece.colors[color]]

    def possible_moves(self, check, check_pin=True):
        pin = self.pinned() if check_pin else None

        moves = []

        # right-up diagonal
        i, j = self.square.row + 1, self.square.column + 1
        while i <= 8 and j <= 8:
            move = self.board.get_square(i, j)

            if not self.add_if_legal(moves, move, check, pin):
                break

            i += 1
            j += 1

        # left-down diagonal
        i, j = self.square.row - 1, self.square.column - 1
        while i >= 1 and j >= 1:
            move = self.board.get_square(i, j)

            if not self.add_if_legal(moves, move, check, pin):
                break

            i -= 1
            j -= 1

        # left-up diagonal
        i, j = self.square.row + 1, self.square.column - 1
        while i <= 8 and j >= 1:
            move = self.board.get_square(i, j)

            if not self.add_if_legal(moves, move, check, pin):
                break

            i += 1
            j -= 1

        # right-down diagonal
        i, j = self.square.row - 1, self.square.column + 1
        while i >= 1 and j <= 8:
            move = self.board.get_square(i, j)

            if not self.add_if_legal(moves, move, check, pin):
                break

            i -= 1
            j += 1

        return moves


class Rook(Piece):
    def __init__(self, board, color, square):
        super().__init__(board, color, square)
        self.img = self.images['Rook'][Piece.colors[color]]

    def possible_moves(self, check, check_pin=True):
        pin = self.pinned() if check_pin else None

        moves = []

        # up
        i, j = self.square.row + 1, self.square.column
        while i <= 8:
            move = self.board.get_square(i, j)

            if not self.add_if_legal(moves, move, check, pin):
                break

            i += 1

        # down
        i, j = self.square.row - 1, self.square.column
        while i >= 0:
            move = self.board.get_square(i, j)

            if not self.add_if_legal(moves, move, check, pin):
                break

            i -= 1

        # left
        i, j = self.square.row, self.square.column - 1
        while i >= 1:
            move = self.board.get_square(i, j)

            if not self.add_if_legal(moves, move, check, pin):
                break

            j -= 1

        # right
        i, j = self.square.row, self.square.column + 1
        while i <= 8:
            move = self.board.get_square(i, j)

            if not self.add_if_legal(moves, move, check, pin):
                break

            j += 1

        return moves


class Queen(Piece):
    def __init__(self, board, color, square):
        super().__init__(board, color, square)
        self.img = self.images['Queen'][Piece.colors[color]]

    def possible_moves(self, check, check_pin=True):
        dummy_bishop = Bishop(self.board, self.color, self.square)
        dummy_rook = Rook(self.board, self.color, self.square)

        return dummy_bishop.possible_moves(check) + dummy_rook.possible_moves(check)


class Dummy(Knight, Bishop, Rook, Queen):
    def __init__(self, board, color, square, piece, king):
        super().__init__(board, color, square)
        self.type = piece
        self.king = king

    def add_if_legal(self, moves, move, check, pin):
        if move is None:
            return False

        if move.piece is None:
            return True
        elif move.piece.color != self.color:
            moves.append(move)
            return False
        elif move.piece == self.king:
            return True
        else:
            return False

    def possible_moves(self, check, check_pin=False):
        if self.type == Queen:
            dummy_bishop = Dummy(self.board, self.color, self.square, Bishop, self.king)
            dummy_rook = Dummy(self.board, self.color, self.square, Rook, self.king)
            return dummy_bishop.possible_moves(check, check_pin) + dummy_rook.possible_moves(check, check_pin)
        return self.type.possible_moves(self, check, check_pin)


# TODO: add castling
class King(Piece):
    def __init__(self, board, color, square):
        super().__init__(board, color, square)
        self.img = self.images['King'][Piece.colors[color]]

    def checked_by(self, square, piece):
        dummy = Dummy(self.board, self.color, square, piece, self)
        moves = dummy.possible_moves(None)
        for move in moves:
            if isinstance(move.piece, piece) and move.piece.color != self.color:
                return move.piece

        return None

    def opposition(self, square):
        i, j = square.row, square.column
        squares = [(i - 1, j - 1), (i - 1, j), (i - 1, j + 1), (i, j + 1), (i + 1, j + 1), (i + 1, j), (i + 1, j - 1),
                   (i, j - 1)]

        for r, c in squares:
            move = self.board.get_square(r, c)
            if move is None:
                continue
            if isinstance(move.piece, King) and move.piece.color != self.color:
                return True

        return False

    def in_check(self, square):
        checking_pieces = []
        for piece in [Knight, Bishop, Rook, Queen]:
            checking_piece = self.checked_by(square, piece)
            if checking_piece is not None:
                checking_pieces.append(checking_piece)

        right = left = None

        if self.color == 'White':
            right = self.board.get_square(square.row + 1, square.column + 1)
            left = self.board.get_square(square.row + 1, square.column - 1)
        elif self.color == 'Black':
            right = self.board.get_square(square.row - 1, square.column + 1)
            left = self.board.get_square(square.row - 1, square.column - 1)

        if right is not None and isinstance(right.piece, Pawn):
            if right.piece.color != self.color:
                checking_pieces.append(right.piece)
        if left is not None and isinstance(left.piece, Pawn):
            if left.piece.color != self.color:
                checking_pieces.append(left.piece)

        return None if len(checking_pieces) == 0 else Check(self, checking_pieces)

    def add_if_legal(self, moves, move, check, pin):
        if move is None:
            return
        if move.piece is None or move.piece.color != self.color:
            if self.in_check(move) is None and not self.opposition(move):
                moves.append(move)

    def possible_moves(self, check, check_pin=True):
        moves = []

        i, j = self.square.row, self.square.column

        squares = [(i - 1, j - 1), (i - 1, j), (i - 1, j + 1), (i, j + 1), (i + 1, j + 1), (i + 1, j), (i + 1, j - 1),
                   (i, j - 1)]

        for r, c in squares:
            move = self.board.get_square(r, c)
            self.add_if_legal(moves, move, check, None)

        return moves


class DummyKing(King):
    def checked_by(self, square, piece):
        dummy = Dummy(self.board, self.color, square, piece, self)
        moves = dummy.possible_moves(None)
        pieces = []
        for move in moves:
            if isinstance(move.piece, piece) and move.piece.color != self.color:
                pieces.append(move.piece)

        return pieces

    def in_check(self, square):
        checking_pieces = []
        for piece in [Bishop, Rook, Queen]:
            checking_piece = self.checked_by(square, piece)
            checking_pieces.extend(checking_piece)

        return None if len(checking_pieces) == 0 else Check(self, checking_pieces)