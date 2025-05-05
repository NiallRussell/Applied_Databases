import pymysql
import pymysql.cursors
from datetime import datetime
from neo4j import GraphDatabase

def main():
    #try block to manage connections
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
    -------------------------------------
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

                month = input("Enter Month:")
                try:
                    month = int(month)
                except ValueError:
                    month = month.lower()

                month_query = f'''SELECT ActorName, ActorDOB, ActorGender
                from actor
                WHERE month(ActorDOB) = %s'''

                while month:
                    if month not in valid.values() and month not in valid.keys():
                        print("Please input a valid month")
                        month = input("Enter Month:")
                        if int(month) in nums:
                            month = int(month)
                        else:
                            month = month.lower()
                    else:
                        if month in nums:
                            month_param = month
                            month = 0
                        else:
                            month_param = valid[month]
                            month = 0
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
                print(f'''Add New Actor
                    ----------------''')
                new_actor_id = int(input("Actor ID: "))
                new_actor_name = input("Name: ")
                new_actor_dob = input("DOB: ")
                try:
                    datetime.strptime(new_actor_dob, '%Y-%m-%d')
                except ValueError:
                    print("Please enter date in format YYYY-MM-DD")
                    continue
                new_actor_gender = input("Gender: ")
                new_actor_country_id = int(input("Country ID: "))
                values = (new_actor_id, new_actor_name, new_actor_dob, new_actor_gender, new_actor_country_id)

                new_actor_insert = f'''INSERT INTO actor(ActorID, ActorName, ActorDOB, ActorGender, ActorCountryID) 
                VALUES (%s, %s, %s, %s, %s)'''
                
                "INSERT INTO patient_table(ppsn, first_name, surname, address, doctorID) VALUES (%s, %s, %s, %s, %s)"


                try:
                    with conn.cursor() as cursor:   
                        cursor.execute(new_actor_insert, values)
                        conn.commit()
                        print("Insert Successful")
                        display_menu()

                except pymysql.err.IntegrityError as e:
                    error_code = e.args[0]
                    error_msg = str(e)

                    if (error_code == 1062 and "PRIMARY" in error_msg):
                        print(f"*** ERROR *** Actor ID: {new_actor_id} already exists")
                    elif (error_code == 1452 and "Country" in error_msg):
                        print(f"*** ERROR *** Country ID: {new_actor_country_id} does not exist")
                    else:
                        print("Integrity Error:", e)
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
                        with conn:   
                            cursor = conn.cursor()
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

            #Create marriage
            elif choice == "5":

                #Create Neo4j function
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
                                    session.execute_write(create_marriage, newlywed_id1, newlywed_id2)
                                display_menu()
                                
                        except pymysql.MySQLError as e:
                            print("Database error:", e)
                            continue
                        break
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
          x - Exit Application
          ''')


if __name__ == "__main__":
    main()

