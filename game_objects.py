# Minitest Games
# Game Objects

import random, time, math, pygame, copy
import viewport
from pygame.locals import *
from geometry import *
import game_utils as gu
import game_constants as gc


# Constants.

# Generic types of object.
# Special interactions can be overloaded by testing for the collision item's type.
class InteractionType( object ):
    NONE = 0
    IMPERVIOUS = 1      # Impervious to anything except perhaps neutrino.
    HARD = 2            # Like the wall of a background.
    SOLID = 4           # Like normal sprites and items.
    OVERLAY = 8         # Normally no collision but some interaction, eg. coin.
    GHOST = 16          # Only interacts with things sensitive to ghosts, but collides with IMPERVIOUS.
    FOG = 32            # Doesn't collide with anything but can have some interaction.
    NEUTRINO = 64       # Very rarely interacts. Only with huge tanks of water.




# Example of access dataObj.<attr> and setting dataObj.<attr> = <value>.
class Data( object ):
    def __init__( self ):
        self.__dict__['_data'] = {}


    def __getattr__( self, key ):
        data = self.__dict__['_data']

        if key == '_data' or key not in data:
            raise AttributeError( "Unrecognised image attribute '%s' in __getattr__!" % key )

        val = data[key]

        return val


    def __setattr__( self, key, val ):
        if key == '_data':
            raise AttributeError( "Image attribute '%s' not allowed in __setattr__!" % key )

        self.__dict__['_data'][key] = val




class CollisionSpecification( object ):
    def __init__( self, width = 0.5, height = 0.25, top = None, bottom = None, left = 0.25, right = None ):
        self.width = ( width is None or width > 1.0 ) and 1.0 or width
        self.height = ( height is None or height > 1.0 ) and 1.0 or height
        bottom = bottom is not None and ( bottom + self.height ) <= 1.0 and bottom or 0.0 # 0.0 default.
        self.top = ( top is None or ( top + self.height ) > 1.0 ) and 1.0 - height - bottom or top
        self.bottom = 1.0 - height - self.top # 0.0 default.
        right = ( right is None or ( right + self.width ) > 1.0 ) and ( 1.0 - width ) / 2 or right # If left is not specified.
        self.left = ( left is None or ( left + self.width ) > 1.0 ) and 1.0 - width - right or left
        self.right = 1.0 - width - self.left




class CollisionData( object ):
    def __init__( self, offset, rect ):
        self.offset = offset
        self.rect = rect




class ImageAnimation( object ):
    def __init__( self, images, speed = 5 ):
        self._images = images
        self._numImages = len( images )
        self._index = 0
        self._speed = 5
        self._counter = 0


    def asImageList( self ):
        return self._images


    def advance( self ):
        self._counter += 1

        if self._counter >= self._speed:
            self._counter = 0
            self._index += 1

            if self._index >= self._numImages:
                self._index = 0


    def getImage( self, advance = True ):
        image = self._images[self._index]

        if advance:
            self.advance()

        return image




class ImageCollection( object ):
    def __init__( self, *args, **kwArgs ):
        self._images = images = kwArgs

        for obj in args:
            if isinstance( obj, ImageCollection ):
                images.update( obj._images )
            elif isinstance( obj, dict ):
                images.update( obj )

        # Add a default image if one doesn't already exist.
        self._images['image'] = images.get( 'image', next( iter( images.values() ), None ) )


    def asImageList( self ):
        images = []

        for image in self._images.values():
            if isinstance( image, pygame.Surface ):
                images.append( image )
            else:
                images.extend( image.asImageList() )

        return images


    def getImage( self, key, advance = True ):
        if not key:
            return None

        image = self._images.get( key, None )

        return isinstance( image, ImageAnimation ) and image.getImage( advance=advance ) or image


    def __getitem__( self, key ):
        return self.getImage( key )



