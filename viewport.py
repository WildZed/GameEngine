# Monkey-Rabbit Games
# ViewPort

import random, pygame, copy
from pygame.locals import *
from geometry import *
from game_utils import fontCache
from game_constants import *


# Constants:

DEFAULT_BACKGROUND_COLOUR = WHITE
# How far from the center the player moves before moving the camera.
CAMERASLACK = 90




class ViewPort( object ):
    # Class variables.
    debugDraw = False


    @staticmethod
    def setDebugDraw( on ):
        ViewPort.debugDraw = on


    @staticmethod
    def toggleDebugDraw():
        ViewPort.debugDraw = not ViewPort.debugDraw


    @staticmethod
    def sdrawRect( surface, rect, colour = BLACK ):
        pygame.draw.rect( surface, colour, rect )


    @staticmethod
    def sdrawBox( surface, rect, colour = BLACK ):
        pygame.draw.lines( surface, colour, True, ( rect.topleft, rect.topright, rect.bottomright, rect.bottomleft ) )


    @staticmethod
    def sdrawPos( surface, pos, colour = BLACK ):
        rect = Rectangle( pos - 20, pos + 20 )
        points = rect.asTupleTuple()
        pygame.draw.lines( surface, self.colour, True, points )


    def __init__( self, width, height ):
        self.width = width
        self.height = height
        self.halfWidth = int( width / 2 )
        self.halfHeight = int( height / 2 )
        self.backGroundColour = DEFAULT_BACKGROUND_COLOUR
        # Camera is the top left of where the camera view is.
        self.camera = Point()

        pygame.init()

        self.displaySurface = pygame.display.set_mode( ( width, height ) )
        fontCache.addFont( 'basic', 'freesansbold', 32 )
        fontCache.addFont( 'small', 'freesansbold', 22 )


    def resetCamera( self ):
        camera = Point()


    def adjustCamera( self, pos ):
        camera = self.camera

        # print "Camera %s" % camera
        # print "Pos %s" % pos

        if ( ( camera.x + self.halfWidth ) - pos.x ) > CAMERASLACK:
            camera.x = pos.x + CAMERASLACK - self.halfWidth
        elif ( pos.x - ( camera.x + self.halfWidth ) ) > CAMERASLACK:
            camera.x = pos.x - CAMERASLACK - self.halfWidth

        if ( ( camera.y + self.halfHeight ) - pos.y ) > CAMERASLACK:
            camera.y = pos.y + CAMERASLACK - self.halfHeight
        elif ( pos.y - ( camera.y + self.halfHeight ) ) > CAMERASLACK:
            camera.y = pos.y - CAMERASLACK - self.halfHeight


    def getWorldCoordinate( self, pos ):
        return pos + self.camera


    def positionNear( self, pos, oldPos, distance ):
        xDist = abs( pos.x - oldPos.x )
        yDist = abs( pos.y - oldPos.y )
        isNear = False

        if xDist <= distance and yDist <= distance:
            isNear = True

        return isNear


    def getCameraRect( self ):
        return pygame.Rect( self.camera.x, self.camera.y, self.width, self.height )


    def getRandomX( self ):
        return random.randint( self.camera.x - self.width, self.camera.x + ( 2 * self.width ) )


    def getRandomY( self ):
        return random.randint( self.camera.y - self.height, self.camera.y + ( 2 * self.height ) )


    def getRandomPos( self ):
        return Point( getRandomX(), getRandomY() )


    def getRandomOffCameraPos( self, objWidth, objHeight ):
        # Create a Rect of the camera view.
        camera = self.camera
        width = self.width
        height = self.height
        cameraRect = self.getCameraRect()
        objRect = pygame.Rect( 0, 0, objWidth, objHeight )

        while True:
            pos = getRandomPos()
            # Create a Rect object with the random coordinates and use colliderect()
            # to make sure the right edge isn't in the camera view.
            objRect = pygame.Rect( pos.x, pos.y, objWidth, objHeight )

            if not objRect.colliderect( cameraRect ):
                break

        return Point( x, y )


    def drawBackGround( self, colour ):
        self.backGroundColour = colour
        self.displaySurface.fill( colour )


    def drawRect( self, rect, **kwArgs ):
        ViewPort.drawBox( self.displaySurface, rect, **kwArgs )


    def drawBox( self, rect, **kwArgs ):
        ViewPort.drawBox( self.displaySurface, rect, **kwArgs )


    def drawPos( self, pos, **kwArgs ):
        ViewPort.drawPos( self.displaySurface, pos, **kwArgs )


    # Does the point collide with a colour other than the background colour.
    def collisionOfPoint( self, pos, obj = None, collisionColour = None ):
        collides = ( 0 > pos.x or pos.x >= self.width ) or ( 0 > pos.y or pos.y >= self.height )

        if collides:
            return True

        # Use the object's bounding rectangle to filter the position, if provided.
        # Convert point to world (object) coordinates.
        collides = ( obj is None or obj.collidesWithPoint( self.getWorldCoordinate( pos ), True ) )

        # print "collisionAtPoint pos %s camera %s wpos %s rect %s collides %s" % ( pos, self.camera, self.getWorldCoordinate( pos ), obj.asRectangle(), collides )

        if collides:
            if collisionColour is None:
                collisionColour = self.backGroundColour

            # print pos

            # Find the colour on the display at the given position.
            colour = pygame.display.get_surface().get_at( pos.asTuple() )
            # Drop the mask from the return colour tuple.
            colour = colour[:3]
            collides = ( colour != collisionColour )

            # print "collisionAtPoint %s col %s bgcol %s" % ( collides, colour, self.backGroundColour )

        return collides


    # Does the point collide with a colour other than the background colour.
    def collisionOfRect( self, rect, obj = None, collisionColour = None ):
        collides = ( 0 > pos.x or pos.x >= self.width ) or ( 0 > pos.y or pos.y >= self.height )

        if collides:
            return True

        # Use the object's bounding rectangle to filter the position, if provided.
        collides = ( obj is None or obj.collidesWithPoint( pos, True ) )

        # print "collisionAtPoint %s %s %s" % ( pos, obj.asRect(), collides )

        if collides:
            if collisionColour is None:
                collisionColour = self.backGroundColour

            # print pos

            # Find the colour on the display at the given position.
            colour = pygame.display.get_surface().get_at( pos.asTuple() )
            # Drop the mask from the return colour tuple.
            colour = colour[:3]
            collides = ( colour != collisionColour )

            # print "collisionAtPoint %s col %s bgcol %s" % ( collides, colour, self.backGroundColour )

        return collides


    def update( self ):
        pygame.display.update()


    def playSound( self, soundFileName ):
        soundFilePath = soundFileName + '.ogg'
        pygame.mixer.init()
        # pygame.mixer.pre_init(44100, -16, 2, 2048)
        # pygame.init()
        sound = pygame.mixer.Sound( soundFilePath )
        sound.play()
        # pygame.time.delay(8000)
        # ]]


    def loadMusic( self, musicFile ):
        pygame.mixer.music.load( musicFile )


    def playMusic( self, loops = 0 ):
        try:
            pygame.mixer.music.play( loops=loops, start=0.0 )
        except:
            import traceback

            traceback.print_exc()



