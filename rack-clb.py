#!/usr/bin/python

def create(args):
  clb_nodes = []
  for node in set(args.nodes):
    server = cs.servers.get(node)
    private_ip = server.networks['private'][0]
    clb_node = clb.Node(address=private_ip, port=args.port, condition='ENABLED')
    clb_nodes.append(clb_node)
  vip = clb.VirtualIP(type='PUBLIC')
  lb = clb.create(args.name, port=args.port, protocol='HTTP',nodes=clb_nodes, virtual_ips=[vip],algorithm=args.algorithm)
  print 'Cloud Load Balancer has been created successfully. Details for the Load Balancer are below.'
  print '\tName:\t\t',lb.name
  print '\tID:\t\t',lb.id
  print '\tPublic IP:\t',lb.sourceAddresses['ipv4Public']
  print '\tPort:\t\t',lb.port
  print '\tAlgorithm:\t',lb.algorithm
  print '\tNodes:'
  for node in lb.nodes:
    print '\t\t',node.address

  
def add_server(args):
  if len(args.nodes) < 1:
    print "ERROR: you need to specify at least one node to add to the Load Balancer"
    sys.exit(1)
  lb = clb.get(args.id)
  clb_nodes = []
  for node in set(args.nodes):
    server = cs.servers.get(node)
    private_ip = server.networks['private'][0]
    clb_node = clb.Node(address=private_ip, port=lb.port, condition='ENABLED')
    clb_nodes.append(clb_node)
  lb.add_nodes(clb_nodes)
  while lb.status == 'ACTIVE':
    lb = clb.get(args.id)
  print 'Nodes have been added to Cloud Load Balancer successfully. Details for the Load Balancer are below.'
  print '\tName:\t\t',lb.name
  print '\tID:\t\t',lb.id
  print '\tPublic IP:\t',lb.sourceAddresses['ipv4Public']
  print '\tPort:\t\t',lb.port
  print '\tAlgorithm:\t',lb.algorithm
  print '\tStatus:\t\t',lb.status
  print '\tNodes:'
  for node in lb.nodes:
    print '\t\t',node.address
  

import argparse

parser = argparse.ArgumentParser(description='Manage Rackspace Cloud LoadBalancers')

parent_parser = argparse.ArgumentParser(add_help=False)
parent_parser.add_argument('-f','--file',help='the file containing Rackspace Cloud API credentials (default: ~/.pyrax/auth)',default='~/.pyrax/auth')
parent_parser.add_argument('-r','--region',choices=['DFW','ORD','LON'],default='DFW',help='the region in which to manage Cloud Load Balancers (default: DFW)')
parent_parser.add_argument('-n','--nodes',help='IDs of nodes to be added to the Cloud Load Balancer',nargs='*',default=[])

sp = parser.add_subparsers(title='Actions')

sp_create = sp.add_parser('create',help='create a Cloud LoadBalancer',parents=[parent_parser])
sp_create.add_argument('name',help='name of the new Load Balancer to create')
sp_create.add_argument('-p','--port',help='the port at which the new Cloud Load Balancer will be listening (default: 80)',default=80,type=int)
sp_create.add_argument('-a','--algorithm',choices=['LEAST_CONNECTIONS', 'RANDOM', 'ROUND_ROBIN', 'WEIGHTED_LEAST_CONNECTIONS', 'WEIGHTED_ROUND_ROBIN'],help='algoithm to use for Load Balancing (default: RANDOM)',default='RANDOM')
sp_create.set_defaults(func=create)

sp_add_server = sp.add_parser('add_server',help='add a server to a Cloud LoadBalancer',parents=[parent_parser])
sp_add_server.add_argument('id',type=int,help='ID of the Cloud Load Balancer to add nodes to')
sp_add_server.set_defaults(func=add_server)


args = parser.parse_args()

import pyrax
import os
import sys
import time

pyrax.set_setting('identity_type','rackspace')
pyrax.set_setting('region',args.region)
pyrax.set_credential_file(os.path.expanduser(args.file))

cs = pyrax.cloudservers
clb = pyrax.cloud_loadbalancers


args.func(args)
