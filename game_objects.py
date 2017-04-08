# Monkey-Rabbit Games
# Game Objects

import random, sys, time, math, pygame, copy
from geometry import *
from pygame.locals import *


# Constants.

WHITE = (255, 255, 255)




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
            raise
            # raise AttributeError( "Unrecognised Object attribute '%s' in __getattr__!" % key )

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
    def __init__( self, image, pos, size ):
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




class Player( Object ):
    def __init__( self, imageL, imageR, size, pos, movementStyle ):
        self.imageL = imageL
        self.imageR = imageR
        self.left = True
        self.steps = 0
        self.movementStyle = movementStyle
        movementStyle.setMoveObject( self )

        Object.__init__( self, imageL, size, pos )


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
        movementStyle = self.movementStyle
        bounceRate = movementStyle.bounceRate
        bounceHeight = bounceRate

        return int( math.sin( ( math.pi / float( bounceRate ) ) * movementStyle.bounce ) * bounceHeight )


    def setMovement( self, key ):
        movementStyle = self.movementStyle
        movementStyle.setMovement( key )

        # Flip the player image if changed direction.
        if movementStyle.moving( 'left' ) and self.image is not self.imageL:
            self.left = True
            self.swapImage( self.imageL )
        elif movementStyle.moving( 'right' ) and self.image is not self.imageR:
            # Flip the player image.
            self.left = False
            self.swapImage( self.imageR )


    def stopMovement( self, key ):
        self.movementStyle.stopMovement( key )


    def move( self ):
        newPos = self.movementStyle.move( self.pos )

        if newPos != self.pos:
            self.pos = newPos
            self.steps += 1


    def update( self, camera, gameOverMode, invulnerableMode ):
        flashIsOn = round( time.time(), 1 ) * 10 % 2 == 1

        if not gameOverMode and not ( invulnerableMode and flashIsOn ):
            jitter = Point( 0, - self.getBounceAmount() )
            Object.update( self, camera, jitter )
            self.visible = True
        else:
            self.visible = False

