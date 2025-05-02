import pymysql
import pymysql.cursors


def main():
    conn = pymysql.connect(
        host ="localhost",
        user = "root",
        password = "root",
        database = "appdbproj",
        cursorclass=pymysql.cursors.DictCursor)
    
    display_menu()

    while True:
        choice = input("Choice:")
    
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

