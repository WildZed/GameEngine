# Minitest Games
# Game Dynamics

import copy, random, pygame, math
from pygame.locals import *
from geometry import *
import game_constants as gc
import game_objects as go


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
        self._horizontalFacing = 'left'
        self._verticalFacing = 'down'


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

            self._horizontalFacing = self.horizontal
        elif direction == 'vertical':
            if self.vertical == 'up':
                self.vertical = 'down'
            elif self.vertical == 'down':
                self.vertical = 'up'

            self._verticalFacing = self.vertical


    def facing( self, direction = 'horizontal' ):
        return direction and getattr( self, '_' + direction + 'Facing', None ) or None


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
                self.__dict__['_' + axis + 'Facing'] = axisValue
            else:
                axisValue = False

                # Checking for other movement in the same axis.
                for direction in Directions.AXES[axis]:
                    if direction in self.__dict__ and self.__dict__[direction]:
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
        self.resetEvent()


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


    def setBlocked( self, val = True ):
        self.blockedHorizontally = val
        self.blockedVertically = val


    def resetEvent( self ):
        self.event = None


    def popEvent( self ):
        event = self.event
        self.event = None

        return event


    # Set the first interaction or collision event to occur.
    def setEvent( self, event ):
        if not self.event:
            self.event = event


    def getBoundedPosition( self, newPos ):
        return newPos


    def collidesWithRect( self, rect ):
        return False




# Bound positions by rectangular area.
class RectangleBoundary( Boundary ):
    def __init__( self, rect, grow = 0 ):
        super().__init__()
        # PyGame Rect.
        self.rect = rect.inflate( grow, grow )


    def getBoundedPosition( self, moveObject, newPos ):
        rect = Rectangle( self.rect )

        return rect.boundPoint( newPos )


    def collidesWith( self, obj ):
        rect = obj.getMaskRect( obj.getCollisionMask(), obj.getOffSetPos() )

        if self.collidesWithRect( rect ):
            collisionData = go.CollisionData( Point( rect.left, rect.top ), rect )
        else:
            collisionData = None

        return collisionData


    def collidesWithRect( self, rect ):
        return not self.rect.colliderect( rect )




