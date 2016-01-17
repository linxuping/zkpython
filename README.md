wget http://apache.claz.org/zookeeper/zookeeper-3.4.6/zookeeper-3.4.6.tar.gz    pip  install zkpython
cd zookeeper-3.3.4/  
bin/zkServer.sh start    进程:QuorumPeerMain  zookeeper 集群安装（单点与分布式成功安装）摘录
对于客户端来说，ZooKeeper是一个整体（ensemble），连接到ZooKeeper集群实际上感觉在独享整个集群的服务，所以，你可以在任何一个结点上建立到服务集群的连接

problems:
1、客户端连接zookeeper集群时如何才能避开失效的服务器

