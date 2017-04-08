# Monkey-Rabbit Games
# Candy Seller
# You need money to buy a car so you make a candy-selling shop.

# 16th October 2016: You dream about a monster. When you wake up, it all felt so real... You prepare for another candy-selling day. You spot something green in the shop window and are sure you had seen it before... The letter 'Q' pops into your head.

import random, sys, time, math, pygame
from pygame.locals import *




class Point:
    def __init__( self, posOrX = None, y = None ):
        if y is not None:
            self.x = posOrX
            self.y = y
        elif posOrX:
            self.x = posOrX[0]
            self.y = posOrX[1]
        else:
            self.x = 0
            self.y = 0

    def __add__( self, pointOrNum ):
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
            self.ll = rectOrll.ll
            self.ur = rectOrll.ur
        else:
            self.ll = rectOrll
            self.ur = ur

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
        self.ll += pointOrNum
        self.ur += pointOrNum

        return self

    def __repr__( self ):
        return 'll %s ur %s' % (self.ll, self.ur)




FPS = 30 # frames per second to update the screen
WINWIDTH = 800 # width of the program's window, in pixels
WINHEIGHT = 800 # height in pixels
HALF_WINWIDTH = int(WINWIDTH / 2)
HALF_WINHEIGHT = int(WINHEIGHT / 2)
ORIGIN = Point()

BACKGROUND_COLOUR = (211, 211, 211)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
# PINK = (255, 105, 180)

LEFT = 'left'
RIGHT = 'right'

CAMERASLACK = 90     # how far from the center the man moves before moving the camera
STARTSIZE = 150      # how big the player starts off
MOVERATE = 17        # how fast the player moves
BOUNCERATE = 6       # how fast the player bounces (large is slower)
BOUNCEHEIGHT = 10    # how high the player bounces
SHOPSIZE = 400       # how big the shops are
MONEYSIZE = 80       # how big the money is
ARROWSIZE = 250      # how big the arrows are
BUSHSIZE = 150       # how big the bushes are
MONSTERSIZE = 800    # how big the jumpscare monster is




def main():
    global FPSCLOCK, DISPLAYSURF, BASICFONT, L_MAN_IMG, R_MAN_IMG, F_CHILD_IMG, R_CHILD_IMG, SHOPIMAGES, ARROWIMAGES, MONEY_IMG, BUSH_IMG, INGRE_STORE_IMG, JUMPSCARE_IMG

    print "You own a business that's in London. You live in Poole. Poole is too far away from London to walk, and you do not have a car. You have to make money somehow. I know, you can create a candy shop!"
    #time.sleep(10)

    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    pygame.display.set_icon(pygame.image.load('gameiconc.png'))
    DISPLAYSURF = pygame.display.set_mode((WINWIDTH, WINHEIGHT))
    pygame.display.set_caption('Candy Seller')
    BASICFONT = pygame.font.Font('freesansbold.ttf', 32)

    # load the image files
    L_MAN_IMG = pygame.image.load('man.png')
    R_MAN_IMG = pygame.transform.flip(L_MAN_IMG, True, False)
    L_CHILD_IMG = pygame.image.load('child.png')
    R_CHILD_IMG = pygame.transform.flip(L_CHILD_IMG, True, False)
    BUSH_IMG = pygame.image.load('bush.png')
    INGRE_STORE_IMG = pygame.image.load('ingredients store.png')
    JUMPSCARE_IMG = pygame.image.load('jumpscare monster.png')
    SHOPIMAGES = []
    ARROWIMAGES = []
    
    for i in range(1, 4):
        SHOPIMAGES.append(pygame.image.load('shop%d.png' % i))
        ARROWIMAGES.append(pygame.image.load('arrow%d.png' % i))
        
    MONEY_IMG = pygame.image.load('money.png')

    # load the sounds
    pygame.mixer.music.load('Money Ping.mp3')


    while True:
        runGame()


