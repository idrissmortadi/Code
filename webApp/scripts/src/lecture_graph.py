""" Step 1 : Preprocessing data """

# Imports
from termcolor import colored

# File import
from .debug import printb
from .node import Graph, Node
from time import time


def lecture_graph(driver, edge):
    with driver.session() as session:
        # Query to get nodes with IDs, labels, and properties
        print(colored("Querying Neo4j to get a part of the graph:", "yellow"))
        nodes = session.run(
            "MATCH (n) \
             RETURN id(n) AS id, labels(n) AS labels, keys(n) AS keys, COUNT(n) AS count"
        )

        graph = Graph()
        for node in nodes:
            node_id = str(node["id"])  # Fetch original ID as a string
            labels = set(node["labels"])
            properties = set(node["keys"])
            count = node["count"]
            n = Node(node_id, labels, properties)

            graph.add_node(n, count)

        print(colored("Done fetching nodes.", "green"))
        printb(graph)

        edges = None
        if edge:
            print(colored("Querying Neo4j to get all the edges:", "yellow"))
            query = """
                MATCH (n)-[r]->(m)
                RETURN id(n) AS source_id, id(m) AS target_id, type(r) AS relationship_type
            """
            edges_a = session.run(query)
            edges = [
                {"source_id": str(e["source_id"]), "target_id": str(e["target_id"]), "type": e["relationship_type"]}
                for e in edges_a
            ]
            print(colored("Done fetching edges.", "green"))

        return graph, edges
