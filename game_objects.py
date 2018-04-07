# Monkey-Rabbit Games
# Game Objects

import random, time, math, pygame, copy
import viewport
from pygame.locals import *
from geometry import *
from game_utils import fontCache, debugPrintMask
from game_constants import *


# Constants.

# Generic types of object.
# Special interactions can be overloaded by testing for the collision item's type.
class InteractionType( object ):
    NONE = 0
    IMPERVIOUS = 1      # Objects that collide with all objects.
    SOLID = 2           # Objects that collide with other solid objects.
    OVERLAY = 4         # Objects that don't normally collide with others, but otherwise interact, eg. coin.
    GHOST = 8           # Only interacts with things sensitive to ghosts.
    NEUTRINO = 64       # Very rarely interacts. Only with huge tanks of water.




# Example of access dataObj.<attr> and setting dataObj.<attr> = <value>.
class Data( object ):
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
class Object( object ):
    # Constants.
    DEFAULT_OBJECT_SIZE = 20


    # Constructor.
    def __init__( self, pos, **kwArgs ):
        # generalSize = random.randint( 5, 25 )
        # multiplier = random.randint( 1, 3 )
        # self.width  = ( generalSize + random.randint( 0, 10 ) ) * multiplier
        # self.height = ( generalSize + random.randint( 0, 10 ) ) * multiplier
        self.parent = None
        self.scene = None
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
        self.vpRect = None
        self.vpColRect = None
        self.attachedObjects = []
        self.surface = None
        # The mask used for collision detection.
        self.mask = None
        # Keep hold of the surface used to create the mask for debugging purposes.
        self.maskSurface = None
        # The object type and collision mask used to check if objects can collide.
        self.objectProperties = kwArgs.get( 'objectProperties', InteractionType.SOLID )
        self.interactionMask = kwArgs.get( 'interactionMask', InteractionType.IMPERVIOUS | InteractionType.SOLID | InteractionType.OVERLAY )
        self.collisionMask = kwArgs.get( 'collisionMask', InteractionType.IMPERVIOUS | InteractionType.SOLID )
        # Surface created first. Rects are calculated from the surface width and height.
        self.updateSurface()
        self.updateRect()


    def delete( self ):
        if self.scene:
            self.scene.deleteObject( self )


    def __repr__( self ):
        return "%s: '%s' %s" % ( self.__class__.__name__, self.name, self.pos )


    def setVisible( self, visible ):
        self.visible = visible


    def getScene( self ):
        return self.scene


    # Only call from Scene.
    def setScene( self, scene ):
        self.scene = scene


    def setObjectProperties( self, objectProperties ):
        self.objectProperties = objectProperties


    def setInteractionMask( self, interactionMask ):
        self.interactionMask = interactionMask


    def setCollisionMask( self, collisionMask ):
        self.collisionMask = collisionMask


    # Insert the supplied keyword unless set from the constructor.
    def mergeKwArg( self, key, value, kwArgs ):
        kwArgs[key] = kwArgs.get( key, value )
        # print "mergeKwArg %s %s" % ( key, kwArgs[key] )


    def mergeNonInteractingKwArgs( self, kwArgs ):
        self.mergeKwArg( 'objectProperties', InteractionType.OVERLAY, kwArgs )
        self.mergeKwArg( 'interactionMask', InteractionType.IMPERVIOUS | InteractionType.SOLID, kwArgs )
        self.mergeKwArg( 'collisionMask', InteractionType.IMPERVIOUS, kwArgs )


    def moveToScene( self, scene ):
        # Cannot use this to add or delete from scene.
        if scene and self.scene:
            self.scene.moveObjectToScene( self, scene )


    def getPos( self ):
        return self.pos


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


    def getWidth( self ):
        return self.size


    def getHeight( self ):
        return int( ( float( self.size ) * self.ratio ) + 0.5 )


    def getSurface( self ):
        width = self.getWidth()
        height = self.getHeight()
        surface = pygame.Surface( ( width, height ) )
        surface.fill( self.colour )

        return surface


    # Get a mask surface given a surface (image display object).
    def getMaskSurface( self, surface ):
        width, height = surface.get_size()
        # Create a surface of the given surface's width and height.
        # maskSurface = pygame.Surface( ( width, height ) )
        maskSurface = pygame.Surface.copy( surface )
        maskSurface.fill( 0 )
        # Get rect and collision rect relative to ORIGIN for blitting just the collision part of the image.
        rect = self.getRect()
        colRect = self.getCollisionRect( rect )
        relTop = colRect.top - rect.top
        relLeft = colRect.left - rect.left
        # Area of surface to blit onto maskSurface.
        blitArea = ( relLeft, relTop, colRect.width, colRect.height )
        # Destination in maskSurface needs to match area.
        dest = ( relLeft, relTop )
        maskSurface.blit( surface, dest, area=blitArea )

        return maskSurface


    def updateSurface( self ):
        self.surface = self.getSurface()
        self.maskSurface = self.getMaskSurface( self.surface )
        self.mask = pygame.mask.from_surface( self.maskSurface )


    def getPositionStyleOffset( self, camera = ORIGIN, offset = ORIGIN ):
        if self.positionStyle[:8] == 'viewport':
            offset = camera - offset

        return offset


    def getViewportPositionStyleOffset( self, camera = ORIGIN, offset = ORIGIN ):
        if self.positionStyle[:8] != 'viewport':
            offset = offset - camera

        return offset


    def updateRect( self, camera = ORIGIN, offset = ORIGIN ):
        # Normally the offset is ORIGIN and the world coordinate rectangle is returned.
        self.rect = self.getRect( camera, offset )
        self.colRect = self.getCollisionRect( self.rect )
        self.vpRect = self.getViewportRect( camera, offset )
        self.vpColRect = self.getCollisionRect( self.vpRect )


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


    def getRect( self, camera = ORIGIN, offset = ORIGIN ):
        offset = self.getPositionStyleOffset( camera, offset )

        # Normally the offset is ORIGIN and the world coordinate rectangle is returned.
        return self.getOffSetRect( offset )


    def getCollisionRect( self, rect ):
        # The default collision rectangle is the same as the object's rectangle.
        return rect


    def getViewportRect( self, camera = ORIGIN, offset = ORIGIN ):
        offset = self.getViewportPositionStyleOffset( camera, offset )

        # self.vpRect = self.surface.get_rect()
        return self.getOffSetRect( offset )


    def getSceneCollisions( self, pos ):
        if not self.scene:
            return []

        return self.scene.getCollisions( self )


    def collidesWithScene( self ):
        if not self.scene:
            return False

        collides = self.scene.collides( self )

        return collides


    def canInteract( self, obj ):
        return self.objectProperties & obj.interactionMask and self.interactionMask & obj.objectProperties


    def canCollide( self, obj ):
        # if self.objectProperties == InteractionType.IMPERVIOUS or obj.objectProperties == InteractionType.IMPERVIOUS:
        #     print "self.objectProperties %d" % self.objectProperties
        #     print "obj.objectProperties %d" % obj.objectProperties
        #     print "self.collisionMask %d" % self.collisionMask
        #     print "obj.collisionMask %d" % obj.collisionMask
        return self.objectProperties & obj.collisionMask and self.collisionMask & obj.objectProperties


    def interactsWith( self, obj ):
        return self.canInteract( obj ) and self.collidesWithColour( obj )


    def collidesWith( self, obj ):
        return self.canCollide( obj ) and self.collidesWithColour( obj )


    def collidesWithRect( self, obj ):
        if self == obj:
            collides = False
        else:
            collides = ( 0 != self.colRect.colliderect( obj.colRect ) )

        return collides


    def collidesWithColour( self, obj ):
        collides = self.collidesWithRect( obj )

        if collides:
            offset = obj.pos - self.pos
            overlapPoint = self.mask.overlap( obj.mask, offset.asTuple() )
            collides = ( overlapPoint is not None )

            # print "collidesWithRect %s" % collides

            # numOverlapPixels = self.mask.overlap_area( obj.mask, offset.asTuple() )
            #  = ( numOverlapPixels > 0 )

        return collides


    # Ask if the given world coordinate position collides with the object's full or collision rectangle.
    def collidesWithPoint( self, pos, useFullRect = False ):
        if useFullRect:
            rect = self.rect
        else:
            rect = self.colRect

        collides = ( rect.left <= pos.x and pos.x <= rect.right ) and ( rect.top <= pos.y and pos.y <= rect.bottom )

        # print "collidesWithPoint %s %s %s" % ( pos, rect, collides )
        # print "rect l %s r %s t %s b %s" % ( rect.left, rect.right, rect.top, rect.bottom )

        return collides


    # Deprecated. DON'T USE.
    # Does the object's foot position collide with the collision colour (default is a colour that is not the background colour).
    def collidesWithViewPortColour( self, viewPort, offset = ORIGIN, collisionColour = None ):
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
        return Rectangle( Point( self.pos.x, self.pos.y ), Point( self.pos.x + self.width, self.pos.y + self.height ) )


    def update( self, camera = ORIGIN, offset = ORIGIN ):
        if self.updateCallback:
            self.updateCallback( self, camera, offset )

        self.updateRect( camera, offset )
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
            surface.blit( self.surface, self.vpRect )
            viewPortCls = viewport.ViewPort

            if viewPortCls.debugDraw:
                viewPortCls.sdrawBox( surface, self.vpRect, colour=self.colour )
                viewPortCls.sdrawBox( surface, self.vpColRect, colour=self.colour )
                surface.blit( self.maskSurface, self.vpRect )

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




