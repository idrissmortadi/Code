""" Write clusters into a file """

# Imports
import csv
import os 
from threading import main_thread

from numpy.core.arrayprint import DatetimeFormat

from .node import Cluster, Node

dirname = os.path.dirname(__file__)

import csv
from typing import List
added_rels= set()
edges_org = os.path.join(dirname, "../graph/edge_origin.csv")

class EdgesOriginCSVWriter:
    def __init__(self, clusters: List["Cluster"], output_file: str = edges_org) -> None:
        """
        Initializes the writer for processing edges between nodes in clusters.

        Args:
            clusters (List[Cluster]): List of clusters to process.
            output_file (str): Path to the file where relationships will be written.
        """
        self.clusters = clusters
        self.output_file = output_file

    def write_edges(self) -> None:
        """
        Processes clusters and writes subtype relationships between nodes to a CSV file.
        """
        with open(self.output_file, mode="w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            # Write the header
            writer.writerow(["Node ID (sub-cluster)", "Relationship", "Node ID (cluster)"])

            # Write edges recursively
            for cluster in self.clusters:
                self._process_cluster(writer, cluster)

    def _process_cluster(self, writer, cluster: "Cluster") -> None:
        """
        Recursively processes a cluster and writes subtype relationships between nodes.

        Args:
            writer (csv.writer): CSV writer object.
            cluster (Cluster): The cluster being processed.
        """
        parent_nodes = cluster.get_nodes().keys()  # Get parent cluster nodes
        for sub_cluster in cluster.get_son():
            sub_nodes = sub_cluster.get_nodes().keys()  # Get sub-cluster nodes

            # Write edges: each sub-cluster node is a SUBTYPE of each parent node
            for sub_node in sub_nodes:
                for parent_node in parent_nodes:
                    if sub_node.get_id()!=parent_node.get_id() and (sub_node.get_id()+" SUBTYPE " +parent_node.get_id()) not in added_rels:
                        writer.writerow([sub_node.get_id(), "SUBTYPE", parent_node.get_id()]) 
                        added_rels.add(sub_node.get_id()+" SUBTYPE " +parent_node.get_id())

            # Recursively process sub-clusters
            self._process_cluster(writer, sub_cluster)
