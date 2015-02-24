
import os.path
import sys
import sqlite3 as lite
import SimpleXMLRPCServer
import xmlrpclib

class Replica(object):
    def __init__(self):
        self.name = "replica"

        try:
            con = lite.connect(self.name + ".db")
            self.con = con

            if os.path.isfile(self.name + '.log'):
                self.f = open(self.name + '.log', 'a')
                self.recover()
            else:
                self.f = open(self.name + '.log', 'a')
                cur = con.cursor()
                cur.execute("DROP TABLE IF EXISTS TestTable")
                cur.execute("CREATE TABLE TestTable(id INT, data TEXT)")
                con.commit()

        except lite.Error, e:
            print "Error %s: " % e.args[0]
            sys.exit(1)

        finally:
            if con:
                con.close()

    def recover(self):
        f = open(self.name + '.log', 'r')
        lastline = ""
        currentline = ""

        for line in f.readlines():
            lastline = currentline
            currentline = line.strip()

        last_transaction = currentline.split(" ")

        if last_transaction[0] == "yes":
            tid = int(last_transaction[1])
            participants = last_transaction[2].split(",")
            c = participants[0]
            self.get_decision(tid, c)

        elif last_transaction[0] == "abort":
            con = lite.connect(self.name + ".db")
            if con:
                con.rollback()
                con.close()
        else:
            con = lite.connect(self.name + ".db")
            if con:
                con.rollback()
                con.close()

    def get_decision(self, tid, c):
        coordinator = xmlrpclib.Server(c, allow_none=True)
        result = coordinator.decision_request(tid)
        if result == 1:
            self.con = lite.connect(self.name + ".db")
            self.replica_commit()
        else:
            self.con = lite.connect(self.name + ".db")
            self.replica_abort()


    def replica_put(self, tid, p, k, v):
        vote = 0
        try:
            con = lite.connect(self.name + ".db")
            self.con = con
            cur = con.cursor()
            cur.execute("INSERT INTO TestTable VALUES(?, ?)", (k , v))
            vote = 1
            self.f.write("yes " + str(tid) + " "
                         + ",".join(str(x) for x in p) + "\n")
            self.f.flush()

        except lite.Error, e:
            print "Error %s: " % e.args[0]
            if con:
                con.close()
            self.f.write("abort\n");
            self.f.flush()

        return vote


    def replica_del(self, tid, p, k):
        vote = 0
        try:
            con = lite.connect(self.name + ".db")
            self.con = con
            cur = con.cursor()
            cur.execute("DELETE FROM TestTable WHERE id=?", str(k))
            vote = 1
            self.f.write("yes " + str(tid) + " "
                         + ",".join(str(x) for x in p) + "\n")
            self.f.flush()

        except lite.Error, e:
            print "Error %s: " % e.args[0]
            if con:
                con.close()
            self.f.write("abort\n");
            self.f.flush()

        return vote


    def replica_get(self, k):
        data = "Error"
        try:
            con = lite.connect(self.name + ".db")
            self.con = con
            cur = con.cursor()
            cur.execute("SELECT data FROM TestTable WHERE id=?", str(k))

            data = cur.fetchone()
            con.close()

        except lite.Error, e:
            print "Error %s: " % e.args[0]
            if con:
                con.close()

        return data


    def replica_commit(self):
        con = self.con
        if con:
            con.commit()
            con.close()
            self.f.write("commit\n")
            self.f.flush()

    def replica_abort(self):
        con = self.con
        if con:
            con.rollback()
            con.close()
            self.f.write("abort\n")
            self.f.flush()


def main():
    replica = Replica()
    server = SimpleXMLRPCServer.SimpleXMLRPCServer(("", 8001),
                            allow_none=True)
    server.register_instance(replica)
    print("Replica ready.")
    server.serve_forever()


if __name__ == "__main__":
   main()

