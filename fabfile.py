from fabric.api import *

env.hosts = [
    "slice316.pcvm3-1.geni.case.edu",
#    "slice316.pcvm1-1.geni.it.cornell.edu",
    "slice316.pcvm3-1.instageni.metrodatacenter.com",
    "slice316.pcvm2-2.instageni.rnoc.gatech.edu",
    "slice316.pcvm3-2.instageni.illinois.edu",
#    "slice316.pcvm5-7.lan.sdn.uky.edu",
#    "slice316.pcvm3-1.instageni.lsu.edu",
#    "slice316.pcvm2-2.instageni.maxgigapop.net",
#    "slice316.pcvm1-1.instageni.iu.edu",
#    "slice316.pcvm3-4.instageni.rnet.missouri.edu",
#    "slice316.pcvm3-7.instageni.nps.edu",
#    "slice316.pcvm2-1.instageni.nysernet.org",
#    "slice316.pcvm3-11.genirack.nyu.edu",
#    "slice316.pcvm5-1.instageni.northwestern.edu",
#    "slice316.pcvm5-2.instageni.cs.princeton.edu",
#    "slice316.pcvm3-3.instageni.rutgers.edu",
#    "slice316.pcvm1-6.instageni.sox.net",
#    "slice316.pcvm3-1.instageni.stanford.edu",
#    "slice316.pcvm2-1.instageni.idre.ucla.edu",
#    "slice316.pcvm4-1.utahddc.geniracks.net",
#    "slice316.pcvm1-1.instageni.wisc.edu",
  ]

Replica = ["slice316.pcvm3-1.instageni.metrodatacenter.com",
           "slice316.pcvm3-2.instageni.illinois.edu"]
Coordinator = ["slice316.pcvm3-1.geni.case.edu"]
Client = ["slice316.pcvm2-2.instageni.rnoc.gatech.edu"]

env.key_filename="./id_rsa"
env.use_ssh_config = True
env.ssh_config_path = './ssh-config'
env.roledefs.update({'replica': Replica,
                     'coordinator': Coordinator,
                     'client': Client})

def pingtest():
    run('ping -c 3 www.yahoo.com')

def uptime():
    run('uptime')

def getip():
    run('ifconfig')

def getls():
    run('ls')


@parallel
@roles('replica')
def upload_replica():
    put('replica.py')

@roles('coordinator')
def upload_coordinator():
    put('coordinator.py')

@parallel
@roles('client')
def upload_client():
    put('client.py')



@parallel
@roles('replica')
def run_replica():
    run('python replica.py')

@roles('coordinator')
def run_coordinator():
    run('python coordinator.py')

@parallel
@roles('client')
def run_client():
    run('python client.py')


@parallel
@roles('replica')
def get_replicalog():
    get('replica.log')

@roles('coordinator')
def get_coordinatorlog():
    get('coordinator.log')


@parallel
@roles('replica')
def clean_replica():
    run('rm -f replica.log')
    run('rm -f replica.db')

@roles('coordinator')
def clean_coordinator():
    run('rm -f coordinator.log')


