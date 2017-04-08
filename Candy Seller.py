# Monkey-Rabbit Games
# Candy Seller
# You need money to buy a car so you make a candy-selling shop.

# 16th October 2016: You dream about a monster. When you wake up, it all felt so real... You prepare for another candy-selling day. You spot something green in the shop window and are sure you had seen it before... The letter 'Q' pops into your head.

import random, sys, time, math, pygame, copy
from pygame.locals import *




class Point:
    def __init__( self, posOrX = None, y = None ):
        if y is not None:
            self.x = posOrX
            self.y = y
        elif posOrX.__class__.__name__ is 'Point':
            self.x = posOrX.x
            self.y = posOrX.y
        elif posOrX:
            self.x = posOrX[0]
            self.y = posOrX[1]
        else:
            self.x = 0
            self.y = 0


    def __add__( self, pointOrNum ):
        point = Point( self )

        if isinstance( pointOrNum, Point ):
            point.x += pointOrNum.x
            point.y += pointOrNum.y
        else:
            point.x += pointOrNum
            point.y += pointOrNum

        return point


    def __iadd__( self, pointOrNum ):
        if isinstance( pointOrNum, Point ):
            self.x += pointOrNum.x
            self.y += pointOrNum.y
        else:
            self.x += pointOrNum
            self.y += pointOrNum

        return self


    def __repr__( self ):
        return '(%d, %d)' % (self.x, self.y)


    def asTuple( self ):
        return ( self.x, self.y )




class Rect:
    def __init__( self, rectOrll = None, ur = None ):
        if rectOrll is None:
            self.ll = Point( 0, 0 )
            self.ur = Point( 0, 0 )
        elif ur is None:
            self.ll = copy.copy( rectOrll.ll )
            self.ur = copy.copy( rectOrll.ur )
        else:
            self.ll = copy.copy( rectOrll )
            self.ur = copy.copy( ur )


    def boundPoint( self, pos ):
        pos = Point( pos )

        if pos.x < self.ll.x :
            pos.x = self.ll.x
        elif pos.x > self.ur.x:
            pos.x = self.ur.x

        if pos.y < self.ll.y:
            pos.y = self.ll.y
        elif pos.y > self.ur.y:
            pos.y = self.ur.y

        return pos


    def __getattr__( self, key ):
        val = 0

        if key == 'top':
            val = self.ur.y
        elif key == 'bottom':
            val = self.ll.y
        elif key == 'left':
            val = self.ll.x
        elif key == 'right':
            val = self.ur.x
        else:
            raise AttributeError( "Rect attribute '%s' not recognised." % key )

        return val


    def __add__( self, pointOrNum ):
        rect = Rect( self.ll, self.ur )
        rect.ll += pointOrNum
        rect.ur += pointOrNum

        return self


    def __iadd__( self, pointOrNum ):
        self.ll += pointOrNum
        self.ur += pointOrNum

        return self


    def __repr__( self ):
        return 'll %s ur %s' % (self.ll, self.ur)




# Constants.

FPS = 30 # frames per second to update the screen
WINWIDTH = 800 # width of the program's window, in pixels
WINHEIGHT = 800 # height in pixels
ORIGIN = Point()

BACKGROUND_COLOUR = (211, 211, 211)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
# PINK = (255, 105, 180)

LEFT = 'left'
RIGHT = 'right'

