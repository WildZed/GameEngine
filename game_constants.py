# Monkey-Rabbit Games
# Game Constants.

from pygame.locals import *
from geometry import *

TRANSPARENT_ALPHA = 0
SEMI_TRANSPARENT_ALPHA = 127
OPAQUE_ALPHA = 255
BLACK = ( 0, 0, 0 )
BLACK_TRANSPARENT_ALPHA = ( 0, 0, 0, TRANSPARENT_ALPHA )
BLACK_SEMI_TRANSPARENT_ALPHA = ( 0, 0, 0, SEMI_TRANSPARENT_ALPHA )
BLACK_OPAQUE_ALPHA = ( 0, 0, 0, OPAQUE_ALPHA )
WHITE = ( 255, 255, 255 )
RED = ( 255, 0, 0 )
GREEN = ( 0, 255, 0 )
BLUE = ( 0, 0, 255 )
PINK = (255, 105, 180)

DEFAULT_IMAGE_OBJECT_TEXT_OFFSET = Point( -20, -20 )

INTERACTION_EVENT = USEREVENT + 1
COLLISION_EVENT = USEREVENT + 2
CLICK_COLLISION_EVENT = USEREVENT + 3