# A generic game object.
class Object( object ):
    # Constants.
    DEFAULT_OBJECT_SIZE = 20

    pickPriority = 2


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
        self.enabled = kwArgs.get( 'enabled', True )
        self.drawOrder = kwArgs.get( 'drawOrder', 4 )
        self.pos = pos
        self.posStack = []
        self.size = kwArgs.get( 'size', Object.DEFAULT_OBJECT_SIZE )
        self.ratio = kwArgs.get( 'ratio', 1.0 )
        # Default position style of 'centre' in world coordinates is the same as '',
        # but '' indicates that no override position style has been passed in.
        # Styles: 'top_left', 'centre', 'relative_top_left', 'relative_centre',
        #         'viewport_top_left', 'viewport_centre'
        self.positionStyle = kwArgs.get( 'positionStyle', '' )
        # print( '%s: positionStyle = %s' % ( self.__class__, self.positionStyle ) )
        self.colour = kwArgs.get( 'colour', gc.BLACK )
        # self.mirrorV = kwArgs.get( 'mirrorV', False )
        # self.mirrorH = kwArgs.get( 'mirrorH', False )
        self.updateCallback = kwArgs.get( 'updateCallback', None )
        self.lifetime = kwArgs.get( 'lifetime', None )

        # The object's world coordinate rectangle containing all of its shape.
        self.rect = None
        # The collision rectangle in world coordinates.
        self.colRect = None
        self._collisionSpecification = kwArgs.get( 'collisionSpecification', None )
        # The object's viewport coordinate rectangle.
        self.vpRect = None
        # self.vpColRect = None
        self.attachedObjects = []
        self.associatedObjects = []
        self.surface = None
        # The mask used for interaction detection.
        self.interactionMask = None
        # The mask used for collision detection.
        self._collisionMask = None
        # Keep hold of the surface used to create the mask for debugging purposes.
        self._collisionMaskSurface = None
        # The object type and collision mask used to check if objects can collide.
        self.objectProperties = kwArgs.get( 'objectProperties', InteractionType.SOLID )
        self.interactionTypes = kwArgs.get( 'interactionTypes', InteractionType.SOLID | InteractionType.OVERLAY | InteractionType.GHOST )
        self.collisionTypes = kwArgs.get( 'collisionTypes', InteractionType.IMPERVIOUS | InteractionType.HARD | InteractionType.SOLID )
        self._staticCollisionMask = kwArgs.get( 'staticCollisionMask', False )
        # Surface created first. Rects are calculated from the surface width and height.
        self.updateSurface( forceUpdateCollisionMask=True )
        self.updateRect()


    def delete( self ):
        if self.scene:
            self.scene.removeObject( self )
            del self


    def __repr__( self ):
        return "%s: '%s' %s" % ( self.__class__.__name__, self.name, self.pos )


    def setVisible( self, visible ):
        self.visible = visible


    def toggleVisibility( self ):
        self.visible = not self.visible


    def setEnabled( self, enabled ):
        self.enabled = enabled


    def toggleEnabled( self ):
        self.enabled = not self.enabled


    def getCentre( self ):
        return Point( self.x + int( ( float( self.size ) + 0.5 ) / 2 ), self.y + int( ( float( self.size ) + 0.5 ) / 2 ) )


    def getScene( self ):
        return self.scene


    # Only call from Scene.
    def setScene( self, scene ):
        self.scene = scene


    def setObjectProperties( self, objectProperties ):
        self.objectProperties = objectProperties


    def setInteractionTypes( self, interactionTypes ):
        self.interactionTypes = interactionTypes


    def setCollisionTypes( self, collisionTypes ):
        self.collisionTypes = collisionTypes


    def mergeOverlayKwArgs( self, kwArgs ):
        kwArgs.setdefault( 'objectProperties', InteractionType.OVERLAY )
        kwArgs.setdefault( 'interactionTypes', InteractionType.IMPERVIOUS | InteractionType.HARD | InteractionType.SOLID )
        kwArgs.setdefault( 'collisionTypes', InteractionType.IMPERVIOUS | InteractionType.HARD )


    def mergeNonInteractingKwArgs( self, kwArgs ):
        kwArgs.setdefault( 'objectProperties', InteractionType.NONE )
        kwArgs.setdefault( 'interactionTypes', InteractionType.NONE )
        kwArgs.setdefault( 'collisionTypes', InteractionType.NONE )


    def moveToScene( self, scene ):
        # Cannot use this to add or delete from scene.
        if scene and self.scene:
            self.scene.moveObjectToScene( self, scene )


    def getPos( self ):
        return self.pos


    def setPos( self, pos ):
        self.pos = pos
        # Updating rects to world coords.
        # No need to update rects, because collision detection doesn't use them.
        # self.updateRect()


    def pushPos( self, newPos, adjustedOldPos = None, offsetOldPos = None ):
        if adjustedOldPos:
            self.pos = adjustedOldPos
        elif offsetOldPos:
            self.pos += offsetOldPos

        self.posStack.append( self.pos )
        self.setPos( newPos )


    def popPos( self ):
        self.setPos( self.posStack.pop() )

        return self.pos


    def getCollisionRectCentre( self ):
        return Point( self.colRect.center )


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
    def getMaskSurface( self, surfaces = None ):
        if not surfaces:
            surfaces = ( self.surface, )

        # Area of surface to blit onto maskSurface.
        blitArea = self.getCollisionArea()
        # Destination in maskSurface needs to match area.
        dest = blitArea[0:2] # ( relLeft, relTop )
        # Assuming that all surfaces are the same size.
        maskSurface = gu.createTransparentSurfaceCopy( surfaces[0] )

        for surface in surfaces:
            maskSurface.blit( surface, dest, area=blitArea )

        # if isinstance( self, Player ):
        #     print( "Player transparent surface:" )
        #     gu.debugPrintSurface( maskSurface )

        return maskSurface


    def updateSurface( self, forceUpdateCollisionMask = False ):
        self.surface = self.getSurface()
        self.interactionMask = pygame.mask.from_surface( self.surface )

        if forceUpdateCollisionMask or not self._staticCollisionMask:
            self.updateCollisionMask()


    def updateCollisionMask( self ):
        self._collisionMaskSurface = self.getMaskSurface()
        self._collisionMask = pygame.mask.from_surface( self._collisionMaskSurface )


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
        # Only uses camera if it is a viewport position style object.
        self.rect = self.getRect( camera, offset )
        self.vpRect = self.getViewportRect( camera, offset )
        self.colRect = self.getCollisionRect( self.rect )


    # Get the object's surface top left (viewport) position given an offset
    # from the object's world coordinate position.
    # This is usually used to find where to draw the surface,
    # which is from top left.
    # OR in other words, get a position offset from the top left position.
    def getOffSetPos( self, offset = ORIGIN ):
        offset = self.pos + offset

        if self.positionStyle[-8:] != 'top_left':
            offset -= Point( self.width / 2, self.height / 2 )

        return offset


    # Get the object's rectangle viewport coordinate and offset from its world coordinate position.
    def getOffSetRect( self, offset = ORIGIN ):
        offSetPos = self.getOffSetPos( offset )

        return pygame.Rect( offSetPos.x, offSetPos.y, self.width, self.height )


    # Offset a rectangle relative to this object's position in viewport coordinates.
    def getOffSetOtherRect( self, rect, offset = ORIGIN ):
        offSetPos = self.getOffSetPos( offset )

        return pygame.Rect( rect.left + offSetPos.x, rect.top + offSetPos.y, rect.width, rect.height )


    def getOffSetRectangle( self, offset = ORIGIN ):
        offsetPos = self.getOffSetPos( offset )

        return Rectangle( ul=offsetPos, width=self.width, height=self.height )


    def getRelativeOffset( self, obj ):
        selfPos = self.getOffSetPos()
        objPos = obj.getOffSetPos()

        return objPos - selfPos


    def attachObject( self, obj, style = 'tight', pos = None ):
        if obj.scene:
            obj.scene.removeObject( obj )

            if pos is None:
                obj.pos = ORIGIN

        if pos:
            obj.pos = pos

        if 'loose' == style or self.drawOrder != obj.drawOrder:
            self.associatedObjects.append( obj )
        else:
            self.attachedObjects.append( obj )

        obj.parent = self

        if obj.positionStyle == '':
            obj.positionStyle = 'relative_centre'

        return obj


    def getAttachedObjects( self ):
        return self.attachedObjects


    def getAssociatedObjects( self ):
        return self.associatedObjects


    def getNamedAttachedObject( self, name ):
        for obj in self.attachedObjects:
            if obj.name == name:
                return obj

        for obj in self.associatedObjects:
            if obj.name == name:
                return obj

        return None


    def detachObject( self, obj ):
        try:
            obj.parent = None
            self.attachedObjects.remove( obj )
            self.associatedObjects.remove( obj )
        except ValueError:
            obj = None

        return obj


    def detachNamedObject( self, name ):
        attachedObject = getNamedAttachedObject( name )

        if attachedObject:
            self.detachObject( attachedObject )

        return attachedObject


    def detachAllObjects( self, includeAssociated = False ):
        attachedObjectList = self.attachedObjects
        self.attachedObjects = []

        if includeAssociated:
            attachedObjectList.extend( self.associatedObjects )
            self.associatedObjects = []

        for obj in attachedObjectList:
            obj.parent = None

        return attachedObjectList


    # Get the object's rectangle given an optional camera shift and/or additional offset.
    # With no offset, it gives the rectangle in world coordinates.
    def getRect( self, camera = ORIGIN, offset = ORIGIN ):
        offset = self.getPositionStyleOffset( camera, offset )

        # Normally the offset is ORIGIN and the world coordinate rectangle is returned.
        return self.getOffSetRect( offset )


    # Get the object's rectangle in viewport coordinates given camera shift and/or additional offset.
    def getViewportRect( self, camera = ORIGIN, offset = ORIGIN ):
        offset = self.getViewportPositionStyleOffset( camera, offset )

        # self.vpRect = self.surface.get_rect()
        return self.getOffSetRect( offset )


    def getCollisionMask( self ):
        return self._collisionMask


    def getCollisionRect( self, rect ):
        collisionSpec = self._collisionSpecification

        # The default collision rectangle is the same as the object's rectangle.
        if not collisionSpec:
            return rect

        # Use a smaller collision rectangle that represents the player's feet.
        colRect = colRect = rect.copy()
        # Collision rect from feet to a quarter height.
        colRect.top = int( colRect.top + ( colRect.height * collisionSpec.top ) )
        colRect.height = int( colRect.height * collisionSpec.height )
        # Collision rect thinner than the image width by a quarter on each side.
        colRect.left = int( colRect.left + ( colRect.width * collisionSpec.left ) )
        colRect.width = int( colRect.width * collisionSpec.width )

        return colRect


    def getCollisionArea( self ):
        # Get rect and collision rect relative to ORIGIN for blitting just the collision part of the image.
        rect = self.getRect()
        colRect = self.getCollisionRect( rect )
        relTop = colRect.top - rect.top
        relLeft = colRect.left - rect.left

        return ( relLeft, relTop, colRect.width, colRect.height )


    def getSceneCollisions( self ):
        if not self.scene:
            return []

        return self.scene.getAllCollisions( self )


    def collidesWithScene( self ):
        if not self.scene:
            return None

        event = self.scene.collides( self )

        return event


    def isInteractionTypePair( self, obj, objTypePlusNameA, objTypePlusNameB ):
        selfType = self.__class__.__name__
        objType = obj.__class__.__name__

        splitA = objTypePlusNameA.split( '=' )
        splitB = objTypePlusNameB.split( '=' )
        objTypeA = splitA[0]
        objTypeB = splitB[0]

        if 2 == len( splitA ):
            nameA = splitA[1]
        else:
            nameA = None

        if 2 == len( splitB ):
            nameB = splitB[1]
        else:
            nameB = None

        # print( "Checking iteraction/collision selfType %s objType %s objTypePlusNameA %s objTypePlusNameB %s" % ( selfType, objType, objTypePlusNameA, objTypePlusNameB ) )

        isPair = False

        if selfType == objTypeA and objType == objTypeB:
            if ( not nameA or nameA == self.name ) and ( not nameB or nameB == obj.name ):
                isPair = True
        elif objType == objTypeA and selfType == objTypeB:
            if ( not nameA or nameA == obj.name ) and ( not nameB or nameB == self.name ):
                isPair = True

        return isPair


    def canInteract( self, obj ):
        # if self.objectProperties == InteractionType.GHOST or obj.objectProperties == InteractionType.GHOST:
        #     print( "self.objectProperties %d" % self.objectProperties )
        #     print( "obj.objectProperties %d" % obj.objectProperties )
        #     print( "self.interactionTypes %d" % self.interactionTypes )
        #     print( "obj.interactionTypes %d" % obj.interactionTypes )

        # if self.__class__.__name__ == 'Player' and obj.__class__.__name__ == 'GhostSprite' and self.collidesWithRect( obj ):
        #     print( "Checking interaction for %s and %s" % ( self.__class__.__name__, obj.__class__.__name__ ) )
        #     print( "self.objectProperties %d" % self.objectProperties )
        #     print( "obj.interactionTypes %d" % obj.interactionTypes )
        #     print( "canInteract %s" % ( self.objectProperties & obj.interactionTypes ) )

        return self != obj and self.enabled and obj.enabled and self.interactionTypes & obj.objectProperties


    def canCollide( self, obj ):
        # if self.objectProperties == InteractionType.IMPERVIOUS or obj.objectProperties == InteractionType.IMPERVIOUS:
        #     print( "self.objectProperties %d" % self.objectProperties )
        #     print( "obj.objectProperties %d" % obj.objectProperties )
        #     print( "self.collisionTypes %d" % self.collisionTypes )
        #     print( "obj.collisionTypes %d" % obj.collisionTypes )
        return self != obj and self.enabled and obj.enabled and self.collisionTypes & obj.objectProperties


    def interactsWith( self, obj ):
        interactionPoint = None

        if self.canInteract( obj ):
            interactionPoint = self.interactsWithColour( obj )

        # print( "interacts %s" % interacts )

        return interactionPoint


    def collidesWith( self, obj, forceCollision = False ):
        collisionData = None

        if forceCollision or self.canCollide( obj ):
            collisionData = self.collidesWithColour( obj )

        return collisionData


    def collidesWithRect( self, obj ):
        if self == obj:
            collides = False
        else:
            collides = ( 0 != self.colRect.colliderect( obj.colRect ) )

        return collides


    def collidesWithInteractionMask( self, obj ):
        offset = self.getRelativeOffset( obj )
        overlapOffset = self.interactionMask.overlap( obj.interactionMask, offset.asTuple() )

        if overlapOffset:
            overlapOffset = Point( overlapOffset )

        return overlapOffset


    def getMaskRect( self, mask, offset = ORIGIN ):
        rects = mask.get_bounding_rects()
        numRects = len( rects )

        # Unfortunately get_bounding_rects() doesn't aways work.
        if numRects > 0:
            maskRect = rects[0]

            if numRects > 1:
                maskRect.unionall( rects[1:] )

            maskRect.move_ip( offset.x, offset.y )
        else:
            # print( 'Mask.get_bounding_rects() failed to return overlapping rectangles!' )
            width, height = mask.get_size()
            maskRect = pygame.Rect( offset.x, offset.y, width, height )

        return maskRect



    def collidesWithCollisionMask( self, obj ):
        offset = self.getRelativeOffset( obj ).asTuple()
        overlapOffset = self._collisionMask.overlap( obj._collisionMask, offset )
        collisionData = None

        if overlapOffset:
            overlapOffset = Point( overlapOffset ) # self.getOffSetPos() +
            overlapMask = self._collisionMask.overlap_mask( obj._collisionMask, offset )
            overlapRect = self.getMaskRect( overlapMask, overlapOffset )
            collisionData = CollisionData( overlapOffset, overlapRect )

        # print( "collidesWithRect %s" % collides )

        # numOverlapPixels = self._collisionMask.overlap_area( obj._collisionMask, offset )
        #  = ( numOverlapPixels > 0 )

        return collisionData


    def interactsWithColour( self, obj ):
        return self.collidesWithInteractionMask( obj )


    def collidesWithColour( self, obj, useInteractionMask = False ):
        # Rect is now only used for drawing, not collision. It is not guaranteed to be in the right place.
        # collides = self.collidesWithRect( obj )
        return self.collidesWithCollisionMask( obj )


    # Ask if the given world coordinate position collides with the object's full or collision rectangle.
    def collidesWithPoint( self, pos, useFullRect = False ):
        if useFullRect:
            rect = self.rect
        else:
            rect = self.colRect

        collides = ( rect.left <= pos.x and pos.x <= rect.right ) and ( rect.top <= pos.y and pos.y <= rect.bottom )

        # print( "collidesWithPoint %s %s %s" % ( pos, rect, collides ) )
        # print( "rect l %s r %s t %s b %s" % ( rect.left, rect.right, rect.top, rect.bottom ) )

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


    # Update the view of the object, ie. when in the current scene.
    def update( self, camera = ORIGIN, offset = ORIGIN ):
        if self.updateCallback:
            self.updateCallback( self, camera, offset )

        self.updateRect( camera, offset )
        self.updateAttachedObjects( camera, offset )
        self.checkLifetime()


    # Need to convert this to real time based delay.
    def checkLifetime( self ):
        if self.lifetime:
            self.lifetime -= 1

            if self.lifetime <= 0:
                self.parent.detachObject( self )
                del self


    def updateAttachedObjects( self, camera = ORIGIN, offset = ORIGIN ):
        for attachedObject in self.attachedObjects + self.associatedObjects:
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


    def draw( self, surface, viewRect ):
        if self.visible:
            if viewRect.colliderect( self.rect ):
                self.drawToSurface( surface )
                self.drawDebug( surface )

            self.drawAttachedObjects( surface, viewRect )


    def drawToSurface( self, surface ):
        vpRect = self.vpRect

        if False:
            # Faster method to non-per-pixel alpha surface.
            clippedVpRect = vpRect.clip( surface.get_rect() )
            subSurface = surface.subsurface( clippedVpRect ).convert_alpha()
            subSurface.blit( self.surface, (0, 0) )
            # print( 'clippedRect:', clippedVpRect )
            # if isinstance( self, Player ):
            #     print( "Player:" )
            #     gu.debugPrintSurface( self.surface )
            surface.blit( subSurface, clippedVpRect ) #, special_flags=BLEND_RGBA_MULT )
        else:
            # Basic method.
            surface.blit( self.surface, vpRect )


    def drawDebug( self, surface ):
        viewPortCls = viewport.ViewPort

        if not viewPortCls.debugDraw:
            return

        vpRect = self.vpRect
        maskVpRect = vpRect.copy()
        maskVpRect.left += 40
        vpColRect = self.getCollisionRect( vpRect )
        viewPortCls.sdrawBox( surface, vpRect, colour=self.colour )
        viewPortCls.sdrawBox( surface, vpColRect, colour=self.colour )
        # Hmmmm, for some unknown reason convert() makes the mask surface completely invisible, unless it is a non-per-pixel alpha surface, in which case it is completely black.
        collisionMaskSurface = self._collisionMaskSurface # .convert()
        surface.blit( collisionMaskSurface, maskVpRect )


    def drawAttachedObjects( self, surface, viewRect ):
        for attachedObject in self.attachedObjects:
            attachedObject.draw( surface, viewRect )


    def __getattr__( self, key ):
        try:
            selfDict = self.__dict__

            if key == 'width':
                if 'surface' in selfDict:
                    return selfDict['surface'].get_width()
                else:
                    return self.getWidth()
            elif key == 'height':
                if 'surface' in selfDict:
                    return selfDict['surface'].get_height()
                else:
                    return self.getHeight()
            elif key == 'x':
                return selfDict['pos'].x
            elif key == 'y':
                return selfDict['pos'].y

            value = selfDict[key]
        except KeyError:
            raise AttributeError( "Unrecognised Object attribute '%s' in __getattr__!" % key )
        except:
            raise

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
        self._image = image
        self._attachedText = None

        kwArgs['ratio'] = self.calculateRatio( **kwArgs )

        super().__init__( pos, **kwArgs )


    def getSurface( self, image = None ):
        if not image:
            image = self._image

        width = int( self.getWidth() )
        height = int( self.getHeight() )
        surface = pygame.transform.scale( image, ( width, height ) )

        # This prevents collision detection working properly for some reason.
        # It's not supposed to have any effect on per pixel alpha surfaces.
        # if self.scene:
        #     # print( 'Colour key:', surface.get_colorkey() )
        #     surface.set_colorkey( self.scene.backGroundColour, pygame.RLEACCEL )

        return surface


    def getImage( self ):
        return self._image


    def swapImage( self, image ):
        self._image = image
        self.updateSurface()


    def checkSwapImage( self, image ):
        currentImage = self.getImage()

        if not image or image is currentImage:
            return False

        self.swapImage( image )
        swapped = True

        event = self.collidesWithScene()

        if event and event.type == gc.COLLISION_EVENT:
            self.swapImage( currentImage )
            swapped = False

        return swapped


    def calculateRatio( self, **kwArgs ):
        # The ratio of height to width.
        image = self._image
        ratio = float( image.get_height() ) / float( image.get_width() )

        if 'ratio' in kwArgs:
            modRatio = kwArgs['ratio']

            if modRatio:
                ratio *= modRatio

        return ratio


    def attachText( self, text, offset = gc.DEFAULT_IMAGE_OBJECT_TEXT_OFFSET, colour = gc.GREEN ):
        if self._attachedText:
            self.detachObject( self._attachedText )

        self._attachedText = Text( offset, text, font=gu.fontCache['small'], colour=colour )
        self.attachObject( self._attachedText )





