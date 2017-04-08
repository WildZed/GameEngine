# Monkey-Rabbit Games
# Game Engine

import random, sys, time, math, pygame, copy
from geometry import *
from pygame.locals import *




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


    def setBackGroundColour( self, colour ):
        self.backGroundColour = colour




class Map:
    def __init__( self ):
        self.scenes = {}
        self.sprites = ObjectStore()
        self.players = ObjectStore()
        self.overlays = ObjectStore()
        self.scene = None
        self.images = None


    def setImageStore( self, images ):
        self.images = images


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

