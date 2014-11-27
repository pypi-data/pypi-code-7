# -*- python -*-
#
#  This file is part of the cinapps.tcell package
#
#  Copyright (c) 2012-2013 - EMBL-EBI
#
#  File author(s): Thomas Cokelaer (cokelaer@ebi.ac.uk)
#
#  Distributed under the GLPv3 License.
#  See accompanying file LICENSE.txt or copy at
#      http://www.gnu.org/licenses/gpl-3.0.html
#
#  website: www.cellnopt.org
#
##############################################################################
"""Module dedicated to convertion of kinexus data into MIDAS


.. testsetup:: *

    from cellnopt.core import *
"""
from csv2pd import SimpleDataFrame
import pandas as pd

class Kinexus(SimpleDataFrame):
    """Class dedicated to kinexus data

    The Kinexus data are provided as Excel documents with several sheets. The
    main sheet called "kinetic" contains all the relevant data. It can be a pure
    excel document or a CSV file with separator as : character.

    The following columns are looked for:

        * Target Protein Name
        * Uniprot Link
        * Globally Normalized TXX where XX is a time

    See Constructor for more information about the CSV format.

    ::

        >>> k = Kinexus("kinetic.csv")
        >>> k.data
        >>> k.select_globally_normalised()
        >>> k.export2midas()



    """
    def __init__(self, filename=None, sheet=None, 
                header_uniprot="Uniprot_Link",
                header_protein_name="Target_Protein_Name",
                sep=":", **kargs):
        """.. rubric:: Constructor

        :param str filename: the file is a CSV file that was exported from an excel
            document (sheet called kinetic). Make sure the header is on 1
            single line. Strings are bracketed with double quotes. CSV file means comma
            separated but we used ":" character as a delimiter since spaces and commas may be
            used within cells. In LibreOffice, "save as" your excel and set the
            field delimiter to ":" character. Set Text delimiter no nothing.

        If you do not provide a filename, you cannot export to midas but you can
        still play with some methods such as :meth:`get_name_from_uniprot`.


        This class will try to identify the meaning of the columns. We want to
        retrieve the data at different time points given the target protein name
        or antibody names. Kinexus daa may be diverse so there is no guarantee
        that this class will work for a variety of different input format. 

        The data at different time points are extracted from the column that are
        tagged "Globally Normalized TX" where X is the time tag (e.g., 0, 1, 5) 
        All columns starting with "Globally" are extracted. The different times
        are stored. (see :meth:`select_globally_normalised`.

        :meth:`get_name_from_uniprot` retrieve the exact UniProt name given a
        uniprot accession number, which is more meaningful. 

        Several rows may target the same protein with the same uniprot ID. So,
        we need to differentiate them in the data. This is done by appending the
        phosphosite to the target protein name.

        """
        super(Kinexus, self).__init__(filename, sep=sep, sheet=sheet, **kargs)
        #: can be changed to fit your data
        self.header_uniprot = header_uniprot
        self.header_protein_name = header_protein_name

        self.uniprot = None

    def _get_times(self):
        times = [x for x in self.columns if "Globally" in x]
        times = [x.split("-")[1].strip().replace("\"", "") for x in times]
        for t in times:
            assert t.startswith("T")
        return times

    def _get_time_indices(self):
        times = [i for i,x in enumerate(self.columns) if "Globally" in x]
        return times

    def select_globally_normalised(self):
        """Returns a subset of the entire data set

        The selection is the protein name, followed by the data at different
        time point labelled "Globally Normalised" and finally the uniprot ID. The number
        of time points and their values can be retrieved from _get_times() method

        protein names are obtained from the uniprot ID given in the kinexus data.

        :return: list of tuples. Each tuple contain the data as exaplained
            above (protein name, data, uniprot ID)


        """

        # ignore data without uniprot id
        mask = pd.isnull(self.df['Uniprot_Link'])==False
        subdf = self.df[mask]

        columns = [self.header_protein_name] + \
            [subdf.columns[x] for x in self._get_time_indices()] +  \
            [self.header_uniprot]
        print(columns)
        results = subdf[columns]
        return results

    def _get_index_column(self, name):
        if col in self.columns:
            return list(self.columns).index(name)
        else:
            raise ValueError("name not present in the column names")
    def _get_uniprot_column(self):
        col = [x for x in k.df.columns if "Uniprot" in x]
        assert len(col)==1
        col = col[0]
        return self.df[col]


    def get_name_from_uniprot(self, Id, taxon=9606):
        """Get unique Entry Name (without specy) from a unique uniprot ID

        :param str Id: UniProt ID (e.g., P43403)
        :param str taxon: the specy taxon. 9606 correspond to HUMAN
        :return: the name without taxon (e.g., ZAP70)

            >>> k = Kinexus()
            >>> k.get_name_from_uniprot("P43403")
            'ZAP70'


        .. todo:: a global mapping that is much faster using :
            u.mapping("ACC", "ID", " ".join(k.df.Uniprot_Link))
        """
        if self.uniprot == None:
            from bioservices import UniProt
            self.uniprot = UniProt(verbose=False)
        query = Id+"+and+taxonomy:%s" % taxon
        #print query
        try:
            name = self.uniprot.search(query=query, format="tab", 
                columns="entry name,id", limit=1).split("\n")[1].split("\t")[0]
            name = name.split("_")[0]
        except:
            print("!!!!!!!!!!!!!! not found")
            return "notfound"
        return name

    def export2midas(self, filename="MD-kinexus.csv",
        mode="globally_normalised", uniprot=True):
        """Converts the Kinexus data into a MIDAS file.

        :param str filename: the output name for the MIDAS file
        :param str mode: There are different post processed data in the Kinexus
            data so we used a mode to refine what user can export in the MIDAS file.
            Right now only one mode is allowed that is "globally_normalised".
            See :meth:`select_globally_normalised` method for details.
        :param bool uniprot: specy names in the MIDAS file will be the UniProt
            Entry Name. Otherwise, the hand-written "Target Protein Names"

        .. note:: row with no uniprot (ie. set to NA) are ignored
        """
        assert mode in "globally_normalised"

        data = self.select_globally_normalised()
        data = data.as_matrix()
        data = [list(x) for x in list(data)]
        N1 = len(data)
        newdata = []
        for line in data:
            if line[-1] != "NA" and line[-1]:
                newdata.append(line)
        data = newdata
        N2 = len(data)
        if N2-N1>0: 
            print("Ignored %s entries (NAs)" % N2-N1)
        print("Creating and saving MIDAS into %s" %filename)
        f = open(filename, "w")
        header = "TR::CellLine, TR:hormone, DA:ALL"
        if uniprot==True:
            indices_to_ignore = []
            for i, uniprotID in zip(self.df.index, self.df.Uniprot_Link):
                if "Uniprot_entry" in self.df.columns:
                    name = self.df.Uniprot_entry[i]
                else:
                    #name = self.get_name_from_uniprot(uniprotID)
                    pass
                print(i, len(data), uniprotID, name)
                # no need if we use uniprot names
                #name = name.replace(" ", "_")  # replaces spaces with underscores
                if "notfound" not in name:
                    header += ", DV:%s" % name
                else:
                    indices_to_ignore.append(i)
            data = [x for i,x in enumerate(data) if i not in indices_to_ignore]
        else:
            for name in [x[0] for x in data]:
                name = name.replace(" ", "_")  # replaces spaces with underscores
                header += ", DV:%s" % name
        f.write(header + "\n")

        times = [float(x[1:]) for x in self._get_times()]
        Ntimes = len(times)
        # there is only one stimuli (hormone). Let us call it "hormone"
        # Number of time is len(times). We use DA:ALL. CellLine is irrelevant
        # for now.
        for i,time in enumerate(times):
            this_time_data = [x[i+1] for x in data]
            row = "1, 1, " + str(time)
            for value in this_time_data:
                row += ", %s" % value
            f.write(row+"\n")
        f.close()


    # scan the DataFrame to extractc uniprot name. convert with bioservices into protein or gene names
    # append the phospho_site ?? how to deal with names in the PKN ?










