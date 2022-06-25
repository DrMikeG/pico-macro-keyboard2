import board
import rotaryio


#ENCODER = rotaryio.IncrementalEncoder(board.A2, board.A3)
ENCODER = rotaryio.IncrementalEncoder(board.GP26, board.GP27)


# MAIN LOOP ----------------------------------------------------------------

LAST_POSITION = ENCODER.position
while True:
    POSITION = ENCODER.position
    if POSITION != LAST_POSITION:
        MOVE = POSITION - LAST_POSITION
        LAST_POSITION = POSITION
        print("Move",MOVE)