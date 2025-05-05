import pymysql
import pymysql.cursors



def main():
    conn = pymysql.connect(
        host ="localhost",
        user = "root",
        password = "root",
        database = "appdbproj",
        cursorclass=pymysql.cursors.DictCursor)
    
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
                with conn:   
                    cursor = conn.cursor()
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
                    print(results)
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