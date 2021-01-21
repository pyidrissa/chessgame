# chessgame
A simple chess game has been developped in an educationnal purpose to improve my python skills.
For this project, no chess packages has been used. I completely wrote the chessEngine from scratch. There are two versions of the chess engine: 
  - 'ChessEngineA' is a more advanced algorithm to determine the valid moves
  To make this algorithm more efficient, the alogorithm is only focusing on the pawn that can put the king in check. Therefore, there are different conditions in function on the type of the chesspawn.
  - 'ChessEngineB' is a more simple algorithm to determine the valid moves
  This chess engine determine the valid moves by checking if every chess pawns can put the opponent king in check.

For the UI part, the python package pygame has been used. That will allow to manage the mouse event.
And Finally for the AI part has been written by applying the the Minimax and the NegaMax algorithms and finally adding the alpha beta pruning to both algorithm ( https://www.youtube.com/watch?v=l-hh51ncgDI ). All the algorithms are in this project, however, the NegaMax with alpha beta is the one used by default.


This project wouldn't been possible without the help of Eddie Sharick, a youtuber. The link to his videos is:
https://www.youtube.com/watch?v=EnYui0e73Rs&list=PLBwF487qi8MGU81nDGaeNE1EnNEPYWKY_
