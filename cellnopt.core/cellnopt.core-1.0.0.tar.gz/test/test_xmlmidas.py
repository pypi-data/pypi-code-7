from cellnopt.core import XMLMidas, get_share_file
import warnings
warnings.simplefilter("ignore")




def test_xmlmidas():

    m = XMLMidas(get_share_file("XML/midas.xml"))
    m.test()
    sorted(m.stimuliNames) == ["EGF", "TNFa"]




