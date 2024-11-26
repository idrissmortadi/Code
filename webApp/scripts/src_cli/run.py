import argparse
import time
from typing import Dict

from neo4j import GraphDatabase
from termcolor import colored

from ..settings import global_variable
from .clustering_algo import clustering

from .lecture_graph import lecture_graph
from .sampling import sampling

# from .storing import storing
from .storing_org import EdgesOriginCSVWriter


def algorithm_script(params: Dict[str, str]):
    print(
        colored(
            "Schema inference using Gaussian Mixture Model clustering on PG\n", "red"
        )
    )

    # {'dataset': 'ldbc', 'method': 'k-mean', 'has_limit': False, 'limit_to': 5, 'use_incremental': False, 'nb_subcluster': 1}
    DBname = ""
    uri = ""
    user = ""
    passwd = ""

    if params["dataset"] == "ldbc":
        DBname = "DBP-15k"
        uri = "bolt://localhost:7687"
        user = "neo4j"
        passwd = "password"
    elif params["dataset"] == "covid-19":
        DBname = "covid19"
        uri = "bolt://db.covidgraph.org:7687"
        user = "public"
        passwd = "password"
    elif params["dataset"] == "fib25":
        DBname = "fib25"
        uri = "bolt://localhost:7687"
        user = "neo4j"
        passwd = "password"
    else:
        exit(1)
    # Connection a la base de donnée Neo4j
    # set encrypted to False to avoid possible errors

    driver = GraphDatabase.driver(uri, auth=(user, passwd), encrypted=False)

    print(
        colored("Starting to query on ", "red"),
        colored(DBname, "red"),
        colored(":", "red"),
    )
    t1 = time.perf_counter()
    graph, edges = lecture_graph(driver, params["query_edge"])
    t1f = time.perf_counter()

    global_variable("edges", edges)

    step1 = t1f - t1  # time to complete step 1
    print(colored("Queries are done.", "green"))
    print("Step 1: Preprocessing was completed in ", step1, "s")

    print("---------------")

    print(colored("Data sampling : ", "blue"))
    ts = time.perf_counter()
    trainning_graph = sampling(graph, int(params["limit_to"]))
    tsf = time.perf_counter()
    steps = tsf - ts  # time to complete the sampling step
    print(colored("Separating done.", "green"))
    print("The sampling step was processed in ", steps, "s")

    print("---------------")

    # We create the run

    # bm = Benchmark.objects.create(
    #     algo_type="GMM-S",
    #     data_set=params["dataset"],
    #     n_iterations=0,
    #     size=sum(trainning_graph._node_occurs.values()),
    #     t_pre=0,
    #     t_cluster=0,
    #     t_write=0,
    # )

    # global_variable("bm", bm)

    print(colored("Starting to cluster data using GMM :", "red"))
    t2 = time.perf_counter()
    cluster = clustering(trainning_graph, int(params["nb_subcluster"]))
    t2f = time.perf_counter()
    print("Cluster nods:", cluster.get_nodes())
    step2 = t2f - t2  # time to complete step 2
    print(colored("Clustering done.", "green"))
    print("Step 2: Clustering was completed in ", step2, "s")

    print("---------------")
    print(colored("Writing file and identifying subtypes :", "red"))
    t3 = time.perf_counter()
    # file = storing(cluster, edges, params["dataset"])

    csv_writer = EdgesOriginCSVWriter([cluster])

    # Write the edges
    csv_writer.write_edges()
    # if params["evaluate"]:
    #     eval_quality()
    t3f = time.perf_counter()

    step3 = t3f - t3  # time to complete step 3
    print(colored("Writing done.", "green"))
    print(
        "Step 3: Identifying subtypes and storing to file was completed in", step3, "s"
    )

    # We update the data of the runs in the database with the time of execution
    # Benchmark.objects.filter(pk=bm.pk).update(
    #     t_pre=step1 + steps, t_cluster=step2, t_write=step3
    # )

    return {
        "t_pre": step1,
        "t_cluster": step2,
        "t_write": step3,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run algorithm script with parameters."
    )
    parser.add_argument("--dataset", required=True, help="Specify the dataset name.")
    parser.add_argument("--limit_to", required=True, help="Specify the limit.")
    parser.add_argument(
        "--nb_subcluster", required=True, help="Specify the number of subclusters."
    )
    parser.add_argument(
        "--query_edge", required=False, action="store_true", help="Enable query edge."
    )

    args = parser.parse_args()

    # Convert args to a dictionary
    params = {
        "dataset": args.dataset,
        "limit_to": args.limit_to,
        "nb_subcluster": args.nb_subcluster,
        "query_edge": "on" if args.query_edge else "off",
    }

    algorithm_script(params)