# Default Image object provides colour collision.
class ImageObject( Object ):
    def __init__( self, pos, image, **kwArgs ):
        self.image = image

        kwArgs['ratio'] = self.calculateRatio( **kwArgs )

        Object.__init__( self, pos, **kwArgs )


    def getSurface( self ):
        width = self.getWidth()
        height = self.getHeight()
        surface = pygame.transform.scale( self.image, ( width, height ) )

        return surface


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


    def getSurface( self ):
        surface = Object.getSurface( self )

        surface = surface.convert_alpha()
        rect = pygame.Rect( 1, 1, self.width - 2, self.height - 2 )
        surface.fill( BLACK_ALPHA, rect )

        return surface




class BackGround( ImageObject ):
    def __init__( self, pos, image, **kwArgs ):
        self.mergeKwArg( 'objectProperties', InteractionType.IMPERVIOUS, kwArgs )
        ImageObject.__init__( self, pos, image, **kwArgs )
        # print "self.objectProperties %d" % self.objectProperties




class Fog( ImageObject ):
    def __init__( self, pos, image, **kwArgs ):
        self.mergeKwArg( 'objectProperties', InteractionType.NONE, kwArgs )
        self.mergeKwArg( 'collisionMask', InteractionType.NONE, kwArgs )
        ImageObject.__init__( self, pos, image, **kwArgs )




