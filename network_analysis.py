import networkx
from dataclasses import dataclass
from collections import defaultdict
from math import log2

class NodeItem:
    ID: str
    keywords: int
    influence:int

nodes_analyzed=dict()
relevant_nodes=set()

G=networkx.DiGraph()
with open("details.txt","r") as details_file, \
     open("list.txt","r") as edges_file:

    #read account details
    for line in details_file.readlines():
        details=line.strip().split()
        keywords=int(details[1])
        node=NodeItem()
        node.ID=details[0]
        node.keywords=keywords
        if float(details[2])==0:
            continue
        node.influence=int(float(details[3]))
        nodes_analyzed[node.ID]=node
        if keywords>=5:
            relevant_nodes.add(node.ID)

    #add accounts deemed irrelevant but which are likely to be relevant
    deemed_irrelevant=defaultdict(int)
    lines=edges_file.readlines()
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

#in-eigenvector centrality
in_centrality=networkx.eigenvector_centrality(G,max_iter=100)
in_centrality=sorted(in_centrality.items(),key=lambda kv:kv[1],reverse=True)
print("in-eigenvector centrality")
for ID,centrality in in_centrality[:50]:
    print(ID,centrality,nodes_analyzed[ID].influence)

#out-eigenvector centrality
G=G.reverse()
print()
out_centrality=networkx.eigenvector_centrality(G,max_iter=100)
out_centrality=sorted(out_centrality.items(),key=lambda kv:kv[1],reverse=True)
print("out-eigenvector centrality")
for ID,centrality in out_centrality[:50]:
    print(ID,centrality,nodes_analyzed[ID].influence)
