
import os.path
import random
import SimpleXMLRPCServer
import xmlrpclib

class Coordinator(object):
    def __init__(self):
        self.name = "http://localhost:8000"
        self.replicas_name = ["http://localhost:8001"]
        self.replicas = []
        self.tid = 0

        if os.path.isfile('coordinator.log'):
            self.decision_request(5)
            self.recover()
            
        self.f = open('coordinator.log', 'a')


    def recover(self):
        f = open('coordinator.log', 'r')
        lastline = ""
        currentline = ""

        for line in f.readlines():
            lastline = currentline
            currentline = line

            last_transaction = currentline.split(" ")
            if last_transaction[0] == "start-2PC":
                self.tid = int(last_transaction[1])

        if currentline == "commit":
            for r in self.replicas:
                r.replica_commit()
        elif currentline == "abort":
            for r in self.replicas:
                r.replica_abort()
        else:
            for r in self.replicas:
                r.replica_abort()

    def decision_request(self, tid):
        f = open('coordinator.log', 'r')

        result = 0

        lastline = ""
        currentline = ""

        for line in f.readlines():
            lastline = currentline
            currentline = line.strip()

            last_transaction = lastline.split(" ")

            if last_transaction[0] == "start-2PC":
                if int(tid) == int(last_transaction[1]):
                    if currentline == "commit":
                        result = 1
                    break

        return result



    def coord_put(self, k, v):
        self.tid += 1
        self.f.write("start-2PC " + str(self.tid) + " "
                     + ",".join(str(r) for r in self.replicas_name) + "\n");
        self.f.flush()
        vote = 1

        for r, r_name in zip(self.replicas, self.replicas_name):
            r_list = list(self.replicas_name)
            r_list.remove(r_name)
            p = [self.name] + r_list
            if r.replica_put(self.tid, p, k, v) == 0:
                vote = 0

        if vote == 1:
            self.f.write("commit\n")
            self.f.flush()
            for r in self.replicas:
                r.replica_commit()
        else:
            self.f.write("abort\n")
            self.f.flush()
            for r in self.replicas:
                r.replica_abort()


    def coord_del(self, k):
        self.tid += 1
        self.f.write("start-2PC " + str(self.tid) + " "
                     + ",".join(str(r) for r in self.replicas_name) + "\n");
        self.f.flush()
        vote = 1

        for r, r_name in zip(self.replicas, self.replicas_name):
            r_list = list(self.replicas_name)
            r_list.remove(r_name)
            p = [self.name] + r_list
            if r.replica_del(self.tid, p, k) == 0:
                vote = 0

        if vote == 1:
            self.f.write("commit\n")
            self.f.flush()
            for r in self.replicas:
                r.replica_commit()
        else:
            self.f.write("abort\n")
            self.f.flush()
            for r in self.replicas:
                r.replica_abort()


    def coord_get(self, k):
        return random.choice(self.replicas).replica_get(k)
        
        

def main():
    coordinator = Coordinator()
    server = SimpleXMLRPCServer.SimpleXMLRPCServer(("", 8000),
                            allow_none=True)
    server.register_instance(coordinator)

    for name in coordinator.replicas_name:
        replica = xmlrpclib.Server(name, allow_none=True)
        coordinator.replicas.append(replica)

    print("Coordinator ready.")
    server.serve_forever()

if __name__ == "__main__":
    main()

