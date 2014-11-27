from cellnopt.core import *
from easydev.easytest import *

def test_normalise():
    # deprecated but kept for back-compatibility
    m = NormaliseMIDAS(get_share_file("MD-unnorm.csv"))
    m.normalise()


    """array([[[ 0.        ,  0.        ,  0.00496278,  1.        ,  0.        ]],
          [[ 0.8       ,  0.8       ,  0.        ,  0.37437265,   nan]],
          [[ 0.        ,  0.86206897,  1.        ,  0.        ,  0.8 ]]])
    """


def test_normalise_xmidas():
    m = midas.XMIDAS(get_share_file("MD-unnorm.csv"))
    n = normalisation.XMIDASNormalise(m)


    # check simple normalisation with time and no ec50noise
    m.df = n.time_normalisation()
    m.df.fillna(0,inplace=True)
    assert_list_almost_equal(m.df.ix[0], [0,0,0.00496277,1,0])
    # !! replace na,none by zeros
    assert_list_almost_equal(m.df.ix[1], [ 0.8, 0.8, 0, 0.3743726, 0.])
    assert_list_almost_equal(m.df.ix[2], [ 0, 0.862069, 1,0,0.8])


    # check simple normalisation with time and ec50noise
    n.EC50noise = 1
    m.df = n.time_normalisation()
    m.df.fillna(0,inplace=True)
    assert_list_almost_equal(m.df.ix[0], [0,0,0.003914189,1,0])
    # !! replace na,none by zeros
    assert_list_almost_equal(m.df.ix[1], [ 0.4, 0.3764706, 0, 0., 0.])
    assert_list_almost_equal(m.df.ix[2], [ 0, 0.4310345, 1, 0.9880419, 0.4])


    # check simple normalisation with time and ec50noise
    n.EC50noise = 1
    n.saturation = 850
    m.df = n.time_normalisation()
    m.df.fillna(0,inplace=True)
    assert_list_almost_equal(m.df.ix[0], [0,0,0.003914189,1,0])
    assert_list_almost_equal(m.df.ix[1], [ 0.4, 0.4, 0, 0., 0.])
    assert_list_almost_equal(m.df.ix[2], [ 0, 0, 1, 0.9880419, 0.4])

    # test EC50data 
    n.EC50data = 1
    n.saturation = 1e6
    m.df = n.time_normalisation()
    m.df.fillna(0,inplace=True)
    assert_list_almost_equal(m.df.ix[0], [0,0,0.002454544,1,0])
    assert_list_almost_equal(m.df.ix[1], [ 0.25, 0.2352941, 0, 0., 0.])
    assert_list_almost_equal(m.df.ix[2], [ 0, 0.304878, 1, 0.9813436, 0.25])

    # hill coeff tested manually



def test_normalise_xmidas_attributes():
    m = midas.XMIDAS(get_share_file("MD-unnorm.csv"))
    n = normalisation.XMIDASNormalise(m)
    trysetattr(n, "saturation", "", False)
    trysetattr(n, "saturation", 1, True)
    trysetattr(n, "detection", "", False)
    trysetattr(n, "detection", 1, True)
    trysetattr(n, "EC50noise", "", False)
    trysetattr(n, "EC50data", "", False)
    trysetattr(n, "changeThreshold", "", False)
    trysetattr(n, "HillCoeff", "", False)



def _test_ctrl_normalisation():


    # case where control time 0 is not provided
    m = midas.XMIDAS(get_share_file("MD-unnorm_exp_nozero.csv"))
    n = normalisation.XMIDASNormalise(m)
    m.df = n.control_normalisation()
    m.df.fillna(0,inplace=True)
    
    # check values
    assert_list_almost_equal(m.df.ix[0], [0,0,1,1,0])
    assert_list_almost_equal(m.df.ix[1], [0.917431, 0.8, 0.987531, 0.261802, 0], places=5)
    assert_list_almost_equal(m.df.ix[2], [0, 0.862069,  0, 0, 0.8])
    assert_list_almost_equal(m.df.ix[3], [0,0,0,0,0])
    assert_list_almost_equal(m.df.ix[4], [0,0,0,0,0])
    assert_list_almost_equal(m.df.ix[5], [0,0,0,0,0])



    m =  midas.XMIDAS(get_share_file("MD-unnorm_exp.csv"))
    n = normalisation.XMIDASNormalise(m)
    m.df = n.control_normalisation()
    m.df.fillna(0, inplace=True)

    assert_list_almost_equal(m.df.ix[0], [0,0,1,1,0])
    assert_list_almost_equal(m.df.ix[3], [0,0,0.8485477,1,0])
    assert_list_almost_equal(m.df.ix[6], [0,0,0,0,0])

    assert_list_almost_equal(m.df.ix[1], [0.9174312,0.8,0.9875312,0.2618020,0])
    assert_list_almost_equal(m.df.ix[4], [0.9307692,0.8350515,1,0.3512397,0])
    assert_list_almost_equal(m.df.ix[7], [0,0,0,0,0])

    assert_list_almost_equal(m.df.ix[2], [0,0.8620690,0,0,0.8])
    assert_list_almost_equal(m.df.ix[5], [0.05882353,0.8832117,0,0,0.8350515])
    assert_list_almost_equal(m.df.ix[8], [0,0,0,0,0])






