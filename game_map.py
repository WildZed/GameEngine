# Monkey-Rabbit Games
# Game Engine

import pygame, copy
import game_objects as go
import game_utils as gu
from pygame.locals import *
from geometry import *
from game_constants import *


# Constants.

# Temporary constant.
DEFAULT_BACKGROUND_COLOUR = (211, 211, 211)




def createInteractionEvent( obj1, obj2, interactionOffset ):
    # print( "Creating interaction event %s <-> %s" % ( obj1, obj2 ) )
    point = obj1.getOffSetPos( interactionOffset )

    return pygame.event.Event( INTERACTION_EVENT, obj1=obj1, obj2=obj2, offset=interactionOffset, point=point )


def createCollisionEvent( obj1, obj2, collisionData ):
    # print( "Creating collision event %s <-> %s" % ( obj1, obj2 ) )
    point = obj1.getOffSetPos( collisionData.offset )
    rect = obj1.getOffSetOtherRect( collisionData.rect, collisionData.offset )

    return pygame.event.Event( COLLISION_EVENT, obj1=obj1, obj2=obj2, collisionData=collisionData, point=point, rect=rect )


def createClickCollisionEvent( obj, pos ):
    # print( "Creating click collision event %s <-> %s" % ( obj, pos ) )
    return pygame.event.Event( CLICK_COLLISION_EVENT, obj=obj, pos=pos )




class ImageStore( object ):
    def __init__( self, imageDir = 'images' ):
        self.imageDir = imageDir


    def load( self, fileName, modes = None, name = None, alpha = True ):
        if not name:
            name = fileName

        nameNoSpace = name.replace( ' ', '_' )

        if modes:
            if modes == 'LR':
                imageFile = '%s.png' % fileName
                image = self.loadImage( imageFile, alpha=alpha )
                self.__dict__[nameNoSpace + 'L'] = image
                self.__dict__[nameNoSpace + 'R'] = pygame.transform.flip( image, True, False )
            elif modes == 'RL':
                imageFile = '%s.png' % fileName
                image = self.loadImage( imageFile, alpha=alpha )
                self.__dict__[nameNoSpace + 'R'] = image
                self.__dict__[nameNoSpace + 'L'] = pygame.transform.flip( image, True, False )
            else:
                # Assume sequence for now.
                self.__dict__[nameNoSpace + 's'] = images = {}

                for postFix in modes:
                    imageFile = '%s%s.png' % ( fileName, postFix )
                    image = self.loadImage( imageFile, alpha=alpha )
                    images[postFix] = image

        else:
            imageFile = '%s.png' % fileName
            image = self.loadImage( imageFile, alpha=alpha )
            self.__dict__[nameNoSpace] = image

        return image


    def loadImage( self, imageFile, alpha = True ):
        imageFile = '%s/%s' % ( self.imageDir, imageFile )

        image = pygame.image.load( imageFile )

        if alpha:
            image = image.convert_alpha()
        else:
            image = image.convert()
            # Images with transparency appear to use WHITE as the transparent colour.
            image.set_colorkey( WHITE )
            # image.set_colorkey( BLACK )

        return image




class ObjectDrawSortKey:
    def __init__( self, obj ):
        self.obj = obj


    def __lt__( self, other ):
        return self.obj.drawOrder < other.obj.drawOrder or ( self.obj.drawOrder == other.obj.drawOrder and self.obj.colRect.centery < other.obj.colRect.centery )


    def __eq__( self, other ):
        return self.obj.drawOrder == other.obj.drawOrder and self.obj.colRect.bottom == other.obj.colRect.bottom


    def __gt__( self, other ):
        return self.obj.drawOrder > other.obj.drawOrder or ( self.obj.drawOrder == other.obj.drawOrder and self.obj.colRect.centery > other.obj.colRect.centery )


    def __le__( self, other ):
        return not ( self > other )


    def __ge__( self, other ):
        return not ( self < other )


    def __ne__( self, other ):
        return not ( self == other )




