# Monkey-Rabbit Games
# Game Engine

import sys, pygame
import game_map
from pygame.locals import *
from geometry import *
from game_utils import fontCache


# Constants.

DEFAULT_FPS = 30 # frames per second to update the screen




class Game( object ):
    currentGame = None


    def __init__( self, name, iconName, viewPort ):
        # Set up the game state variables.
        print( "Initialising game engine..." )

        # Store the current game for debugging purposes.
        # Only one instance supported.
        Game.currentGame = self

        self.viewPort = viewPort
        self.clickDragLimit = 10
        self.fpsClock = pygame.time.Clock()
        self.updateOrder = None
        print( "Loading images..." )
        self.images = game_map.ImageStore()
        iconImage = self.images.load( iconName )
        self.loadImages()

        pygame.display.set_caption( name )
        pygame.display.set_icon( iconImage )

        print( "Game run initialisation..." )
        self.init()
        print( "Game engine initialised." )


    def init( self ):
        self.running = True
        self.paused = False
        self.clickPos = None
        self.dragPos = None
        self.gameMap = game_map.Map()

        print( "Initialising map..." )
        self.initMap()


    def loadImages( self ):
        pass

    # Initialise the contents of the map
    def initMap( self ):
        pass


    def reset( self ):
        self.init()


    def terminate( self ):
        pygame.quit()
        sys.exit()


    def setPaused( self, paused = True ):
        self.paused = paused
        self.gameMap.setPaused( paused )


    def togglePaused( self ):
        self.paused = not self.paused
        self.gameMap.setPaused( self.paused )


    def setGameMap( self, gameMap ):
        self.gameMap = gameMap


    # Control drawing order.
    def setDrawOrder( self, *args ):
        self.gameMap.setDrawOrder( args )


    # Control update order. This may not matter but if it does this will control it.
    def setUpdateOrder( self, *args ):
        self.updateOrder = args


    def addDebugText( self, text, pos, colour ):
        self.gameMap.addObject( DebugText( fontCache['basic'], text, pos, colour ) )
        # DebugText( '%s' % (pos), ( pos.x + 80, pos.y + 40 ), RED )
        # DebugText( '%s' % (rect), ( pos.x + 120, pos.y + 80 ), RED )


    def postEvent( self, event ):
        pygame.event.post( event )


    def processEvents( self ):
        # Event handling loop.
        for event in pygame.event.get():
            self.processEvent( event )


    # Generic game event processing.
    def processEvent( self, event ):
        if event.type == QUIT:
            self.terminate()
            self.running = False
        elif KEYUP == event.type:
            if K_ESCAPE == event.key:
                self.terminate()
            elif K_F5 == event.key:
                self.running = False
            elif K_F12 == event.key:
                import viewport

                viewport.ViewPort.toggleDebugDraw()
            elif K_PAUSE == event.key:
                self.togglePaused()
        elif MOUSEBUTTONDOWN == event.type:
            # Remember position.
            self.clickPos = Point( event.pos )
        elif MOUSEBUTTONUP == event.type:
            # If clickPos nearby event.pos.
            dragPos = Point( event.pos )
            self.dragPos = None

            if self.clickPos and self.viewPort.positionNear( dragPos, self.clickPos, self.clickDragLimit ):
                viewPort = self.viewPort
                gameMap = self.gameMap
                scene = gameMap.getScene()

                if scene:
                    clickPos = viewPort.getWorldCoordinate( self.clickPos )
                    event = scene.collidesWithPoint( clickPos )
                    viewPort.postEvent( event )
            else:
                self.dragPos = dragPos


    # Update the state of the game.
    def updateState( self ):
        # Move the sprites and other dynamic objects.
        if not self.paused:
            self.gameMap.move()


    # Update the positions of all the map objects according to the camera and new positions.
    def updateMap( self ):
        viewPort = self.viewPort
        gameMap = self.gameMap

        # Update the objects offset by the camera.
        gameMap.update( viewPort.camera, updateOrder=self.updateOrder )


    # Update the game state, map and player.
    def update( self ):
        self.updateState()
        self.updateMap()


    def draw( self ):
        viewPort = self.viewPort
        gameMap = self.gameMap

        # Draw all the map objects.
        gameMap.draw( viewPort )

        viewPort.update()


    def run( self ):
        self.draw()

        # Main game loop.
        while self.running:
            self.update()
            self.draw()
            self.processEvents()

            self.fpsClock.tick( DEFAULT_FPS )
