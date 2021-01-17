""" 
SIMPLE CHESS ENGINE
This class is responsible for stroring all the information about the current state of a chess game

It will also be responsible for determining the valid moves at the current state.
It will also keep a move lop

"""

from typing import Sequence


class GameState():
    def __init__(self):
        """
        Board is an 8x8 2d list, eadcj element of te list has 2 characters.
        The firest character represents the color of the piece; 'b' or 'w'
        The second character represents the type of the piece, 'K', 'Q', 'R', 'B', 'N', or 'P'
        "--" represents an empty space with no piece
        """
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"], #row = 0 || rank = 8 
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"], #row = 1 || rank = 7
            ["--", "--", "--", "--", "--", "--", "--", "--"], #row = 2 || rank = 6
            ["--", "--", "--", "--", "--", "--", "--", "--"], #row = 3 || rank = 5
            ["--", "--", "--", "--", "--", "--", "--", "--"], #row = 4 || rank = 4
            ["--", "--", "--", "--", "--", "--", "--", "--"], #row = 5 || rank = 3
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"], #row = 6 || rank = 2
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]  #row = 7 || rank = 1
        ]

        self.moveFunctions = {'p': self.get_pawn_moves, 'R': self.get_rook_moves, 'N': self.get_knight_moves,
                              'B': self.get_bishop_moves, 'Q': self.get_queen_moves, 'K': self.get_king_moves}

        self.whiteToMove = True
        self.moveLog = []

        self.whiteKingLocation = (7,4)
        self.blackKingLocation = (0,4)
        self.checkMate = False
        self.staleMate = False
        self.enpassantPossible = () #coordinates for the square where en passant capture is possible
        self.currentCastlingRight = CastleRights(True, True, True, True)
        self.castleRightsLog = [CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks, 
                                            self.currentCastlingRight.wqs, self.currentCastlingRight.bqs)]

    def make_move(self, move):
        """ 
        Function that will take a MOVE as a parameter and executes it 
        N.B: this will not work for castling, pawn promotion, and en-passant
        """
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move) #log the move so we can undo it later
        self.whiteToMove = not self.whiteToMove #swap players turn
        #update the King location after being moved
        if move.pieceMoved == "wK":
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == "bK":
            self.blackKingLocation = (move.endRow, move.endCol)
        
        #pawn Promotion
        if move.isPawnPromotion:
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + 'Q'
        
        #en passant move
        if move.isEnpassantMove:
            self.board[move.startRow][move.endCol] = '--' #capture the pawn
        #update enpassantPossible variable:
        if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2:
            self.enpassantPossible = ((move.startRow + move.endRow)//2, move.startCol)
        else:
            self.enpassantPossible = ()
        
        #Make castle move
        if move.isCastleMove:
            if move.endCol - move.startCol == 2: #kingside castle move
                self.board[move.endRow][move.endCol-1] = self.board[move.endRow][move.endCol+1] #move the rook (1 square away from the click move)
                self.board[move.endRow][move.endCol+1 ] = '--'
            else: #queenside castle move
                self.board[move.endRow][move.endCol+1] = self.board[move.endRow][move.endCol-2] #move the rook (2 square away from the click move)
                self.board[move.endRow][move.endCol-2 ] = '--'

        #update castling rights - whenever it is a rook or a king move
        self.update_castle_rights(move)
        self.castleRightsLog.append(CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks, 
                                                self.currentCastlingRight.wqs, self.currentCastlingRight.bqs))

    def undo_move(self):
        """
        Undo the last move made
        """
        if len(self.moveLog) != 0 : #Make sur that there is a move to undo
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove #swith turns back
            #update the King location after being moved
            if move.pieceMoved == "wK":
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == "bK":
                self.blackKingLocation = (move.startRow, move.startCol)
            #undo the enpassant move
            if move.isEnpassantMove:
                self.board[move.endRow][move.endCol] = '--' #leave lending square empty
                self.board[move.startRow][move.endCol] = move.pieceCaptured
                self.enpassantPossible = (move.endRow, move.endCol)
            #undo a 2 square pawn advance
            if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2:
                self.enpassantPossible = ()
            
            #Undo castling rights
            self.castleRightsLog.pop() #Get rid of the new castling right
            new_Rights = self.castleRightsLog[-1] #set the current state rights to the last one in the list
            self.currentCastlingRight = CastleRights(new_Rights.wks, new_Rights.bks, new_Rights.wqs, new_Rights.bqs)
            #undo the castling move
            if move.isCastleMove:
                if move.endCol - move.startCol == 2: #kingside
                    self.board[move.endRow][move.endCol+1] = self.board[move.endRow][move.endCol-1]
                    self.board[move.endRow][move.endCol-1] = '--'
                else: #queenside
                    self.board[move.endRow][move.endCol-2] = self.board[move.endRow][move.endCol+1]
                    self.board[move.endRow][move.endCol+1] = '--'


    def update_castle_rights(self, move):
        '''
        Update the castle rights given by the move
        '''
        if move.pieceMoved == 'wK':
            self.currentCastlingRight.wks = False
            self.currentCastlingRight.wqs = False
        elif move.pieceMoved == 'bK':
            self.currentCastlingRight.bks = False
            self.currentCastlingRight.bqs = False
        elif move.pieceMoved == 'wR':
            if move.startRow == 7:
                if move.startCol == 0: #left rook
                    self.currentCastlingRight.wqs = False
                elif move.startCol == 7: #right rook
                    self.currentCastlingRight.wks = False
        elif move.pieceMoved == 'bR':
            if move.startRow == 0:
                if move.startCol == 0: #left rook
                    self.currentCastlingRight.bqs = False
                elif move.startCol == 7: #right rook
                    self.currentCastlingRight.bks = False
        
    def get_valid_moves(self):
        '''
        Function that will general ONLY the valid moves
        '''
        temp_enpassant_possible = self.enpassantPossible #save the value in a temp parameter to avoid to have it changed
        temp_castle_rights = CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                        self.currentCastlingRight.wqs, self.currentCastlingRight.bqs)
        #1.) generate all possible moves
        moves = self.get_all_possible_moves()
        if self.whiteToMove:
            self.get_castle_moves(self.whiteKingLocation[0], self.whiteKingLocation[1], moves)
        else:
            self.get_castle_moves(self.blackKingLocation[0], self.blackKingLocation[1], moves)
        #2.) for each move, make the move
        for i in range(len(moves)-1, -1, -1): #when removing from a list go backwards through that list
            self.make_move(moves[i])            
            #3.) generate all opponent's moves            
            #4.) for each of your opponent's moves, see if they attack your king
            self.whiteToMove = not self.whiteToMove # because make_move switch the turn, 
                                                    # we need to switch back to the player turn
                                                    # to verify opponent possible moves before 
                                                    # giving him the turn
            if self.in_Check(): #if the move make the king in check
                moves.remove(moves[i])
            self.whiteToMove = not self.whiteToMove # give the turn to the opponent
            self.undo_move()
        if len(moves) == 0: #either checkmate or stalemate
            if self.in_Check():
                self.checkMate = True
            else:
                self.staleMate = True
        else:
            self.checkMate = False
            self.staleMate = False
        
        self.enpassantPossible = temp_enpassant_possible #Reset the value back
        self.currentCastlingRight = temp_castle_rights
        #5.) if they do attack your king, not a valid move        
        return moves #for now we will not worry about checks

    def in_Check(self):
        '''
        Function that will determine if the current player is in check
        '''
        if self.whiteToMove:
            return self.square_under_attack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        else:
            return self.square_under_attack(self.blackKingLocation[0], self.blackKingLocation[1])

    def square_under_attack(self, r, c):
        '''
        Determine if the enemy can attack the square r,c
        '''
        self.whiteToMove = not self.whiteToMove #switch to the opponent move, to see their possible moves
        opp_Moves = self.get_all_possible_moves()
        self.whiteToMove = not self.whiteToMove #swith back to the player turn
        for move in opp_Moves:
            if move.endRow == r and move.endCol == c : #square r,c is under attack                
                return True
        return False
        
    def get_all_possible_moves(self):
        """
        All moves without considering checks
        """
        moves = []
        for row in range(len(self.board)):  #number of rows
            for column in range (len(self.board[row])): #number of columns in given row
                turn = self.board[row][column][0] #if it is the turn of white or black turn. The '[0]' takes the first later of the element in the matrix 'wR' -> 'w'
                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece = self.board[row][column][1]
                    self.moveFunctions[piece](row,column,moves) #call the appropriate move function based on piece type
        return moves  
    """
    All the functions to make the pawn moves
    """
    def chess_moves(self, r, c, moves, directions): # to define the precise movement of the piece
        """
        r_m : vertical movement (+ : top || - : bottom)
        c_m : horizontal movement (+ : right || - : left)
        """         
        color_enemy = "b" if self.whiteToMove else "w" 
        for d in directions:
            end_row = r + d[0]
            end_col = c + d[1]

            if 0 <= end_col < 8 and 0 <= end_row < 8:
                end_piece = self.board[end_row][end_col] #piece at the position
                if end_piece == "--": #if the case is empty
                    moves.append(Move((r, c), (end_row, end_col), self.board))
                elif end_piece[0] == color_enemy: #if at this case we have an enemy piece to capture
                    moves.append(Move((r, c), (end_row, end_col), self.board))
    
    def chess_moves_long(self, r, c, moves, d_max, directions): #To define the movement for the pieces that can make long movement
        """
        r_m : vertical movement (+ : top || - : bottom)
        c_m : horizontal movement (+ : right || - : left)
        """ 
        color_enemy = "b" if self.whiteToMove else "w" 
        for d in directions:
            for i in range (1, d_max+1):  #Loop among the maximal displacement distance of the pawn
                end_row = r + d[0] * i
                end_col = c + d[1] * i   
                if 0<= end_col < 8 and  0 <= end_row< 8:  #on board
                    end_piece = self.board[end_row][end_col]
                    if end_piece == "--": #empty case
                        moves.append(Move((r, c), (end_row, end_col), self.board))                            
                    elif end_piece[0] == color_enemy: #enemy piece to capture
                        moves.append(Move((r, c), (end_row, end_col), self.board))                        
                        break #we can't go behind the piece
                    else: #friendly piece -> invalid case
                        break #we can't go behind the piece
                else: #off board
                    break 
    '''
    All the pawn moves
    '''
    def get_pawn_moves(self, r, c, moves):                
        """
        Get all the (p)awn moves for the pawn lovated at row, column and add these moves to the list
        """
        if self.whiteToMove: #white pawn moves
            if self.board[r-1][c] == "--": #1 square pawn advance
                moves.append(Move((r,c), (r-1,c), self.board))
                if r == 6 and self.board[r-2][c] == "--" : #2 square pawn advance (the pawn to move need to be at the raw '6' (ranks 2)
                    moves.append(Move((r,c), (r-2,c), self.board))
            if c-1 >= 0: #capture to the left
                if self.board[r-1][c-1][0] == 'b': #enemy piece to capture
                    moves.append(Move((r,c), (r-1,c-1), self.board))
                elif (r-1, c-1) == self.enpassantPossible:
                    moves.append(Move((r,c), (r-1,c-1), self.board, isEnpassantMove= True))

            if c+1 < 8: #capture to the right
                if self.board[r-1][c+1][0] == 'b': #enemy piece to capture
                    moves.append(Move((r,c), (r-1,c+1), self.board))
                elif (r-1, c+1) == self.enpassantPossible:
                    moves.append(Move((r,c), (r-1 , c+1), self.board, isEnpassantMove = True))

        elif not self.whiteToMove: #black pawn moves
            if self.board[r+1][c] == "--": #1 square pawn advance
                moves.append(Move((r,c), (r+1,c), self.board))
                if r == 1 and self.board[r+2][c] == "--" : #2 square pawn advance (the pawn to move need to be at the raw '6' (ranks 2)
                    moves.append(Move((r,c), (r+2,c), self.board))
            if c-1 >= 0: #capture to the left
                if c-1 >= 0 and self.board[r+1][c-1][0] == 'w': #enemy piece to capture
                    moves.append(Move((r,c), (r+1,c-1), self.board))
            if c+1 < 8: #capture to the right
                if self.board[r+1][c+1][0] == 'w': #enemy piece to capture
                    moves.append(Move((r,c), (r+1,c+1), self.board))
        #add pawn promotion

    def get_rook_moves(self, r, c, moves):                
        """
        Get all the (R)ook moves for the rook lovated at row, column and add these moves to the list
        """    
        directions = ((-1,0),(0,-1),(1,0),(0,1)) #Up, left, down, right (straight directions)
        self.chess_moves_long(r, c, moves, 7, directions) # #move like a (R)ook   

    def get_knight_moves(self, r, c, moves):
        """
        Get all the k(N)ight moves for the rook lovated at row, column and add these moves to the list
        The k(N)ight can move in a L shape : 2 vertical - 1 horizontal OR 1 vertical - 2 horizontal
        """
        knight_moves = ((-2,-1),(-2,1),(2,-1),(2,1),(-1,-2),(-1,2),(1,2),(1,-2)) #knight positions     
        self.chess_moves(r, c, moves, knight_moves) #2 vertical and 1 on the side
                   
    def get_bishop_moves(self, r, c, moves):
        """
        Get all the (B)ishop moves for the rook lovated at row, column and add these moves to the list
        The bishop can move in the diagonal direction 
        """
        directions = ((-1,-1),(-1,1),(1,-1),(1,1)) #for diagonals
        self.chess_moves_long(r, c, moves, 7, directions) # #move like a (R)ook
          
    def get_queen_moves(self, r, c, moves):
        """
        Get all the (Q)ueen moves for the rook lovated at row, column and add these moves to the list
        The Quenn can go forward from 7 cases in all the direction. So the Queen can move as a (B)ishop and a (R)ook
        """
        directions = ((-1,-1),(-1,1),(1,-1),(1,1),(-1,0),(0,-1),(1,0),(0,1)) #for diagonals and straight directions 
        self.chess_moves_long(r, c, moves, 7, directions) 
                    
    def get_king_moves(self, r, c, moves):
        """
        Get all the (K)ing moves for the rook lovated at row, column and add these moves to the list
        """
        king_Moves = ((-1,-1),(-1,1),(1,-1),(1,1),(-1,0),(0,-1),(1,0),(0,1)) #for diagonals and straight directions 
        self.chess_moves(r, c, moves, king_Moves) 
        # ally_color = "w" if self.whiteToMove else "b"
        # for row_king_moves, col_king_moves in king_Moves:
        #     endRow = r + row_king_moves
        #     endCol = c + col_king_moves
        #     if 0 <= endRow < 8 and 0 <= endCol < 8:
        #         endPiece = self.board[endRow][endCol]
        #         if endPiece[0] != ally_color: # not an ally piece (empty or enemy piece)
        #             moves.append(Move((r,c), (endRow, endCol), self.board))   
    
    def get_castle_moves(self, r, c, moves):
        '''
        Generate all valid astle moves for the king at (r, c) and add them to the list of moves
        '''
        if self.square_under_attack(r, c):
            return #can't castle while we are in check
        if (self.whiteToMove and self.currentCastlingRight.wks) or (not self.whiteToMove and self.currentCastlingRight.bks) :
            self.get_king_side_castle_moves(r,c,moves)
        if (self.whiteToMove and self.currentCastlingRight.wqs) or (not self.whiteToMove and self.currentCastlingRight.bqs) :
            self.get_queen_side_castle_moves(r,c,moves)
    
    def get_king_side_castle_moves(self, r, c, moves):        
        if self.board[r][c+1] == '--' and self.board[r][c+2] == '--':
            if not self.square_under_attack(r, c+1) and not self.square_under_attack(r, c+2):
                moves.append(Move((r, c), (r, c+2), self.board, isCastleMove = True))
                
    def get_queen_side_castle_moves(self, r, c, moves):       
        if self.board[r][c-1] == '--' and self.board[r][c-2] == '--' and self.board[r][c-3] == '--':
            if not self.square_under_attack(r, c-1) and not self.square_under_attack(r, c-2):
                moves.append(Move((r, c), (r, c-2), self.board, isCastleMove = True))
                