class Shop( ImageObject ):
    def __init__( self, pos, image, **kwArgs ):
        ImageObject.__init__( self, pos, image, **kwArgs )




class Digspot( ImageObject ):
    def __init__( self, pos, image, **kwArgs ):
        self.mergeNonInteractingKwArgs( kwArgs )
        ImageObject.__init__( self, pos, image, **kwArgs )

        self.digCount = 0



class Bush( ImageObject ):
    def __init__( self, pos, image, **kwArgs ):
        ImageObject.__init__( self, pos, image, **kwArgs )




class Arrow( ImageObject ):
    def __init__( self, pos, image, **kwArgs ):
        self.mergeNonInteractingKwArgs( kwArgs )
        ImageObject.__init__( self, pos, image, **kwArgs )




class Monster( ImageObject ):
    def __init__( self, pos, image, **kwArgs ):
        self.mergeNonInteractingKwArgs( kwArgs )
        ImageObject.__init__( self, pos, image, **kwArgs )




class Coin( ImageObject ):
    def __init__( self, pos, image, **kwArgs ):
        self.mergeNonInteractingKwArgs( kwArgs )
        ImageObject.__init__( self, pos, image, **kwArgs )




# Creates text in world coordinates.
class Text( Object ):
    def __init__( self, pos, text, **kwArgs ):
        self.font = kwArgs.get( 'font', fontCache['basic'] )
        self.text = text

        Object.__init__( self, pos, **kwArgs )


    def getSurface( self ):
        return self.font.render( self.text, True, self.colour )




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





class Sprite( DynamicObject ):
    def __init__( self, pos, movementStyle, **kwArgs ):
        DynamicObject.__init__( self, pos, movementStyle, **kwArgs )


    # Override getCollisionRect() from Object.
    def getCollisionRect( self, rect ):
        # Use a smaller collision rectangle that represents the player's feet.
        colRect = colRect = rect.copy()
        # Collision rect from feet to a quarter height.
        colRect.top = colRect.top + ( ( colRect.height * 3 ) / 4 )
        colRect.height = colRect.height / 4
        # Collision rect thinner than the image width by a quarter on each side.
        # colRect.left = colRect.left + ( colRect.width / 4 )
        # colRect.width = colRect.width / 2

        return colRect


    def getCentre( self ):
        return Point( self.x + int( ( float( self.size ) + 0.5 ) / 2 ), self.y + int( ( float( self.size ) + 0.5 ) / 2 ) )





class Player( Sprite ):
    def __init__( self, pos, movementStyle, **kwArgs ):
        Sprite.__init__( self, pos, movementStyle, **kwArgs )