CAMERASLACK = 90     # how far from the center the man moves before moving the camera
MOVERATE = 17        # how fast the player moves
BOUNCERATE = 6       # how fast the player bounces (large is slower)
BOUNCEHEIGHT = 10    # how high the player bounces
SHOPSIZE = 400       # how big the shops are
MONEYSIZE = 80       # how big the money is
ARROWSIZE = 250      # how big the arrows are
BUSHSIZE = 150       # how big the bushes are
MONSTERSIZE = 800    # how big the jumpscare monster is



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
    def __init__( self, image, size, pos ):
        # generalSize = random.randint( 5, 25 )
        # multiplier = random.randint( 1, 3 )
        # self.width  = ( generalSize + random.randint( 0, 10 ) ) * multiplier
        # self.height = ( generalSize + random.randint( 0, 10 ) ) * multiplier
        self.visible = True
        self.image = image
        self.size = size
        self.pos = pos
        # The position rectangle.
        self.rect = None
        self.surface = None
        self.updateSurface()
        self.updateRect()
        self.updateCollisionRect()


    def updateSurface( self ):
        self.surface = pygame.transform.scale( self.image, ( self.size, self.size ) )


    def updateRect( self, offset = ORIGIN, jitter = ORIGIN ):
        # self.rect = self.surface.get_rect()
        self.rect = self.getOffSetRect( offset, jitter )


    def getOffSetPos( self, offset = ORIGIN, jitter = ORIGIN ):
        return Point( self.pos.x - offset.x + jitter.x, self.pos.y - offset.y + jitter.y )


    def getOffSetRect( self, offset = ORIGIN, jitter = ORIGIN ):
        offSetPos = self.getOffSetPos( offset, jitter )

        return pygame.Rect( offSetPos.x, offSetPos.y, self.width, self.height )


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


    def asRect( self ):
        return Rect( Point( self.pos.x, self.pos.y ), Point( self.pos.x + self.width, self.pos.y + self.height ) )


    def swapImage( self, image ):
        self.image = image
        self.updateSurface()


    def update( self, offset = ORIGIN, jitter = ORIGIN ):
        self.updateRect( offset, jitter )
        self.updateCollisionRect()


    def draw( self, surface ):
        if self.visible:
            surface.blit( self.surface, self.rect )


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

            val = self.__dict__[key]
        except:
            raise AttributeError( "Unrecognised Object attribute '%s' in __getattr__!" % key )

        return val


    def __setattr__( self, key, val ):
        if key == 'x':
            self.__dict__['pos'].x = val
        elif key == 'y':
            self.__dict__['pos'].y = val
        else:
            self.__dict__[key] = val




class Shop( Object ):
    def __init__( self, image, size, pos ):
        Object.__init__( self, image, size, pos )




class Bush( Object ):
    def __init__( self, image, size, pos ):
        Object.__init__( self, image, size, pos )




class Arrow( Object ):
    def __init__( self, image, size, pos ):
        Object.__init__( self, image, size, pos )




class Monster( Object ):
    def __init__( self, image, size, pos ):
        Object.__init__( self, image, size, pos )




class Coin( Object ):
    def __init__( self, image, size ):
        pos = Point( random.randint( 0, WINWIDTH ), random.randint( 400, 500 ) )
        # bounceAmount = getBounceAmount( my['bounce'], my['bouncerate'], my['bounceheight'] )

        Object.__init__( self, image, size, pos )




# Creates text in world coordinates.
class Text( Object ):
    def __init__( self, font, text, pos, colour ):
        self.font = font
        self.text = text
        self.colour = colour

        Object.__init__( self, None, 0, pos )


    def updateSurface( self ):
        self.surface = self.font.render( self.text, True, self.colour )


    def updateRect( self, offset = ORIGIN, jitter = ORIGIN ):
        self.rect = rect = self.surface.get_rect()
        self.rect = rect.move( -offset.x + jitter.x, -offset.y + jitter.y )




# Creates static text in viewport coordinates.
class StaticText( Text ):
    def __init__( self, font, text, pos, colour ):
        Text.__init__( self, font, text, pos, colour )


    def update( self, offset = ORIGIN, jitter = ORIGIN ):
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




