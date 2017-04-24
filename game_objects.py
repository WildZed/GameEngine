# Monkey-Rabbit Games
# Game Objects

import random, sys, time, math, pygame, copy
from geometry import *
from pygame.locals import *
from game_utils import fontCache


# Constants.

WHITE = ( 255, 255, 255 )
RED = ( 255, 0, 0 )
GREEN = ( 0, 255, 0 )
BLUE = ( 0, 0, 255 )




# Example of access dataObj.<attr> and setting dataObj.<attr> = <value>.
class Data:
    def __init__( self ):
        self.__dict__['_data'] = {}


    def __getattr__( self, key ):
        data = self.__dict__['_data']

        if key == '_data' or not data.has_key( key ) :
            raise AttributeError( "Unrecognised image attribute '%s' in __getattr__!" % key )

        val = data[key]

        return val


    def __setattr__( self, key, val ):
        if key == '_data':
            raise AttributeError( "Image attribute '%s' not allowed in __setattr__!" % key )

        self.__dict__['_data'][key] = val




# A generic game object.
class Object:
    def __init__( self, image, pos, size, ratio = None, positionStyle = '' ):
        # generalSize = random.randint( 5, 25 )
        # multiplier = random.randint( 1, 3 )
        # self.width  = ( generalSize + random.randint( 0, 10 ) ) * multiplier
        # self.height = ( generalSize + random.randint( 0, 10 ) ) * multiplier
        self.name = None
        self.parent = None
        self.visible = True
        self.image = image
        self.size = size
        # Default position style of 'top_left' in world coordinates is the same as ''.
        # Styles: 'top_left', 'centred', 'relative_top_left', 'relative_centred',
        #         'viewport_top_left', 'viewport_centred'
        self.positionStyle = positionStyle

        if image:
            # The ratio of height to width.
            self.ratio = float( image.get_height() ) / float( image.get_width() )
        else:
            self.ratio = 1.0

        if ratio is not None:
            self.ratio *= ratio

        self.pos = pos
        # The position rectangle.
        self.rect = None
        self.colRect = None
        self.surface = None
        self.updateSurface()
        self.updateRect()
        self.updateCollisionRect()
        self.attachedObjects = []


    def setName( self, name ):
        self.name = name


    def setParent( self, parent ):
        self.parent = parent


    def setPositionStyle( self, positionStyle = '' ):
        self.positionStyle = positionStyle


    def updateSurface( self ):
        width = self.size
        height = int( ( float( width ) * self.ratio ) + 0.5 )
        image = self.image

        if image:
            self.surface = pygame.transform.scale( image, ( width, height ) )
        else:
            self.surface = pygame.Surface( ( width, height ) )


    def updateRect( self, camera = ORIGIN, offset = ORIGIN ):
        if self.positionStyle[:8] != 'viewport':
            offset = offset - camera

        # self.rect = self.surface.get_rect()
        self.rect = self.getOffSetRect( offset )


    def getOffSetPos( self, offset = ORIGIN ):
        offset = offset + self.pos

        if self.positionStyle[-7:] == 'centred':
            offset -= Point( self.width / 2, self.height / 2 )

        return offset


    def getOffSetRect( self, offset = ORIGIN ):
        offSetPos = self.getOffSetPos( offset )

        return pygame.Rect( offSetPos.x, offSetPos.y, self.width, self.height )


    def attachObject( self, obj ):
        self.attachedObjects.append( obj )
        obj.setParent( self )

        if obj.positionStyle == '':
            obj.positionStyle = 'relative_top_left'

        return obj


    def detachObject( self, obj ):
        try:
            obj.setParent( None )
            self.attachedObjects.remove( obj )
        except ValueError:
            obj = None

        return obj


    def detachNamedObject( self, name ):
        for attachedObject in self.attachedObjects:
            if attachedObject.name == name:
                self.detachObject( attachedObject )
                break


    def detachAllObjects( self ):
        attachedObjectList = self.attachedObjects

        for attachedObject in attachedObjectList:
            attachedObject.setParent( None )

        self.attachedObjects = []

        return attachedObjectList


    def updateCollisionRect( self ):
        # The collision rectangle.
        self.colRect = self.rect


    def collidesWith( self, obj ):
        return self.colRect.colliderect( obj.colRect )


    def collidesWithPoint( self, pos, useFullRect = False ):
        if useFullRect:
            rect = self.rect
        else:
            rect = self.colRect

        collides = ( rect.left <= pos.x and pos.x <= rect.right ) and ( rect.top <= pos.y and pos.y <= rect.bottom )

        # print "collidesWithPoint %s %s %s" % ( pos, rect, collides )
        # print "rect l %s r %s t %s b %s" % ( rect.left, rect.right, rect.top, rect.bottom )

        return collides


    def collidesWithColour( self, viewPort, offset = ORIGIN ):
        xoff = 0

        if not self.left:
            xoff = self.width

        offSetPos = self.getOffSetPos( offset - viewPort.camera )
        footViewPortPos = offSetPos + Point( xoff, self.height )

        # self.debugPos( 'footViewPortPos', footViewPortPos, positionStyle='viewport_centred' )

        # print( "footViewPortPos %s" % footViewPortPos )

        return viewPort.collisionAtPoint( footViewPortPos )


    def collidesAlt( camera, pos, rect ):
        # Adjust rectangle for camera shift.
        adjustedRect = Rect( rect )
        adjustedRect += camera
        # Is position inside the given rectangle adjusted for camera position.
        collides = ( adjustedRect.left <= pos.x and pos.x <= adjustedRect.right ) and ( adjustedRect.bottom <= pos.y and pos.y <= adjustedRect.top )

        if collides:
            # Find the colour on the display at the given position.
            colour = pygame.display.get_surface().get_at( pos.asTuple() )
            collides = ( colour != BACKGROUND_COLOUR )

        return collides


    def asRectangle( self ):
        return Rectange( Point( self.pos.x, self.pos.y ), Point( self.pos.x + self.width, self.pos.y + self.height ) )


    def swapImage( self, image ):
        self.image = image
        self.updateSurface()


    def update( self, camera = ORIGIN, offset = ORIGIN ):
        self.updateRect( camera, offset )
        self.updateCollisionRect()
        self.updateAttachedObjects( camera, offset )


    def updateAttachedObjects( self, camera = ORIGIN, offset = ORIGIN ):
        for attachedObject in self.attachedObjects:
            attachedObjectOffset = copy.copy( offset )

            # Calculate attached objects' positions relative to this object.
            if attachedObject.positionStyle[:8] == 'relative':
                attachedObjectOffset += self.pos

            attachedObject.update( camera, attachedObjectOffset )


    def drawBox( self, surface, rect ):
        pygame.draw.lines( surface, RED, True, ( rect.topleft, rect.topright, rect.bottomright, rect.bottomleft ) )


    def drawPos( self, surface, pos ):
        rect = Rectangle( pos - 20, pos + 20 )
        points = rect.asTupleTuple()
        # print points
        pygame.draw.lines( surface, RED, True, points )


    def debugPos( self, name, pos, size = 4, positionStyle = '' ):
        self.detachNamedObject( name )
        posBox = Box( pos, size, positionStyle=positionStyle )
        posBox.setName( name )
        self.attachObject( posBox )


    def draw( self, surface, debugDraw = False ):
        if self.visible:
            surface.blit( self.surface, self.rect )

            if debugDraw:
                self.drawBox( surface, self.rect )
                self.drawBox( surface, self.colRect )

            self.drawAttachedObjects( surface, debugDraw=debugDraw )


    def drawAttachedObjects( self, surface, debugDraw = False ):
        for attachedObject in self.attachedObjects:
            attachedObject.draw( surface, debugDraw=debugDraw )


    def __getattr__( self, key ):
        try:
            if key == 'width':
                return self.__dict__['surface'].get_width()
            elif key == 'height':
                return self.__dict__['surface'].get_height()
            elif key == 'x':
                return self.__dict__['pos'].x
            elif key == 'y':
                return self.__dict__['pos'].y

            value = self.__dict__[key]
        except:
            raise
            # raise AttributeError( "Unrecognised Object attribute '%s' in __getattr__!" % key )

        return value


    def __setattr__( self, key, val ):
        if key == 'x':
            self.__dict__['pos'].x = val
        elif key == 'y':
            self.__dict__['pos'].y = val
        else:
            self.__dict__[key] = val


    def __nonzero__( self ):
        return True


    def __eq__( self, obj ):
        return self is obj