class Box( Object ):
    def __init__( self, pos, **kwArgs ):
        super().__init__( pos, **kwArgs )


    def getSurface( self ):
        surface = super().getSurface() #.convert_alpha()
        width = self.getWidth()
        height = self.getHeight()
        rect = pygame.Rect( 1, 1, width - 2, height - 2 )
        surface.fill( gc.BLACK_TRANSPARENT_ALPHA, rect )

        return surface




class Border( ImageObject ):
    def __init__( self, pos, image, **kwArgs ):
        kwArgs.setdefault( 'objectProperties', InteractionType.IMPERVIOUS )
        kwArgs.setdefault( 'interactionTypes', InteractionType.NONE )
        kwArgs.setdefault( 'collisionTypes', InteractionType.IMPERVIOUS | InteractionType.SOLID | InteractionType.OVERLAY | InteractionType.GHOST )
        kwArgs.setdefault( 'drawOrder', 0 )
        super().__init__( pos, image, **kwArgs )
        # print( "self.objectProperties %d" % self.objectProperties )




class BackGround( ImageObject ):
    def __init__( self, pos, image, **kwArgs ):
        kwArgs.setdefault( 'objectProperties', InteractionType.HARD )
        kwArgs.setdefault( 'interactionTypes', InteractionType.NONE )
        kwArgs.setdefault( 'drawOrder', 1 )
        super().__init__( pos, image, **kwArgs )




