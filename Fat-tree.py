#!/usr/bin/env python

from mininet.net import Mininet
from mininet.node import Controller, RemoteController, OVSController
from mininet.node import CPULimitedHost, Host, Node
from mininet.node import OVSKernelSwitch, UserSwitch
from mininet.node import IVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink, Intf
from subprocess import call

def myNetwork():

    net = Mininet( topo=None,
                   build=False,
                   ipBase='10.0.0.0/8')

    info( '*** Adding controller\n' )
    c0=net.addController(name='c0',
                      controller=RemoteController, #controller=Controller,
                      protocol='tcp',
                      port=6633)
    #Agregado de codigo
    k=4
    num_pod=k       # número de Pods
    num_host=(k/2)  # numero de host por cada switch edge        
    num_edge=(k/2)  # Número de Edge Switch en Cada pod
    num_agg=(k/2)   # Número de Agg Switch en cada pod
    num_group=(k/2) # Numero de grupos de core Switches
    num_core=(k/2)  # Número de core switches en cada grupo
    total_host=k*k*k/4
    print(total_host)
    
    group_core = [[] for _ in range (int(num_group))]
    pod_agg = [[] for _ in range (int(num_pod))]
    pod_edge = [[] for _ in range (int(num_pod))]
    host = [[[] for _ in range (int(num_edge))] for _ in range (int(num_pod))]
    
    
    s=0 #numeración de Switches
    h=0 #numeración de host
    TotalSwitches=0
    #Fin de agregado de codigo

    info( '*** Add switches\n')
    
    info( '**** Creación de Core Switches\n')
    
    for g in range(int(num_group)):
        for c in range(int(num_core)):
            s=s+1
            group_core[g].append(net.addSwitch('s'+str(s), cls=OVSKernelSwitch, protocols='OpenFlow13'))
    

    info( '**** Creación de Aggregate Switches\n')
    
    for p in range(int(num_pod)):
        for a in range(int(num_agg)):
            s=s+1
            pod_agg[p].append(net.addSwitch('s'+str(s), cls=OVSKernelSwitch, protocols='OpenFlow13'))
         
    
    info( '**** Creación de Edge Switches\n')
    
    for p in range(int(num_pod)):
        for a in range(int(num_edge)):
            s=s+1
            pod_edge[p].append(net.addSwitch('s'+str(s), cls=OVSKernelSwitch, protocols='OpenFlow13'))
    

    info( '*** Add hosts\n')
    
    for p in range(int(num_pod)):
        for e in range(int(num_edge)):
            for nh in range(int(num_host)):
                h=h+1 #para la numeración de los host
                host[p][e].append(net.addHost('h'+str(h), cls=Host, ip='10.'+str(p)+'.'+str(e)+'.'+str(nh+1), defaultRoute=None))
            

    info( '*** Add links\n')
    
    info( '*** Conectando Core a Aggregate Switches\n')
    
    for g in range(int(num_group)):
        for c in range(int(num_core)):
            for h in range(int(num_pod)):
                imprimirConexion = net.addLink(group_core[g][c], pod_agg[h][g]) #Realiza la conexión y lo guardo para mostrar por pantalla
                print("enlace :",imprimirConexion) # Por tema de validación de conexiones
    
    
    info( '*** Conectando Aggregate a Edge Switches\n')
    
    for p in range(int(num_pod)):
        for a in range(int(num_agg)):
            for e in range(int(num_edge)):
                imprimirConexion = net.addLink(pod_agg[p][a], pod_edge[p][e]) #Realiza la conexión y lo guardo para mostrar por pantalla
                print("enlace :",imprimirConexion) # Por tema de validación de conexiones
                
    
    info( '*** Conectando Edge Switches a Hosts\n')
    
    for p in range(int(num_pod)):
        for e in range(int(num_edge)):
            for h in range(int(num_host)):
                imprimirConexion = net.addLink(host[p][e][h], pod_edge[p][e]) #Realiza la conexión y lo guardo para mostrar por pantalla
                print("enlace :",imprimirConexion) # Por tema de validación de conexiones
              

    info( '*** Starting network\n')
    net.build()
    info( '*** Starting controllers\n')
    for controller in net.controllers:
        controller.start()

    info( '*** Starting switches\n')
    
    TotalSwitches = s
    print("Total Switches ", TotalSwitches)
    
    for i in range(TotalSwitches):
        net.get('s'+str(i+1)).start([c0])
        print('s'+str(i+1))
    

    info( '*** Post configure switches and hosts\n')
    
    info( '*** Iniciando aplicaciones en Host\n')
    
    hostApp=[]
    
    for i in range(int(total_host)):
        hostApp.append(net.get('h'+str(i+1)))
    
    for i in range(int(total_host)):
        hostApp[i].cmd('tcpdump outbound -i '+'h'+str(i+1)+'-eth0 -w h'+str(i+1)+'Eth0-out.pcap &')
        hostApp[i].cmd('tcpdump inbound -i '+'h'+str(i+1)+'-eth0 -w h'+str(i+1)+'Eth0-in.pcap &')

    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    myNetwork()

