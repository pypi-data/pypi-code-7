"""Gunny: A directed acyclic graph executor

See LICENSE.txt for licensing information

"""
import networkx as nx
import sarge
import threading
from queue import Queue

__version__ = '1.0.0b1'

DEFAULT_ASYNC_JOBS = 1


class States:
    """Asynchronous job state enumeration

    """
    waiting = 0
    running = 1
    complete = 2

states = States


class Status:
    """Asynchronous job exit status enumeration

    """
    passed = 0
    failed = 1

status = Status


class Traverse:
    """Asynchronous job executor call graph direction enumeration

    """
    given = 0
    up = 1
    down = 2

traverse = Traverse


class Job(object):
    def __init__(self, name, command, state):
        self.name = name
        self.command = command
        self.state = state


def run_up(dag, **kw):
    run(dag, direction=traverse.up, **kw)


def run_down(dag, **kw):
    run(dag, direction=traverse.down, **kw)


def compose_stream(dag, nodes, fn):
    graphs = []
    for n in nodes:
        subset = fn(dag, n)
        subset.add(n)
        graphs.append(dag.subgraph(subset))
    return nx.compose_all(graphs)


def downstream(dag, nodes):
    return compose_stream(dag, nodes, nx.ancestors)


def upstream(dag, nodes):
    return compose_stream(dag, nodes, nx.descendants)


def run(dag, nodes=None, direction=traverse.given, async_jobs=DEFAULT_ASYNC_JOBS, state_callback=None, **kw):

    def compose_call_graph():
        graph = {traverse.given: nx.subgraph,
                   traverse.down: downstream,
                   traverse.up: upstream}
        return graph[direction](dag, nodes)

    def change_state(job, new_state):
        job.state = new_state
        if state_callback:
            state_callback(job)

    def is_upstream_complete(n):
        for n in nx.descendants(call_graph, n):
            if call_graph.node[n]['gunny'].state != states.complete:
                return False
        return True

    def run_ready():
        for node_id in reversed(ordered_calls):
            node = call_graph.node[node_id]
            job = node['gunny']
            if active_jobs[0] == async_jobs:
                break
            elif job.state == states.waiting and is_upstream_complete(node_id):
                thread = threading.Thread(target=execute_job, args=(job, kw))
                active_jobs[0] += 1
                thread.start()

    def execute_job(job, job_kw):
        change_state(job, states.running)
        job.pipeline = sarge.run(job.command, **job_kw)
        job.pipeline.wait()
        change_state(job, states.complete)
        exit_queue.put(job)

    nodes = nodes if nodes else dag.nodes_iter()
    call_graph = compose_call_graph()

    for n in dag.nodes_iter():
        dag.node[n]['gunny'] = Job(n, dag.node[n]['gunny'], states.waiting)

    ordered_calls = nx.topological_sort(call_graph)
    kw['async'] = True
    active_jobs = 0
    exit_queue = Queue()
    active_jobs = [0]
    while True:
        if ordered_calls:
            run_ready()
            ordered_calls.remove(exit_queue.get().name)
            active_jobs[0] -= 1
        else:
            break