class Box( Object ):
    def __init__( self, pos, size, positionStyle = '' ):
        Object.__init__( self, None, pos, size, positionStyle=positionStyle )




class Shop( Object ):
    def __init__( self, image, pos, size ):
        Object.__init__( self, image, pos, size )




class Bush( Object ):
    def __init__( self, image, pos, size ):
        Object.__init__( self, image, pos, size )




class Arrow( Object ):
    def __init__( self, image, pos, size ):
        Object.__init__( self, image, pos, size )




class Monster( Object ):
    def __init__( self, image, pos, size, ratio = None ):
        Object.__init__( self, image, pos, size, ratio )




class Coin( Object ):
    def __init__( self, image, pos, size ):
        Object.__init__( self, image, pos, size )




# Creates text in world coordinates.
class Text( Object ):
    def __init__( self, font, text, pos, colour ):
        self.font = font
        self.text = text
        self.colour = colour

        Object.__init__( self, None, pos, 0 )


    def updateSurface( self ):
        self.surface = self.font.render( self.text, True, self.colour )




# Creates static text in viewport coordinates.
class StaticText( Text ):
    def __init__( self, font, text, pos, colour ):
        Text.__init__( self, font, text, pos, colour )


    def update( self, camera = ORIGIN, offset = ORIGIN ):
        # Call the base class, but don't use the offset.
        Text.update( self )