class ObjectStore( object ):
    def __init__( self, parentMap ):
        self.parentMap = parentMap
        self.objectLists = {}
        self._objectTypes = None
        self.drawList = []


    def getMap( self ):
        return self.parentMap


    def addObject( self, obj, scene = None ):
        objType = obj.__class__
        objLists = self.objectLists

        if objType in objLists:
            objList = objLists[objType]
        else:
            objLists[objType] = objList = []
            self._objectTypes = None

        objList.append( obj )
        self.drawList.append( obj )
        obj.setScene( scene )

        return obj


    # Removes the object from the ObjectStore but does not delete it.
    def removeObject( self, obj ):
        objType = obj.__class__
        objLists = self.objectLists

        if objType in objLists:
            objList = objLists[objType]

            objList.remove( obj )
            self.drawList.remove( obj )


    def deleteAllObjectsOfType( self, objType ):
        objLists = self.objectLists

        if objType in objLists:
            del objLists[objType]
            self._objectTypes = None



    def prioritisedObjectTypes( self ):
        objectTypes = self._objectTypes

        if not objectTypes:
            objectTypes = list( self.objectLists.keys() )
            objectTypes.sort( key=lambda objectType : objectType.pickPriority, reverse=True )

        return objectTypes


    def objectsOfType( self, objType ):
        objLists = self.objectLists

        if objType in objLists:
            return objLists[objType]
        else:
            return []


    def getObject( self, objOrName ):
        for objList in self.objectLists.values():
            for obj in objList:
                if isinstance( objOrName, str ):
                    if obj.name == objOrName:
                        return obj
                elif obj == objOrName:
                    return obj

        return None



    def update( self, camera, updateOrder = None ):
        objLists = self.objectLists

        if not updateOrder:
            # Non-deterministic order.
            updateOrder = objLists.keys()

        for objType in updateOrder:
            if objType not in objLists:
                continue
                # raise  AttributeError( "No objects of type '%s' in map!" % objType )

            objList = objLists[objType]

            for obj in objList:
                obj.update( camera )


    # def move( self ):
    #     objLists = self.objectLists
    #     objTypes = objLists.keys()
    #
    #     for objType in objTypes:
    #         objList = objLists[objType]
    #
    #         for obj in objList:
    #             if hasattr( obj, 'move' ):
    #                 obj.move()


    def sortObjLists( self, reverse=False ):
        objLists = self.objectLists

        for objType in objLists.keys():
            objList = objLists[objType]
            objList.sort( key=lambda obj : obj.colRect.bottom, reverse=reverse )


    def getSortedDrawList( self ):
        drawList = copy.copy( self.drawList )

        for obj in self.drawList:
            drawList.extend( obj.getAssociatedObjects() )

        drawList.sort( key=lambda obj : ObjectDrawSortKey( obj ) ) #, reverse=reverse )

        return drawList


    def draw( self, viewPort, debugDraw = False ):
        drawList = self.getSortedDrawList()
        surface = viewPort.surface
        viewRect = viewPort.getCameraRect()

        for obj in drawList:
            # if type( obj ) is go.BackGround:
            obj.draw( surface, viewRect )


    def drawByObjectTypeOrder( self, viewPort, objTypes = None, debugDraw = False ):
        objLists = self.objectLists
        currentScene = self.parentMap.scene
        viewRect = viewPort.getCameraRect()

        self.sortObjLists()

        if not objTypes:
            objTypes = self.parentMap.drawOrder

        if not objTypes:
            # Non-deterministic order.
            objTypes = objLists.keys()

        for objType in objTypes:
            if objType not in objLists:
                continue
                # raise  AttributeError( "No objects of type '%s' in map!" % objType )

            objList = objLists[objType]

            for obj in objList:
                if None == obj.scene or obj.scene == currentScene:
                    obj.draw( viewPort.surface, viewRect )


    def collides( self, testObj ):
        event = None
        objLists = self.objectLists
        objTypes = self.prioritisedObjectTypes()

        for objType in objTypes:
            objList = objLists[objType]

            for obj in objList:
                collisionData = testObj.collidesWith( obj )

                if collisionData:
                    event = createCollisionEvent( testObj, obj, collisionData )
                    break
                else:
                    interactionOffset = testObj.interactsWith( obj )

                    if interactionOffset:
                        event = createInteractionEvent( testObj, obj, interactionOffset )

            if event and event.type == COLLISION_EVENT:
                break

        return event


    def collidesWithPoint( self, pos, useFullRect = False ):
        event = None
        objLists = self.objectLists
        objTypes = self.prioritisedObjectTypes()

        for objType in objTypes:
            objList = objLists[objType]

            for obj in objList:
                if obj.collidesWithPoint( pos, useFullRect=useFullRect ):
                    event = createClickCollisionEvent( obj, pos )
                    break

            if event:
                break

        return event


    def getAllCollisions( self, testObj ):
        collisionEvents = []
        objLists = self.objectLists
        objTypes = objLists.keys()

        for objType in objTypes:
            objList = objLists[objType]

            for obj in objList:
                if testObj.collidesWith( obj ):
                    collisionEvents.append( obj )

        return collisionEvents




