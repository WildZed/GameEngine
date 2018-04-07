# Monkey-Rabbit Games
# Game Dynamics

import copy
import random
from pygame.locals import *
from geometry import *


# Constants.

DEFAULT_MOVERATE = Vector( 10, 6 )

DEFAULT_KEYSMAP = {
    'left'  : ( K_LEFT, K_a ),
    'right' : ( K_RIGHT, K_d ),
    'up'    : ( K_UP, K_w, ),
    'down'  : ( K_DOWN, K_s )
}

DIRECTION_LIST = ( 'left', 'right', 'up', 'down' )




class Directions( object ):
    DIRECTIONS = {
        'left'  : 'horizontal',
        'right' : 'horizontal',
        'up'    : 'vertical',
        'down'  : 'vertical'
    }

    AXES = {
        'horizontal'    : ( 'left', 'right' ),
        'vertical'      : ( 'up', 'down' )
    }


    def __init__( self ):
        self.reset()


    def reset( self ):
        self.left = False
        self.right = False
        self.up = False
        self.down = False
        self.horizonal = False
        self.vertical = False


    def reverseDirection( self, direction ):
        if direction == 'horizontal':
            if self.horizontal == 'left':
                self.horizontal = 'right'
            elif self.horizontal == 'right':
                self.horizontal = 'left'
        elif direction == 'vertical':
            if self.vertical == 'up':
                self.vertical = 'down'
            elif self.vertical == 'down':
                self.vertical = 'up'


    def __getattr__( self, key ):
        # if key == 'horizontal':
        #     value = self.__dict__['left'] or self.__dict__['right']
        # elif key == 'vertical':
        #     value = self.__dict__['up'] or self.__dict__['down']
        if key == 'any':
            value = self.horizontal or self.vertical
        else:
            value = self.__dict__[key]

        return value


    def __setattr__( self, key, value ):
        if key in Directions.DIRECTIONS.keys():
            self.__dict__[key] = value
            axis = Directions.DIRECTIONS[key]

            if value:
                axisValue = key
            else:
                axisValue = False

                # Checking for other movement in the same axis.
                for direction in Directions.AXES[axis]:
                    if self.__dict__.has_key( direction ) and self.__dict__[direction]:
                        axisValue = direction
                        break

            self.__dict__[axis] = axisValue
        else:
            self.__dict__[key] = value


    def __getitem__( self, key ):
        return self.__getattr__( key )


    def __setitem__( self, key, value ):
        return self.__setattr__( key, value )


    def __repr__( self ):
        return "left %s right %s up %s down %s horizontal %s vertical %s" % ( self.left, self.right, self.up, self.down, self.horizontal, self.vertical )




class Boundary( object ):
    def __init__( self ):
        self.resetBlocked()


    def resetBlocked( self ):
        self.blockedHorizontally = False
        self.blockedVertically = False


    def getBlockedHorizontally( self ):
        return self.blockedHorizontally


    def setBlockedHorizontally( self, val = True ):
        self.blockedHorizontally = val


    def getBlockedVertically( self ):
        return self.blockedVertically


    def setBlockedVertically( self, val = True ):
        self.blockedVertically = val


    def getBoundedPosition( self, newPos ):
        return newPos




# Bound positions by rectangular area.
class RectangleBoundary( Boundary ):
    def __init__( self, rect ):
        self.rect = rect


    def getBoundedPosition( self, moveObject, newPos ):
        return self.rect.boundPoint( newPos )




# Bound object positions by collision with colour different from the viewport background colour.
# This needs some work because it can't cope with positions outside the viewport.
class CollisionBoundary( Boundary ):
    def __init__( self, viewPort, **kwArgs ):
        self.viewPort = viewPort
        self.collisionPointOffset = kwArgs.get( 'collisionPointOffset', None )
        self.resetBlocked()


    def collides( self, moveObject, newPos ):
        # Temporarily move to new position to check for collision.
        moveObject.pushPos( newPos )
        moveObject.updateRect()
        collides = moveObject.collidesWithScene()
        moveObject.popPos()
        moveObject.updateRect()

        return collides


    # Implement the boundaries by collision.
    def getBoundedPosition( self, moveObject, newPos ):
        # Trigger collision events here? Or store on object?
        self.resetBlocked()
        collides = self.collides( moveObject, newPos )

        if collides:
            # Now check offset x and y separately.
            curPos = moveObject.getPos()
            origNewPos = newPos
            offsetPos = newPos - curPos
            self.setBlockedVertically()
            newPos = curPos + Point( offsetPos.x, 0 )
            collides = self.collides( moveObject, newPos )

            if collides:
                self.setBlockedHorizontally()
                newPos = curPos + Point( 0, offsetPos.y )
                collides = self.collides( moveObject, newPos )

                if collides:
                    collides = self.collides( moveObject, curPos )

                    if collides:
                        # Accept newPos if current pos is already colliding.
                        # nudge = UnitPoint( offsetPos )
                        newPos = curPos # + nudge
                    else:
                        newPos = curPos
                else:
                    self.setBlockedVertically( False )

        return newPos




