
def lineIntersection(line1, line2):
    """
    Return the coordinates of a point of intersection given two lines.
    Return None if the lines are parallel, but non-colli_near.
    Return an arbitrary point of intersection if the lines are colli_near.

    Parameters:
    line1 and line2: lines given by 2 points (a 2-tuple of (x,y)-coords).
    """
    (x1,y1), (x2,y2) = line1
    (u1,v1), (u2,v2) = line2
    (a,b), (c,d) = (x2-x1, u1-u2), (y2-y1, v1-v2)
    e, f = u1-x1, v1-y1
    # Solve ((a,b), (c,d)) * (t,s) = (e,f)
    denom = float(a*d - b*c)
    if _near(denom, 0):
        # parallel
        # If colli_near, the equation is solvable with t = 0.
        # When t=0, s would have to equal e/b and f/d
        if _near(float(e)/b, float(f)/d):
            # colli_near
            px = x1
            py = y1
        else:
            return None
    else:
        t = (e*d - b*f)/denom
        # s = (a*f - e*c)/denom
        px = x1 + t*(x2-x1)
        py = y1 + t*(y2-y1)
    return px, py


def lineSeqmentsDoIntersect(line1, line2):
    """
    Return True if line segment line1 intersects line segment line2 and 
    line1 and line2 are not parallel.
    """
    (x1,y1), (x2,y2) = line1
    (u1,v1), (u2,v2) = line2
    (a,b), (c,d) = (x2-x1, u1-u2), (y2-y1, v1-v2)
    e, f = u1-x1, v1-y1
    denom = float(a*d - b*c)
    if _near(denom, 0):
        # parallel
        return False
    else:
        t = (e*d - b*f)/denom
        s = (a*f - e*c)/denom
        # When 0<=t<=1 and 0<=s<=1 the point of intersection occurs within the
        # line segments
        return 0<=t<=1 and 0<=s<=1


def _near(a, b, rtol=1e-5, atol=1e-8):
    return abs(a - b) < (atol + rtol * abs(b))


if __name__ == '__main__':
    line1 = ((4,4),(10,10)) 
    line2 = ((11,5),(5,11))
    line3 = ((11,5),(9,7))
    line4 = ((4,0),(10,6)) 
    
    assert all(_near(a,b) for a,b in zip(lineIntersection(line1,line2), (8.0, 8.0)))
    assert all(_near(a,b) for a,b in zip(lineIntersection(line1,line3), (8.0, 8.0)))
    assert all(_near(a,b) for a,b in zip(lineIntersection(line2,line3), (11, 5)))
    
    assert lineIntersection(line1, line4) == None # parallel, non-colli_near
    assert lineSeqmentsDoIntersect(line1,line2) == True
    assert lineSeqmentsDoIntersect(line2,line3) == False  