class DebugText( StaticText ):
    def __init__( self, font, text, pos, colour ):
        StaticText.__init__( self, font, text, pos, colour )



class Score( StaticText ):
    def __init__( self, font, pos, score ):
        StaticText.__init__( self, font, 'Money: %d' % score, pos, WHITE )


    def updateScore( self, score ):
        self.text = 'Money: %d' % score
        self.updateSurface()
        # Only update when the score changes.
        self.update()




class Player( Object ):
    def __init__( self, imageL, imageR, pos, size, movementStyle ):
        self.imageL = imageL
        self.imageR = imageR
        self.left = True
        self.steps = 0
        self.movementStyle = movementStyle
        self.attachedText = None
        movementStyle.setMoveObject( self )

        Object.__init__( self, imageL, pos, size )


    # Override updateCollisionRect() from Object.
    def updateCollisionRect( self ):
        # Use a smaller collision rectangle that represents the players feet.
        self.colRect = colRect = self.rect.copy()
        # Collision rect from feet to a quarter height.
        colRect.top = colRect.top + ( ( colRect.height * 3 ) / 4 )
        colRect.height = colRect.height / 4
        # Collision rect thinner than the image width by a quarter on each side.
        # colRect.left = colRect.left + ( colRect.width / 4 )
        # colRect.width = colRect.width / 2


    def getBounceAmount( self ):
        # Returns the number of pixels to offset based on the bounce.
        # Larger bounceRate means a slower bounce.
        # Larger bounceHeight means a higher bounce.
        # currentBounce will always be less than bounceRate.
        movementStyle = self.movementStyle
        bounceRate = movementStyle.bounceRate
        bounceHeight = movementStyle.bounceHeight

        return int( math.sin( ( math.pi / float( bounceRate ) ) * movementStyle.bounce ) * bounceHeight )


    def checkUpdatePlayerDirection( self ):
        # Flip the player image if changed direction.
        horizontalMovement = self.movementStyle.moving( 'horizontal' )

        if horizontalMovement:
            if self.attachedText:
                self.detachObject( self.attachedText )

            self.attachedText = Text( fontCache['small'], horizontalMovement, Point( -20, -20 ), GREEN )
            self.attachObject( self.attachedText )

            if 'left' == horizontalMovement and self.image is not self.imageL:
                self.left = True
                self.swapImage( self.imageL )
            elif 'right' == horizontalMovement and self.image is not self.imageR:
                # Flip the player image.
                self.left = False
                self.swapImage( self.imageR )


    def setMovement( self, key ):
        self.movementStyle.setMovement( key )
        self.checkUpdatePlayerDirection()


    def stopMovement( self, key ):
        self.movementStyle.stopMovement( key )
        self.checkUpdatePlayerDirection()


    def move( self ):
        newPos = self.movementStyle.move( self.pos )
        # print( newPos )

        if newPos != self.pos:
            self.pos = newPos
            self.steps += 1


    def update( self, camera, gameOverMode, invulnerableMode ):
        flashIsOn = round( time.time(), 1 ) * 10 % 2 == 1

        if not gameOverMode and not ( invulnerableMode and flashIsOn ):
            jitter = Point( 0, - self.getBounceAmount() )
            Object.update( self, camera, jitter )
            self.visible = True
        else:
            self.visible = False

