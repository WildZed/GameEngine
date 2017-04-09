# Monkey-Rabbit Games
# Geometry



import copy


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


    def __sub__( self, pointOrNum ):
        point = Point( self )

        if isinstance( pointOrNum, Point ):
            point.x -= pointOrNum.x
            point.y -= pointOrNum.y
        else:
            point.x -= pointOrNum
            point.y -= pointOrNum

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




# Constants:

ORIGIN = Point()
