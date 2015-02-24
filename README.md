# 2PC-Project

2 Phase Commit Project for UVic CSC 562 - Distributed Computing. This project runs on GEE using Python 2.7 (with built-in sqlite3 and XML-RPC).

## Setup

See the included fabfile for getting it to run on GEE. Here is a brief list of important commands:

upload_replica/coordinator/client - uploads python source code to slicelet

run_replica/coordinator/client - runs the python code on the slicelet

get_replicalog/coordinatorlog - downloads relica.log and coordinator.log to your computer

clean_replica/coordinator - cleans replica/coordinator of db and log files

## Code Structure

Source code is organized into three source files.

replica.py:
Source code for the replica. Major interfaces include replica_put(), replica_del() and replica_get() for phase 1 of 2PC; replica_commit() and replica_abort() for phase 2 of 2PC.

coordinator.py:
Source code for the coordinator. Major interfaces exposed to the client are coord_put(), coord_del(), and coord_get(). It also exposes a decision_request() interface to the replica for error recovery.

client.py:
Source code for the client. It connects to the coordinator and does a few test commands.


## Error Recovery

If the coordinator fails, it will read the coordinator.log to determine the last instruction. The last instruction is a commit then it send tells all replicas to commit, else it sends abort to all replicas.

If a replica fails, it checks the replica.log for the last instruction. It aborts if the last instruction is not yes, else it contacts the coordinator and passes the transaction_id for the decision request.


## Test Cases

1. Making sure sample instructions in client.py works properly.
2. Manually shutting down a replica, editing the replica.log so it enters recovery mode when it restarts and making sure it contacts the coordinator properly.


## Known Issues/Future Work

- Timeouts are not currently implemented, a node failure causes transactions to block until it is recovered.
- Replica can only contact coordinator during recovery, in future should add support for contacting other replicas.
- Did not test coordinator failures.
- Did not test running with multiple clients.
