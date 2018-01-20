# Monkey-Rabbit Games
# Game Objects

import random, time, math, pygame, copy
import viewport
from pygame.locals import *
from geometry import *
from game_utils import fontCache
from game_constants import *


# Constants.




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
    # Constants.
    DEFAULT_OBJECT_SIZE = 20


    # Constructor.
    def __init__( self, pos, **kwArgs ):
        # generalSize = random.randint( 5, 25 )
        # multiplier = random.randint( 1, 3 )
        # self.width  = ( generalSize + random.randint( 0, 10 ) ) * multiplier
        # self.height = ( generalSize + random.randint( 0, 10 ) ) * multiplier
        self.parent = None
        self.name = kwArgs.get( 'name', None )
        self.visible = kwArgs.get( 'visible', True )
        self.pos = pos
        self.posStack = []
        self.size = kwArgs.get( 'size', Object.DEFAULT_OBJECT_SIZE )
        self.ratio = kwArgs.get( 'ratio', 1.0 )
        # Default position style of 'top_left' in world coordinates is the same as '',
        # but '' indicates that no override position style has been passed in.
        # Styles: 'top_left', 'centre', 'relative_top_left', 'relative_centre',
        #         'viewport_top_left', 'viewport_centre'
        self.positionStyle = kwArgs.get( 'positionStyle', '' )
        self.colour = kwArgs.get( 'colour', BLACK )
        self.mirrorV = kwArgs.get( 'mirrorV', False )
        self.mirrorH = kwArgs.get( 'mirrorH', False )
        self.updateCallback = kwArgs.get( 'updateCallback', None )
        self.lifetime = kwArgs.get( 'lifetime', None )

        # The position rectangle.
        self.rect = None
        self.colRect = None
        self.surface = None
        self.attachedObjects = []

        self.updateSurface()
        self.updateRect()
        self.updateCollisionRect()


    def __repr__( self ):
        return "%s: '%s' %s" % ( self.__class__.__name__, self.name, self.pos )


    def setVisible( self, visible ):
        self.visible = visible


    def pushPos( self, newPos, adjustedOldPos = None, offsetOldPos = None ):
        if adjustedOldPos:
            self.pos = adjustedOldPos
        elif offsetOldPos:
            self.pos += offsetOldPos

        self.posStack.append( self.pos )
        self.pos = newPos


    def popPos( self ):
        self.pos = self.posStack.pop()

        return self.pos


    def updateSurface( self ):
        width = self.size
        height = int( ( float( width ) * self.ratio ) + 0.5 )
        self.surface = pygame.Surface( ( width, height ) )
        self.surface.fill( self.colour )


    def updateRect( self, camera = ORIGIN, offset = ORIGIN ):
        if self.positionStyle[:8] != 'viewport':
            offset = offset - camera

        # self.rect = self.surface.get_rect()
        self.rect = self.getOffSetRect( offset )


    # Get the object's surface top left position given an offset
    # from the object's world coordinate position.
    # This is usually used to find where to draw the surface,
    # which is from top left.
    # OR in other words, get a position offset from the top left position.
    def getOffSetPos( self, offset = ORIGIN ):
        offset = self.pos + offset

        if self.positionStyle[-6:] == 'centre':
            offset -= Point( self.width / 2, self.height / 2 )

        return offset


    def getOffSetRect( self, offset = ORIGIN ):
        offSetPos = self.getOffSetPos( offset )

        return pygame.Rect( offSetPos.x, offSetPos.y, self.width, self.height )


    def attachObject( self, obj ):
        self.attachedObjects.append( obj )
        obj.parent = self

        if obj.positionStyle == '':
            obj.positionStyle = 'relative_top_left'

        return obj


    def getNamedAttachedObject( self, name ):
        for attachedObject in self.attachedObjects:
            if attachedObject.name == name:
                return attachedObject

        return None


    def detachObject( self, obj ):
        try:
            obj.parent = None
            self.attachedObjects.remove( obj )
        except ValueError:
            obj = None

        return obj


    def detachNamedObject( self, name ):
        attachedObject = getNamedAttachedObject( name )

        if attachedObject:
            self.detachObject( attachedObject )

        return attachedObject


    def detachAllObjects( self ):
        attachedObjectList = self.attachedObjects

        for attachedObject in attachedObjectList:
            attachedObject.parent = None

        self.attachedObjects = []

        return attachedObjectList


    def updateCollisionRect( self ):
        # The collision rectangle.
        self.colRect = self.rect


    def collidesWith( self, obj ):
        return self.colRect.colliderect( obj.colRect )


    # Ask if the given position collides with the object's full or collision rectangle.
    def collidesWithPoint( self, pos, useFullRect = False ):
        if useFullRect:
            rect = self.rect
        else:
            rect = self.colRect

        collides = ( rect.left <= pos.x and pos.x <= rect.right ) and ( rect.top <= pos.y and pos.y <= rect.bottom )

        # print "collidesWithPoint %s %s %s" % ( pos, rect, collides )
        # print "rect l %s r %s t %s b %s" % ( rect.left, rect.right, rect.top, rect.bottom )

        return collides


    # Does the object's foot position collide with the collision colour (default is a colour that is not the background colour).
    def collidesWithColour( self, viewPort, offset = ORIGIN, collisionColour = None ):
        # Calculate the viewport coordinate for the object's top left position
        # plus the supplied offset. The offset can be used to work out if
        # a future position will collide.
        collisionPos = self.getOffSetPos( offset - viewPort.camera )

        if viewport.ViewPort.debugDraw:
            # print( "collisionPos %s" % collisionPos )
            # print( "offset %s" ) % ( viewPort.camera + collisionPos - offset - self.pos )
            # print( "camera %s" % viewPort.camera )
            self.debugPos( 'collisionPos', collisionPos, positionStyle='viewport_centre', size=8 )

        return viewPort.collisionOfPoint( collisionPos, collisionColour=collisionColour )


    def asRectangle( self ):
        return Rectange( Point( self.pos.x, self.pos.y ), Point( self.pos.x + self.width, self.pos.y + self.height ) )


    def update( self, camera = ORIGIN, offset = ORIGIN ):
        if self.updateCallback:
            self.updateCallback( self, camera, offset )

        self.updateRect( camera, offset )
        self.updateCollisionRect()
        self.updateAttachedObjects( camera, offset )
        self.checkLifetime()


    def checkLifetime( self ):
        if self.lifetime:
            self.lifetime -= 1

            if self.lifetime <= 0:
                self.parent.detachObject( self )
                del self


    def updateAttachedObjects( self, camera = ORIGIN, offset = ORIGIN ):
        for attachedObject in self.attachedObjects:
            attachedObjectOffset = copy.copy( offset )

            # Calculate attached objects' positions relative to this object.
            if attachedObject.positionStyle[:8] == 'relative':
                attachedObjectOffset += self.pos

            attachedObject.update( camera, attachedObjectOffset )


    def debugPos( self, name, pos, **kwArgs ):
        posBox = self.getNamedAttachedObject( name )

        if not posBox:
            kwArgs['size'] = kwArgs.get( 'size', 4 )
            kwArgs['name'] = name
            posBox = self.attachObject( Box( pos, **kwArgs ) )

        posBox.pos = pos
        posBox.lifetime = 80


    def draw( self, surface ):
        if self.visible:
            surface.blit( self.surface, self.rect )
            viewPortCls = viewport.ViewPort

            if viewPortCls.debugDraw:
                viewPortCls.sdrawBox( surface, self.rect, colour=self.colour )
                viewPortCls.sdrawBox( surface, self.colRect, colour=self.colour )

            self.drawAttachedObjects( surface )


    def drawAttachedObjects( self, surface ):
        for attachedObject in self.attachedObjects:
            attachedObject.draw( surface )


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




