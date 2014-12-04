
from distopt import cvxpy_expr
from distopt import data_store_pb2
from distopt import master_pb2
from distopt import rpc

HOST = "master.distopt.com"
MASTER_PORT = "8000"
DATA_STORE_PORT = "8002"

master_cache = {}

def get_master(host):
    if not host in master_cache:
        master_cache[host] = master_pb2.Master_Stub(
            rpc.Channel(host, MASTER_PORT))
    return master_cache[host]

def solve(problem, host=HOST):
    request = master_pb2.SolveRequest()
    request.params.tolerance = 1e-3
    request.params.max_iterations = 200
    cvxpy_expr.convert_problem(problem, request.problem)
    return get_master(host).Solve(rpc.RPC(), request)