def runGame():
    # set up variables for the start of a new game
    winMode = False           # if the player has won
    invulnerableMode = False  # if the player is invulnerable
    invulnerableStartTime = 0 # time the player became invulnerable
    gameOverMode = False      # if the player has lost
    gameOverStartTime = 0     # time the player lost
    moneyScore = 0
    stepNumber = 0            # counts how many steps the player has walked

    # create the surfaces to hold game text
    winSurf = BASICFONT.render('You have got enough money! Buy a car! You win!', True, WHITE)
    winRect = winSurf.get_rect()
    winRect.center = (HALF_WINWIDTH, HALF_WINHEIGHT)

    winSurf2 = BASICFONT.render('(But it is all a dream! Press 'r'.)', True, WHITE)
    winRect2 = winSurf2.get_rect()
    winRect2.center = (HALF_WINWIDTH, HALF_WINHEIGHT + 30)

    # Camera is the top left of where the camera view is.
    camera = Point()

    clickPos = None

    thickarrow_strings = (               #sized 24x24
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

    shopObjs = []    # stores all the shop objects
    childObjs = []   # stores all the child objects
    moneyObjs = []   # stores all the money objects
    arrowObjs = []   # stores all the arrow objects
    bushObjs = []    # stores all the bush objects
    jumpObjs = []    # stores all the jumpscare objects
    # stores the player object:
    playerObj = {'surface': pygame.transform.scale(L_MAN_IMG, (STARTSIZE, STARTSIZE)),
                 'facing': LEFT,
                 'size': STARTSIZE,
                 'x': HALF_WINWIDTH,
                 'y': HALF_WINHEIGHT,
                 'bounce':0}

    moveLeft = False
    moveRight = False

    # start off with some shops on the screen
    for i in range(3):
        shopObjs.append( makeNewShop( camera, i ) )
        shopObjs[i]['x'] = i * 320
        shopObjs[i]['y'] = 0
        
    # start off with some bushes on the screen
    bushObjs.append( makeNewBush( camera, -100, 400 ) )
    bushObjs.append( makeNewBush( camera, 1000, 400 ) )

    # start off with some arrows on the screen
    for i in range(3):
        arrowObjs.append( makeNewArrow( camera, i ) )
        arrowObjs[i]['x'] = i * 320 + 80
        arrowObjs[i]['y'] = 550

    # start off with some money on the screen
    for i in range(4):
        mnObj = makeNewCoin( camera )
        moneyObjs.append(mnObj)

    while True: # main game loop

        # adjust camera if beyond the "camera slack"
        playerCentre = Point( playerObj['x'] + int( playerObj['size'] / 2 ),
                              playerObj['y'] + int( playerObj['size'] / 2 ) )
        adjustCamera( camera, playerCentre )

        # draw the grey background
        DISPLAYSURF.fill( BACKGROUND_COLOUR )

        # draw all the shop objects on the screen
        updateAndDrawObjectList( camera, shopObjs )

        # draw all the arrow objects on the screen
        updateAndDrawObjectList( camera, arrowObjs )

        # draw all the money objects on the screen
        updateAndDrawObjectList( camera, moneyObjs )

        # draw all the bush objects on the screen
        updateAndDrawObjectList( camera, bushObjs )

        # draw all the jumpscare objects on the screen
        updateAndDrawObjectList( ORIGIN, jumpObjs )

        # draw the children
        # for cObj in childObjs:
        #     cObj['rect'] = pygame.Rect( ( cObj['x'] - camera.x,
        #                                   cObj['y'] - camera.y - getBounceAmount(cObj['bounce'], cObj['bouncerate'], cObj['bounceheight'] ),
        #                                   cObj['width'],
        #                                   cObj['height'] ) )
        #     DISPLAYSURF.blit( cObj['surface'], cObj['rect'] )

        # draw the player man
        drawPlayer( camera, playerObj, gameOverMode, invulnerableMode )
            
        # draws the money score to show how much money you have
        drawMoneyScore( moneyScore )


        for event in pygame.event.get(): # event handling loop
            if event.type == QUIT:
                terminate()

            elif event.type == KEYDOWN:

                if event.key in (K_UP, K_w):
                    moveDown = False
                    moveUp = True
                elif event.key in (K_DOWN, K_s):
                    moveUp = False
                    moveDown = True
                elif event.key in (K_LEFT, K_a):
                    moveRight = False
                    moveLeft = True
                    if playerObj['facing'] != LEFT: # change player image
                        playerObj['surface'] = pygame.transform.scale(L_MAN_IMG, (playerObj['size'], playerObj['size']))
                    playerObj['facing'] = LEFT
                elif event.key in (K_RIGHT, K_d):
                    moveLeft = False
                    moveRight = True
                    if playerObj['facing'] != RIGHT: # change player image
                        playerObj['surface'] = pygame.transform.scale(R_MAN_IMG, (playerObj['size'], playerObj['size']))
                    playerObj['facing'] = RIGHT
                elif winMode and event.key == K_r:
                    return
                elif event.key is K_q:
                    # releases the jumpscare if you press 'q'
                    playSound( "Jumpscare V2" )
                    jumpObjs.append( makeJumpscareMonster( 0, 0 ) )

            elif event.type == KEYUP:
                # stop moving the player's man
                if event.key in (K_LEFT, K_a):
                    moveLeft = False
                elif event.key in (K_RIGHT, K_d):
                    moveRight = False
                elif event.key in (K_UP, K_w):
                    moveUp = False
                elif event.key in (K_DOWN, K_s):
                    moveDown = False
                elif event.key == K_ESCAPE:
                    terminate()
                elif event.key is K_q:
                    del jumpObjs[0]
            elif event.type == MOUSEBUTTONDOWN:
                # remember position
                clickPos = Point( event.pos )
            elif event.type == MOUSEBUTTONUP:
                # if clickPos nearby event.pos
                if positionNear( Point( event.pos ), clickPos, 10 ):
                    # drawText( 'X', event.pos, RED )

                    if doesCollide( clickPos, camera, objectToRect( arrowObjs[0] ) ):
                        playSound( "Money Ping" )

        # wins the game if you get 100 money
        if moneyScore >= 100:
            winMode = True

        if not gameOverMode:
            # actually move the player
            if moveLeft:
                playerObj['x'] -= MOVERATE
                stepNumber += 1
            if moveRight:
                playerObj['x'] += MOVERATE
                stepNumber += 1
            if playerObj['x'] < 0 :
                playerObj['x'] = 0
            if playerObj['x'] > 900 :
                playerObj['x'] = 900
            if (moveLeft or moveRight) or playerObj['bounce'] != 0:
                playerObj['bounce'] += 1

            # if the man has walked a certain distance then make a new coin
            if stepNumber >= 500:
                mnObj = makeNewCoin( camera.x, camera.y )
                moneyObjs.append(mnObj)
                stepNumber = 0

            if playerObj['bounce'] > BOUNCERATE:
                playerObj['bounce'] = 0 # reset bounce amount

            # check if the player has collided with any money
            for i in range(len(moneyObjs)-1, -1, -1):
                mnObj = moneyObjs[i]
                # drawRect(DISPLAYSURF, RED, mnObj['rect'])
                if 'rect' in mnObj and playerObj['rect'].colliderect(mnObj['rect']):
                    # a player/money collision has occurred
                    del moneyObjs[i]
                    moneyScore += 1
                    pygame.mixer.music.play(loops=0, start=0.0)

        pygame.display.update()
        FPSCLOCK.tick(FPS)


def adjustCamera( camera, playerCentre ):
    if ( camera.x + HALF_WINWIDTH ) - playerCentre.x > CAMERASLACK:
        camera.x = playerCentre.x + CAMERASLACK - HALF_WINWIDTH
    elif playerCentre.x - ( camera.x + HALF_WINWIDTH ) > CAMERASLACK:
        camera.x = playerCentre.x - CAMERASLACK - HALF_WINWIDTH

    if ( camera.y + HALF_WINHEIGHT ) - playerCentre.y > CAMERASLACK:
        camera.y = playerCentre.y + CAMERASLACK - HALF_WINHEIGHT
    elif playerCentre.y - ( camera.y + HALF_WINHEIGHT ) > CAMERASLACK:
        camera.y = playerCentre.y - CAMERASLACK - HALF_WINHEIGHT


def drawText( text, pos, colour ):
    (textSurf, textRect) = createText( text, pos, colour )
    DISPLAYSURF.blit( textSurf, textRect )
    del textSurf


def drawMoneyScore( score ):
    drawText( 'Money: %d' % score, (WINWIDTH - 100, 40), WHITE )


def drawPlayer( camera, playerObj, gameOverMode, invulnerableMode ):
    flashIsOn = round(time.time(), 1) * 10 % 2 == 1
    
    if not gameOverMode and not (invulnerableMode and flashIsOn):
        playerObj['rect'] = pygame.Rect( ( playerObj['x'] - camera.x,
                                           playerObj['y'] - camera.y - getBounceAmount( playerObj['bounce'], BOUNCERATE, BOUNCEHEIGHT ),
                                           playerObj['size'],
                                           playerObj['size'] ) )
        DISPLAYSURF.blit( playerObj['surface'], playerObj['rect'] )


def updateAndDrawObjectList( camera, objList ):
    for gObj in objList:
        gRect = updateObjectRect( gObj, camera )
        DISPLAYSURF.blit( gObj['surface'], gRect )


def updateObjectRect( gObj, camera ):
   rect = pygame.Rect( ( gObj['x'] - camera.x, gObj['y'] - camera.y,
                         gObj['width'], gObj['height'] ) )
   gObj['rect'] = rect
   
   return rect


def drawRect( surface, colour, rect ):
    pygame.draw.rect(surface, colour, rect)


def terminate():
    pygame.quit()
    sys.exit()


def getBounceAmount(currentBounce, bounceRate, bounceHeight):
    # Returns the number of pixels to offset based on the bounce.
    # Larger bounceRate means a slower bounce.
    # Larger bounceHeight means a higher bounce.
    # currentBounce will always be less than bounceRate
    return int(math.sin( (math.pi / float(bounceRate)) * currentBounce ) * bounceHeight)


def getRandomOffCameraPos( camera, objWidth, objHeight):
    # create a Rect of the camera view
    cameraRect = pygame.Rect( camera.x, camera.y, WINWIDTH, WINHEIGHT )
    
    while True:
        x = random.randint( camera.x - WINWIDTH, camera.x + ( 2 * WINWIDTH ) )
        y = random.randint( camera.y - WINHEIGHT, camera.y + ( 2 * WINHEIGHT ) )
        # create a Rect object with the random coordinates and use colliderect()
        # to make sure the right edge isn't in the camera view.
        objRect = pygame.Rect( x, y, objWidth, objHeight )
        
        if not objRect.colliderect( cameraRect ):
            return x, y


def makeNewShop( camera, shopIndex):
    sp = {}
    generalSize = random.randint(5, 25)
    multiplier = random.randint(1, 3)
    shopTypeIndex = shopIndex%3 #random.randint(0, len(SHOPIMAGES) - 1)
    sp['surface'] = pygame.transform.scale(SHOPIMAGES[shopTypeIndex], (SHOPSIZE, SHOPSIZE))
    sp['width']  = (generalSize + random.randint(0, 10)) * multiplier
    sp['height'] = (generalSize + random.randint(0, 10)) * multiplier
    sp['x'], sp['y'] = getRandomOffCameraPos( camera, sp['width'], sp['height'] )
    
    return sp


def makeNewCoin( camera ):
    my = {}
    my['surface'] = pygame.transform.scale(MONEY_IMG, (MONEYSIZE, MONEYSIZE))
    my['width']  = 20
    my['height'] = 20
    # my['x'], my['y'] = getRandomOffCameraPos( camera, my['width'], my['height'])
    my['x'] = random.randint(0, WINWIDTH)
    my['y'] = random.randint(400, 500)
    # bounceAmount = getBounceAmount( my['bounce'], my['bouncerate'], my['bounceheight'] )
    my['rect'] = pygame.Rect( ( my['x'] - camera.x, my['y'] - camera.y,
                                my['width'], my['height'] ) )

    return my


def makeNewArrow( camera, arrowIndex ):
    aw = {}
    generalSize = random.randint(5, 25)
    multiplier = random.randint(1, 3)
    arrowTypeIndex = arrowIndex%3 #random.randint(0, len(ARROWIMAGES) - 1)
    aw['surface'] = pygame.transform.scale(ARROWIMAGES[arrowTypeIndex], (ARROWSIZE, ARROWSIZE))
    # aw['width']  = (generalSize + random.randint(0, 10)) * multiplier
    # aw['height'] = (generalSize + random.randint(0, 10)) * multiplier
    aw['width'] = aw['surface'].get_width()
    aw['height'] = aw['surface'].get_height()
    aw['x'], aw['y'] = getRandomOffCameraPos( camera, aw['width'], aw['height'] )
    
    return aw


def makeNewBush( camera, x, y):
    bh = {}
    generalSize = random.randint(5, 25)
    multiplier = random.randint(1, 3)
    bh['surface'] = pygame.transform.scale(BUSH_IMG, (BUSHSIZE, BUSHSIZE))
    bh['width']  = (generalSize + random.randint(0, 10)) * multiplier
    bh['height'] = (generalSize + random.randint(0, 10)) * multiplier
    bh['x'] = x
    bh['y'] = y
    return bh
    
    
def makeJumpscareMonster( x, y ):
    jm = {}
    generalSize = random.randint(5, 25)
    multiplier = random.randint(1, 3)
    jm['surface'] = pygame.transform.scale(JUMPSCARE_IMG, (MONSTERSIZE, MONSTERSIZE))
    jm['width']  = (generalSize + random.randint(0, 10)) * multiplier
    jm['height'] = (generalSize + random.randint(0, 10)) * multiplier
    jm['x'] = x
    jm['y'] = y
    return jm


def createText( text, pos, colour ):
    # creates text so the game can put text on the screen
    gameOverSurf = BASICFONT.render( text, True, colour )
    gameOverRect = gameOverSurf.get_rect()
    gameOverRect.center = pos
    
    return (gameOverSurf, gameOverRect)


def positionNear( pos, oldPos, distance ):
    xDist = abs( pos.x - oldPos.x )
    yDist = abs( pos.y - oldPos.y )
    isNear = False
    
    if xDist <= distance and yDist <= distance:
        isNear = True

    return isNear


def objectToRect( obj ):
    return Rect( Point( obj['x'], obj['y'] ), Point( obj['x'] + obj['width'], obj['y'] + obj['height'] ) )


def doesCollide( pos, camera, rect ):
    # Adjust rectangle for camera shift.
    adjustedRect = Rect( rect )
    adjustedRect += camera
    # drawText( '%s' % (pos), ( pos.x + 80, pos.y + 40 ), RED )
    # drawText( '%s' % (rect), ( pos.x + 120, pos.y + 80 ), RED )
    # Is position inside the given rectangle adjusted for camera position.
    collides = ( adjustedRect.left <= pos.x and pos.x <= adjustedRect.right ) and ( adjustedRect.bottom <= pos.y and pos.y <= adjustedRect.top )
    
    if collides:
        # Find the colour on the display at the given position.
        colour = pygame.display.get_surface().get_at( pos.asTuple() )
        collides = ( colour != BACKGROUND_COLOUR )

    return collides


def playSound( soundFileName ):
    soundFilePath = 'C:/Users/Zed/Documents/Matt/Programming/' + soundFileName + '.ogg'
    pygame.mixer.init()
    # pygame.mixer.pre_init(44100, -16, 2, 2048)
    pygame.init()
    sounda = pygame.mixer.Sound( soundFilePath )
    sounda.play()
    # pygame.time.delay(8000)
    # ]]




if __name__ == '__main__':
    main()

