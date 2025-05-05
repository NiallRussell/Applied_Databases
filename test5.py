import pymysql
import pymysql.cursors
from datetime import datetime
from neo4j import GraphDatabase


def main():
    conn = pymysql.connect(
        host ="localhost",
        user = "root",
        password = "root",
        database = "appdbproj",
        cursorclass=pymysql.cursors.DictCursor)
    
    uri = "neo4j://localhost:7687"
    neo4jDriver = GraphDatabase.driver(uri, auth=("neo4j", "neo4jneo4j"))

    def create_marriage(tx, newlywed_id1, newlywed_id2):
                
        #Check if already married
        check_query = '''OPTIONAL MATCH (a1:Actor{ActorID: $newlywed_id1})
                               OPTIONAL MATCH (a1)-[m1:MARRIED_TO]-()
                               OPTIONAL MATCH (a2:Actor{ActorID: $newlywed_id2})
                               OPTIONAL MATCH (a2)-[m2:MARRIED_TO]-()
                               RETURN a1, a2, m1, m2'''
                

                
        parameters = {"newlywed_id1": newlywed_id1, "newlywed_id2": newlywed_id2}
        check_result = tx.run(check_query, parameters).single()
        a1, a2, m1, m2 = check_result["a1"], check_result["a2"], check_result["m1"], check_result["m2"]

        #Both actors are married
        if m1 is not None or m2 is not None:
            if m1 is not None:
                print(f"Actor {newlywed_id1} is already married")
            if m2 is not None:
                print(f"Actor {newlywed_id2} is already married")
            return
        
        #Neither actor is married and both already have existing nodes
        if a1 is not None and a2 is not None:
            create_query = '''MATCH (a1:Actor{ActorID:$newlywed_id1}), (a2:Actor{ActorID:$newlywed_id2}) 
                                    CREATE (a1)-[:MARRIED_TO]->(a2)'''
            tx.run(create_query, parameters)
            print(f"Actor {newlywed_id1} is now married to Actor {newlywed_id2}")
  

        #Neither actor is married but only Actor 1 has an existing node
        elif a1 is not None:
            create_query = '''MATCH (a1:Actor{ActorID:$newlywed_id1})
                                    CREATE (a2:Actor{ActorID:$newlywed_id2})-[:MARRIED_TO]->(a1)'''
            tx.run(create_query, parameters)
            print(f"Actor {newlywed_id1} is now married to Actor {newlywed_id2}")
                    

        #Neither actor is married but only Actor 2 has an existing node
        elif a2 is not None:
            create_query = '''MATCH (a2:Actor{ActorID:$newlywed_id2})
                                    CREATE (a1:Actor{ActorID:$newlywed_id1})-[:MARRIED_TO]->(a2)'''
            tx.run(create_query, parameters)
            print(f"Actor {newlywed_id1} is now married to Actor {newlywed_id2}")

        #Neither actor is married nor has an existing node
        else:
            create_query = '''CREATE (a1:Actor{ActorID:$newlywed_id1})-[:MARRIED_TO]->(a2:Actor{ActorID:$newlywed_id2})'''
            tx.run(create_query, parameters)
            print(f"Actor {newlywed_id1} is now married to Actor {newlywed_id2}")

    #Create loop to prompt user to enter until valid entry given
    while True:
        newlywed_id1 = int(input("Enter Actor 1 ID: "))
        newlywed_id2 = int(input("Enter Actor 2 ID: "))

        #Check if inputs are the same
        if newlywed_id1 == newlywed_id2:
            print("An actor cannot marry him/herself")
            continue
        else:    
            #Check if IDs exist
            id_exists_query = (f'''SELECT (SELECT ActorID from actor WHERE ActorID = %s) as ActorID1,
            (SELECT ActorID from actor WHERE ActorID = %s) as ActorID2''')
            values = (newlywed_id1, newlywed_id2)

            try:
                with conn.cursor() as cursor:   
                    cursor.execute(id_exists_query, values)
                    results = cursor.fetchone()
                    check_id1, check_id2 = results["ActorID1"], results["ActorID2"]
                    if check_id1 is None and check_id2 is None:
                        print("Neither Actor IDs exist")
                        continue
                    if check_id1 is None:
                        print(f"Actor ID {newlywed_id1} does not exist")
                        continue
                    if check_id2 is None:
                        print(f"Actor ID {newlywed_id2} does not exist")
                        continue
                    with neo4jDriver.session() as session:
                        session.execute_write(create_marriage, newlywed_id1, newlywed_id2)
                    neo4jDriver.close()
                    display_menu()
                               
            except pymysql.MySQLError as e:
                print("Database error:", e)
                continue
            break
                               
            
            

    

def display_menu():
        print(f'''
          MoviesDB
          ---------
          
          MENU
          ====
          1 - View Directors and Films
          2 - View Actors by Month of Birth
          3 - Add New Actor
          4 - View Married Actors
          5 - Add Actor Marriage
          6 - View Studios
          x - Exit Application
          ''')


if __name__ == "__main__":
    main()