class ImageObject( Object ):
    def __init__( self, pos, image, **kwArgs ):
        self.image = image

        kwArgs['ratio'] = self.calculateRatio( **kwArgs )

        Object.__init__( self, pos, **kwArgs )


    def updateSurface( self ):
        width = self.size
        height = int( ( float( width ) * self.ratio ) + 0.5 )
        self.surface = pygame.transform.scale( self.image, ( width, height ) )


    def swapImage( self, image ):
        self.image = image
        self.updateSurface()


    def calculateRatio( self, **kwArgs ):
        # The ratio of height to width.
        image = self.image
        ratio = float( image.get_height() ) / float( image.get_width() )

        if kwArgs.has_key( 'ratio' ):
            modRatio = kwArgs['ratio']

            if modRatio:
                ratio *= modRatio

        return ratio




class Box( Object ):
    def __init__( self, pos, **kwArgs ):
        Object.__init__( self, pos, **kwArgs )


    def updateSurface( self ):
        Object.updateSurface( self )

        self.surface = self.surface.convert_alpha()
        rect = pygame.Rect( 1, 1, self.width - 2, self.height - 2 )
        self.surface.fill( BLACK_ALPHA, rect )




class BackGround( ImageObject ):
    def __init__( self, pos, image, **kwArgs ):
        ImageObject.__init__( self, pos, image, **kwArgs )




class Shop( ImageObject ):
    def __init__( self, pos, image, **kwArgs ):
        ImageObject.__init__( self, pos, image, **kwArgs )




class Bush( ImageObject ):
    def __init__( self, pos, image, **kwArgs ):
        ImageObject.__init__( self, pos, image, **kwArgs )




class Arrow( ImageObject ):
    def __init__( self, pos, image, **kwArgs ):
        ImageObject.__init__( self, pos, image, **kwArgs )




class Monster( ImageObject ):
    def __init__( self, pos, image, **kwArgs ):
        ImageObject.__init__( self, pos, image, **kwArgs )




class Coin( ImageObject ):
    def __init__( self, pos, image, **kwArgs ):
        ImageObject.__init__( self, pos, image, **kwArgs )




# Creates text in world coordinates.
class Text( Object ):
    def __init__( self, pos, text, **kwArgs ):
        self.font = kwArgs.get( 'font', fontCache['basic'] )
        self.text = text

        Object.__init__( self, pos, **kwArgs )


    def updateSurface( self ):
        self.surface = self.font.render( self.text, True, self.colour )




