import pymysql
import pymysql.cursors
from datetime import datetime
from neo4j import GraphDatabase

def main():
    #Try block to manage connections
    try:
        conn = pymysql.connect(
            host ="localhost",
            user = "root",
            password = "root",
            database = "appdbproj",
            cursorclass=pymysql.cursors.DictCursor)
        
        uri = "neo4j://localhost:7687"
        neo4jDriver = GraphDatabase.driver(uri, auth=("neo4j", "neo4jneo4j"))
        
        display_menu()
        
        #Loop to re-prompt user input
        while True:
            choice = input("Choice:")

            #View Directors and Films
            if choice == '1':
                director = input("Enter director name:")
                pattern = f"%{director}%"
                director_query = f'''
                SELECT d.DirectorName, f.FilmName, s.StudioName
                from director d
                INNER JOIN film f
                on d.DirectorID = f.FilmDirectorID
                INNER JOIN studio s
                on s.StudioID = f.FilmStudioID
                WHERE d.DirectorName LIKE %s;
                '''
                try:
                    with conn.cursor() as cursor:
                        cursor.execute(director_query, (pattern,))
                        rows = cursor.fetchall()
                except pymysql.MySQLError as err:
                    print("Database error", err)
                    display_menu()
                else:
                    if not rows:
                        print("No directors found of that name")
                        display_menu()
                    else:
                        print(f'''
Film Details for {director}
-----------------------------
                        ''')
                        for row in rows:
                            director_name = row["DirectorName"]
                            film_name = row["FilmName"]
                            studio_name = row["StudioName"]
                            print(f"{director_name}  |  {film_name}  |  {studio_name}")
                        display_menu()

            #View actors by month of birth
            elif choice == "2":
                nums = list(range(1,13))
                words = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]
                valid = dict(zip(words, nums))

                #SQL query
                month_query = f'''SELECT ActorName, ActorDOB, ActorGender
                from actor
                WHERE month(ActorDOB) = %s'''

                #Determine if input is valid. While loop to reprompt input
                while True:
                    month = input("Enter Month:")
                
                    #If user enters an integer convert to integer type. If they enter a string, lower it to compare to list
                    try:
                        month = int(month)
                    except ValueError:
                        month = month.lower()
                    
                    #Check if input in dictionary
                    if month not in valid.values() and month not in valid.keys():
                        print("Please input a valid month")
                        continue
                    else:
                        if month in nums:
                            month_param = month
                            break
                        else:
                            month_param = valid[month]
                            break

                try:
                    with conn.cursor() as cursor:
                        cursor.execute(month_query, (month_param,))
                        rows = cursor.fetchall()
                except pymysql.MySQLError as err:
                    print("Database error", err)
                    display_menu()
                else:
                    for row in rows:
                        actor_name = row["ActorName"]
                        actor_dob = row["ActorDOB"].strftime('%Y-%m-%d')
                        actor_gender = row["ActorGender"]
                        print(f"{actor_name}  |  {actor_dob}  |  {actor_gender}")
                    display_menu()

            #Add new actor
            elif choice == "3":
                print(f'''
Add New Actor
----------------
                      ''')
                new_actor_id = int(input("Actor ID: "))
                new_actor_name = input("Name: ")
                new_actor_dob = input("DOB: ")
                #Check date format and reprompt input if incorrect
                try:
                    datetime.strptime(new_actor_dob, '%Y-%m-%d')
                except ValueError:
                    print("Please enter date in format YYYY-MM-DD")
                    continue
                new_actor_gender = input("Gender: ")
                new_actor_country_id = int(input("Country ID: "))
                values = (new_actor_id, new_actor_name, new_actor_dob, new_actor_gender, new_actor_country_id)

                #SQL query
                new_actor_insert = f'''INSERT INTO actor(ActorID, ActorName, ActorDOB, ActorGender, ActorCountryID) 
                VALUES (%s, %s, %s, %s, %s)'''

                try:
                    with conn.cursor() as cursor:   
                        cursor.execute(new_actor_insert, values)
                        conn.commit()
                        print("Insert Successful")
                        display_menu()

                except pymysql.err.IntegrityError as e:
                    error_code = e.args[0]
                    error_msg = str(e)

                    #Check for existing actor ID or nonexistent country ID
                    if (error_code == 1062 and "PRIMARY" in error_msg):
                        print(f"*** ERROR *** Actor ID: {new_actor_id} already exists")
                    elif (error_code == 1452 and "Country" in error_msg):
                        print(f"*** ERROR *** Country ID: {new_actor_country_id} does not exist")
                    else:
                        print(f"Integrity Error: {e}")
                    #Rollback any changes made
                    conn.rollback()
                    display_menu()
                    continue

                except ValueError as e:
                    print(f"Value error: {e}")
                    conn.rollback()
                    display_menu()
                    continue
                
                except pymysql.MySQLError as e:
                    print(f"Database error: {e}")
                    conn.rollback()
                    display_menu()
                    continue

                except Exception as e:
                    print(f"Unexpected error: {e}")
                    conn.rollback()
                    display_menu()
                    continue

            #View marriage
            elif choice == "4":
                #Neo4J function
                def married_to(tx, actorID):
                    query = "MATCH (a1:Actor{ActorID: $actorID})-[m:MARRIED_TO]-(a2:Actor) RETURN a1.ActorID, a2.ActorID, m"
                    parameter = {"actorID": actorID}
                    record = tx.run(query, parameter).single()
                    if not record:
                        print(f'''
------------
This actor is not married
                        ''')
                    else:
                        return (record["a1.ActorID"], record["a2.ActorID"])
        
                actor_choice = int(input("Enter Actor ID: "))

                with neo4jDriver.session() as session:
                    result = session.execute_read(married_to, actor_choice)

                if result: 
                    actor1_id, actor2_id = result
                
                    married_to_query = "SELECT (SELECT ActorName from actor WHERE ActorID = %s) as ActorName1, (SELECT ActorName from actor WHERE ActorID = %s) as ActorName2"
                    values = (int(actor1_id), int(actor2_id))

                    try:
                        with conn.cursor() as cursor:  
                            cursor.execute(married_to_query, values)
                            results = cursor.fetchone()
                            actor1_name = results["ActorName1"]
                            actor2_name = results["ActorName2"]
                            print(f'''
-------------
These Actors are married:
{actor1_id}  |  {actor1_name}
{actor2_id}  |  {actor2_name}
                            ''')
                        display_menu()
            
                    except Exception as e:
                        print(f"Unexpected error: {e}")
        
                else:
                    display_menu()

                #Added this because when choice 5 was selected after choice 4 I got a database error
                if conn.open:
                    conn.commit()

            #Create marriage
            elif choice == "5":

                #Create Neo4j function
                def create_marriage(tx, newlywed_id1, newlywed_id2, newlywed_name1, newlywed_name2):
                    
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
                            print(f"{newlywed_name1} is already married")
                        if m2 is not None:
                            print(f"{newlywed_name2} is already married")
                        return
            
                    #Neither actor is married and both already have existing nodes
                    if a1 is not None and a2 is not None:
                        create_query = '''MATCH (a1:Actor{ActorID:$newlywed_id1}), (a2:Actor{ActorID:$newlywed_id2}) 
                                        CREATE (a1)-[:MARRIED_TO]->(a2)'''
                        tx.run(create_query, parameters)
                        print(f"{newlywed_name1} is now married to {newlywed_name2}")
    

                    #Neither actor is married but only Actor 1 has an existing node
                    elif a1 is not None:
                        create_query = '''MATCH (a1:Actor{ActorID:$newlywed_id1})
                                        CREATE (a2:Actor{ActorID:$newlywed_id2})-[:MARRIED_TO]->(a1)'''
                        tx.run(create_query, parameters)
                        print(f"{newlywed_name1} is now married to {newlywed_name2}")
                        
                    #Neither actor is married but only Actor 2 has an existing node
                    elif a2 is not None:
                        create_query = '''MATCH (a2:Actor{ActorID:$newlywed_id2})
                                        CREATE (a1:Actor{ActorID:$newlywed_id1})-[:MARRIED_TO]->(a2)'''
                        tx.run(create_query, parameters)
                        print(f"{newlywed_name1} is now married to {newlywed_name2}")

                    #Neither actor is married nor has an existing node
                    else:
                        create_query = '''CREATE (a1:Actor{ActorID:$newlywed_id1})-[:MARRIED_TO]->(a2:Actor{ActorID:$newlywed_id2})'''
                        tx.run(create_query, parameters)
                        print(f"{newlywed_name1} is now married to {newlywed_name2}")

                #Create loop to prompt user to enter until valid entry given
                while True:
                    newlywed_id1 = int(input("Enter Actor 1 ID: "))
                    newlywed_id2 = int(input("Enter Actor 2 ID: "))

                    #Check if inputs are the same
                    if newlywed_id1 == newlywed_id2:
                        print("An actor cannot marry him/herself")
                        continue
                    else:    
                        #Check if IDs exist and retrieve names for printing later
                        id_exists_query = (f'''SELECT (SELECT ActorID from actor WHERE ActorID = %s) as ActorID1,
                                           (SELECT ActorName from actor WHERE ActorID = %s) as ActorName1,
                                           (SELECT ActorID from actor WHERE ActorID = %s) as ActorID2,
                                           (SELECT ActorName from actor WHERE ActorID = %s) as ActorName2''')
                        values = (newlywed_id1, newlywed_id1, newlywed_id2, newlywed_id2)

                        try:
                            with conn.cursor() as cursor:   
                                cursor.execute(id_exists_query, values)
                                results = cursor.fetchone()
                                check_id1, check_id2 = results["ActorID1"], results["ActorID2"]
                                newlywed_name1, newlywed_name2 = results["ActorName1"], results["ActorName2"]

                                #If IDs don't exist, inform user and prompt input again
                                if check_id1 is None and check_id2 is None:
                                    print("Neither Actor IDs exist")
                                    continue
                                if check_id1 is None:
                                    print(f"Actor ID {newlywed_id1} does not exist")
                                    continue
                                if check_id2 is None:
                                    print(f"Actor ID {newlywed_id2} does not exist")
                                    continue
                                # Execute neo4j query if IDs exist in SQL
                                with neo4jDriver.session() as session:
                                    session.execute_write(create_marriage, newlywed_id1, newlywed_id2, newlywed_name1, newlywed_name2)
                            display_menu()
                                
                        except pymysql.MySQLError as e:
                            print(f"Database error: {e}")
                            continue
                        except Exception as e:
                            print(f"Unexpected error: {e}")
                            continue
                        break
                #Added this as going from choice 5 to 6 threw an error
                if conn.open:
                    conn.commit()

            # View Studios
            elif choice == "6":

                try:
                    with conn.cursor() as cursor:
                        #Set transaction isolation level to repeatable read to ensure no entries made after entering this choice will be presented
                        cursor.execute("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ")
                        conn.begin()

                        studio_query = "SELECT StudioID, StudioName from studio ORDER BY StudioID ASC"

                        cursor.execute(studio_query)
                        results = cursor.fetchall()
                        print("Studio ID  |  Studio Name")
                        for row in results:
                            print(row["StudioID"], row["StudioName"], sep= "  |  ")
                        display_menu()
                except pymysql.MySQLError as e:
                    print(f"Unexpected error: {e}")
            
            #End marriage/create divorce
            elif choice == "7":

                divorcee1_name = input("Enter name of divorced actor: ")

                #Create Neo4j function
                def end_marriage(tx, divorcee1_id):

                    #Check if actor is actually married
                    check_query = '''MATCH (a1:Actor{ActorID: $divorcee1_id})-[m:MARRIED_TO]-(a2)
                                RETURN a2.ActorID as divorcee2_id, m'''
                    
                    #Create divorce relationship
                    divorce_query = '''MATCH (a1:Actor{ActorID: $divorcee1_id})-
                    [m:MARRIED_TO]-(a2) 
                    DELETE m
                    CREATE (a1)-[:DIVORCED_FROM]->(a2)
                    '''
    
                    parameter = {"divorcee1_id": divorcee1_id}

                    check_results = tx.run(check_query, parameter).single()


                    #If actor is married, remove married relationship and create divorced relationship. If not married, inform user
                    if check_results is None:
                        print("This actor is not married")
                    else:
                        results = tx.run(divorce_query, parameter).single()
                        divorcee2_id = check_results["divorcee2_id"]

                        #Retrieve second divorcee's name from SQL
                        divorcee2_query = "SELECT ActorName from actor WHERE ActorID = %s"
                        try:
                            with conn.cursor() as cursor:
                                cursor.execute(divorcee2_query, (f"{divorcee2_id}"))
                                results = cursor.fetchone()
                                divorcee2_name = results["ActorName"]
                        except pymysql.MySQLError as e:
                            print(f"Unexpected error: {e}")
                        else:
                            print(f"{divorcee1_name} and {divorcee2_name} are now divorced")

                        if conn.open:
                            conn.commit()

                #Check SQL for Actor ID
                divorcee_id_query = "SELECT ActorID from actor WHERE ActorName = %s"
                try:
                    with conn.cursor() as cursor:
                        cursor.execute(divorcee_id_query, (f"{divorcee1_name}"))
                        results = cursor.fetchone()
                        
                        #If Actor Name is in SQL retrieve Actor ID and write Neo4j query with it
                        if results["ActorID"] is not None:
                            divorcee1_id = results["ActorID"]
                            with neo4jDriver.session() as session:
                                session.execute_write(end_marriage, divorcee1_id)
                        else:
                            print("This actor is not in the database")
                except pymysql.MySQLError as e:
                    print(f"Unexpected error: {e}")
                    continue

                if conn.open:
                    conn.commit()
                display_menu()

            #Close the programme
            elif choice == "x":
                break

            #Any other input displays the menu again and reprompts input
            else:
                display_menu()

    #Close the connections
    finally:
        conn.close()
        neo4jDriver.close()       


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
7 - Divorce Actors
x - Exit Application
        ''')


if __name__ == "__main__":
    main()

