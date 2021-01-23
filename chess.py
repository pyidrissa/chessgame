""" 
This is our main driver file.

I will be responsible for handling user input and displaying the current Gamestate object.
Two ChessEngine has been developped:
    * ChessEngineA : a ChessEngine Advanced
    * ChessEngineB : a more simple Chess Engine
"""
import random as r
import pygame as p
import engine.ChessEngineA as ChessEngine
import ai.chessAI as ChessAI

WIDTH = HEIGHT = 512 #HEIGHT of the game
DIMENSION = 8 #dimension of a chess board are 8x8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15 #for animation later on
IMAGES = {}


'''
Initialize a global dictionary of images. This will be called exactly once in the main
'''
def load_images():
    '''
    Initialize a global dictionary of images. This will be called exactly once in the main
    '''
    pieces = ["bp","bR", "bN", "bB", "bQ", "bK", "wp","wR", "wN", "wB", "wQ", "wK"]
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/1/" + piece + ".png"),(SQ_SIZE,SQ_SIZE))
    #Note: we can access an image by saving 'IMAGES['wp']

'''
The main driver for our code. This will handle user input and updating the graphics
'''
def main(P_WHITE, P_BLACK, DEPTH):
    '''
    This function is the main function, launching the chess game
    The main driver for our code. This will handle user input and updating the graphics    

    INPUT
    ------    
    1) P_WHITE = Boolean (if we are playing White or Not)
    2) P_BLACK = Boolean (if we are playing Black or Not)
    3) DEPTH = integer (layer level for the chessAI)
    '''
    p.init()
    screen = p.display.set_mode((WIDTH,HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = ChessEngine.GameState()
    valid_moves = gs.get_valid_moves()
    move_made = False #flag variable for when a move is made
    animate = False #flag variable for when we should animate a move
    load_images() #Load the images once, before the while loop
    running = True
    sq_selected = () #square selected by the mouse. No one is selected initialy. Keep track of the last click of the user (tuple:(row, col))
    player_clicks = [] #keeptrack of player clicks: (1) select the element to move locate a the position (6,4) and 
                       #(2) select the destination position (4,4)  (two tuples : [(6,4), (4,4)])
    game_over = False
    playerOne = P_WHITE    # If a Human is playing -> White, then this will be True.
                        # IF an AI is playing, then False
    playerTwo = P_BLACK # Same as above but for black


    while running: 
        human_turn = (gs.whiteToMove and playerOne) or \
                        (not gs.whiteToMove and playerTwo) #return True of False

        for e in p.event.get(): #Handling mouse event
            if e.type == p.QUIT:
                running = False
            #mouse handler                        
            elif e.type == p.MOUSEBUTTONDOWN:
                if not game_over and human_turn: #Let the player press the keys if WHITE TURN NOT gameOver
                    #print("WHITE TURN : ", gs.whiteToMove, "(CLIK MOVE)")
                    valid_moves = gs.get_valid_moves()
                    location = p.mouse.get_pos() #(x,y) location of the mouse
                    mouse_column = location[0] // SQ_SIZE # 'x' coordonate
                    mouse_row = location [1] // SQ_SIZE # 'y' coordonate
                    if sq_selected == (mouse_row , mouse_column): #the user clicked the same square twice
                        sq_selected = () #deselect
                        player_clicks = [] #clear the player clicks
                    else:
                        sq_selected = (mouse_row, mouse_column) #sq_selected contain the postion where the mouse click
                        player_clicks.append(sq_selected) #append for both 1st and 2nd Clicks
                    if len(player_clicks) == 2: #what to do after the 2nd click
                        move = ChessEngine.Move(player_clicks[0], player_clicks[1], gs.board)
                        print(move.get_chess_notation())                         
                        for i in range (len(valid_moves)):
                            if move == valid_moves[i]:                              
                                gs.make_move(valid_moves[i])
                                move_made = True 
                                animate = True
                                #the 2 following lines will reset the click only if we made valid selection       
                                sq_selected = () #reset the user clicks
                                player_clicks = [] #reset the players clicks
                    
                        if not move_made:
                            player_clicks = [sq_selected]   # set the current click at the position of 
                                                            # the set of two clicks we need to make           
            #key handler
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z: #undo when 'z' is pressed
                    gs.undo_move()               
                    move_made = True
                    animate = False
                    game_over = False
                if e.key == p.K_r: #reset the board when r is pressed
                    gs = ChessEngine.GameState() #reinitialise the gameState
                    valid_moves = gs.get_valid_moves()
                    sq_selected = ()
                    player_clicks = []
                    move_made = False
                    animate = False
                    game_over = False

        #AI MOVE (ARTIFICIAL INTELLIGENCE FOR MY CHESS GAME)
        if not game_over and not human_turn: #AI play black 
            AI_valid_moves = gs.get_valid_moves()
            AI_move = ChessAI.find_best_moves(gs, AI_valid_moves, DEPTH) 
            if AI_move is None: #IF no best move
                turn_color = 'white' if gs.whiteToMove else 'black'
                print(turn_color ," -> random move made")                 
                AI_move = ChessAI.find_random_move(valid_moves)
            gs.make_move(AI_move)
            move_made = True 
            animate = True

        # FOR THE DRAWING BOARD PART
        if move_made:
            if animate:
                animated_move(gs.moveLog[-1], screen, gs.board, clock) 
                #we are making the move with the last element in the move log
            valid_moves = gs.get_valid_moves()
            move_made = False
            animate = False

        draw_game_state(screen, gs, valid_moves, sq_selected)       
        
        if gs.checkMate:
            game_over = True
            if gs.whiteToMove: 
                draw_text(screen, 'Black WINS by checkmate')
            else:
                draw_text(screen, 'White WINS by checkmate')
        elif gs.staleMate:            
            game_over = True
            draw_text(screen, 'Stalemate')        

        clock.tick(MAX_FPS) # means that for every second at most MAX_FPS frames should pass
        p.display.flip()    # display.flip() will update the contents of the entire display

        
'''
Highlight square selected and moves for piece selected
'''
def highlight_squares(screen, gs, valid_moves, sq_selected):
    '''
    Highlight square selected and moves for piece selected
    '''
    if sq_selected != (): #if we select a case
        r, c = sq_selected
        if gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'): #square selected is a piece that can be moved
            #highlight selected square
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100) #transparency value -> if 0 : transparent. If 255: opaque
            s.fill(p.Color('blue'))
            screen.blit(s,(c*SQ_SIZE, r*SQ_SIZE))
            #highlight moves from that square
            s.fill(p.Color('yellow'))
            for move in valid_moves:
                if move.startRow == r and move.startCol == c:
                    screen.blit(s, (move.endCol*SQ_SIZE, move.endRow*SQ_SIZE))

'''
Responsible for all the graphics within a current game state
'''
def draw_game_state(screen, gs, valid_moves, sq_selected):
    '''
    Responsible for all the graphics within a current game state
    '''
    draw_board(screen) #draw the square on the board
    highlight_squares(screen, gs, valid_moves, sq_selected)
    #add in piece highlighting or move suggestions (later)
    draw_pieces(screen, gs.board) #draw pieces on top of those squares

'''
Draw the squares on the board. The top legt square is always light
'''
def draw_board(screen):
    '''
    Draw the squares on the board. The top legt square is always light
    '''
    global colors
    colors = [p.Color(227,193,111), p.Color(184,139,74)] #(light case, dark case)
    for raw in range (DIMENSION):
        for column in range (DIMENSION):
            color = colors[((raw + column) % 2)]
            p.draw.rect(screen, color, p.Rect(column*SQ_SIZE, raw*SQ_SIZE, SQ_SIZE, SQ_SIZE))

'''
Draw the pieces on the board using the current GameState.board
'''
def draw_pieces(screen, board):
    '''
    Draw the pieces on the board using the current GameState.board
    '''
    for raw in range(DIMENSION):
        for column in range(DIMENSION):
            piece = board[raw][column]
            if piece != "--": #not empty square
                screen.blit(IMAGES[piece], p.Rect(column*SQ_SIZE, raw*SQ_SIZE, SQ_SIZE, SQ_SIZE))

'''
Animating a move
'''
def animated_move(move, screen, board, clock):
    '''
    Animating a move
    '''
    global colors
   
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    frames_per_square = 10 #frames to move one square
    frame_count = (abs(dR) + abs(dC)) * frames_per_square
    for frame in range(frame_count + 1):
        r , c = (move.startRow + dR*(frame/frame_count), move.startCol + dC*(frame/frame_count))
        draw_board(screen)
        draw_pieces(screen, board)
        #erase the piece moved from its ending square
        color = colors[(move.endRow + move.endCol) % 2]
        end_square = p.Rect(move.endCol*SQ_SIZE, move.endRow*SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, end_square)
        #draw captured piece onto rectangle
        if move.pieceCaptured != '--':
            screen.blit(IMAGES[move.pieceCaptured], end_square)
        #draw moving piece
        screen.blit(IMAGES[move.pieceMoved], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip() #to see through the all animation
        clock.tick(120) #we want 60 frames per animation

'''
Draw text on the screen
'''
def draw_text(screen, text):
    font = p.font.SysFont('Helvitca', 32, True, False)
    text_object = font.render(text, 0, p.Color('Black'))
    text_location = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH/2 - text_object.get_width()/2, HEIGHT/2 - text_object.get_height()/2)
    screen.blit(text_object, text_location)
    text_object = font.render(text, 0, p.Color(213,87,87,1))
    screen.blit(text_object, text_location.move(2,2))


    
if __name__ == "__main__":
    main(P_WHITE = False, P_BLACK = False, DEPTH = 3)