class Movement:
    def __init__( self, moveRate = MOVERATE ):
        self.moveBounds = None
        self.moveRate = moveRate
        self.bounceRate = 0
        self.directions = {
            'horizontal'    : None,
            'vertical'      : None
        }
        self.directionTypes = {
            'left'          : ( 'left', ),
            'right'         : ( 'right', ),
            'up'            : ( 'up', ),
            'down'          : ( 'down', ),
            'horizontal'    : ( 'left', 'right' ),
            'vertical'      : ( 'up', 'down' )
        }
        self.bounce = 0
        self.dirToKeysMap = {
            'left'  : ( K_LEFT, K_a ),
            'right' : ( K_RIGHT, K_d ),
            'up'    : ( K_UP, K_w, ),
            'down'  : ( K_DOWN, K_s )
        }
        self.axisMap = {
            'left'  : 'horizontal',
            'right' : 'horizontal',
            'up'    : 'vertical',
            'down'  : 'vertical'
        }
        self.keyToDirMap = {}

        for direction in self.dirToKeysMap.keys():
            keys = self.dirToKeysMap[direction]

            for key in keys:
                self.keyToDirMap[key] = direction

        self.dirToKeysMap['horizontal'] = self.dirToKeysMap['left'] + self.dirToKeysMap['right']
        self.dirToKeysMap['vertical'] = self.dirToKeysMap['up'] + self.dirToKeysMap['down']
        self.dirToKeysMap['all'] = self.dirToKeysMap['horizontal'] + self.dirToKeysMap['vertical']


    def setMoveStyle( self, moveRate, bounceRate ):
        self.moveRate = moveRate
        self.bounceRate = bounceRate


    def setMoveBounds( self, bounds ):
        self.moveBounds = bounds


    def setMovement( self, key ):
        if key in self.dirToKeysMap['all']:
            direction = self.keyToDirMap[key]
            axis = self.axisMap[direction]
            self.directions[axis] = direction


    def stopMovement( self, key = None ):
        if not key:
            self.directions = {}
        elif key in self.dirToKeysMap['all']:
            direction = self.keyToDirMap[key]
            axis = self.axisMap[direction]

            if self.directions[axis] == direction:
                self.directions[axis] = None


    def moving( self, direction = 'any' ):
        horizontal = self.directions['horizontal']
        vertical = self.directions['vertical']

        if not horizontal and not vertical:
            return False
        elif direction == 'any':
            return True

        moving = False

        if horizontal in self.directionTypes[direction] \
           or vertical in self.directionTypes[direction]:
            moving = True

        return moving



class Player( Object, Movement ):
    def __init__( self, imageL, imageR, size, pos ):
        self.imageL = imageL
        self.imageR = imageR
        self.left = True
        self.steps = 0
        Object.__init__( self, imageL, size, pos )
        Movement.__init__( self )


    # Override updateCollisionRect() from Object.
    def updateCollisionRect( self ):
        # Use a smaller collision rectangle that represents the players feet.
        self.colRect = colRect = self.rect.copy()
        # Collision rect from feet to a quarter height.
        colRect.top = colRect.top + ( ( colRect.height * 3 ) / 4 )
        # Collision rect thinner than the image width by a quarter on each side.
        colRect.left = colRect.left + ( colRect.width / 4 )
        colRect.width = colRect.width / 2


    def getBounceAmount( self ):
        # Returns the number of pixels to offset based on the bounce.
        # Larger bounceRate means a slower bounce.
        # Larger bounceHeight means a higher bounce.
        # currentBounce will always be less than bounceRate.
        bounceRate = self.bounceRate
        bounceHeight = self.bounceRate

        return int( math.sin( ( math.pi / float( bounceRate ) ) * self.bounce ) * bounceHeight )


    def setMovement( self, key ):
        Movement.setMovement( self, key )

        # Flip the player image if changed direction.
        if self.moving( 'left' ) and self.image is not self.imageL:
            self.left = True
            self.swapImage( self.imageL )
        elif self.moving( 'right' ) and self.image is not self.imageR:
            # Flip the player image.
            self.left = False
            self.swapImage( self.imageR )


    def move( self, viewPort = None ):
        oldPos = Point( self.pos )

        if self.moving():
            self.steps += 1

            if self.moving( 'left' ):
                self.x -= self.moveRate
            elif self.moving( 'right' ):
                self.x += self.moveRate
            if self.moving( 'up' ):
                self.y -= self.moveRate
            elif self.moving( 'down' ):
                self.y += self.moveRate

        # Restrict the player's movement to the specified boundary.
        if self.moveBounds:
            self.pos = self.moveBounds.boundPoint( self.pos )
        elif viewPort:
            offSetPos = self.getOffSetPos( viewPort.camera )

            if self.left:
                xoff = 0
            else:
                xoff = self.width

            footViewPortPos = offSetPos + Point( xoff, self.height )

            print "footViewPortPos %s" % footViewPortPos

            if viewPort.collisionAtPoint( footViewPortPos ):
                self.pos = oldPos

        if self.moving( 'horizontal' ) or self.bounce != 0:
            self.bounce += 1

        if self.bounce > self.bounceRate:
            # Reset bounce amount.
            self.bounce = 0


    def update( self, camera, gameOverMode, invulnerableMode ):
        flashIsOn = round( time.time(), 1 ) * 10 % 2 == 1

        if not gameOverMode and not ( invulnerableMode and flashIsOn ):
            jitter = Point( 0, - self.getBounceAmount() )
            Object.update( self, camera, jitter )
            self.visible = True
        else:
            self.visible = False




