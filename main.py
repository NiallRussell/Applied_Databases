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
                        print(row)
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

