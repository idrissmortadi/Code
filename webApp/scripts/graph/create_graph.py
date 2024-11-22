import json
from neo4j import GraphDatabase

# Initialize Neo4j driver
driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))

def add_nodes_from_file(file_path):
    with driver.session() as session:
        with open(file_path, 'r', encoding='latin-1') as file:
            next(file)  # Skip header row if there is one
            for line in file:
                try:
                    # Process each line in the CSV
                    id, labels, properties_str, depth, number, new, old_number = line.strip().split(',')

                    # Parse properties from JSON string format
                    properties = json.loads(properties_str)

                    # Extract property keys and values separately
                    property_keys = list(properties.keys())
                    property_values = list(properties.values())

                    # Create query to add node and set properties
                    query = f"""
                    MERGE (n {{id: $id}})
                    SET n:{labels.replace(';', ':')}
                    CALL apoc.create.setProperties(n, $property_keys, $property_values)
                    """
                    
                    # Run query with parameters
                    session.run(query, id=id, property_keys=property_keys, property_values=property_values)

                except ValueError:
                    print("Skipping line due to unexpected format:", line)
                except json.JSONDecodeError:
                    print("Skipping line due to JSON decode error:", line)

# Run the function
add_nodes_from_file("node.csv")
