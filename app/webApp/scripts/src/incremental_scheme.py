from sklearn.semi_supervised import LabelSpreading
from .clustering_algo import *
from .node import *
from copy import deepcopy


def add_node(cluster, node):
    """ This function add a node to a cluster (it has to be the main one). """
    cluster.add_node(node)
    cluster._modification += 1

    labs = node.get_labels()

    fils = cluster.get_son()
    first_cluster = cluster._cutting_values

    if cluster._modification / sum(cluster.get_nodes().values()) < 0.1:
        for i in range(len(first_cluster)):
            if first_cluster[i].issubset(labs):
                add_node_rec(fils[i], node)

    else:
        nodes = cluster.get_nodes()
        graph = Graph()
        for node in nodes.key():
            graph.add_node(node, nodes[node])
        cluster = clustering(graph)

    return cluster


def add_node_rec(cluster, node):
    """This function goes recursivly to insert a node, and only take subclusters ( created with gmm, not by the lab_set )  """

    cluster.add_node(node)

    d = dist(node, cluster._ref_node)

    cuts = cluster._cutting_values
    list_son = cluster.get_son()

    if cuts != []:

        # We set this value in order to be sure to find a place for the node
        cuts[0] = 0

        for i in range(len(cuts)-1, -1, -1):
            if d >= cuts[i]:
                add_node_rec(list_son[i], node)
                break

        raise Exception(
            "We shouldn't be in this situation, as the minimum distance, 0, is supposed to be reached")


def add_node_exact(cluster, node):
    """
    The point of this function is to insert a node, exactly as if we were recomputing everything,
    computing only the part we didn't already compute.
    """

    cluster.add_node(node)
    labs = node.get_labels()

    nodes_cluster = cluster.get_nodes()
    fils = cluster.get_son()
    first_cluster = cluster._cutting_values

    for i in range(len(first_cluster)):
        if first_cluster[i].issubset(labs):
            add_node_exact_rec(fils[i], node)

    if labs not in first_cluster:  # That mean we have a new type of node with a new set of label
        new_cluster = Cluster()
        correct_nodes = dict()
        cluster._cutting_values.append(labs)
        correct_nodes[node] = 1
        for node_c in nodes_cluster:
            if labs.issubset(node_c.get_labels()):
                correct_nodes[node_c] = nodes_cluster[node_c]
                new_cluster._nodes = correct_nodes
        rec_clustering(new_cluster)
        cluster.add_son(new_cluster)
        new_cluster._name = ":".join(list(LabelSpreading))

    return cluster


def add_node_exact_rec(cluster, node):

    nb_cluster = len(cluster.get_son())
    cluster.add_node(node)

    correct_nodes = cluster.get_nodes()
    ref_node = max_labs_props(correct_nodes)

    cluster._name = str(ref_node)
    cluster._ref_node = ref_node
    similarities_dict = compute_similarities(correct_nodes, ref_node)

    computed_measures, ecrasage = to_format(similarities_dict, correct_nodes)

    if len(correct_nodes) >= nb_cluster:

        bgmm = BayesianGaussianMixture(
            n_components=nb_cluster, tol=1, max_iter=10).fit(computed_measures)
        predictions = bgmm.predict(computed_measures)

        # variable to keep track on the index of the node in the list 'predictions'
        j = 0
        new_clusters = [Cluster("Oh") for _ in range(nb_cluster)]
        cluster._cutting_values = cutting_value(computed_measures, predictions)
        # iterate through each different nodes in this dataset
        for node in correct_nodes:
            amount = correct_nodes[node] // (10**ecrasage)
            for i in range(amount):
                if node in new_clusters[predictions[j]]._nodes:
                    new_clusters[predictions[j]]._nodes[node] += 10**ecrasage
                else:
                    print("&", end="")
                    new_clusters[predictions[j]]._nodes[node] = 10**ecrasage
                j += 1

        count = 0
        for c in new_clusters:
            count += len(c.get_nodes()) != 0
        if (count < 2):
            return

        # For each cluster cluster
        dict_of_id = cluster.get_sons_id()
        for i in range(nb_cluster):

            new_id = frozenset(new_clusters[i]._node)
            if frozenset(new_id) in dict_of_id:
                cluster.add_son(dict_of_id[new_clusters[i]])

            elif new_clusters[i]._nodes != dict():
                # search for more subclusters in this subcluster
                add_node_exact_rec(new_clusters[i], nb_cluster)
                cluster.add_son(new_clusters[i])


def add_node_hybrid(cluster, node):
    """Insert a node in our cluster not recalculating GMM as lon as the reference node shoudl not change"""

    cluster.add_node(node)
    cluster.add_node(node)
    labs = node.get_labels()

    nodes_cluster = cluster.get_nodes()
    fils = cluster.get_son()
    first_cluster = cluster._cutting_values

    for i in range(len(first_cluster)):
        if first_cluster[i].issubset(labs):
            add_node_exact_rec(fils[i], node)


def add_node_hybrid_rec(cluster, node):

    cluster.add_node(node)

    d = dist(node, cluster._ref_node)

    cuts = cluster._cutting_values
    list_son = cluster.get_son()

    correct_nodes = cluster.get_nodes()
    ref_node = max_labs_props(correct_nodes)

    if cuts != [] and ref_node == cluster._ref_node:

        # We set this value in order to be sure to find a place for the node
        cuts[0] = 0

        for i in range(len(cuts)-1, -1, -1):
            if d >= cuts[i]:
                add_node_rec(list_son[i], node)
                break

        raise Exception(
            "We shouldn't be in this situation, as the minimum distance, 0, is supposed to be reached")

    else:
        rec_clustering(cluster)