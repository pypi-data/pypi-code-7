"""Split files or tasks for distributed processing across multiple machines.

This tackles parallel work within the context of a program, where we split
based on input records like fastq or across regions like chromosomes in a
BAM file. Following splitting, individual records and run and then combined
back into a summarized output file.

This provides a framework for that process, making it easier to utilize with
splitting specific code.
"""
import collections

from bcbio import utils

def grouped_parallel_split_combine(args, split_fn, group_fn, parallel_fn,
                                   parallel_name, combine_name,
                                   file_key, combine_arg_keys,
                                   split_outfile_i=-1):
    """Parallel split runner that allows grouping of samples during processing.

    This builds on parallel_split_combine to provide the additional ability to
    group samples and subsequently split them back apart. This allows analysis
    of related samples together. In addition to the arguments documented in
    parallel_split_combine, this needs:

    group_fn: A function that groups samples together given their configuration
      details.
    """
    grouped_args = group_fn(args)
    split_args, combine_map, finished_out, extras = _get_split_tasks(grouped_args, split_fn, file_key,
                                                                     split_outfile_i)
    final_output = parallel_fn(parallel_name, split_args)
    combine_args, final_args = _organize_output(final_output, combine_map,
                                                file_key, combine_arg_keys)
    parallel_fn(combine_name, combine_args)
    return finished_out + final_args + extras

def parallel_split_combine(args, split_fn, parallel_fn,
                           parallel_name, combiner,
                           file_key, combine_arg_keys, split_outfile_i=-1):
    """Split, run split items in parallel then combine to output file.

    split_fn: Split an input file into parts for processing. Returns
      the name of the combined output file along with the individual
      split output names and arguments for the parallel function.
    parallel_fn: Reference to run_parallel function that will run
      single core, multicore, or distributed as needed.
    parallel_name: The name of the function, defined in
      bcbio.distributed.tasks/multitasks/ipythontasks to run in parallel.
    combiner: The name of the function, also from tasks, that combines
      the split output files into a final ready to run file. Can also
      be a callable function if combining is delayed.
    split_outfile_i: the location of the output file in the arguments
      generated by the split function. Defaults to the last item in the list.
    """
    args = [x[0] for x in args]
    split_args, combine_map, finished_out, extras = _get_split_tasks(args, split_fn, file_key,
                                                                     split_outfile_i)
    split_output = parallel_fn(parallel_name, split_args)
    if isinstance(combiner, basestring):
        combine_args, final_args = _organize_output(split_output, combine_map,
                                                    file_key, combine_arg_keys)
        parallel_fn(combiner, combine_args)
    elif callable(combiner):
        final_args = combiner(split_output, combine_map, file_key)
    return finished_out + final_args + extras

def _get_extra_args(extra_args, arg_keys):
    """Retrieve extra arguments to pass along to combine function.

    Special cases like reference files and configuration information
    are passed as single items, the rest as lists mapping to each data
    item combined.
    """
    # XXX back compatible hack -- should have a way to specify these.
    single_keys = set(["sam_ref", "config"])
    out = []
    for i, arg_key in enumerate(arg_keys):
        vals = [xs[i] for xs in extra_args]
        if arg_key in single_keys:
            out.append(vals[-1])
        else:
            out.append(vals)
    return out

def _organize_output(output, combine_map, file_key, combine_arg_keys):
    """Combine output details for parallelization.

    file_key is the key name of the output file used in merging. We extract
    this file from the output data.

    combine_arg_keys are extra items to pass along to the combine function.
    """
    out_map = collections.defaultdict(list)
    extra_args = collections.defaultdict(list)
    final_args = collections.OrderedDict()
    extras = []
    for data in output:
        cur_file = data.get(file_key)
        if not cur_file:
            extras.append([data])
        else:
            cur_out = combine_map[cur_file]
            out_map[cur_out].append(cur_file)
            extra_args[cur_out].append([data[x] for x in combine_arg_keys])
            data[file_key] = cur_out
            if cur_out not in final_args:
                final_args[cur_out] = [data]
            else:
                extras.append([data])
    combine_args = [[v, k] + _get_extra_args(extra_args[k], combine_arg_keys)
                    for (k, v) in out_map.iteritems()]
    return combine_args, final_args.values() + extras

def _get_split_tasks(args, split_fn, file_key, outfile_i=-1):
    """Split up input files and arguments, returning arguments for parallel processing.

    outfile_i specifies the location of the output file in the arguments to
    the processing function. Defaults to the last item in the list.
    """
    split_args = []
    combine_map = {}
    finished_map = collections.OrderedDict()
    extras = []
    for data in args:
        out_final, out_parts = split_fn(data)
        for parts in out_parts:
            split_args.append([utils.deepish_copy(data)] + list(parts))
        for part_file in [x[outfile_i] for x in out_parts]:
            combine_map[part_file] = out_final
        if len(out_parts) == 0:
            if out_final is not None:
                if out_final not in finished_map:
                    data[file_key] = out_final
                    finished_map[out_final] = [data]
                else:
                    extras.append([data])
            else:
                extras.append([data])
    return split_args, combine_map, finished_map.values(), extras
