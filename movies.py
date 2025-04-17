from neo4j import GraphDatabase

uri = "neo4j://localhost:7687"
neo4jDriver = GraphDatabase.driver(uri, auth=("neo4j", "neo4jneo4j"))


def movie_from_name(tx, name1, name2):
    query = "MATCH (p1:Person{name: {$name1}})-[:ACTED_IN]->(m:Movie)<-[:ACTED_IN]- (p2:Person {name:$name2}) RETURN m.title as Title, m.released as Released, substring(m.tagline, 0, 20) as Short Tagline"
    parameters = {"name1": name1, "name2": name2}
    result = tx.run(query, parameters)
    return [record for record in result]




if __name__ == "__main__":
    name1 = input("Enter the first actor's name:")
    name2 = input("Enter the second actor's name:")
    #movie_from_name(name1, name2)

    with neo4jDriver.session() as session:
        result = session.execute_read(movie_from_name, name1, name2)

        for record in result:
            print((f"Title: {record['Title']}, Released: {record['Released']}, Tagline: {record['Short Tagline']}"))
        neo4jDriver.close()