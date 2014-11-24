from .complex import *

class CubicalComplex(Complex):
    pass

    def __init__(self, cubes):
        super(CubicalComplex, self).__init__(CubicalComplex._create(cubes))

    @classmethod
    def _create(cls, cubes):
        from .impl import capd_impl
        if not cubes:
            return capd_impl.CubicalComplex([0,0]) # todo []

        dim = len(cubes[0])
        capd_cubes = []
        max_coor = [0]*dim

        for c in cubes:
            assert len(c) == dim
            capd_cube = [ (b, (e - b > 0)) for b, e in c]
            capd_cubes.append(capd_cube)
            for d in xrange(dim):
                if max_coor[d] < c[d][1]:
                    max_coor[d] = c[d][1]

        max_coor = map(lambda x: x, max_coor)
        impl = capd_impl.CubicalComplex(max_coor)
        for c in capd_cubes:
            impl.insert(list(c))

        impl.fillWithBoundaries()
        return impl