# Creates static text in viewport coordinates.
class StaticText( Text ):
    def __init__( self, pos, text, **kwArgs ):
        Text.__init__( self, pos, text, **kwArgs )


    def update( self, camera = ORIGIN, offset = ORIGIN ):
        # Call the base class, but don't use the offset.
        Text.update( self )




class DebugText( StaticText ):
    def __init__( self, pos, text, **kwArgs ):
        StaticText.__init__( self, pos, text, **kwArgs )



class Score( StaticText ):
    def __init__( self, pos, score, **kwArgs ):
        kwArgs['colour'] = kwArgs.get( 'colour', WHITE )
        StaticText.__init__( self, pos, 'Money: %d' % score, **kwArgs )


    def updateScore( self, score ):
        self.text = 'Money: %d' % score
        self.updateSurface()
        # Only update when the score changes.
        self.update()




class DynamicObject( ImageObject ):
    def __init__( self, pos, movementStyle, **kwArgs ):
        self.images = images = {}
        images['left'] = kwArgs.get( 'imageL', None )
        images['right'] = kwArgs.get( 'imageR', None )
        images['up'] = kwArgs.get( 'imageUp', None )
        images['down'] = kwArgs.get( 'imageDown', None )
        images['image'] = kwArgs.get( 'image', self.images['left'] )
        self.steps = 0
        self.movementStyle = movementStyle
        self.attachedText = None
        movementStyle.setMoveObject( self )

        ImageObject.__init__( self, pos, self.images['left'], **kwArgs )


    def getBounceAmount( self ):
        # Returns the number of pixels to offset based on the bounce.
        # Larger bounceRate means a slower bounce.
        # Larger bounceHeight means a higher bounce.
        # currentBounce will always be less than bounceRate.
        movementStyle = self.movementStyle
        bounceRate = movementStyle.bounceRate
        bounceHeight = movementStyle.bounceHeight

        return int( math.sin( ( math.pi / float( bounceRate ) ) * movementStyle.bounce ) * bounceHeight )


    def checkUpdateObjectDirection( self ):
        # Flip the player image if changed direction.
        horizontalMovement = self.movementStyle.moving( 'horizontal' )
        verticalMovement = self.movementStyle.moving( 'vertical' )

        if horizontalMovement or verticalMovement:
            if self.attachedText:
                self.detachObject( self.attachedText )

            # self.attachedText = Text( Point( -20, -20 ), horizontalMovement, font=fontCache['small'], colour=GREEN )
            # self.attachObject( self.attachedText )

        if horizontalMovement:
            if 'left' == horizontalMovement and self.mirrorH and self.images.has_key( 'left' ):
                self.mirrorH = False
                self.swapImage( self.images['left'] )
            elif 'right' == horizontalMovement and not self.mirrorH and self.images.has_key( 'right' ):
                # Flip the player image.
                self.mirrorH = True
                self.swapImage( self.images['right'] )
        elif verticalMovement:
            if 'up' == verticalMovement and self.images.has_key( 'up' ):
                self.mirrorV = False
                #self.swapImage( self.images['up'] )
            elif 'down' == verticalMovement and self.images.has_key( 'down' ):
                self.mirrorV = True
                #self.swapImage( self.images['down'] )
                # Up and down images are only for Sheriff Quest, so I suggest making seperate files.


    def setMovement( self, key ):
        self.movementStyle.setMovement( key )
        self.checkUpdateObjectDirection()


    def stopMovement( self, key ):
        self.movementStyle.stopMovement( key )
        self.checkUpdateObjectDirection()


    def move( self ):
        newPos = self.movementStyle.move( self.pos )
        # print( newPos )

        if newPos != self.pos:
            self.pos = newPos
            self.steps += 1


    def update( self, camera = ORIGIN, offset = ORIGIN, gameOverMode = False, invulnerableMode = False ):
        flashIsOn = round( time.time(), 1 ) * 10 % 2 == 1

        if not gameOverMode and not ( invulnerableMode and flashIsOn ):
            if offset == ORIGIN :
                # Add jitter or bounce as an offset.
                offset = Point( 0, - self.getBounceAmount() )

            Object.update( self, camera, offset )
            self.setVisible( True )
        else:
            self.setVisible( False )




class Player( DynamicObject ):
    def __init__( self, pos, movementStyle, **kwArgs ):
        DynamicObject.__init__( self, pos, movementStyle, **kwArgs )


    # Override updateCollisionRect() from Object.
    def updateCollisionRect( self ):
        # Use a smaller collision rectangle that represents the player's feet.
        self.colRect = colRect = self.rect.copy()
        # Collision rect from feet to a quarter height.
        colRect.top = colRect.top + ( ( colRect.height * 3 ) / 4 )
        colRect.height = colRect.height / 4
        # Collision rect thinner than the image width by a quarter on each side.
        # colRect.left = colRect.left + ( colRect.width / 4 )
        # colRect.width = colRect.width / 2



class Sprite( DynamicObject ):
    def __init__( self, pos, movementStyle, **kwArgs ):
        DynamicObject.__init__( self, pos, movementStyle, **kwArgs )
