# Monkey-Rabbit Games
# Geometry

import copy, pygame




class Point( object ):
    def __init__( self, posOrX = None, y = None ):
        if y is not None:
            self.x = posOrX
            self.y = y
        elif posOrX.__class__.__name__ is 'Point':
            self.x = posOrX.x
            self.y = posOrX.y
        elif type( posOrX ) is tuple:
            self.x = posOrX[0]
            self.y = posOrX[1]
        else:
            self.x = posOrX
            self.y = posOrX


    def isValid( self ):
        return self.x is not None and self.y is not None


    # Shrink a Point as an offset by the given amount.
    def shrinkBy( self, x, y ):
        if self.x > 0:
            if self.x > x:
                self.x -= x
            else:
                self.x = 0
        elif self.x < 0:
            if self.x < -x:
                self.x += x

        if self.y > 0:
            if self.y > y:
                self.y -= y
            else:
                self.y = 0
        elif self.y < 0:
            if self.y < -y:
                self.y += y


    def __add__( self, pointOrNum ):
        point = Point( self )
        point += pointOrNum

        return point


    def __sub__( self, pointOrNum ):
        point = Point( self )
        point -= pointOrNum

        return point


    def __neg__( self ):
        return Point( -self.x, -self.y )


    def __iadd__( self, pointOrNum ):
        if isinstance( pointOrNum, Point ):
            self.x += pointOrNum.x
            self.y += pointOrNum.y
        else:
            self.x += pointOrNum
            self.y += pointOrNum

        return self


    def __isub__( self, pointOrNum ):
        if isinstance( pointOrNum, Point ):
            self.x -= pointOrNum.x
            self.y -= pointOrNum.y
        else:
            self.x -= pointOrNum
            self.y -= pointOrNum

        return self


    def __div__( self, pointOrNum ):
        point = Point( self )
        point /= pointOrNum

        return point


    def __idiv__( self, pointOrNum ):
        if isinstance( pointOrNum, Point ):
            self.x /= pointOrNum.x
            self.y /= pointOrNum.y
        else:
            self.x /= pointOrNum
            self.y /= pointOrNum

        return self


    def __mul__( self, pointOrNum ):
        point = Point( self )
        point *= pointOrNum

        return point


    def __imul__( self, pointOrNum ):
        if isinstance( pointOrNum, Point ):
            self.x *= pointOrNum.x
            self.y *= pointOrNum.y
        else:
            self.x *= pointOrNum
            self.y *= pointOrNum

        return self


    def __eq__( self, point ):
        return self.x == point.x and self.y == point.y


    def __ne__( self, point ):
        return not self.__eq__( point )


    def __repr__( self ):
        return '(%d, %d)' % (self.x, self.y)


    def asTuple( self ):
        return ( self.x, self.y )


    def manhattanDistance( self, point ):
        return abs( self.x - point.x ) + abs( self.y - point.y )




class UnitPoint( Point ):
    def __init__( self, posOrX = None, y = None ):
        Point.__init__( self, posOrX, y )
        self.x = self.unitCoord( self.x )
        self.y = self.unitCoord( self.y )


    def unitCoord( self, coord ):
        if coord:
            coord = coord / abs( coord )

        return coord




class Rectangle( object ):
    def __init__( self, rectOrll = None, ur = None, ul = None, width = None, height = None ):
        if type( rectOrll ) is Rectangle:
            self.ll = Point( rectOrll.left, rectOrll.bottom )
            self.ur = Point( rectOrll.right, rectOrll.top )
        elif type( rectOrll ) is pygame.Rect:
            self.ll = copy.copy( rectOrll.ll )
            self.ur = copy.copy( rectOrll.ur )
        elif type( rectOrll ) is Point:
            if type( ur ) is Point:
                self.ll = copy.copy( rectOrll )
                self.ur = copy.copy( ur )
            else:
                self.ll = copy.copy( rectOrll )
                self.ur = copy.copy( rectOrll )

                if width and height:
                    self.ur += Point( width, height )
        elif type( ur ) is Point:
            self.ll = copy.copy( ur )
            self.ur = copy.copy( ur )

            if width and height:
                self.ur -= Point( width, height )
        elif type( ul ) is Point:
            self.ll = copy.copy( ul )
            self.ur = copy.copy( ul )

            if width and height:
                self.ll -= Point( 0, height )
                self.ur += Point( width, 0 )
        else:
            self.ll = Point()
            self.ur = Point()


    def isValid( self ):
        return self.ll.isValid() and self.ur.isValid()


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


    def encloseRectangle( self, rect ):
        rect = Rectangle( rect )

        if self.ll.x < rect.ll.x:
            rect.ll.x = self.ll.x

        if self.ll.y < rect.ll.y:
            rect.ll.y = self.ll.y

        if self.ur.x > rect.ur.x:
            rect.ur.x = self.ur.x

        if self.ur.y > rect.ur.y:
            rect.ur.y = self.ur.y

        return rect


    def collapse( self, direction, coord = None ):
        if 'left' == direction:
            if coord is None:
                coord = self.ll.x

            self.ur.x = coord
        elif 'right' == direction:
            if coord is None:
                coord = self.ur.x

            self.ll.x = coord
        elif 'top' == direction:
            if coord is None:
                coord = self.ur.y

            self.ll.y = coord
        elif 'bottom' == direction:
            if coord is None:
                coord = self.ll.y

            self.ur.y = coord


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
        elif key == 'ul':
            val = Point( self.ll.x, self.ur.y )
        elif key == 'lr':
            val = Point( self.ur.x, self.ll.y )
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


    def asTupleTuple( self ):
        return ( self.ul.asTuple(), self.ur.asTuple(), self.lr.asTuple(), self.ll.asTuple() )




class Vector( Point ):
    pass




# Constants:

ORIGIN = Point( 0, 0 )
