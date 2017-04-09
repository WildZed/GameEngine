# Monkey-Rabbit Games
# ViewPort

import random, sys, time, math, pygame, copy
from geometry import *
from pygame.locals import *


# Constants:

DEFAULT_BACKGROUND_COLOUR = ( 255, 255, 255 )
# How far from the center the player moves before moving the camera.
CAMERASLACK = 90




class ViewPort:
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
        self.basicFont = pygame.font.Font( 'freesansbold.ttf', 32 )


    def adjustCamera( self, pos ):
        camera = self.camera

        if ( camera.x + self.halfWidth ) - pos.x > CAMERASLACK:
            camera.x = pos.x + CAMERASLACK - self.halfWidth
        elif pos.x - ( camera.x + self.halfWidth ) > CAMERASLACK:
            camera.x = pos.x - CAMERASLACK - self.halfWidth

        if ( camera.y + self.halfHeight ) - pos.y > CAMERASLACK:
            camera.y = pos.y + CAMERASLACK - self.halfHeight
        elif pos.y - ( camera.y + self.halfHeight ) > CAMERASLACK:
            camera.y = pos.y - CAMERASLACK - self.halfHeight


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


    def drawRect( self, rect, colour ):
        pygame.draw.rect( self.displaySurface, colour, rect )


    def collisionAtPoint( self, pos, obj = None ):
        # Use the object's bounding rectangle to filter the position, if provided.
        collides = ( obj is None or obj.collidesWithPoint( pos, True ) )

        # print "collisionAtPoint %s %s %s" % ( pos, obj.asRect(), collides )

        if collides:
            # Find the colour on the display at the given position.
            colour = pygame.display.get_surface().get_at( pos.asTuple() )
            collides = ( colour != self.backGroundColour )

            # print "collisionAtPoint %s col %s bgcol %s" % ( collides, colour, self.backGroundColour )

        return collides


    def draw( self ):
        pygame.display.update()


    def playSound( self, soundFileName ):
        soundFilePath = 'C:/Users/Zed/Documents/Matt/Programming/' + soundFileName + '.ogg'
        pygame.mixer.init()
        # pygame.mixer.pre_init(44100, -16, 2, 2048)
        # pygame.init()
        sound = pygame.mixer.Sound( soundFilePath )
        sound.play()
        # pygame.time.delay(8000)
        # ]]


    def loadMusic( self, musicFile ):
        pygame.mixer.music.load( musicFile )


    def playMusic( self ):
        pygame.mixer.music.play( loops=0, start=0.0 )



