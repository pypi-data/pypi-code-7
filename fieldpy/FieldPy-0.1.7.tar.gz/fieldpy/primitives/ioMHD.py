import os
import numpy


def mhdReadHeader(fname):
    """Return a dictionary of meta data from meta header file"""
    fileIN = open(fname, "r")
    line = fileIN.readline()

    meta_dict = {}
    tag_set1 = ['ObjectType', 'NDims', 'DimSize', 'ElementType',
                'ElementDataFile']
    tag_set2 = ['BinaryData', 'BinaryDataByteOrderMSB', 'CompressedData',
                'CompressedDataSize']
    tag_set3 = ['Offset', 'CenterOfRotation', 'AnatomicalOrientation',
                'ElementSpacing', 'TransformMatrix']
    tag_set4 = ['Comment', 'SeriesDescription', 'AcquisitionDate',
                'AcquisitionTime', 'StudyDate', 'StudyTime']
    tag_set = []

    tag_set.extend(tag_set1)
    tag_set.extend(tag_set2)
    tag_set.extend(tag_set3)
    tag_set.extend(tag_set4)
    tag_flag = [False] * len(tag_set)
    while line:
        tags = str.split(line, '=')
        #print tags[0]
        for i in range(len(tag_set)):
            tag = tag_set[i]
            if (str.strip(tags[0]) == tag) and (not tag_flag[i]):
                #print tags[1]
                meta_dict[tag] = str.strip(tags[1])
                tag_flag[i] = True
        line = fileIN.readline()
        #print comment
    fileIN.close()
    return meta_dict


def mhdRead(fname):
    r"""Read an mhd file under 'fname'"""

    # read the header file
    meta_dict = mhdReadHeader(fname)

    # get the array dimensions (which are reversed in the file)
    dimsize = [int(i) for i in meta_dict['DimSize'].split()]
    dimsize.reverse()

    # get the array spacing
    spacing = [float(i) for i in meta_dict['ElementSpacing'].split()]
    spacing.reverse()

    # get the array offset, i.e., first coordinates
    offset = [float(i) for i in meta_dict['Offset'].split()]
    offset.reverse()

    #define the datatype (float or double)
    if meta_dict['ElementType'] == 'MET_FLOAT':
        typeData = numpy.float32
    elif meta_dict['ElementType'] == 'MET_DOUBLE':
        typeData = numpy.float64

    data = numpy.fromfile(fname.replace(".mhd", ".raw"), typeData)
    data = data.reshape(dimsize)

    return data, spacing, offset


def mhdWriteHeader(fname, meta_dict):
    header = ''
    # do not use tags = meta_dict.keys() because the order of tags matters
    tags = ['ObjectType', 'NDims', 'BinaryData',
            'BinaryDataByteOrderMSB', 'CompressedData', 'CompressedDataSize',
            'TransformMatrix', 'Offset', 'CenterOfRotation',
            'AnatomicalOrientation',
            'ElementSpacing',
            'DimSize',
            'ElementType',
            'ElementDataFile',
            'Comment', 'SeriesDescription', 'AcquisitionDate',
            'AcquisitionTime', 'StudyDate', 'StudyTime']
    for tag in tags:
        if tag in meta_dict.keys():
            header += '%s = %s\n' % (tag, meta_dict[tag])
    f = open(fname, 'w')
    f.write(header)
    f.close()


def mhdWrite(fname, data, spacing, offset):
    r"""Write an mhd file under 'fname'

    This function saves an array into an .mhd file. It requires information
    on the array's 'spacing' and 'offset' which would define the data
    coordinates.

    Note:
        This function works for both 2D and 3D arrays but the 'spacing' and
        'offset' properties must be defined accordingly

    Parameters:
        fname (str): The filename under which the .mhd file is saved
        data (numpy.ndarray): The data array to be saved
        spacing (list, tuple): A list/tuple containing float numbers with the
            spacing of the array elements. The order must be x-y-z
        offset (list, tuple): A list/tuple containing float number with the
            first coordinate of the array's elements. The order must be x-y-z
    """

    # create the header dictionary
    meta_dict = {}

    # set standard info
    meta_dict['ObjectType'] = 'Image'
    meta_dict['BinaryData'] = 'True'
    meta_dict['BinaryDataByteOrderMSB'] = 'False'
    meta_dict['CompressedData'] = 'False'
    meta_dict['CenterOfRotation'] = ' '.join([str(i) for i in [0, 0, 0]])

    # define the data type
    if data.dtype == numpy.float32:
        meta_dict['ElementType'] = 'MET_FLOAT'
    elif data.dtype == numpy.float64:
        meta_dict['ElementType'] = 'MET_DOUBLE'

    # define the number of dimensions
    meta_dict['NDims'] = str(len(data.shape))

    #define the data of the dimensions
    dimsize = list(data.shape)
    dimsize.reverse() #MHD requires Z-Y-X order in this lists
    meta_dict['DimSize'] = ' '.join([str(i) for i in dimsize])

    # define the filename of the raw data
    meta_dict['ElementDataFile'] = (os.path.split(fname)[-1]).replace('.mhd',
                                                                      '.raw')

    # define the data offset (again reverse)
    offset = list(offset)
    offset.reverse()
    meta_dict['Offset'] = ' '.join([str(i) for i in offset])

    # define the data spacing (again reverse)
    spacing = list(spacing)
    spacing.reverse()
    meta_dict['ElementSpacing'] = ' '.join([str(i) for i in spacing])

    # write the header file
    mhdWriteHeader(fname, meta_dict)

    # write the raw data file
    data.tofile(fname.replace('.mhd', '.raw'))


