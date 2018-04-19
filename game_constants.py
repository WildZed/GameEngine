# Monkey-Rabbit Games
# Game Constants.

from pygame.locals import *
from geometry import *

BLACK = ( 0, 0, 0 )
BLACK_ALPHA = ( 0, 0, 0, 0 )
WHITE = ( 255, 255, 255 )
RED = ( 255, 0, 0 )
GREEN = ( 0, 255, 0 )
BLUE = ( 0, 0, 255 )
PINK = (255, 105, 180)

DEFAULT_IMAGE_OBJECT_TEXT_OFFSET = Point( -20, -20 )

INTERACTION_EVENT = USEREVENT + 1
COLLISION_EVENT = USEREVENT + 2
CLICK_COLLISION_EVENT = USEREVENT + 3
