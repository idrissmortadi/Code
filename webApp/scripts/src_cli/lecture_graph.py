""" Step 1 : Preprocessing data """

# Imports
from termcolor import colored

# File import
from .debug import printb
from .node import Graph, Node
from time import time


def lecture_graph(driver, edge):
    with driver.session() as session:

        # We do one query to get all differents set of labels
        print(colored("Querying neo4j to get a part of the graph:", "yellow"))
        nodes = session.run(
            "MATCH(n) \
            RETURN DISTINCT id(n) AS id, labels(n), keys(n), COUNT(n)"
        )

        graph = Graph()
        for node in nodes:
            node_id = str(node["id"])
            labels = set(node["labels(n)"])
            properties = set(node["keys(n)"])
            count = node["COUNT(n)"]
            n = Node(node_id, labels, properties)

            graph.add_node(n, count)

        print(colored("Done.", "green"))
        printb(graph)

        edges = None
        if edge:
            print(colored("Querying neo4j to get all the edges:", "yellow"))
            query = "MATCH (n)-[r]->(m) \
                    RETURN DISTINCT id(n) AS source_id,labels(n),keys(n),type(r),labels(m),keys(m), id(m) AS target_id"
            edges_a = session.run(query)
            edges = [e for e in edges_a]
            print(colored("Done.", "green"))
    
        return graph, edges