# Bound object positions by collision with non-transparent part of other objects.
class CollisionBoundary( Boundary ):
    def __init__( self, **kwArgs ):
        super().__init__()
        self.collisionPointOffset = kwArgs.get( 'collisionPointOffset', None )
        self.resetBlocked()


    def collides( self, moveObject, newPos ):
        # Temporarily move to new position to check for collision.
        moveObject.pushPos( newPos )
        event = moveObject.collidesWithScene()
        moveObject.popPos()
        self.setEvent( event )

        if event and event.type != gc.COLLISION_EVENT:
            return None

        return event


    def collidesWithSubSetFromCurrentPosition( self, moveObject, curPos, newPos ):
        moveObject.pushPos( curPos )
        curCollisions = moveObject.getSceneCollisions()
        moveObject.popPos()
        moveObject.pushPos( newPos )
        newCollisions = moveObject.getSceneCollisions()
        moveObject.popPos()

        if len( newCollisions ) <= len( curCollisions ):
            for curCollision in curCollisions:
                try:
                    newCollisions.remove( curCollision )
                except:
                    pass

            collidesWithSubSet = ( 0 == len( newCollisions ) )
        else:
            collidesWithSubSet = False

        return collidesWithSubSet


    def getTightPoint( self, event, curPos, offsetPos ):
        collisionData = event.collisionData
        overlapRect = collisionData.rect
        overlapWidth = overlapRect.width
        overlapHeight = overlapRect.height

        offsetPos.shrinkBy( overlapRect.width, overlapRect.height )

        return curPos + offsetPos


    # Implement the boundaries by collision.
    def getBoundedPosition( self, moveObject, newPos ):
        # Trigger collision events here? Or store on object?
        self.resetBlocked()
        event = self.collides( moveObject, newPos )

        if not event:
            return newPos

        curPos = moveObject.getPos()
        offsetPos = newPos - curPos

        # First try to go up tight to the obstacle.
        testPos = curPos + offsetPos / 2
        event = self.collides( moveObject, testPos )

        if not event:
            return testPos

        testPos = curPos + offsetPos / 3
        event = self.collides( moveObject, testPos )

        if not event:
            return testPos

        testPos = curPos + UnitPoint( offsetPos )
        event = self.collides( moveObject, testPos )

        if not event:
            return testPos

        # Now check offset x and y separately.
        if offsetPos.x:
            horizontaltTestPos = curPos + Point( offsetPos.x, 0 )
            event = self.collides( moveObject, horizontaltTestPos )

            if not event:
                self.setBlockedVertically()
                # print( 'Allowed horizontal movement.' )
                return horizontaltTestPos

        if offsetPos.y:
            verticalTestPos = curPos + Point( 0, offsetPos.y )
            event = self.collides( moveObject, verticalTestPos )

            if not event:
                # print( 'Allowed vertical movement.' )
                self.setBlockedHorizontally()
                return verticalTestPos

        self.setBlocked()

        if self.collidesWithSubSetFromCurrentPosition( moveObject, curPos, testPos ):
            # Accept newPos if current pos is already colliding.
            # But not with things that it should never collide with.
            self.resetBlocked()
        else:
            testPos = curPos

        return testPos




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
        super().__init__()

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


    def getBounceAmount( self ):
        # Returns the number of pixels to offset based on the bounce.
        # Larger bounceRate means a slower bounce.
        # Larger bounceHeight means a higher bounce.
        # currentBounce will always be less than bounceRate.
        bounceRate = self.bounceRate
        bounceHeight = self.bounceHeight

        return int( math.sin( ( math.pi / float( bounceRate ) ) * self.bounce ) * bounceHeight ) if bounceRate and bounceHeight else 0


    def moving( self, direction = 'any' ):
        return self.directions[direction]


    def facing( self, direction = 'horizontal' ):
        return self.directions.facing( direction )


    # No boundary for general movement.
    def getBoundedPosition( self, newPos ):
        if self.boundaryStyle:
            newPos = self.boundaryStyle.getBoundedPosition( self.getMoveObject(), newPos )

        return newPos


    def getImage( self, images, key ):
        image = images[key]

        # No specific up or down image, choose a horizontal facing image.
        if image is None and key in ( 'up', 'down' ):
            image = images[self.facing( 'horizontal' )]

        return image


    def chooseImage( self, images ):
        # Flip the player image if changed direction.
        movement = self.moving( 'horizontal' )

        if movement:
            image = self.getImage( images, movement )
        else:
            movement = self.moving( 'vertical' )

            if movement:
                image = self.getImage( images, movement )
            else:
                image = None

        return image


    def postEvent( self, event ):
        if event:
            # print "Posting event " + `event`
            pygame.event.post( event )


    def sendEvent( self ):
        if self.boundaryStyle:
            event = self.boundaryStyle.popEvent()
            self.postEvent( event )


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
                self.sendEvent()

        return newPos


    def adjustMoveOffset( self, offset ):
        if not self.moving( 'horizontal' ):
            offset.x = 0

        if not self.moving( 'vertical' ):
            offset.y = 0




# Move by key presses.
class KeyMovementStyle( GeneralMovementStyle ):
    def __init__( self, **kwArgs ):
        super().__init__( **kwArgs )

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


    def setMovement( self, key = None ):
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
        super().__init__( **kwArgs )


    def decideMovement( self, multiplier = 1 ):
        rand = random.random()

        if rand < 0.05 * multiplier:
            if rand < 0.04 * multiplier:
                direction = random.choice( DIRECTION_LIST )
                self.setMovement( direction )
            else:
                self.stopMovement()
        # Else continue in the current direction.



    # Get the new position based on the movement style.
    def move( self, pos ):
        self.decideMovement()

        newPos = GeneralMovementStyle.move( self, pos )
        boundaryStyle = self.getBoundaryStyle()

        if boundaryStyle.getBlockedHorizontally():
            rand = random.random()

            if rand < 0.2:
                self.reverseMovement( 'horizontal' )
            elif rand > 0.8:
                self.setMovement( 'up' )
            elif rand > 0.9:
                self.setMovement( 'down' )
            else:
                self.stopMovement( 'horizontal' )

        if boundaryStyle.getBlockedVertically():
            rand = random.random()

            if rand < 0.2:
                self.reverseMovement( 'vertical' )
            elif rand > 0.8:
                self.setMovement( 'left' )
            elif rand > 0.9:
                self.setMovement( 'right' )
            else:
                self.stopMovement( 'vertical' )

        return newPos