class CastleRights():
    def __init__(self, wks, bks, wqs, bqs):
        '''
        wks : white king side
        bks : black king side
        wqs : white queen side
        bqs : black queen side
        '''
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs

class Move():
    """
    A class that will keep track of the movement of the chess pieces
    """ 
    # maps keys to values
    # keys : value
    ranks_to_rows = {"1": 7, "2": 6, "3": 5, "4": 4,
                     "5": 3, "6": 2, "7": 1, "8": 0} #row = 0 is the top row of the chess board
    rows_to_ranks = {v:k for k, v in ranks_to_rows.items()} #reverse the dictionnary rows_to_ranks
    files_to_column = {"a": 0, "b": 1, "c": 2, "d": 3,
                       "e": 4, "f": 5, "g": 6, "h": 7}
    column_to_files = {v:k for k,v in files_to_column.items()} #reverse the dictionnary files_to_column

    def __init__(self, start_sq, end_sq, board, isEnpassantMove = False, isCastleMove = False ) :
        self.startRow = start_sq[0]
        self.startCol = start_sq[1]
        self.endRow = end_sq[0]
        self.endCol = end_sq[1]
        self.pieceMoved = board[self.startRow][self.startCol] #determine the first square selected and thus, the piece that needs to be moved.
        self.pieceCaptured = board[self.endRow][self.endCol] #determine the second square selected and thus, the piece that will be captured.
        #pan promotion      
        self.isPawnPromotion = (self.pieceMoved == 'wp' and self.endRow == 0) or (self.pieceMoved == 'bp' and self.endRow == 7)
        #En passant
        self.isEnpassantMove = isEnpassantMove
        if self.isEnpassantMove:
            self.pieceCaptured = 'wp' if self.pieceMoved == 'bp' else 'bp'
        #castle move
        self.isCastleMove = isCastleMove

        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol #we create a ID for the case in the shape of XXXX -> 6444. 

    def __eq__(self, other):
        '''
        Overriding the equals method
        '''
        if isinstance(other, Move): #Verify that the elements 'other' and 'Move' are the same instance, type
            return self.moveID == other.moveID   
        return False 
    
    def get_chess_notation(self):
        """ you can add to make this like real chess notation """
        return self.get_rank_file(self.startRow, self.startCol) + self.get_rank_file(self.endRow, self.endCol)

    def get_rank_file(self, row, column):
        """ To help to make a real chess notation """
        return self.column_to_files[column] + self.rows_to_ranks[row]
