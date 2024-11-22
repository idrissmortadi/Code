from typing import List, Set

class Node:
    def __init__(self, id: str, labels: Set[str], properties: Set[str], edges_out=None, edges_in=None) -> None:
        self.id = id  # Store the original ID
        self._labels = labels
        self._proprety = properties
        self._out = edges_out
        self._in = edges_in

    def get_labels(self) -> Set[str]:
        return self._labels
    
    def get_properties(self) -> Set[str]:
        return self._proprety

    def get_proprety(self) -> Set[str]:
        return self._proprety

    def get_id(self) -> str:
        return self.id

    def __str__(self) -> str:
        return f"ID: {self.id} | Labels: {', '.join(sorted(self._labels))} | Properties: {', '.join(sorted(self._proprety))}"

    def __repr__(self) -> str:
        return self.__str__()

    def __eq__(self, other) -> bool:
        if not isinstance(other, Node):
            return False
        return (
            self.id == other.id and
            self._labels == other._labels and 
            self._proprety == other._proprety and
            self._out == other._out and
            self._in == other._in
        )

    def __hash__(self) -> int:
        return hash((self.id, frozenset(self._labels), frozenset(self._proprety)))
    
class Graph:
    def __init__(self, nodes = None) -> None:
        self._nodes = set()
        self._node_occurs = dict()
        self._labels = set()
        self._set_labels = set()
        self._proprety = set()

    def get_nodes(self) -> List[Node]:
        return self._nodes

    def add_node(self, x, n=1) -> None:
        if (x in self._nodes):
            self._node_occurs[x] += n
        else:
            self._nodes.add(x)
            self._node_occurs[x] = n
            for l in x.get_labels():
                self._labels.add(l)
            for p in x.get_proprety():
                self._proprety.add(p)
    
    def del_node(self, x):
        if x in self._nodes:
            self._nodes.pop(x)
        if x in self._node_occurs:
            del self._node_occurs[x]

    def distinct_node(self) -> Set[Node]:
        return self._nodes
    
    def get_sets_labels(self):
        s = list({"#".join(list(n.get_labels())) for n in self._nodes})
        return [set(x.split("#")) for x in s]

    def occurs(self, node):
        return self._node_occurs[node]

    def __str__(self) -> str:
        mot = ""
        for n in self._nodes:
            mot += str(n) + "\n"
        return mot

#------------------------------------------------------------------------------

import uuid

class Cluster:
    def __init__(self, name="") -> None:
        self._id = str(uuid.uuid4())  # Generate a unique ID
        self._name = name
        self._ref_node = None
        self._cutting_values = []
        self._nodes = dict()
        self._fils = []
        self._modification = 0
        self._sons_id = None

    def get_original_id(self):
        return self._id
    
    def get_nodes(self):
        return self._nodes

    def add_son(self, sous_cluster):
        self._fils.append(sous_cluster)

    def get_son(self):
        return self._fils

    def get_name(self):
        return self._name
    
    def add_node(self, node, n=1):
        if node in self._nodes:
            self._nodes[node] += n
        else:
            self._nodes[node] = n
    
    def get_sons_id(self):
        if self._sons_id == None:
            l = self.get_son()
            return {frozenset(cluster._nodes().items()) : l for cluster in l}
        else:
            return self._sons_id

    def get_number_node(self):
        return sum(self._nodes.values())
