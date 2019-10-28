# Minitest Games
# Game Engine

import sys, pygame
import game_map
from pygame.locals import *
from geometry import *
from game_utils import fontCache
from game_constants import *
from game_objects import *


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
        self.allowDrag = True
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
        self.clackPos = None
        self.dragPos = None
        self.dragObject = None
        self.gameMap = game_map.Map()
        self.cameraMovement = False

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


    def setAllowDrag( self, allowDrag = True ):
        self.allowDrag = allowDrag


    def setPaused( self, paused = True ):
        self.paused = paused
        self.gameMap.setPaused( paused )


    def togglePaused( self ):
        self.paused = not self.paused
        self.gameMap.setPaused( self.paused )


    def setGameMap( self, gameMap ):
        self.gameMap = gameMap


    # Control drawing order.
    # def setDrawOrder( self, *args ):
    #     self.gameMap.setDrawOrder( args )


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


    # Remember mouse button down.
    def setClickPos( self, event ):
        self.clickPos = Point( event.pos )


    # Remember mouse button down.
    def setDragPos( self, event ):
        self.dragPos = Point( event.pos )


    # Remember mouse button up.
    def checkSetClackPosAndSendEvent( self, event ):
        clackPos = Point( event.pos )
        self.clackPos = None
        self.dragObject = None

        # If clickPos nearby event.pos.
        if self.clickPos and self.viewPort.positionNear( clackPos, self.clickPos, self.clickDragLimit ):
            viewPort = self.viewPort
            gameMap = self.gameMap
            scene = gameMap.getScene()

            if scene:
                worldClickPos = viewPort.getWorldCoordinate( self.clickPos )
                event = scene.collidesWithPoint( worldClickPos, useFullRect=True )
                viewPort.postEvent( event )
        else:
            self.clackPos = clackPos


    def checkSetDragObject( self ):
        self.dragObject = None

        if not self.allowDrag:
            return

        gameMap = self.gameMap
        scene = gameMap.getScene()

        if not scene:
            return

        viewPort = self.viewPort
        worldClickPos = viewPort.getWorldCoordinate( self.clickPos )
        event = scene.collidesWithPoint( worldClickPos, useFullRect=True )

        if event and issubclass( type( event.obj ), ( DynamicObject, Portal ) ):
            # print( "Dragging..." )
            self.dragObject = event.obj


    def movePlayerToScene( self, player, portal, scene, otherPortal ):
        gameMap = self.gameMap

        if not gameMap.changeScene( scene ):
            return

        viewPort = self.viewPort
        scene = gameMap.getScene( scene ) # Name or scene.
        player.moveToScene( scene )
        otherPortal = scene.getObject( otherPortal )
        offset = portal.getCollisionRectCentre() - player.getCollisionRectCentre()

        if not player.movementStyle.moving( 'horizontal' ):
            offset.x = 0

        if not player.movementStyle.moving( 'vertical' ):
            offset.y = 0

        newPos = otherPortal.getPos() + offset
        player.setPos( newPos )
        viewPort.adjustCamera( newPos )


    def moveSpriteToScene( self, sprite, portal, scene, otherPortal ):
        gameMap = self.gameMap
        viewPort = self.viewPort
        scene = gameMap.getScene( scene ) # Name or scene.
        sprite.moveToScene( scene )
        otherPortal = scene.getObject( otherPortal )
        offset = portal.getCollisionRectCentre() - sprite.getCollisionRectCentre()

        if not sprite.movementStyle.moving( 'horizontal' ):
            offset.x = 0

        if not sprite.movementStyle.moving( 'vertical' ):
            offset.y = 0

        newPos = otherPortal.getPos() + offset
        sprite.setPos( newPos )


    # Generic game event processing.
    def processEvent( self, event ):
        viewPort = self.viewPort
        gameMap = self.gameMap
        player = gameMap.player

        if event.type == QUIT:
            self.terminate()
            self.running = False
        elif VIDEORESIZE == event.type:
            viewPort.resize( *event.dict['size'] )
        elif KEYDOWN == event.type:
            keyMods = pygame.key.get_mods()

            if keyMods:
                pass
            else:
            if K_c == event.key:
                if player:
                    player.stopMovement()

                self.cameraMovement = True

            if self.cameraMovement:
                viewPort.setCameraMovement( key=event.key )
            elif player:
                # Check if the key moves the player in a given direction.
                player.setMovement( key=event.key )
        elif KEYUP == event.type:
            keyMods = pygame.key.get_mods()

            if keyMods:
                if keyMods & pygame.KMOD_SHIFT:
                    if K_f == event.key:
                        pygame.display.toggle_fullscreen()
            else:
            if K_ESCAPE == event.key:
                self.terminate()
            elif K_F5 == event.key:
                self.running = False
            elif K_F12 == event.key:
                import viewport

                viewport.ViewPort.toggleDebugDraw()
            elif K_PAUSE == event.key:
                self.togglePaused()
            elif K_c == event.key:
                self.cameraMovement = False
                viewPort.stopCameraMovement()
            elif K_m == event.key:
                viewPort.pauseMusic()
            elif K_q == event.key:
                self.running = False
            #elif K_e == event.key:
                # Show the bag.

            if self.cameraMovement:
                viewPort.stopCameraMovement( key=event.key )
            elif player:
                # Check if the key stops the player in a given direction.
                player.stopMovement( key=event.key )
        elif MOUSEBUTTONDOWN == event.type:
            # Remember mouse down position.
            self.setClickPos( event )
            self.checkSetDragObject()
        elif MOUSEBUTTONUP == event.type:
            self.checkSetClackPosAndSendEvent( event )
        elif MOUSEMOTION == event.type:
            self.setDragPos( event )
        # elif event.type == INTERACTION_EVENT:
        #     print( "Interaction event %s <-> %s" % ( event.obj1, event.obj2 ) )
        # elif event.type == COLLISION_EVENT:
        #     print( "Collision event %s <-> %s" % ( event.obj1, event.obj2 ) )
        # elif event.type == CLICK_COLLISION_EVENT:
        #     print( "Click collision event %s <-> %s" % ( event.obj, event.pos ) )


    # Update the state of the game.
    def updateState( self ):
        # Move the sprites and other dynamic objects.
        if not self.paused:
            self.gameMap.move()

        viewPort = self.viewPort
        gameMap = self.gameMap
        player = gameMap.player

        # Adjust camera if beyond the "camera slack".
        if self.cameraMovement:
            viewPort.moveCamera()
        elif player and not self.areDraggingObject():
            playerCentre = player.getCentre()
            viewPort.adjustCamera( playerCentre )


    # Update the positions of all the map objects according to the camera and new positions.
    def updateMap( self ):
        viewPort = self.viewPort
        gameMap = self.gameMap

        # Update the objects offset by the camera.
        gameMap.update( viewPort.camera, updateOrder=self.updateOrder )


    def areDraggingObject( self ):
        return self.dragObject and self.dragPos


    def updateDragObject( self ):
        if not self.areDraggingObject():
            return

        viewPort = self.viewPort
        worldPos = viewPort.getWorldCoordinate( self.dragPos )
        dragObject = self.dragObject
        dragObject.setPos( worldPos )
        objectCentre = dragObject.getCentre()

        if viewPort.adjustCamera( objectCentre ):
            adjustedViewPortPos = viewPort.getViewPortCoordinate( dragObject.getPos() )
            relativePos = self.dragPos - adjustedViewPortPos
            # print( 'Relative drag pos %s' % relativePos )
            relativePos *= 95
            relativePos /= 100
            # print( 'Adjusted relative drag pos %s' % relativePos )
            newMousePos = adjustedViewPortPos + relativePos
            pygame.mouse.set_pos( newMousePos.asTuple() )


    # Update the game state, map and player.
    def update( self ):
        self.updateState()
        self.updateMap()
        self.updateDragObject()


    def draw( self ):
        viewPort = self.viewPort
        gameMap = self.gameMap

        # Draw all the map objects within the view port rectangle.
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