# Interface of all movement Styles.
class MovementStyle( object ):
    def __init__( self ):
        self.moveObject = None


    def getMoveObject( self ):
        return self.moveObject


    def setMoveObject( self, moveObject ):
        self.moveObject = moveObject


    def moving( self ):
        return False


    # Get the new position based on the movement style.
    def move( self, pos ):
        return pos




class GeneralMovementStyle( MovementStyle ):
    def __init__( self, moveRate = DEFAULT_MOVERATE, bounceRate = 0, bounceHeight = 0, boundaryStyle = None ):
        self.moveBounds = None
        self.moveRate = moveRate
        self.bounceRate = bounceRate
        self.bounceHeight = bounceHeight
        self.directions = Directions()
        self.bounce = 0
        self.boundaryStyle = boundaryStyle


    def setMoveRate( self, moveRate ):
        self.moveRate = moveRate


    def setBounceRates( self, bounceRate, bounceHeight ):
        self.bounceRate = bounceRate
        self.bounceHeight = bounceHeight


    def setBoundaryStyle( self, boundaryStyle ):
        self.boundaryStyle = boundaryStyle


    def setMovement( self, direction ):
        self.directions[direction] = True


    def reverseMovement( self, direction ):
        self.directions.reverseDirection( direction )


    def stopMovement( self, direction = None ):
        if direction is None:
            self.directions.reset()
        else:
            self.directions[direction] = False


    def getBoundaryStyle( self ):
        return self.boundaryStyle


    def moving( self, direction = 'any' ):
        return self.directions[direction]


    # No boundary for general movement.
    def getBoundedPosition( self, newPos ):
        if self.boundaryStyle:
            newPos = self.boundaryStyle.getBoundedPosition( self.getMoveObject(), newPos )

        return newPos


    # Get the new position based on the movement style.
    def move( self, pos ):
        newPos = Point( pos )

        if self.moving():
            horizontalMovement = self.moving( 'horizontal' )
            verticalMovement = self.moving( 'vertical' )

            if horizontalMovement:
                if 'left' == horizontalMovement:
                    newPos.x -= self.moveRate.x
                else:
                    newPos.x += self.moveRate.x

            if verticalMovement:
                if 'up' == verticalMovement:
                    newPos.y -= self.moveRate.y
                else:
                    newPos.y += self.moveRate.y

            # if horizontalMovement or self.bounce != 0:
            self.bounce += 1

            if self.bounce > self.bounceRate:
                # Reset bounce amount.
                self.bounce = 0

            if newPos != pos:
                newPos = self.getBoundedPosition( newPos )

        return newPos




# Move by key presses.
class KeyMovementStyle( GeneralMovementStyle ):
    def __init__( self, **kwArgs ):
        GeneralMovementStyle.__init__( self, **kwArgs )
        self.dirToKeysMap = DEFAULT_KEYSMAP
        self.allDirsToKeysMap = copy.copy( DEFAULT_KEYSMAP )
        self.createKeyToDirMap()


    def createKeyToDirMap( self ):
        dirToKeysMap = self.dirToKeysMap
        self.keyToDirMap = keyToDirMap = {}

        for direction in dirToKeysMap.keys():
            keys = dirToKeysMap[direction]

            for key in keys:
                keyToDirMap[key] = direction

        allDirsToKeysMap = self.allDirsToKeysMap
        allDirsToKeysMap['horizontal'] = dirToKeysMap['left'] + dirToKeysMap['right']
        allDirsToKeysMap['vertical'] = dirToKeysMap['up'] + dirToKeysMap['down']
        allDirsToKeysMap['all'] = allDirsToKeysMap['horizontal'] + allDirsToKeysMap['vertical']


    def setMovement( self, key ):
        if key in self.allDirsToKeysMap['all']:
            direction = self.keyToDirMap[key]
            GeneralMovementStyle.setMovement( self, direction )


    def stopMovement( self, key = None ):
        if key is None:
            GeneralMovementStyle.stopMovement( self )
        elif key in self.allDirsToKeysMap['all']:
            direction = self.keyToDirMap[key]
            GeneralMovementStyle.stopMovement( self, direction )




# Move randomly bounded by collisions with colour that is not the background colour.
class RandomWalkMovementStyle( GeneralMovementStyle ):
    def __init__( self, **kwArgs ):
        GeneralMovementStyle.__init__( self, **kwArgs )


    def decideMovement( self ):
        rand = random.random()

        if rand < 0.05:
            if rand < 0.04:
                direction = random.choice( DIRECTION_LIST )
                self.setMovement( direction )
            else:
                self.stopMovement()
        # Continue in the current direction.



    # Get the new position based on the movement style.
    def move( self, pos ):
        self.decideMovement()

        newPos = GeneralMovementStyle.move( self, pos )
        boundaryStyle = self.getBoundaryStyle()

        if boundaryStyle.getBlockedHorizontally():
            rand = random.random()

            if rand < 0.6:
                self.reverseMovement( 'vertical' )
            else:
                self.stopMovement( 'horizontal' )

        if boundaryStyle.getBlockedVertically():
            rand = random.random()

            if rand < 0.6:
                self.reverseMovement( 'horizontal' )
            else:
                self.stopMovement( 'vertical' )

        return newPos
