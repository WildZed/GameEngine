# Monkey-Rabbit Games
# Game Engine

import pygame, copy
from pygame.locals import *
from geometry import *


# Temporary constant.
DEFAULT_BACKGROUND_COLOUR = (211, 211, 211)



class ImageStore( object ):
    def __init__( self ):
        pass


    def load( self, name, modes = None ):
        nameNoSpace = name.replace( ' ', '_' )

        if modes:
            if modes == 'LR':
                imageFile = '%s.png' % name
                image = self.loadImage( imageFile )
                self.__dict__[nameNoSpace + 'L'] = image
                self.__dict__[nameNoSpace + 'R'] = pygame.transform.flip( image, True, False )
            elif modes == 'RL':
                imageFile = '%s.png' % name
                image = self.loadImage( imageFile )
                self.__dict__[nameNoSpace + 'R'] = image
                self.__dict__[nameNoSpace + 'L'] = pygame.transform.flip( image, True, False )
            else:
                # Assume sequence for now.
                self.__dict__[nameNoSpace + 's'] = images = {}

                for postFix in modes:
                    imageFile = '%s%s.png' % ( name, postFix )
                    image = self.loadImage( imageFile )
                    images[postFix] = image

        else:
            imageFile = '%s.png' % name
            image = self.loadImage( imageFile )
            self.__dict__[nameNoSpace] = image


    def loadImage( self, imageFile ):
        return pygame.image.load( imageFile ).convert_alpha()




class ObjectStore( object ):
    def __init__( self, parentMap ):
        self.parentMap = parentMap
        self.objectLists = {}


    def getMap( self ):
        return self.parentMap


    def addObject( self, obj, scene = None ):
        objType = obj.__class__.__name__
        objLists = self.objectLists

        if objLists.has_key( objType ):
            objList = objLists[objType]
        else:
            objLists[objType] = objList = []

        objList.append( obj )
        obj.setScene( scene )



    def deleteObject( self, obj ):
        objType = obj.__class__.__name__
        objLists = self.objectLists

        if objLists.has_key( objType ):
            objList = objLists[objType]

            objList.remove( obj )


    def deleteAllObjectsOfType( self, objType ):
        objLists = self.objectLists

        if objLists.has_key( objType ):
            del objLists[objType]


    def objectsOfType( self, objType ):
        objLists = self.objectLists

        if objLists.has_key( objType ):
            return objLists[objType]
        else:
            return []


    def update( self, camera, objTypes = None ):
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
                obj.update( camera )


    def move( self ):
        objLists = self.objectLists
        objTypes = objLists.keys()

        for objType in objTypes:
            objList = objLists[objType]

            for obj in objList:
                if hasattr( obj, 'move' ):
                    obj.move()


    def draw( self, viewPort, objTypes = None, debugDraw = False ):
        objLists = self.objectLists
        currentScene = self.parentMap.scene

        if not objTypes:
            # Non-deterministic order.
            objTypes = objLists.keys()

        for objType in objTypes:
            if not objLists.has_key( objType ):
                continue
                # raise  AttributeError( "No objects of type '%s' in map!" % objType )

            objList = objLists[objType]

            for obj in objList:
                if None == obj.scene or obj.scene == currentScene:
                    obj.draw( viewPort.displaySurface )


    def collides( self, testObj ):
        collides = False
        objLists = self.objectLists
        objTypes = objLists.keys()

        for objType in objTypes:
            objList = objLists[objType]

            for obj in objList:
                if testObj.collidesWith( obj ):
                    collides = True
                    break
                elif testObj.interactsWith( obj ):
                    break

            if collides:
                break

        return collides


    def getCollisions( self, testObj ):
        collisions = []
        objLists = self.objectLists
        objTypes = objLists.keys()

        for objType in objTypes:
            objList = objLists[objType]

            for obj in objList:
                if testObj.collidesWith( obj ):
                    collisions.append( obj )

        return collisions




class Scene( ObjectStore ):
    def __init__( self, parentMap, name, backGroundColour ):
        self.name = name
        self.backGroundColour = backGroundColour
        ObjectStore.__init__( self, parentMap )


    def getName( self ):
        return self.name


    def getBackGroundColour( self ):
        return backGroundColour


    def setBackGroundColour( self, colour ):
        self.backGroundColour = colour


    def addObject( self, obj ):
        ObjectStore.addObject( self, obj, scene=self )


    # Called from Object only.
    def moveObjectToScene( self, obj, scene ):
        self.deleteObject( obj )
        scene.addObject( obj )


    def collides( self, testObj ):
        collides = self.parentMap.collides( testObj )

        if not collides:
            collides = ObjectStore.collides( self, testObj )

        return collides


    def getCollisions( self, testObj ):
        collisions = self.parentMap.getCollisions( testObj )
        collisions.extend( ObjectStore.getCollisions( self, testObj ) )




class Map( object ):
    def __init__( self ):
        self.scenes = {}
        self.sprites = ObjectStore( self )
        self.players = ObjectStore( self )
        self.overlays = ObjectStore( self )
        self.scene = None
        self.images = None


    def setImageStore( self, images ):
        self.images = images


    def createScene( self, name, backGroundColour ):
        self.scenes[name] = scene = Scene( self, name, backGroundColour )

        if not self.scene:
            self.scene = scene


    def ensureScene( self ):
        if not self.scene:
            self.scene = Scene( self, 'default', DEFAULT_BACKGROUND_COLOUR )


    def getScene( self, name ):
        return self.scenes[name]


    def changeScene( self, name ):
        self.scene = self.getScene( name )


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
        self.ensureScene()
        self.sprites.addObject( obj, scene=self.scene )


    def addPlayer( self, obj ):
        self.players.addObject( obj, scene=self.scene )


    def movePlayerToScene( self, player, name ):
        scene = self.getScene( name )
        player.setScene( scene )


    def moveSprityeToScene( self, sprite, name ):
        scene = self.getScene( name )
        sprite.setScene( scene )


    def addOverlay( self, obj ):
        self.overlays.addObject( obj )


    def update( self, camera, objTypes = None ):
        self.ensureScene()
        self.scene.update( camera, objTypes )
        # Always update the sprites after the scene.
        self.sprites.update( camera )
        # self.players.update( camera, objTypes )
        self.overlays.update( camera, objTypes )


    def move( self ):
        self.sprites.move()


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


    def collides( self, testObj ):
        collides = self.sprites.collides( testObj )

        if not collides:
            collides = self.players.collides( testObj )

        return collides


    def getCollisions( self, testObj ):
        collisions = self.sprites.getCollisions( testObj )
        collisions.extend( self.players.getCollisions( testObj ) )