class ImageStore:
    def __init__( self ):
        pass


    def load( self, name, modes = None ):
        nameNoSpace = name.replace( ' ', '_' )

        if modes:
            if modes == 'LR':
                imageFile = '%s.png' % name
                image = pygame.image.load( imageFile )
                self.__dict__[nameNoSpace + 'L'] = image
                self.__dict__[nameNoSpace + 'R'] = pygame.transform.flip( image, True, False )
            else:
                # Assume sequence for now.
                self.__dict__[nameNoSpace + 's'] = images = {}

                for postFix in modes:
                    imageFile = '%s%s.png' % ( name, postFix )
                    image = pygame.image.load( imageFile )
                    images[postFix] = image

        else:
            imageFile = '%s.png' % name
            image = pygame.image.load( imageFile )
            self.__dict__[nameNoSpace] = image




class ViewPort:
    def __init__( self, width, height ):
        self.width = width
        self.height = height
        self.halfWidth = int( width / 2 )
        self.halfHeight = int( height / 2 )
        self.backGroundColour = BACKGROUND_COLOUR
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
        collides = ( not obj or obj.collidesWithPoint( pos, True ) )

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
        pygame.init()
        sounda = pygame.mixer.Sound( soundFilePath )
        sounda.play()
        # pygame.time.delay(8000)
        # ]]




class ObjectStore:
    def __init__( self ):
        self.objectLists = {}


    def addObject( self, obj ):
        objType = obj.__class__.__name__
        objLists = self.objectLists

        if objLists.has_key( objType ):
            objList = objLists[objType]
        else:
            objLists[objType] = objList = []

        objList.append(obj)


    def objectsOfType( self, objType ):
        objLists = self.objectLists

        if objLists.has_key( objType ):
            return objLists[objType]
        else:
            return []


    def deleteAllObjectsOfType( self, objType ):
        objLists = self.objectLists

        if objLists.has_key( objType ):
            del objLists[objType]


    def update( self, offset, objTypes = None ):
        objLists = self.objectLists

        if not objTypes:
            # Non-deterministic order.
            objTypes = objLists.keys()

        for objType in objTypes:
            if not objLists.has_key( objType ):
                continue
                # raise  AttributeError( "No objects of type '%s' in map!" % objType )

            objList = objLists[objType]

            for obj in objList:
                obj.update( offset )


    def draw( self, viewPort, objTypes = None ):
        objLists = self.objectLists

        if not objTypes:
            # Non-deterministic order.
            objTypes = objLists.keys()

        for objType in objTypes:
            if not objLists.has_key( objType ):
                continue
                # raise  AttributeError( "No objects of type '%s' in map!" % objType )

            objList = objLists[objType]

            for obj in objList:
                obj.draw( viewPort.displaySurface )



class Scene( ObjectStore ):
    def __init__( self, name, backGroundColour ):
        self.name = name
        self.backGroundColour = backGroundColour
        ObjectStore.__init__( self )




