from neo4j import GraphDatabase

uri = "neo4j://localhost:7687"
neo4jDriver = GraphDatabase.driver(uri, auth=("neo4j", "neo4jneo4j"))

def add_movie(tx, title, released, tagline):
        check_query = "MATCH (m:Movie {title: $title}) RETURN m"
        check_result = tx.run(check_query, {"title": title}).single()

        if check_result:
             return "Movie already exists"
        else:
             create_query = "CREATE (m:Movie {title: $title, released: $released, tagline: $tagline})"
             parameters = {"title": title, "released": released, "tagline": tagline}
             tx.run(create_query, parameters)
             return "Movie added to database"


if __name__ == "__main__":
    title = input("Enter the movie title:")
    released = input("Enter the year released:")
    tagline = input("Enter a short tagline:")

    with neo4jDriver.session() as session:
        result = session.execute_write(add_movie, title, released, tagline)
        print(result)
        
        neo4jDriver.close()