import pymysql
import pymysql.cursors
from neo4j import GraphDatabase

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
        
uri = "neo4j://localhost:7687"
neo4jDriver = GraphDatabase.driver(uri, auth=("neo4j", "neo4jneo4j"))

conn = pymysql.connect(
        host ="localhost",
        user = "root",
        password = "root",
        database = "appdbproj",
        cursorclass=pymysql.cursors.DictCursor)

def married_to(tx, actorID):
    query = "MATCH (a1:Actor{ActorID: $actorID})-[m:MARRIED_TO]-(a2:Actor) RETURN a1.ActorID, a2.ActorID, m"
    parameter = {"actorID": actorID}
    record = tx.run(query, parameter).single()
    if not record:
        print(f'''------------
This actor is not married''')
    else:
        return (record["a1.ActorID"], record["a2.ActorID"])
    
actor_choice = int(input("Enter Actor ID: "))

with neo4jDriver.session() as session:
    result = session.execute_read(married_to, actor_choice)

neo4jDriver.close()

if result: 
    actor1_id, actor2_id = result
            
    married_to_query = "SELECT (SELECT ActorName from actor WHERE ActorID = %s) as ActorName1, (SELECT ActorName from actor WHERE ActorID = %s) as ActorName2"
    values = (int(actor1_id), int(actor2_id))

    try:
        with conn:   
            cursor = conn.cursor()
            cursor.execute(married_to_query, values)
            results = cursor.fetchone()
            actor1_name = results["ActorName1"]
            actor2_name = results["ActorName2"]
            print(f'''-------------
              These Actors are married:
              {actor1_id}  |  {actor1_name}
{actor2_id}  |  {actor2_name}''')
            display_menu()

    except Exception as e:
        print(f"Unexpected error: {e}")
else:
    display_menu()
    

