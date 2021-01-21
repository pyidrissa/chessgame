import ai.chessAI as AI

""" 
ADVANCED CHESS ENGINE
This class is responsible for stroring all the information about the current state of a chess game

It will also be responsible for determining the valid moves at the current state.
It will also keep a move lop

"""

class GameState():
    def __init__(self):
        """
        Board is an 8x8 2d list, each element of te list has 2 characters.
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
        self.absPawnValue = {'p': 10, 'R': 50, 'N': 30,
                              'B': 30, 'Q': 90, 'K': 900}

        self.whiteToMove = True
        self.moveLog = []
        self.moveMade = False
        self.whiteKingLocation = (7,4)
        self.blackKingLocation = (0,4)
        
        #Not in his code
        self.inCheck = False
        self.pins = [] #pins are the pawns that can't move because, they would live the king into a check position
        self.checks = []
        self.checkMate = False
        self.staleMate = False
        #note in his code

        self.enpassantPossible = () #sqaare where en passant capture can happen
        #castling rights
        self.whiteCastleKingside = True
        self.whiteCastleQueenside = True
        self.blackCastleKingside = True
        self.blackCastleQueenside = True
        self.castleRightsLog = [CastleRights(self.whiteCastleKingside, self.blackCastleKingside, 
                                                self.whiteCastleQueenside, self.blackCastleQueenside)]

        #Artificial Intelligence for the Chess Play
        # Working with the class chessAI inside the GameState, allow the evaluation
        # of the chessboard directly when a move is made         
        # self.ai = AI.chessAI(self.board)  #set an AI for this chess board
        # self.ai.evaluate_board() #generate the evaluation of the starting board        


    def make_move(self, move):
        """ 
        Take a move as a parameter and executes it 

        This will not work for castling, pawn promotion, and en-passant
        """
        #self.moveMade = False

        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move) #log the move so we can undo it later
        if self.whiteToMove:
            self.moveMade = True

        self.whiteToMove = not self.whiteToMove #swap players turn
        #update the King's location if moved
        if move.pieceMoved == 'wK':
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == 'bK':
            self.blackKingLocation = (move.endRow, move.endCol)

        #if pawn promotion -> change piece
        if move.pawnPromotion:
            # promotedPiece = input("Promote to Q, R, B or N:") #we can make this part of the ui later
            # promotedPiece = promotedPiece.capitalize() #we capitalize the input to accept q and Q
            # self.board[move.endRow][move.endCol] = move.pieceMoved[0] + promotedPiece 
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + 'Q'

        #if pawn moves twice, next move can capture enpassant
        if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2:
            self.enpassantPossible = ((move.endRow + move.startRow)//2, move.endCol)
        else: 
            self.enpassantPossible = ()
        #en passant move, must update the board to capture the pawn
        if move.enPassant:
            self.board[move.startRow][move.endCol] = '--' #capture the pawn

        #Make castle move
        if move.castle:
            if move.endCol - move.startCol == 2: #kingside castle move
                self.board[move.endRow][move.endCol-1] = self.board[move.endRow][move.endCol+1] #move the rook (1 square away from the click move)
                self.board[move.endRow][move.endCol+1 ] = '--'
            else: #queenside castle move
                self.board[move.endRow][move.endCol+1] = self.board[move.endRow][move.endCol-2] #move the rook (2 square away from the click move)
                self.board[move.endRow][move.endCol-2 ] = '--'           
        #update castling rights - whenever it is a rook or a king move
        self.update_castle_rights(move)
        self.castleRightsLog.append(CastleRights(self.whiteCastleKingside, self.blackCastleKingside, 
                                                self.whiteCastleQueenside, self.blackCastleQueenside))
        
        #Update the chess board evaluation
        #self.ai.adjust_board_values(move.pieceMoved, move.startRow, move.startCol, move.endRow, move.endCol, move.pieceCaptured)
    
    def undo_move(self):
        """
        Undo the last move made
        """

        if len(self.moveLog) != 0 : #Make sur that there is a move to undo
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove #swith turns back
            ## print("WHITE TURN : ", self.whiteToMove, "(UNDO MOVE)")
            #update the King's location if unmoved
            if move.pieceMoved == 'wK':
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == 'bK':
                self.blackKingLocation = (move.startRow, move.startCol)
            #undo enpassant 
            if move.enPassant:
                self.board[move.endRow][move.endCol] = '--' #removes the pawn that was added n the wrong square
                self.board[move.startRow][move.endCol] = move.pieceCaptured #puts the pawn back on the correct square it was capture from
                self.enpassantPossible = (move.endRow, move.endCol) #allow an en passant to happen on the next move
            #if a 2 square pawn advance should make enpassantPossible = () again:
            if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2:
                self.enpassantPossible = ()
            
            #Undo castling rights
            self.castleRightsLog.pop() #Get rid of the new castling right
            new_Rights = self.castleRightsLog[-1] #set the current state rights to the last one in the list
            self.whiteCastleKingside = new_Rights.wks
            self.blackCastleKingside = new_Rights.bks
            self.whiteCastleQueenside = new_Rights.wqs
            self.blackCastleQueenside =  new_Rights.bqs
            #undo the castling move
            if move.castle:
                if move.endCol - move.startCol == 2: #kingside
                    self.board[move.endRow][move.endCol+1] = self.board[move.endRow][move.endCol-1]
                    self.board[move.endRow][move.endCol-1] = '--'
                else: #queenside
                    self.board[move.endRow][move.endCol-2] = self.board[move.endRow][move.endCol+1]
                    self.board[move.endRow][move.endCol+1] = '--'

            #RESET the checkMate and staleMate status when we undo a move
            self.checkMate = False
            self.staleMate = False

        self.moveMade = False

    def update_castle_rights(self, move):
        '''
        Update the castle rights given by the move
        '''
        if move.pieceMoved == 'wK':
            self.whiteCastleKingside = False
            self.whiteCastleQueenside = False
        elif move.pieceMoved == 'bK':
            self.blackCastleKingside = False
            self.blackCastleQueenside = False
        elif move.pieceMoved == 'wR':
            if move.startRow == 7:
                if move.startCol == 0: #left rook
                    self.whiteCastleQueenside = False
                elif move.startCol == 7: #right rook
                    self.whiteCastleKingside = False
        elif move.pieceMoved == 'bR':
            if move.startRow == 0:
                if move.startCol == 0: #left rook
                    self.blackCastleQueenside = False
                elif move.startCol == 7: #right rook
                    self.blackCastleKingside = False

    def get_valid_moves(self): #verify that the move can be done without living the King in check position
        """
        All moves considering check
        """
        moves = []        
        self.inCheck, self.pins, self.checks = self.check_for_pins_and_checks()
        if self.whiteToMove: #white turn
            king_row = self.whiteKingLocation[0]
            king_col = self.whiteKingLocation[1]
        else: #black turn
            king_row = self.blackKingLocation[0]
            king_col = self.blackKingLocation[1]

        if self.inCheck:
            if len(self.checks) == 1 : #only 1 check -> block the check or move the king
                moves = self.get_all_possible_moves()
                #To block a check you must move a piece into one of the squares between 
                #the enemy piece and the king
                check = self.checks[0] #information about the check
                check_row = check[0]
                check_col = check[1]
                piece_checking = self.board[check_row][check_col] #enemy piece causing the check
                valid_squares = [] #the squares where that pieces can move to 
                #if knight, must capture knight or move king, other pieces can be blocked
                if piece_checking[1] == 'N':
                    #IF the attacking piece is a k(N)ight, we have to take it
                    valid_squares = [(check_row, check_col)]
                else: 
                    #For the other pieces
                    for i in range(1,8):
                        #check[2] and check[3] are the check directions
                        valid_square = (king_row + check[2] * i, king_col + check[3] * i) 
                        valid_squares.append(valid_square)
                        if valid_square[0] == check_row and valid_square[1] == check_col: 
                            #WHAT we have to do once we get the piece putting the (K)ing in check
                            break #when we reach the attacking piece, we can break the loop
                #get rid of any moves that don't block check or move king
                for i in range(len(moves)-1, -1, -1): 
                    #go through backwards when you are removing from a list as iterating
                    if moves[i].pieceMoved[1] != 'K': 
                        #if the piece moved was not a king -> that piece need to move 
                        #to a valid square to block or capture the enemy piece making a check
                        if (moves[i].endRow, moves[i].endCol) not in valid_squares: 
                            #if the move doesn't protect the (K)ing or allow the (K)ing to move, 
                            #we have to remove it
                            moves.remove(moves[i])
            else: #double check -> king has to move
                self.get_king_moves(king_row, king_col, moves)
        else: #not in check so all moves are fine
            moves = self.get_all_possible_moves()

        self.get_castle_moves(king_row, king_col, moves) #Add the castling moves
        #Now we try to determine if we are in a checkMate or staleMate situation
        if len(moves) == 0: #IF no move is possible         
            if self.inCheck:                
                self.checkMate = True
            else:                
                self.staleMate = True
        else:
            self.checkMate = False
            self.staleMate = False

        return moves
    
    def check_for_pins_and_checks(self):
        """
        This function is the algorithm that will verify the pins and the checks

        pins : pawns that can't move because they will leave the King in a check position
        check : when the King is in a check position
        double check : when we need to move the King
        """
        pins = []
        checks = []
        in_check = False #we start the game with a (Ki)ng not in a check position

        if self.whiteToMove:
            enemy_color = "b"
            ally_color = "w"
            start_row = self.whiteKingLocation[0] #position of the white King
            start_col = self.whiteKingLocation[1] #position of the white King
        else: #black turn to move
            enemy_color = "w"
            ally_color = "b"
            start_row = self.blackKingLocation[0] #position of the white King
            start_col = self.blackKingLocation[1] #position of the white King
        
        #check further from the king position for pins and checks and thus, keep track of pins
        #1) we are going to check in each direction if a pawn can attack the king position
        directions = ((-1,0),(0,-1),(1,0),(0,1),(-1,-1),(-1,1),(1,-1),(1,1))
        for j in range(len(directions)):
            d = directions[j]
            possible_pin = () #reset possible pin
            for i in range (1,8): 
                #we'll focus on the closest case and the further one.
                #we start at 1 because, we'll mutliply the direction by 'i'
                end_row = start_row + d[0] * i
                end_col = start_col + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    end_piece = self.board[end_row][end_col]
                    #First we check is we have a piece protecting our (K)ing
                    if end_piece[0] == ally_color and end_piece[1] != 'K':
                        if possible_pin == () : 
                            #1st allied piece could be pinned because the 
                            #pin couple is empty
                            possible_pin = (end_row, end_col, d[0], d[1])
                            #we gathered the row and col of the piece that should be pin and
                            #the direction from where the attack is comming because, that piece
                            #could move ONLY in this direction. Because the piece will keep the
                            #protecting the (K)ing
                        else: 
                            #2nd allied piece, so no pin or check possible in this direction
                            break
                    #Secondly, we check if our (K)ing is under attack
                    elif end_piece[0] == enemy_color:
                        type = end_piece[1] #determine the type of the piece
                        #In function of the type of the piece, there are different possibilities
                        '''
                        5 possibilities here in this complex conditional
                            (1) orthogonally away from the (K)ing and the piece is a (R)ook
                                -> (0 <= j <= 3 and type == 'R')
                            (2) diagonally away from the (K)ing and the piece is a (B)ishop
                                -> (4 <= j <= 7 and type == 'B')
                            (3) 1 square away diagonally from (K)ing and the piece is a (p)awn
                                -> (i == 1 and type == 'p')
                            (4) any direction and the piece is a (Q)ueen
                                -> (type == 'Q')
                            (5) any direction 1 square away and the piece is a (K)ing 
                                (this is necessary to prevent a king to move to a square 
                                controlled by another king)
                                -> (i == 1 and type == 'K')
                        '''
                        if (0 <= j <= 3 and type == 'R') or \
                            (4 <= j <= 7 and type == 'B') or \
                            ( 
                                (i == 1 and type == 'p') and \
                                (
                                    (enemy_color == 'w' and 6 <= j <= 7) or \
                                    (enemy_color == 'b' and 4 <= j <= 5)
                                )
                            ) or (type == 'Q') or (i == 1 and type == 'K'):
                            if possible_pin == (): 
                                #there are no piece protecting the king, 
                                # so we are in a check position
                                in_check = True
                                #we are in a check position , so we append the row 
                                # and column of the piece making the king in check
                                checks.append((end_row, end_col, d[0], d[1])) 
                                break
                            else: 
                                #piece blocking so we have a pin pawn
                                #because of the piece protecting the (K)ing, we can pin 
                                # the piece and add it to the list of pins elements
                                pins.append(possible_pin)                                 
                                break
                        else: #enemy pieces are not applying a check
                            break
                else: # out the board
                    break 
        
        #2) Check for the k(N)ight movements
        #   Because the knight don't move in the "original" direction, we had to make a 
        #   special case for him by considering his own moves directions
        knight_moves = ((-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1))
        for move in knight_moves:
            end_row = start_row + move[0]
            end_col = start_col + move[1]

            if 0 <= end_row < 8 and 0 <= end_col < 8: #if in the board
                end_piece = self.board[end_row][end_col]
                if end_piece[0] == enemy_color and end_piece[1] == 'K': 
                    #enemy k(N)ight attacking the (K)ing
                    in_check = True
                    checks.append((end_row, end_col, move[0], move[1]))
            else: #out of the board
                break

        return in_check, pins, checks
    
    def square_under_attack(self, r, c):
        """
        Determine if the enemy can attack the square (r,c)
        """
        self.whiteToMove = not self.whiteToMove #switch to opponent's turn
        opponent_moves = self.get_all_possible_moves() #Get the opponent's moves
        self.whiteToMove = not self.whiteToMove #reset the turn

        for move in opponent_moves:
            if move.endRow == r and move.endCol == c:                
                return True        
        return False

    def get_all_possible_moves(self):
        """
        All moves without considering checks
        """
        moves = []
        for row in range(len(self.board)):  #number of rows in the board
            for column in range (len(self.board[row])): 
                #number of columns in a given row in the board
                turn = self.board[row][column][0] 
                #if it is the turn of white or black turn. 
                # The '[0]' takes the first later of the element in the matrix 'wR' -> 'w'
                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece = self.board[row][column][1] 
                    #Bishop, kNight, Rook, Queen, King or pawn
                    self.moveFunctions[piece](row,column,moves) 
                    #call the appropriate move function based on piece type
        return moves  

    '''    All the functions to make the pawn moves    '''
    def chess_moves(self, r, c, moves, directions, piece_pinned): # to define the precise movement of the piece
        """
        r_m : vertical movement (+ : top || - : bottom)
        c_m : horizontal movement (+ : right || - : left)
        """  
        color_enemy = "b" if self.whiteToMove else "w" 
        for d in directions:
            end_row = r + d[0]
            end_col = c + d[1]
            if 0 <= end_col < 8 and 0 <= end_row < 8:
                if not piece_pinned:
                    end_piece = self.board[end_row][end_col] #piece at the position
                    if end_piece == "--": #if the case is empty
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                    elif end_piece[0] == color_enemy: #if at this case we have an enemy piece to capture
                        moves.append(Move((r, c), (end_row, end_col), self.board))
        
    def chess_moves_long(self, r, c, moves, d_max, directions, piece_pinned = False, pin_direction = ()): #To define the movement for the pieces that can make long movement
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
                    if not piece_pinned or pin_direction == d or pin_direction == (-d[0], -d[1]): # -d[0], -d[0]) say that we can move to and away of the piece making the check
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
    '''   All the pawn moves    '''
    def get_pawn_moves(self, r, c, moves):                
        """
        Get all the (p)awn moves for the pawn lovated at row, column and add these moves to the list
        """
        piece_pinned = False
        pin_direction =()
        for i in range (len(self.pins)-1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        if self.whiteToMove:
            moveAmount = -1
            startRow = 6
            backRow = 0
            enemyColor = 'b'
        else: 
            moveAmount = 1
            startRow = 1
            backRow = 7
            enemyColor = 'w'
        pawnPromotion = False
        pawn_capture = False
        
        if self.board[r+moveAmount][c] == "--": #1 square pawn advance
            if not piece_pinned or pin_direction == (moveAmount, 0):
                if r+moveAmount == backRow:
                    pawnPromotion = True
                moves.append(Move((r,c), (r+moveAmount, c), self.board, pawn_promotion = pawnPromotion))
                if r == startRow and self.board[r+2*moveAmount][c] == "--" : #2 square pawn advance (the pawn to move need to be at the raw '6' (ranks 2)
                    moves.append(Move((r,c), (r+2*moveAmount,c), self.board))
            
        if c-1 >= 0: #capture to the left
            if not piece_pinned or pin_direction == (moveAmount,-1):
                if self.board[r+moveAmount][c-1][0] == enemyColor: #enemy piece to capture
                    if r + moveAmount == backRow: # if piece gets to bank rank then it is a pawn promotion
                        pawnPromotion = True
                    moves.append(Move((r,c), (r+moveAmount,c-1), self.board, pawn_promotion = pawnPromotion))

                if (r + moveAmount, c - 1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r+moveAmount, c-1), self.board, en_passant = True))
                
        if c+1 <= 7: #capture to the right
            if not piece_pinned or pin_direction == (moveAmount,1):
                if self.board[r + moveAmount][c + 1][0] == enemyColor: #enemy piece to capture     
                    if r + moveAmount == backRow: # if piece gets to bank rank then it is a pawn promotion
                        pawnPromotion = True           
                    moves.append(Move((r,c), (r+moveAmount, c+1), self.board, pawn_promotion = pawnPromotion))
                if (r + moveAmount, c + 1) == self.enpassantPossible:
                    moves.append(Move((r,c), (r + moveAmount, c+1), self.board, en_passant=True))
        
        return pawn_capture

    def get_rook_moves(self, r, c, moves):                
        """
        Get all the (R)ook moves for the rook lovated at row, column and add these moves to the list
        """    
        piece_pinned = False
        pin_direction =()
        for i in range (len(self.pins)-1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                if self.board[r][c][1] != 'Q': #can't remove queen from pin on rook moves, only remove it on bishop moves
                    self.pins.remove(self.pins[i])
                break

        directions = ((-1,0),(0,-1),(1,0),(0,1)) #Up, left, down, right (straight directions)
        self.chess_moves_long(r, c, moves, 7, directions, piece_pinned, pin_direction) # #move like a (R)ook
        
    def get_knight_moves(self, r, c, moves):
        """
        Get all the k(N)ight moves for the rook lovated at row, column and add these moves to the list
        The k(N)ight can move in a L shape : 2 vertical - 1 horizontal OR 1 vertical - 2 horizontal
        """
        piece_pinned = False
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piece_pinned = True
                self.pins.remove(self.pins[i])
                break
        knight_moves = ((-2,-1),(-2,1),(2,-1),(2,1),(-1,-2),(-1,2),(1,2),(1,-2)) #knight positions     
        self.chess_moves(r, c, moves, knight_moves, piece_pinned) #2 vertical and 1 on the side
                           
    def get_bishop_moves(self, r, c, moves):
        """
        Get all the (B)ishop moves for the rook lovated at row, column and add these moves to the list
        The bishop can move in the diagonal direction 
        """
        piece_pinned = False
        pin_direction =()
        for i in range (len(self.pins)-1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                if self.board[r][c][1] != 'Q': #can't remove queen from pin on rook moves, only remove it on bishop moves
                    self.pins.remove(self.pins[i])
                break

        directions = ((-1,-1),(-1,1),(1,-1),(1,1)) #for diagonals
        self.chess_moves_long(r, c, moves, 7, directions, piece_pinned, pin_direction) # #move like a (R)ook
          
    def get_queen_moves(self, r, c, moves):
        """
        Get all the (Q)ueen moves for the rook lovated at row, column and add these moves to the list
        The Quenn can go forward from 7 cases in all the direction. So the Queen can move as a (B)ishop and a (R)ook
        """

        self.get_bishop_moves(r, c, moves) #Move as a (B)ishop
        self.get_rook_moves(r, c, moves) #Move as a (R)ook
                  
    def get_king_moves(self, r, c, moves):
        """
        Get all the (K)ing moves for the rook lovated at row, column and add these moves to the list
        """
        
        row_moves = (-1, -1, -1, 0, 0, 1, 1, 1)
        col_moves = (-1, 0, 1, -1, 1, -1, 0, 1) 
        ally_color = "w" if self.whiteToMove else "b"

        for i in range (8):
            end_row = r + row_moves[i]
            end_col = c + col_moves[i]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] != ally_color: #not an ally piece (empty or enemy piece)
                    #place king at the end square and check for checks
                    if ally_color == "w":
                        self.whiteKingLocation = (end_row, end_col)
                    else:
                        self.blackKingLocation = (end_row, end_col)
                    in_check, pins, checks = self.check_for_pins_and_checks()
                    #print(in_check)
                    if not in_check:
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                    # place king back on original location
                    if ally_color == "w": 
                        self.whiteKingLocation = (r, c) #reset the position of the white king
                    else:
                        self.blackKingLocation = (r, c) #reset the position of the black king

    ''' Castling Movements: King and Queen side '''
    def get_castle_moves(self, r, c, moves):
        '''
        Generate all valid astle moves for the king at (r, c) and add them to the list of moves
        '''        
        if self.square_under_attack(r, c):
            return #can't castle while we are in check
        if (self.whiteToMove and self.whiteCastleKingside) or (not self.whiteToMove and self.blackCastleKingside) :
            self.get_king_side_castle_moves(r,c,moves)
        if (self.whiteToMove and self.whiteCastleQueenside) or (not self.whiteToMove and self.blackCastleQueenside) :
            self.get_queen_side_castle_moves(r,c,moves)
    
    def get_king_side_castle_moves(self, r, c, moves):   
        '''
        Castling in the right side, with the right rook
        '''     
        if self.board[r][c+1] == '--' and self.board[r][c+2] == '--':
            if not self.square_under_attack(r, c+1) and not self.square_under_attack(r, c+2):
                moves.append(Move((r, c), (r, c+2), self.board, castle = True))
                
    def get_queen_side_castle_moves(self, r, c, moves):   
        '''
        Castling in the left side, with the left rook
        '''      
        if self.board[r][c-1] == '--' and self.board[r][c-2] == '--' and self.board[r][c-3] == '--':
            if not self.square_under_attack(r, c-1) and not self.square_under_attack(r, c-2):
                moves.append(Move((r, c), (r, c-2), self.board, castle= True))

'''
Class to contain the castling rights
'''      
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

'''
Class to contain the pieces's movements
''' 
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

    def __init__(self, start_sq, end_sq, board, en_passant = False, pawn_promotion = False, castle = False) :
        self.startRow = start_sq[0]
        self.startCol = start_sq[1]
        self.endRow = end_sq[0]
        self.endCol = end_sq[1]
        self.pieceMoved = board[self.startRow][self.startCol]   #determine the first square selected and thus, the piece that needs to be moved.
        self.pieceCaptured = board[self.endRow][self.endCol]    #determine the second square selected and thus, the piece that will be captured.
        self.enPassant = en_passant
        self.pawnPromotion = pawn_promotion
        self.castle = castle
        if self.enPassant :
            self.pieceCaptured = 'bp' if self.pieceMoved == 'wp' else 'wp' #en passant captures opposite colored pawn

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
