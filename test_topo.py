from mininet.net import Mininet
from mininet.node import Controller, OVSSwitch, RemoteController
from mininet.cli import CLI
from mininet.log import setLogLevel, info

def topo():
    SWITCH_PROTOCOL = 'OpenFlow13'

    info('Creating Network \n')
    net = Mininet(controller=RemoteController, switch=OVSSwitch)

    info('Adding Controller \n')
    c0 = net.addController('c0', ip='127.0.0.1', port=6653)
    
    info('Adding Hosts \n')
    h1 = net.addHost('h1')
    h2 = net.addHost('h2')
    h3 = net.addHost('h3')
    h4 = net.addHost('h4')
    
    info('Adding Switches \n')
    s1 = net.addSwitch('s1', protocols=SWITCH_PROTOCOL)
    s2 = net.addSwitch('s2', protocols=SWITCH_PROTOCOL)
    s3 = net.addSwitch('s3', protocols=SWITCH_PROTOCOL)
    s4 = net.addSwitch('s4', protocols=SWITCH_PROTOCOL)

    info('Adding Links \n')
    net.addLink(h1, s1)
    net.addLink(h2, s2)
    net.addLink(h3, s3)
    net.addLink(h4, s4)
    net.addLink(s1, s2)
    net.addLink(s2, s3)
    net.addLink(s3, s4)
    net.addLink(s4, s1)

    info('Starting Network \n')
    s1.start([c0])
    s2.start([c0])
    s3.start([c0])
    s4.start([c0])

    net.start()
    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    topo()

