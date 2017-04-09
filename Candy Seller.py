# Monkey-Rabbit Games
# Candy Seller
# You need money to buy a car so you make a candy-selling shop.

# 16th October 2016: You dream about a monster. When you wake up, it all felt so real... You prepare for another candy-selling day. You spot something green in the shop window and are sure you had seen it before... The letter 'Q' pops into your head.

import random, sys, time, math, pygame
from pygame.locals import *
from geometry import Point
import viewport, game, game_map, game_dynamics, geometry
from game_objects import *




# Constants.

WINWIDTH = 800 # width of the program's window, in pixels
WINHEIGHT = 800 # height in pixels

BACKGROUND_COLOUR = (211, 211, 211)
SHOP_FLOOR_COLOUR = (240, 180, 211)
RED = (255, 0, 0)
# PINK = (255, 105, 180)

LEFT = 'left'
RIGHT = 'right'

MOVERATE = 17        # how fast the player moves
BOUNCERATE = 6       # how fast the player bounces (large is slower)
BOUNCEHEIGHT = 10    # how high the player bounces
SHOPSIZE = 400       # how big the shops are
MONEYSIZE = 80       # how big the money is
ARROWSIZE = 250      # how big the arrows are
BUSHSIZE = 150       # how big the bushes are
MONSTERSIZE = 800    # how big the jumpscare monster is




