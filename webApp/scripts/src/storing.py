""" Write clusters into a file """

# Imports
import csv
import os 
from threading import main_thread

from numpy.core.arrayprint import DatetimeFormat

from .node import Cluster, Node

dirname = os.path.dirname(__file__)

def storing(cluster, edges, name):
    """
    Write clusters and edges into separate CSV files with preserved original IDs.

    Parameters
    ----------
    cluster : Cluster
        Root cluster containing all subclusters and nodes.
    edges : list
        List of edges from the graph.
    name : str
        Base name for the output files.

    Returns
    -------
    str
        Filenames of the generated CSV files.
    """

    # Prepare file paths
    nodes_file = os.path.join(dirname, "../graph/node.csv")
    edges_file = os.path.join(dirname, "../graph/edge.csv")

    # Write nodes to file
    with open(nodes_file, "w") as f:
        writer = csv.writer(f)
        header = ["id", "original_id", "labels", "properties", "depth", "number", "new", "old_number"]
        writer.writerow(header)

        # Initialize variables
        data = []
        run_clusters = []
        i = 1  # Node ID counter
        main_node = dict()
        cluster_list = [cluster]
        esubtype = []

        # Iterate through basic type clusters
        for basic_type in cluster.get_son():
            parent_id = i
            data_line = [str(parent_id)]
            labels = basic_type.get_name()

            # Collect data for the base type
            data_line += [
                "N/A",  # Original ID not applicable for base types
                labels,
                "",  # No properties for base types
                "1",  # Depth level
                str(basic_type.get_number_node()),  # Number of nodes
                "0",  # Not new
                "Nan",  # Old number not applicable
            ]
            writer.writerow(data_line)
            cluster_list.append(basic_type)
            main_node[labels] = i

            h = i
            i += 1
            k = 2  # Depth for subtypes

            # Recursively store subclusters
            for sous_cluster in basic_type.get_son():
                if sous_cluster is not None:
                    i, _ = rec_storing(
                        sous_cluster, writer, i, parent_id, run_clusters, k, cluster_list, esubtype, h
                    )

    # Write edges to file
    with open(edges_file, "w") as f:
        writer = csv.writer(f)
        header = ["source_id", "target_id", "original_source_id", "original_target_id", "types", "new"]
        writer.writerow(header)
        print(edges)
        if edges is not None:
            N = len(cluster_list)
            tab = [[0 for _ in range(N)] for _ in range(N)]

            for edge in edges:
                ln = set(edge["labels(n)"])
                pn = set(edge["keys(n)"])
                node_id = edge.get("source_id", "unknown")
                n = Node(id=node_id, labels=ln, properties=pn)  # Fixed instantiation

                cn = 0
                original_source_id = edge["source_id"]
                for i in range(1, N):
                    if cluster_list[i].get_son() == [] and n in cluster_list[i]._nodes:
                        cn = i

                lm = set(edge["labels(m)"])
                pm = set(edge["keys(m)"])
                target_id = edge.get("target_id", "unknown")
                m = Node(id=target_id, labels=lm, properties=pm)  # Fixed instantiation

                cm = 0
                original_target_id = edge["target_id"]
                for i in range(1, N):
                    if cluster_list[i].get_son() == [] and m in cluster_list[i]._nodes:
                        cm = i

                t = edge["type(r)"]
                tab[cn][cm] = t

                writer.writerow([cn, cm, original_source_id, original_target_id, t, "0"])



        # Write subtypes
        for p in esubtype:
            writer.writerow([p[0], p[1], "N/A", "N/A", "SUBTYPE_OF", "0"])

    return "node.csv, edge.csv"


def rec_storing(cluster, writer, i, parent_id, run_clusters, k, cluster_list, subtype, h):
    """
    Recursive function to write cluster data into a file.
    """
    all_labels = set()
    all_properties = set()
    always_labels = set()
    always_properties = set()

    j = True

    for node in cluster.get_nodes():
        cur_labels = node.get_labels()
        cur_properties = node.get_proprety()

        all_labels = all_labels.union(cur_labels)
        all_properties = all_properties.union(cur_properties)

        if j:
            always_labels = cur_labels.union(set())
            always_properties = cur_properties.union(set())
        j = False

        always_labels = always_labels.intersection(cur_labels)
        always_properties = always_properties.intersection(cur_properties)

    optional_labels = all_labels - always_labels
    optional_properties = all_properties - always_properties

    if optional_labels:
        labels = ":".join(sorted(always_labels)) + ":?" + ":?".join(sorted(optional_labels))
    else:
        labels = ":".join(sorted(always_labels))

    if optional_properties:
        properties = ":".join(sorted(always_properties)) + ":?" + ":?".join(sorted(optional_properties))
    else:
        properties = ":".join(sorted(always_properties))

    if labels + properties not in run_clusters:
        subtype.append((i, h))
        data_line = [
            str(i),
            cluster.get_original_id(),  # Include original ID
            labels,
            properties,
            str(k),
            str(cluster.get_number_node()),
            "0",  # Not new
            "Nan",
        ]
        writer.writerow(data_line)
        cluster_list.append(cluster)
        run_clusters.append(labels + properties)

        h = i
        k += 1
        i += 1

        for sous_cluster in cluster.get_son():
            if sous_cluster is not None:
                i, _ = rec_storing(
                    sous_cluster, writer, i, parent_id, run_clusters, k, cluster_list, subtype, h
                )

    return i, k
