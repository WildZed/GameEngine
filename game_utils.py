# Minitest Games
# Game Utilities

import sys, copy
import pygame


class FontCache( object ):
    def __init__( self ):
        self.fonts = {}


    def addFont( self, fontId, fontName, size ):
        self.fonts[fontId] = font = pygame.font.Font( '%s.ttf' % fontName, size )

        return font


    def __getitem__( self, fontId ):
        try:
            font = self.fonts[fontId]
        except:
            font = None

        return font


    def __setitem__( self, fontId, font ):
        self.fonts[fontId] = font



def debugPrintSurface( surface ):
    width, height = surface.get_size()
    colourKey = surface.get_colorkey()

    for y in range( height ):
        line = ''

        for x in range( width ):
            r, g, b, a = colour = surface.get_at( (x, y) )

            if colourKey is None and a == 0 or colour == colourKey:
                line += ' '
            else:
                line += 'O'

        print( line )



def debugPrintMask( mask ):
    width, height = mask.get_size()

    for y in range( height ):
        line = ''

        for x in range( width ):
            if mask.get_at( (x, y) ):
                line += 'O'
            else:
                line += ' '

        print( line )


def classByName( classname ):
    return getattr( sys.modules[__name__], classname )


def fillSurfaceMinusRectangle( surface, rect, colour ):
    surfaceRect = surface.get_rect()
    fillRect = copy.copy( surfaceRect )
    # print( 'Surface rect:', surfaceRect, 'rect:', rect )

    if rect.top > 0:
        # Top to rect.
        fillRect.height = rect.top # - surfaceRect.top
        fillRect.bottom = rect.top
        # print( 'Fill rect    top:', fillRect )
        surface.fill( colour, fillRect )
        fillRect.bottom = surfaceRect.bottom

    if rect.bottom < surfaceRect.bottom:
        # Rect to bottom.
        fillRect.height = surfaceRect.bottom - rect.bottom
        fillRect.top = rect.bottom
        # print( 'Fill rect bottom:', fillRect )
        surface.fill( colour, fillRect )

    fillRect.top = rect.top
    fillRect.height = rect.height

    if rect.left > 0:
        # Left to rect.
        fillRect.width = rect.left # - surface.left
        fillRect.right = rect.left
        # print( 'Fill rect  left:', fillRect )
        surface.fill( colour, fillRect )
        fillRect.right = surfaceRect.right

    if rect.right < surfaceRect.right:
        # Rect to right.
        fillRect.width = surfaceRect.right - rect.right # - surface.left
        fillRect.left = rect.right
        # print( 'Fill rect right:', fillRect )
        surface.fill( colour, fillRect )


fontCache = FontCache()