class SoftBackGround( ImageObject ):
    def __init__( self, pos, image, **kwArgs ):
        self.mergeNonInteractingKwArgs( kwArgs )
        kwArgs.setdefault( 'drawOrder', 1 )
        super().__init__( pos, image, **kwArgs )




class Fog( ImageObject ):
    pickPriority = 1

    def __init__( self, pos, image, **kwArgs ):
        kwArgs.setdefault( 'objectProperties', InteractionType.FOG )
        kwArgs.setdefault( 'interactionTypes', InteractionType.NONE )
        kwArgs.setdefault( 'collisionTypes', InteractionType.NONE )
        kwArgs.setdefault( 'drawOrder', 8 )
        super().__init__( pos, image, **kwArgs )


    def drawToSurface( self, surface ): # override
        vpRect = self.vpRect
        colour = self.surface.get_at( ( 0, 0 ) )

        if False:
            # The fast method. Fill all other areas of the surface with the fog colour.
            gu.fillSurfaceMinusRectangle( surface, vpRect, colour )
            # Clip the fog viewport rectangle by the surface we're drawing to.
            clippedVpRect = vpRect.clip( surface.get_rect() )
            # Make reference sub-set surface with per pixel alpha.
            # WARNING: Per pixel alpha drawing is SLOW.
            # Blit doesn't blit to referenced display surface if it is hardward accelerated.
            subSurface = surface.subsurface( clippedVpRect ).convert_alpha()
            # objClippedRect = vpRect.copy()
            # Create a clipped fog viewport rectangle, relative to the object's surface.
            objClippedRect = pygame.Rect( clippedVpRect.left - vpRect.left, clippedVpRect.top - vpRect.top, clippedVpRect.width, clippedVpRect.height )
            # print( 'obj clipped rect:', objClippedRect )
            # Make reference sub-set fog surface.
            objSubSurface = self.surface.subsurface( objClippedRect )
            # Blit only the remaining clipped area of the fog to the clipped sub-surface.
            subSurface.blit( objSubSurface, (0, 0) )
            # Should be unnecessary because the sub-surface is a reference copy. Except that it doesn't work that way.
            # Apparently only works for the display surface if it is not hardward accelerated.
            surface.blit( subSurface.convert(), clippedVpRect ) #, special_flags=BLEND_RGBA_MULT )
        else:
            # The slow method. Fill a copy window surface with the fog colour and blit (draw) the smaller fog surface onto it with per pixel alpha.
            fogSurface = surface.copy().convert_alpha() # This is neccessary for the fog to work.
            fogSurface.fill( colour )
            fogSurface.blit( self.surface, vpRect, special_flags=BLEND_RGBA_MULT )
            surface.blit( fogSurface, ( 0, 0 ) )