class Map:
    def __init__( self ):
        self.scenes = {}
        self.sprites = ObjectStore()
        self.players = ObjectStore()
        self.overlays = ObjectStore()
        self.scene = None


    def createScene( self, name, backGroundColour ):
        self.scenes[name] = scene = Scene( name, backGroundColour )

        if not self.scene:
            self.scene = scene


    def ensureScene( self ):
        if not self.scene:
            self.scene = Scene( 'default', BACKGROUND_COLOUR )


    def changeScene( self, name ):
        self.scene = self.scenes[name]


    def addObject( self, obj ):
        self.ensureScene()
        self.scene.addObject( obj )


    def objectsOfType( self, objType ):
        self.ensureScene()

        return self.scene.objectsOfType( objType )


    def deleteAllObjectsOfType( self, objType ):
        self.ensureScene()
        self.scene.deleteAllObjectsOfType( objType )
        self.sprites.deleteAllObjectsOfType( objType )
        self.players.deleteAllObjectsOfType( objType )
        self.overlays.deleteAllObjectsOfType( objType )


    def addSprite( self, obj ):
        self.sprites.addObject( obj )


    def addPlayer( self, obj ):
        self.players.addObject( obj )


    def addOverlay( self, obj ):
        self.overlays.addObject( obj )


    def update( self, offset, objTypes = None ):
        self.ensureScene()
        self.scene.update( offset, objTypes )
        self.sprites.update( offset, objTypes )
        # self.players.update( offset, objTypes )
        self.overlays.update( offset, objTypes )


    def draw( self, viewPort, objTypes = None ):
        self.ensureScene()
        self.scene.draw( viewPort, objTypes )
        self.sprites.draw( viewPort, objTypes )
        self.players.draw( viewPort, objTypes )
        self.overlays.draw( viewPort, objTypes )


    def __getattr__( self, key ):
        if key == 'player':
            return self.__dict__['players'].objectLists['Player'][0]
        elif key == 'score':
            return self.__dict__['overlays'].objectLists['Score'][0]
        elif key == 'backGroundColour':
            self.ensureScene()

            return self.__dict__['scene'].backGroundColour

        if not self.__dict__.has_key( key ) :
            raise AttributeError( "Unrecognised Map attribute '%s' in __getattr__!" % key )

        val = self.__dict__[key]

        return val