class CandySeller( game.Game ):
    def __init__( self, viewPort ):
        self.images = self.loadImages()

        # Set up generic game one time set up.
        game.Game.__init__( self, 'Candy Seller', 'gameiconc.png', viewPort )

        # Game one time setup.
        self.setDrawOrder( 'Shop', 'Arrow', 'Bush', 'Coin', 'Player', 'Score', 'Monster' )
        self.setCameraUpdates( 'Shop', 'Arrow', 'Bush', 'Coin' )
        self.setCursor()
        viewPort.loadMusic( 'Money Ping.mp3' )


    # Per game initialisation.
    def init( self ):
        game.Game.init( self )

        self.winMode = False           # If the player has won.
        self.invulnerableMode = False  # If the player is invulnerable.
        self.invulnerableStartTime = 0 # Time the player became invulnerable.
        self.gameOverMode = False      # If the player has lost.
        self.gameOverStartTime = 0     # Time the player lost.
        self.moneyScore = 0
        self.gameMap = self.createMap()


    def loadImages( self ):
        images = game_map.ImageStore()

        images.load( 'man', 'LR' )
        images.load( 'bush' )
        images.load( 'ingredients store' )
        images.load( 'jumpscare monster' )
        images.load( 'money' )
        images.load( 'shop', range( 1, 4 ) )
        images.load( 'arrow', range( 1, 4 ) )

        return images


    def createMap( self ):
        viewPort = self.viewPort
        gameMap = game_map.Map()
        images = self.images

        gameMap.setImageStore( images )

        gameMap.createScene( 'shops', BACKGROUND_COLOUR )

        # Create scene objects.

        # Start off with some shops on the screen.
        self.createShops( gameMap )

        # Start off with some bushes on the screen.
        gameMap.addObject( Bush( images.bush, BUSHSIZE, Point( -100, 400 ) ) )
        gameMap.addObject( Bush( images.bush, BUSHSIZE, Point( 1000, 400 ) ) )

        # Start off with some arrows on the screen.
        self.createArrows( gameMap )

        # Start off with some money on the screen.
        self.createCoins( gameMap, 4 )

        gameMap.createScene( 'insideShop1', SHOP_FLOOR_COLOUR )
        gameMap.changeScene( 'insideShop1' )
        self.createCoins( gameMap, 4 )

        gameMap.changeScene( 'shops' )

        gameMap.addOverlay( Score( viewPort.basicFont, Point( viewPort.width - 100, 40 ), self.moneyScore ) )
        gameMap.addPlayer( self.createPlayer() )

        return gameMap


    def createPlayer( self ):
        viewPort = self.viewPort
        images = self.images
        # How big the player starts off.
        manSize = 150
        playerStartPos = Point( viewPort.halfWidth, viewPort.halfHeight )

        # Sets up the movement style of the player.
        playerBounds = geometry.Rect( Point( 0, 300 ), Point( 900, 440 ) )
        moveStyle = game_dynamics.BoundedKeyMovementStyle( playerBounds )
        # moveStyle = game_dynamics.CollisionKeyMovementStyle( viewPort )
        moveStyle.setMoveRates( MOVERATE, BOUNCERATE )

        return Player( images.manL, images.manR, manSize, playerStartPos, moveStyle )


    def createShops( self, gameMap ):
        for shopNum in range( 1, 4 ):
            gameMap.addObject( Shop( self.images.shops[shopNum], SHOPSIZE, Point( ( shopNum - 1 ) * 320, 0 ) ) )


    def createArrows( self, gameMap ):
        for arrowNum in range( 1, 4 ):
            gameMap.addObject( Arrow( self.images.arrows[arrowNum], ARROWSIZE, Point( ( arrowNum - 1 ) * 320 + 80, 550 ) ) )


    def createCoins( self, gameMap, num ):
        for ii in range( num ):
            pos = Point( random.randint( 0, WINWIDTH ), random.randint( 400, 500 ) )
            gameMap.addObject( Coin( self.images.money, pos, MONEYSIZE ) )


    # Could move cursor description into a file and read from there.
    def setCursor( self ):
        thickarrow_strings = (               # Sized 24x24.
            "XXXXXXXXXXX             ",
            " X.......X              ",
            "  X.....X               ",
            "   X...X                ",
            "  X.....X               ",
            " X.......X              ",
            "X.........X             ",
            "X.........X             ",
            "X.........X             ",
            " X.......X              ",
            "  X.....X               ",
            "   X...X                ",
            "  X.....X               ",
            " X.......X              ",
            "XXXXXXXXXXX             ",
            "                        ",
            "                        ",
            "                        ",
            "                        ",
            "                        ",
            "                        ",
            "                        ",
            "                        ",
            "                        ")
        datatuple, masktuple = pygame.cursors.compile( thickarrow_strings,
                                      black='X', white='.', xor='o' )
        pygame.mouse.set_cursor( (24,24), (0,0), datatuple, masktuple )


    def processEvent( self, event ):
        game.Game.processEvent( self, event )

        viewPort = self.viewPort
        gameMap = self.gameMap
        player = gameMap.player

        if event.type == KEYDOWN:
            # Check if the key moves the player in a given direction.
            player.setMovement( event.key )

            if event.key == K_r and self.winMode:
                self.running = False
            elif event.key is K_q:
                # Releases the jumpscare if you press 'q'.
                viewPort.playSound( "Jumpscare V2" )
                gameMap.addSprite( Monster( gameMap.images.jumpscare_monster, MONSTERSIZE, Point( 0, 0 ) ) )
        elif event.type == KEYUP:
            # Check if the key stops the player in a given direction.
            player.stopMovement( event.key )

            if event.key is K_q:
                gameMap.deleteAllObjectsOfType( 'Monster' )
            elif event.key is K_i:
                gameMap.changeScene( 'insideShop1' )
            elif event.key is K_o:
                gameMap.changeScene( 'shops' )
        elif event.type == MOUSEBUTTONUP:
            if None is self.dragPos:
                arrow = gameMap.objectsOfType( 'Arrow' )[0]

                if viewPort.collisionAtPoint( self.clickPos, arrow ):
                    viewPort.playSound( "Money Ping" )


    def updateState( self ):
        game.Game.updateState( self )

        viewPort = self.viewPort
        gameMap = self.gameMap
        player = gameMap.player

        # Wins the game if you get 100 money.
        if self.moneyScore >= 100:
            self.winMode = True

        if not self.gameOverMode:
            # Move the player according to the movement instructions.
            player.move()

            # If the man has walked a certain distance then make a new coin.
            if player.steps >= 400:
                self.createCoins( gameMap, 1 )
                player.steps = 0

            # Check if the player has collided with any money.
            money = gameMap.objectsOfType( 'Coin' )

            for ii in range( len( money ) - 1, -1, -1 ):
                coin = money[ii]

                if player.collidesWith( coin ):
                    # A player/money collision has occurred.
                    del money[ii]
                    self.moneyScore += 1
                    viewPort.playMusic()

        # Update the money score.
        gameMap.score.updateScore( self.moneyScore )

        # Adjust camera if beyond the "camera slack".
        playerCentre = Point( player.x + int( player.size / 2 ), player.y + int( player.size / 2 ) )
        viewPort.adjustCamera( playerCentre )


    # Update the positions of all the map objects according to the camera and new positions.
    def updateMap( self ):
        # Update the generic map stuff.
        game.Game.updateMap( self )

        viewPort = self.viewPort
        gameMap = self.gameMap
        player = gameMap.player

        # Update the player man.
        player.update( viewPort.camera, self.gameOverMode, self.invulnerableMode )


    def run( self ):
        print( "You own a business that's in London. You live in Poole." )
        print( "Poole is too far away from London to walk, and you do not have a car." )
        print( "You have to make money somehow. I know, you can create a candy shop!" )
        #time.sleep(10)

        game.Game.run( self )




def main():
    viewPort = viewport.ViewPort( WINWIDTH, WINHEIGHT )
    game = CandySeller( viewPort )

    while True:
        game.run()
        # Re-initialised the game state.
        game.reset()


if __name__ == '__main__':
    main()