class Scene( ObjectStore ):
    @staticmethod
    def isScene( scene ):
        return scene.__class__ == Scene


    def __init__( self, parentMap, name, backGroundColour = DEFAULT_BACKGROUND_COLOUR, boundaryStyle = None ):
        self.name = name
        self.backGroundColour = backGroundColour
        self.boundaryStyle = boundaryStyle

        super().__init__( parentMap )


    def getName( self ):
        return self.name


    def getBackGroundColour( self ):
        return self.backGroundColour


    def setBackGroundColour( self, colour ):
        self.backGroundColour = colour


    def addObject( self, obj ):
        return ObjectStore.addObject( self, obj, scene=self )


    # Called from Object only.
    def moveObjectToScene( self, obj, scene ):
        if not Scene.isScene( scene ):
            scene = self.parentMap.getScene( scene )

        self.removeObject( obj )
        scene.addObject( obj )


    def draw( self, viewPort ):
        # Draw the background.
        viewPort.drawBackGround( self.backGroundColour )

        super().draw( viewPort )


    def collidesWithBoundary( self, obj ):
        collisionEvent = None

        if self.boundaryStyle:
            collisionData = self.boundaryStyle.collidesWith( obj )

            if collisionData:
                collisionEvent = createCollisionEvent( obj, self.boundaryStyle, collisionData )

        return collisionEvent


    def collides( self, testObj ):
        return super().collides( testObj ) or self.collidesWithBoundary( testObj )


    def getAllCollisions( self, testObj ):
        collisionEvents = super().getAllCollisions( testObj )
        boundaryCollisionEvent = self.collidesWithBoundary( testObj )

        if boundaryCollisionEvent:
            collisionEvents.append( boundaryCollisionEvent )

        return collisionEvents




