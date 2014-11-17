#!/usr/bin/env python
# DX_APP_WIZARD_NAME DX_APP_WIZARD_VERSION
# Generated by dx-app-wizard.
#
# Parallelized execution pattern (GTable input and output): This
# pattern is useful for performing parallel computations such as
# mapping or filtering reads stored in an existing GenomicTable
# (GTable), the results of which will be aggregated into another
# GTable.  Your app will create the output GTable, dispatch the row
# ranges to "process" stages to perform the parallel computations, and
# finally the "postprocess" stage will close the GTable when all
# "process" stages are done adding results to your output.
#
# See https://wiki.dnanexus.com/Developer-Portal for documentation and
# tutorials on how to modify this file.
#
# DNAnexus Python Bindings (dxpy) documentation:
#   http://autodoc.dnanexus.com/bindings/python/current/

import os
import dxpy

# This example will break an input GenomicTable into chunks of 100000
# rows each.
row_chunk_size = 100000

@dxpy.entry_point("postprocess")
def postprocess(output_gtable_id):
    DX_APP_WIZARD_||_OUTPUT = dxpy.DXGTable(output_gtable_id)
    DX_APP_WIZARD_||_OUTPUT.close()

@dxpy.entry_point("process")
def process(input_gtable_id, start_row, end_row, output_gtable_id):
    DX_APP_WIZARD_||_INPUT = dxpy.DXGTable(input_gtable_id)

    # Using the context manager here is useful so that the flush()
    # method is called once the context manager exits, and any rows
    # added will be flushed to the platform.  The mode is set to "a"
    # for "append".

    with dxpy.open_dxgtable(output_gtable_id, mode="a") as DX_APP_WIZARD_||_OUTPUT:

        # The following loop iterates over each row from start_row to
        # end_row (not including end_row).  You can find documentation on
        # other useful GTable methods (such as iterating over a genomic
        # range query with iterate_query_rows) in the dxpy library here:
        # http://autodoc.dnanexus.com/bindings/python/current/dxpy_dxgtable.html

        for row in DX_APP_WIZARD_||_INPUT.iterate_rows(start_row, end_row):
            # Fill in code here to perform whatever computation is
            # necessary to process the row and compute the new row.
            #
            # *row* is an array where the first element is the row ID,
            # and the rest of the elements appear in the same order as
            # the GTable's column specification.  You can retrieve the
            # column specifications or names by using
            # DX_APP_WIZARD_||_INPUT.get_columns() or DX_APP_WIZARD_||_INPUT.get_col_names().

            new_row = []

            # The following line queues up the array new_row as a row
            # of data that should be added to the output GTable.
            # Queued rows will be flushed to the platform periodically.

            DX_APP_WIZARD_||_OUTPUT.add_row(new_row)

    # At the end of the "with" block, any queued rows for
    # DX_APP_WIZARD_||_OUTPUT will have been flushed to the platform.

@dxpy.entry_point("main")
def main(DX_APP_WIZARD_INPUT_SIGNATURE):
DX_APP_WIZARD_INITIALIZE_INPUTDX_APP_WIZARD_DOWNLOAD_ANY_FILES
    # First, create the output GTable that will contain your results.
    # NOTE: You must specify the columns and indices for a GTable when
    # you create it, and they are immutable thereafter.
    #
    # Note: If you are filtering a GTable or are otherwise happy with
    # using the same exact columns and indices as your input GTable,
    # you can easily initialize your new GTable as follows:
    #
    # DX_APP_WIZARD_||_OUTPUT = dxpy.new_dxgtable(init_from=DX_APP_WIZARD_||_INPUT)
    #
    # In the more general case, you may want to specify different
    # columns.  The following lines assume you would like to create a
    # GTable with a genomic range index, i.e. there is a string column
    # for chromosome names and two integer columns for low and high
    # coordinates.

    columns = [dxpy.DXGTable.make_column_desc("chr", "string"),
               dxpy.DXGTable.make_column_desc("lo", "int"),
               dxpy.DXGTable.make_column_desc("hi", "int"),
               dxpy.DXGTable.make_column_desc("somedata", "string")]
    DX_APP_WIZARD_||_OUTPUT = dxpy.new_dxgtable(columns=columns,
                                                          indices=[dxpy.DXGTable.genomic_range_index("chr", "lo", "hi")])

    # Split your input to be solved by the next stage of your app.
    # The following assumes you are splitting the input by giving
    # 100000 rows of a GenomicTable per subjob running the
    # "process" entry point.

    num_rows = DX_APP_WIZARD_||_INPUT.describe()["length"]

    subjobs = []
    for i in range(num_rows / row_chunk_size + (0 if num_rows % row_chunk_size == 0 else 1)):
        subjob_input = { "input_gtable_id": DX_APP_WIZARD_||_INPUT.get_id(),
                         "start_row": row_chunk_size * i,
                         "end_row": min(row_chunk_size * (i + 1), num_rows),
                         "output_gtable_id": DX_APP_WIZARD_||_OUTPUT.get_id()}
        subjobs.append(dxpy.new_dxjob(subjob_input, "process"))

    # The next line creates the job that will perform the
    # "postprocess" step of your app.  It assumes that you do not need
    # to aggregate any output from your "process" stages (other than
    # closing the output GTable), but you can add the output of those
    # stages to the input of your "postprocess" stage easily by adding
    # the following value as a field in the "fn_input" dict and adding
    # the parameter to your "postprocess" entry point.
    #
    #   fn_input={"process_outputs": [subjob.get_output_ref("output") for subjob in subjobs], ...}
    #
    # With no other input other than the output GTable ID for the
    # "postprocess" stage, we will force it to run only after all the
    # "process" stages have finished running by providing the list of
    # their DXJob handlers to the "depends_on" field (it accepts
    # either dxpy handlers or string IDs in the list).

    postprocess_job = dxpy.new_dxjob(fn_input={ "output_gtable_id": DX_APP_WIZARD_||_OUTPUT.get_id() },
                                     fn_name="postprocess",
                                     depends_on=subjobs)

    # If you would like to include any of the output fields from the
    # postprocess_job as the output of your app, you should return it
    # here using a job-based object reference.  If the output field is
    # called "answer", you can pass that on here as follows:
    #
    # return {"app_output_field": postprocess_job.get_output_ref("answer"), ...}
    #
    # Tip: you can include in your output at this point any open
    # objects (such as GTables) which are closed by a job that
    # finishes later.  The system will check to make sure that the
    # output object is closed and will attempt to clone it out as
    # output into the parent container only after all subjobs have
    # finished.

    output = {}
DX_APP_WIZARD_OUTPUT
    return output

dxpy.run()
