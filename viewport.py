# Monkey-Rabbit Games
# ViewPort

import random, pygame, copy, os
from pygame.locals import *
from geometry import *
import game_utils as gu
import game_constants as gc


# Constants:

DEFAULT_BACKGROUND_COLOUR = gc.WHITE
# How far from the center the player moves before moving the camera.
DEFAULT_CAMERASLACK = 90




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
    def sdrawRect( surface, rect, colour = gc.BLACK ):
        pygame.draw.rect( surface, colour, rect )


    @staticmethod
    def sdrawBox( surface, rect, colour = gc.BLACK ):
        pygame.draw.lines( surface, colour, True, ( rect.topleft, rect.topright, rect.bottomright, rect.bottomleft ) )


    @staticmethod
    def sdrawPos( surface, pos, colour = gc.BLACK ):
        rect = Rectangle( pos - 20, pos + 20 )
        points = rect.asTupleTuple()
        pygame.draw.lines( surface, colour, True, points )


    def __init__( self, width, height, topLeft = None ):
        self.backGroundColour = DEFAULT_BACKGROUND_COLOUR
        # Camera is the top left of where the camera view is.
        self.camera = Point( 0, 0 )
        self.cameraSlack = DEFAULT_CAMERASLACK
        self.cameraMovementStyle = None

        if topLeft:
            self.setWindowPosition( topLeft )

        pygame.init()
        self.setSize( width, height )
        gu.fontCache.addFont( 'basic', 'freesansbold', 32 )
        gu.fontCache.addFont( 'small', 'freesansbold', 22 )
        # print( pygame.display.Info() )


    def setWindowPosition( self, topLeft ):
        os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % ( topLeft.x, topLeft.y )


    def setSize( self, width, height ):
        self.width = width
        self.height = height
        self.halfWidth = int( width / 2 )
        self.halfHeight = int( height / 2 )
        size = ( width, height )
        self.displaySurface = pygame.display.set_mode( size, HWSURFACE | DOUBLEBUF | RESIZABLE )
        self.surface = self.displaySurface.convert()


    def resize( self, width, height ):
        self.setSize( width, height )
        self.update()


    def setCameraSlack( self, cameraSlack = DEFAULT_CAMERASLACK ):
        self.cameraSlack = cameraSlack


    def resetCamera( self ):
        self.camera = Point( 0, 0  )


    def adjustCamera( self, pos ):
        camera = self.camera
        cameraSlack = self.cameraSlack
        adjusted = False

        # print "Camera %s" % camera
        # print "Pos %s" % pos

        if ( ( camera.x + self.halfWidth ) - pos.x ) > cameraSlack:
            camera.x = pos.x + cameraSlack - self.halfWidth
            adjusted = True
        elif ( pos.x - ( camera.x + self.halfWidth ) ) > cameraSlack:
            camera.x = pos.x - cameraSlack - self.halfWidth
            adjusted = True

        if ( ( camera.y + self.halfHeight ) - pos.y ) > cameraSlack:
            camera.y = pos.y + cameraSlack - self.halfHeight
            adjusted = True
        elif ( pos.y - ( camera.y + self.halfHeight ) ) > cameraSlack:
            camera.y = pos.y - cameraSlack - self.halfHeight
            adjusted = True

        return adjusted


    def setCameraMovementStyle( self, cameraMovementStyle ):
        self.cameraMovementStyle = cameraMovementStyle


    def setCameraMovement( self, **kwArgs ):
        if self.cameraMovementStyle:
            self.cameraMovementStyle.setMovement( **kwArgs )


    def stopCameraMovement( self, **kwArgs ):
        if self.cameraMovementStyle:
            self.cameraMovementStyle.stopMovement( **kwArgs )


    def moveCamera( self ):
        if self.cameraMovementStyle:
            self.camera = self.cameraMovementStyle.move( self.camera )


    def getWorldCoordinate( self, pos ):
        return pos + self.camera


    def getViewPortCoordinate( self, pos ):
        return pos - self.camera


    def positionNear( self, pos, oldPos, distance ):
        xDist = abs( pos.x - oldPos.x )
        yDist = abs( pos.y - oldPos.y )
        isNear = False

        if xDist <= distance and yDist <= distance:
            isNear = True

        return isNear


    def getViewportRect( self ):
        return pygame.Rect( 0, 0, self.width, self.height )


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
        self.surface.fill( colour )


    def drawRect( self, rect, **kwArgs ):
        ViewPort.sdrawRect( self.surface, rect, **kwArgs )


    def drawBox( self, rect, **kwArgs ):
        ViewPort.sdrawBox( self.surface, rect, **kwArgs )


    def drawPos( self, pos, **kwArgs ):
        ViewPort.sdrawPos( self.surface, pos, **kwArgs )


    # Does the point collide with a colour other than the background colour.
    def collisionOfPoint( self, pos, obj = None, collisionColour = None ):
        collides = ( 0 > pos.x or pos.x >= self.width ) or ( 0 > pos.y or pos.y >= self.height )

        if collides:
            return False

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


    def postEvent( self, event ):
        if event:
            pygame.event.post( event )


    def update( self ):
        viewRect = self.getViewportRect()
        self.displaySurface.blit( self.surface, viewRect )
        pygame.display.update( viewRect )


    def playSound( self, soundFileName, ext = 'ogg', checkBusy = False, soundsDir = 'sounds' ):
        if checkBusy and pygame.mixer.get_busy():
            # print "Not playing sound %s because already playing a sound." % soundFileName
            return

        soundFilePath = '%s/%s.%s' % ( soundsDir, soundFileName, ext )
        pygame.mixer.init()
        # pygame.mixer.pre_init(44100, -16, 2, 2048)
        # pygame.init()
        sound = pygame.mixer.Sound( soundFilePath )
        sound.play()
        # pygame.time.delay(8000)
        # ]]


    def loadMusic( self, musicFile, soundsDir = 'sounds' ):
        musicFile = '%s/%s' % ( soundsDir, musicFile )
        pygame.mixer.music.load( musicFile )
        self._paused = False


    def pauseMusic( self ):
        if pygame.mixer.music.get_busy():
            if self._paused:
                self._paused = False
                pygame.mixer.music.unpause()
            else:
                self._paused = True
                pygame.mixer.music.pause()


    def playMusic( self, loops = 0 ):
        try:
            pygame.mixer.music.play( loops=loops, start=0.0 )
        except:
            import traceback

            traceback.print_exc()