class Shop( ImageObject ):
    pickPriority = 2

    def __init__( self, pos, image, **kwArgs ):
        kwArgs.setdefault( 'drawOrder', 2 )
        super().__init__( pos, image, **kwArgs )




class Digspot( ImageObject ):
    pickPriority = 12

    def __init__( self, pos, image, **kwArgs ):
        self.mergeOverlayKwArgs( kwArgs )
        kwArgs.setdefault( 'drawOrder', 2 )
        super().__init__( pos, image, **kwArgs )
        self.digCount = 0




class Bush( ImageObject ):
    pickPriority = 6

    def __init__( self, pos, image, **kwArgs ):
        # Objects with the same draw order will go behind each other based on the y coordinate.
        # kwArgs.setdefault( 'drawOrder', 2 )
        super().__init__( pos, image, **kwArgs )



# A door or portal.
class Portal( ImageObject ):
    pickPriority = 6

    def __init__( self, pos, image, collisionArea = None, **kwArgs ):
        kwArgs.setdefault( 'collisionSpecification', CollisionSpecification() )
        super().__init__( pos, image, **kwArgs )




class Arrow( ImageObject ):
    pickPriority = 6

    def __init__( self, pos, image, **kwArgs ):
        self.mergeOverlayKwArgs( kwArgs )
        kwArgs.setdefault( 'drawOrder', 2 )
        super().__init__( pos, image, **kwArgs )




