# Monkey-Rabbit Games
# Game Utilities

import pygame


class FontCache:
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




fontCache = FontCache()