class Map( object ):
    def __init__( self ):
        self.scenes = {}
        # self.sprites = ObjectStore( self )
        # self.players = ObjectStore( self )
        self.movingObjects = []
        self.overlays = ObjectStore( self )
        self.scene = None
        self.images = None
        # self.drawOrder = None
        self.paused = False


    def setImageStore( self, images ):
        self.images = images


    # def getDrawOrder( self, drawOrder ):
    #     return self.drawOrder
    #
    #
    # def setDrawOrder( self, drawOrder ):
    #     self.drawOrder = drawOrder


    def setPaused( self, paused = True ):
        self.paused = paused


    def createScene( self, name, **kwArgs ):
        self.scenes[name] = scene = Scene( self, name, **kwArgs )

        if not self.scene:
            self.scene = scene


    def ensureScene( self ):
        if not self.scene:
            self.scene = Scene( self, 'default', DEFAULT_BACKGROUND_COLOUR )


    def getScene( self, scene = None ):
        if scene:
            scene = Scene.isScene( scene ) and scene or self.scenes[scene]
        else:
            scene = self.scene

        return scene


    def changeScene( self, newScene ):
        newScene = self.getScene( newScene )

        if newScene == self.scene:
            return False

        self.scene = newScene

        return True


    def addObject( self, obj ):
        self.ensureScene()
        self.scene.addObject( obj )

        if hasattr( obj, 'move' ):
            self.movingObjects.append( obj )

        return obj


    def addOverlay( self, obj ):
        self.overlays.addObject( obj )


    def objectsOfType( self, objType ):
        self.ensureScene()
        objectsOfType = []
        objectsOfType.extend( self.scene.objectsOfType( objType ) )
        objectsOfType.extend( self.overlays.objectsOfType( objType ) )

        return objectsOfType


    def deleteAllObjectsOfType( self, objType ):
        self.ensureScene()
        self.scene.deleteAllObjectsOfType( objType )
        # self.sprites.deleteAllObjectsOfType( objType )
        # self.players.deleteAllObjectsOfType( objType )
        self.overlays.deleteAllObjectsOfType( objType )
        # Need to ensure that objects are removed from the movingObjects list.
        # Although del should do it.


    # def addSprite( self, obj ):
    #     self.ensureScene()
    #     self.sprites.addObject( obj, scene=self.scene )


    # def addPlayer( self, obj ):
    #     self.players.addObject( obj, scene=self.scene )


    # def movePlayerToScene( self, player, name ):
    #     scene = self.getScene( name )
    #     player.setScene( scene )


    # def moveSpriteToScene( self, sprite, name ):
    #     scene = self.getScene( name )
    #     sprite.setScene( scene )


    def update( self, camera, updateOrder = None ):
        self.ensureScene()
        self.scene.update( camera, updateOrder=updateOrder )
        # Always update the sprites after the scene.
        # self.sprites.update( camera )
        # self.players.update( camera, objTypes )
        self.overlays.update( camera, updateOrder=updateOrder )


    def move( self ):
        # self.players.move()
        # self.sprites.move()
        for moveObj in self.movingObjects:
            if self.paused:
                break

            moveObj.move()



    def draw( self, viewPort ):
        self.ensureScene()

        self.scene.draw( viewPort )
        # self.sprites.draw( viewPort, objTypes )
        # self.players.draw( viewPort, objTypes )
        self.overlays.draw( viewPort )


    def debugPos( self, name, pos, **kwArgs ):
        posBox = self.overlays.getObject( name )

        if not posBox:
            kwArgs['size'] = kwArgs.get( 'size', 4 )
            kwArgs['name'] = name
            posBox = self.overlays.addObject( go.Box( pos, **kwArgs ) )

        posBox.pos = pos


    def __getattr__( self, key ):
        self.ensureScene()

        if key == 'player':
            # return self.__dict__['players'].objectLists[go.Player][0]
            # Need to check in all scenes for the player, or the movingObjects list.
            return self.__dict__['scene'].objectLists[go.Player][0]
        elif key == 'sprites':
            # Currently just return sprites in the current scene, but it could gather from all scenes.
            return self.__dict__['scene'].objectLists[go.Sprite]
        elif key == 'score':
            return self.__dict__['overlays'].objectLists[go.Score][0]
        elif key == 'backGroundColour':
            return self.__dict__['scene'].backGroundColour

        if key not in self.__dict__ :
            raise AttributeError( "Unrecognised Map attribute '%s' in __getattr__!" % key )

        val = self.__dict__[key]

        return val


    # def collides( self, testObj ):
    #     # May need to test players first.
    #     # May need to check sprites are in the current scene.
    #     # event = self.sprites.collides( testObj )
    #     #
    #     # if not event or event.type != COLLISION_EVENT:
    #     #     newEvent = self.players.collides( testObj )
    #     #
    #     #     if not event or ( newEvent and newEvent.type == COLLISION_EVENT ):
    #     #         event = newEvent
    #     event = None
    #
    #     for moveObj in self.movingObjects:
    #         if testObj.collidesWith( obj ):
    #             event = self.createCollisionEvent( testObj, obj )
    #             break
    #         elif testObj.interactsWith( obj ):
    #             event = self.createInteractionEvent( testObj, obj )
    #
    #     return event
    #
    #
    # def collidesWithPoint( self, pos ):
    #     # event = self.sprites.collidesWithPoint( pos )
    #     #
    #     # if not event:
    #     #     event = self.players.collidesWithPoint( pos )
    #     event = None
    #
    #     for moveObj in self.movingObjects:
    #         if obj.collidesWithPoint( pos ):
    #             event = self.createClickCollisionEvent( obj, pos )
    #             break
    #
    #     return event
    #
    #
    # def getAllCollisions( self, testObj ):
    #     # collisions = self.sprites.getAllCollisions( testObj )
    #     # collisions.extend( self.players.getAllCollisions( testObj ) )
    #     collisions = []
    #
    #     for moveObj in self.movingObjects:
    #         if testObj.collidesWith( obj ):
    #             collisions.append( obj )
    #
    #     return collisions