class Monster( ImageObject ):
    pickPriority = 6

    def __init__( self, pos, image, **kwArgs ):
        self.mergeOverlayKwArgs( kwArgs )
        kwArgs.setdefault( 'drawOrder', 20 )
        super().__init__( pos, image, **kwArgs )




class Coin( ImageObject ):
    pickPriority = 10

    def __init__( self, pos, image, **kwArgs ):
        self.mergeOverlayKwArgs( kwArgs )
        super().__init__( pos, image, **kwArgs )




# Creates text in world coordinates.
class Text( Object ):
    def __init__( self, pos, text, **kwArgs ):
        self.font = kwArgs.get( 'font', gu.fontCache['basic'] )
        self.text = text
        self.mergeNonInteractingKwArgs( kwArgs )

        super().__init__( pos, **kwArgs )


    def getSurface( self ):
        surface = self.font.render( self.text, True, self.colour )

        # if self.scene:
        #     surface.set_colorkey( self.scene.backGroundColour )

        return surface




# Creates static text in viewport coordinates.
class StaticText( Text ):
    def __init__( self, pos, text, **kwArgs ):
        kwArgs.setdefault( 'positionStyle', 'viewport_top_left' )
        Text.__init__( self, pos, text, **kwArgs )


    # def update( self, camera = ORIGIN, offset = ORIGIN ):
    #     # Call the base class, but don't use the offset.
    #     Text.update( self, camera )




