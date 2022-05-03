import networkx
from dataclasses import make_dataclass
from collections import defaultdict
from math import log2
import pandas as pd
import pyreadstat

NodeItem = make_dataclass("NodeItem", [("ID", str),
                                       ("keywords", int),
                                       ("retweets",int),
                                       ("tweets",int),
                                       ("in_centrality", float),
                                       ("out_centrality", float),
                                       ("retweets_normalized", int)])

nodes_analyzed=dict()
relevant_nodes=set()

G=networkx.DiGraph()
with open("details.txt","r") as details_file, \
     open("list.txt","r") as edges_file:
    lines=edges_file.readlines()
    #read account details
    for line in details_file.readlines():
        details=line.strip().split()
        keywords=int(details[1])
        node=NodeItem(details[0],keywords,0,0,0,0,0)
        if float(details[2])==0:
            continue
        node.tweets=float(details[2])
        node.retweets=int(float(details[3]))
        node.retweets_normalized=node.retweets/node.tweets*400
        nodes_analyzed[node.ID]=node
        if keywords>=5:
            relevant_nodes.add(node.ID)

#add accounts deemed irrelevant but which are likely to be relevant
deemed_irrelevant=defaultdict(int)
for line in lines:
    edge=line.strip().split()
    if edge[0] in relevant_nodes and edge[1] not in relevant_nodes:
        if edge[1] in nodes_analyzed:
            deemed_irrelevant[edge[1]]+=1
            
deemed_irrelevant_sorted=sorted(deemed_irrelevant.items(),
                                 key=lambda kv:kv[1],
                                 reverse=True)
for k,v in deemed_irrelevant_sorted[:50]:
    relevant_nodes.add(k)

#add nodes
for line in lines:
    edge=line.strip().split()
    if edge[0] in relevant_nodes and edge[1] in relevant_nodes:
        G.add_edge(edge[0],edge[1],weight=log2(float(edge[2])))

multiply_constant=1

#write graph to gephi
networkx.set_node_attributes(G,0,"influence")
for x in G.nodes:
    G.nodes[x]["influence"]=nodes_analyzed[x].retweets_normalized
    #print(x,G.nodes[x]["influence"])
networkx.write_gexf(G,"data.gexf")

#in-eigenvector centrality
in_centrality=networkx.eigenvector_centrality(G,max_iter=100)
in_centrality=sorted(in_centrality.items(),key=lambda kv:kv[1],reverse=True)
for ID,centrality in in_centrality:
    nodes_analyzed[ID].in_centrality=centrality*multiply_constant

#out-eigenvector centrality
G=G.reverse()
out_centrality=networkx.eigenvector_centrality(G,max_iter=100)
out_centrality=sorted(out_centrality.items(),key=lambda kv:kv[1],reverse=True)
for ID,centrality in out_centrality:
    nodes_analyzed[ID].out_centrality=centrality*multiply_constant

data=pd.DataFrame([nodes_analyzed[x] for x in relevant_nodes])
print(data)
pyreadstat.write_sav(data, "data.sav")
