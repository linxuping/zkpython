# coding: utf-8
# zktest.py
'''
这个简单的demo所做的事情，就是通过在zookeeper的/app/workers节点下建立临时的子节点( flags=zookeeper.EPHEMERAL | zookeeper.SEQUENCE )，每次create完成之后检查自己是不是在最小的MASTERS_NUM(例子中为1，即单master)里。如果是的话，作为master运行，否则的话，作为slave运行。

这样的话，当我们的master挂掉以后，与zookeeper之间的连接也会中断，过了指定的TIMEOUT以后，master之前在worker下的子节点就会被删除，于是slave节点之前设置的watcher会被触发，再次检查自己是否为master，如果是的话则完成切换。

zkCli.sh
[zk: localhost:2181(CONNECTED) 8] ls /app/workers 
[worker0000000007, worker0000000006]
'''

import logging
from os.path import basename, join

from zkclient import ZKClient, zookeeper, watchmethod

logging.basicConfig(
    level = logging.DEBUG,
    format = "[%(asctime)s] %(levelname)-8s %(message)s"
)

log = logging

class GJZookeeper(object):

    ZK_HOST = "localhost:2181"
    ROOT = "/app"
    WORKERS_PATH = join(ROOT, "workers")
    MASTERS_NUM = 1
    TIMEOUT = 10000

    def __init__(self, verbose = True):
        self.VERBOSE = verbose
        self.masters = []
        self.is_master = False
        self.path = None

        self.zk = ZKClient(self.ZK_HOST, timeout = self.TIMEOUT)
        self.say("login ok!")
        # init
        self.__init_zk()
        # register
        self.register()

    def __init_zk(self):
        """
        create the zookeeper node if not exist
        """
        nodes = (self.ROOT, self.WORKERS_PATH)
        for node in nodes:
            if not self.zk.exists(node):
                try:
                    self.zk.create(node, "")
                except:
                    pass

    @property
    def is_slave(self):
        return not self.is_master

    def register(self):
        """
        register a node for this worker
        """
        self.path = self.zk.create(self.WORKERS_PATH + "/worker", "1", flags=zookeeper.EPHEMERAL | zookeeper.SEQUENCE)
        self.path = basename(self.path)
        self.say("register ok! I'm %s" % self.path)
        # check who is the master
        self.get_master()

    def get_master(self):
        """
        get children, and check who is the smallest child
        """
        @watchmethod
        def watcher(event):
            self.say("child changed, try to get master again.")
            self.get_master()

        children = self.zk.get_children(self.WORKERS_PATH, watcher)
        children.sort()
        self.say("%s's children: %s" % (self.WORKERS_PATH, children))

        # check if I'm master
        self.masters = children[:self.MASTERS_NUM]
        if self.path in self.masters:
            self.is_master = True
            self.say("I've become master!")
        else:
            self.say("%s is masters, I'm slave" % self.masters)


    def say(self, msg):
        """
        print messages to screen
        """
        if self.VERBOSE:
            if self.path:
                if self.is_master:
                    log.info("[ %s(%s) ] %s" % (self.path, "master" , msg))
                else:
                    log.info("[ %s(%s) ] %s" % (self.path, "slave", msg))
            else:
                log.info(msg)

def main():
    gj_zookeeper = GJZookeeper()

if __name__ == "__main__":
    main()
    import time
    time.sleep(1000)