class Game:
    def __init__( self, viewPort ):
        # Set up the game state variables.
        self.viewPort = viewPort
        self.drawOrder = ( 'Shop', 'Arrow', 'Bush', 'Coin', 'Player', 'Score', 'Monster' )
        self.cameraUpdates = ( 'Shop', 'Arrow', 'Bush', 'Coin' )
        self.setCursor()

        pygame.display.set_caption( 'Candy Seller' )
        pygame.display.set_icon( pygame.image.load( 'gameiconc.png' ) )

        # Load the sounds.
        pygame.mixer.music.load( 'Money Ping.mp3' )

        self.init()


    def init( self ):
        self.winMode = False           # If the player has won.
        self.invulnerableMode = False  # If the player is invulnerable.
        self.invulnerableStartTime = 0 # Time the player became invulnerable.
        self.gameOverMode = False      # If the player has lost.
        self.gameOverStartTime = 0     # Time the player lost.
        self.moneyScore = 0
        self.clickPos = None
        self.fpsClock = pygame.time.Clock()
        self.running = True
        self.gameMap = self.createMap()


    def reset( self ):
        self.init()

    def terminate( self ):
        pygame.quit()
        sys.exit()


    def loadImages( self ):
        images = ImageStore()

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
        gameMap = Map()

        gameMap.createScene( 'shops', BACKGROUND_COLOUR )
        gameMap.createScene( 'insideShop1', BACKGROUND_COLOUR )

        # Load the image files.
        gameMap.images = images = self.loadImages()

        # How big the player starts off.
        manSize = 150
        playerStartPos = Point( viewPort.halfWidth, viewPort.halfHeight )
        playerBounds = Rect( Point( 0, 300 ), Point( 900, 440 ) )

        # Stores the player object.
        player = Player( images.manL, images.manR, manSize, playerStartPos )
        player.setMoveStyle( MOVERATE, BOUNCERATE )
        # player.setMoveBounds( playerBounds )
        gameMap.addPlayer( player )

        # Storing game objects.

        # Start off with some shops on the screen.
        for shopNum in range( 1, 4 ):
            gameMap.addObject( Shop( images.shops[shopNum], SHOPSIZE, Point( ( shopNum - 1 ) * 320, 0 ) ) )

        # Start off with some bushes on the screen.
        gameMap.addObject( Bush( images.bush, BUSHSIZE, Point( -100, 400 ) ) )
        gameMap.addObject( Bush( images.bush, BUSHSIZE, Point( 1000, 400 ) ) )

        # Start off with some arrows on the screen.
        for arrowNum in range( 1, 4 ):
            gameMap.addObject( Arrow( images.arrows[arrowNum], ARROWSIZE, Point( ( arrowNum - 1 ) * 320 + 80, 550 ) ) )

        # Start off with some money on the screen.
        for i in range( 4 ):
            gameMap.addObject( Coin( images.money, MONEYSIZE ) )

        gameMap.addOverlay( Score( viewPort.basicFont, Point( viewPort.width - 100, 40 ), self.moneyScore ) )

        return gameMap


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


    def addDebugText( self, text, pos, colour ):
        self.gameMap.addObject( DebugText( self.viewPort.basicFont, text, pos, colour ) )
        # DebugText( '%s' % (pos), ( pos.x + 80, pos.y + 40 ), RED )
        # DebugText( '%s' % (rect), ( pos.x + 120, pos.y + 80 ), RED )


    def processEvents( self ):
        # Event handling loop.
        for event in pygame.event.get():
            self.processEvent( event )


    def processEvent( self, event ):
        viewPort = self.viewPort
        gameMap = self.gameMap
        player = gameMap.player

        if event.type == QUIT:
            self.terminate()
            self.running = False

        elif event.type == KEYDOWN:
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

            if event.key == K_ESCAPE:
                self.terminate()
            elif event.key is K_q:
                gameMap.deleteAllObjectsOfType( 'Monster' )
            elif event.key is K_i:
                gameMap.changeScene( 'insideShop1' )
            elif event.key is K_o:
                gameMap.changeScene( 'shops' )

        elif event.type == MOUSEBUTTONDOWN:
            # Remember position.
            self.clickPos = Point( event.pos )

        elif event.type == MOUSEBUTTONUP:
            # If clickPos nearby event.pos.
            if viewPort.positionNear( Point( event.pos ), self.clickPos, 10 ):
                pos = self.clickPos
                arrow = gameMap.objectsOfType( 'Arrow' )[0]

                if viewPort.collisionAtPoint( pos, arrow ):
                    viewPort.playSound( "Money Ping" )


    def updateState( self ):
        viewPort = self.viewPort
        gameMap = self.gameMap
        player = gameMap.player

        # Wins the game if you get 100 money.
        if self.moneyScore >= 100:
            self.winMode = True

        if not self.gameOverMode:
            # Move the player according to the movement instructions.
            player.move( viewPort )

            # If the man has walked a certain distance then make a new coin.
            if player.steps >= 400:
                gameMap.addObject( Coin( gameMap.images.money, MONEYSIZE ) )
                player.steps = 0

            # Check if the player has collided with any money.
            money = gameMap.objectsOfType( 'Coin' )

            for ii in range( len( money ) - 1, -1, -1 ):
                coin = money[ii]
                # viewPort.drawRect( coin.rect, RED )

                if player.collidesWith( coin ):
                    # A player/money collision has occurred.
                    del money[ii]
                    self.moneyScore += 1
                    pygame.mixer.music.play( loops=0, start=0.0 )

        # Update the money score.
        gameMap.score.updateScore( self.moneyScore )

        # Adjust camera if beyond the "camera slack".
        playerCentre = Point( player.x + int( player.size / 2 ), player.y + int( player.size / 2 ) )
        viewPort.adjustCamera( playerCentre )


    # Update the positions of all the map objects according to the camera and new positions.
    def updateMap( self ):
        viewPort = self.viewPort
        gameMap = self.gameMap
        player = gameMap.player

        # Update the objects offset by the camera.
        gameMap.update( viewPort.camera, self.cameraUpdates )

        # Update the player man.
        player.update( viewPort.camera, self.gameOverMode, self.invulnerableMode )


    # Update the game state, map and player.
    def update( self ):
        self.updateState()
        self.updateMap()
        self.fpsClock.tick( FPS )


    def draw( self ):
        viewPort = self.viewPort
        gameMap = self.gameMap

        # Draw the background.
        viewPort.drawBackGround( gameMap.backGroundColour )

        # Draw all the map objects.
        gameMap.draw( viewPort, self.drawOrder )

        viewPort.draw()


    def run( self ):
        print "You own a business that's in London. You live in Poole."
        print "Poole is too far away from London to walk, and you do not have a car."
        print "You have to make money somehow. I know, you can create a candy shop!"
        #time.sleep(10)

        viewPort = self.viewPort
        gameMap = self.gameMap

        # Main game loop.
        while self.running:
            self.draw()
            self.processEvents()
            self.update()




def main():
    viewPort = ViewPort( WINWIDTH, WINHEIGHT )
    game = Game( viewPort )

    while True:
        game.run()
        # Re-initialised the game state.
        game.reset()


if __name__ == '__main__':
    main()