class DebugText( StaticText ):
    def __init__( self, pos, text, **kwArgs ):
        super().__init__( pos, text, **kwArgs )




class Score( StaticText ):
    def __init__( self, pos, score, **kwArgs ):
        kwArgs['colour'] = kwArgs.get( 'colour', gc.WHITE )
        super().__init__( pos, 'Money: %d' % score, **kwArgs )


    def updateScore( self, score ):
        self.text = 'Money: %d' % score
        self.updateSurface()
        # Only update when the score changes.
        self.update()




class DynamicObject( ImageObject ):
    pickPriority = 8

    def __init__( self, pos, movementStyle, **kwArgs ):
        # Can't get property setter to work.
        self.steps = 0
        self._canMove = True
        self._movementStyle = movementStyle
        self._images = self._determineImages( kwArgs )
        movementStyle.setMoveObject( self )
        kwArgs.setdefault( 'staticCollisionMask', True )
        super().__init__( pos, **kwArgs )


    # @property
    # def steps( self ):
    #     return self._steps
    #
    #
    # @steps.setter
    # def steps( self, steps ):
    #     print( "Setting steps to:", steps )
    #     self._steps = steps


    def getMaskSurface( self ):
        return super().getMaskSurface( [ self.getSurface( image ) for image in self._images.asImageList() ] )


    def toggleMovement( self ):
        self._canMove = not self._canMove


    def setMovement( self, **kwArgs ):
        self._movementStyle.setMovement( **kwArgs )


    def stopMovement( self, **kwArgs ):
        self._movementStyle.stopMovement( **kwArgs )


    def debugCollisionEvent( self, event, label = '' ):
        import game

        collisionPoint = event.point
        print( "%sself %s collides in curPos with %s at %s" % ( label, event.obj1.name, event.obj2.name, collisionPoint ) )

        currentGame = game.Game.currentGame
        currentGame.setPaused()
        gameMap = currentGame.gameMap
        gameMap.debugPos( 'collisionPoint', collisionPoint )


    def adjustMoveOffset( self, offset ):
        self._movementStyle.adjustMoveOffset( offset )


    def move( self ):
        if not self._canMove:
            return

        newPos = self._movementStyle.move( self.pos )

        if newPos != self.pos:
            self.setPos( newPos )
            self.steps += 1
            # Updating the object image for the direction is another move, which needs collision detection.
            self.checkSwapImage( self._movementStyle.chooseImage( self._images ) )


    def update( self, camera = ORIGIN, offset = ORIGIN, gameOverMode = False, invulnerableMode = False ):
        flashIsOn = ( ( round( time.time(), 1 ) * 10 ) % 2 ) == 1

        if not gameOverMode and not ( invulnerableMode and flashIsOn ):
            if offset == ORIGIN :
                # Add jitter or bounce as an offset.
                offset = Point( 0, - self._movementStyle.getBounceAmount() )

            Object.update( self, camera, offset )

            if invulnerableMode:
                self.setVisible( True )
        elif invulnerableMode:
            self.setVisible( False )


    def _determineImages( self, kwArgs ):
        images = kwArgs.get( 'image', None )
        images = images if isinstance( images, ImageCollection ) else ImageCollection()
        kwArgs['image'] = images['image']

        return images




class Sprite( DynamicObject ):
    def __init__( self, pos, movementStyle, **kwArgs ):
        kwArgs.setdefault( 'collisionSpecification', CollisionSpecification() )
        super().__init__( pos, movementStyle, **kwArgs )





class GhostSprite( Sprite ):
    def __init__( self, pos, movementStyle, **kwArgs ):
        kwArgs.setdefault( 'objectProperties', InteractionType.GHOST )
        kwArgs.setdefault( 'interactionTypes', InteractionType.SOLID | InteractionType.OVERLAY | InteractionType.GHOST )
        kwArgs.setdefault( 'collisionTypes', InteractionType.IMPERVIOUS | InteractionType.GHOST )
        Sprite.__init__( self, pos, movementStyle, **kwArgs )





class Player( Sprite ):
    def __init__( self, pos, movementStyle, **kwArgs ):
        Sprite.__init__( self, pos, movementStyle, **kwArgs )
