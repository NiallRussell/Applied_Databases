# Query Hollywood Application

### Description

##### This application allows the user to query data on holywood actors, directors, studios, and films

##### The majority of data to be queried is stored in an SQL database. Marriages between actors are stored in a Neo4J database, with the two databases linked by Actor ID. 

##### The options presented to the user are:

- 1 - View Directors and Films
        - Allows the user to enter a director's name and returns the films they have directed and the studio involved. The user can enter any number of strings from the director's name and the script will return any directors in the database whose name contains those characters. This queries the SQL database

- 2 - View Actors by Month of Birth
        - Allows the user to enter a month and returns any actor born in that month. The user can either enter the first three letters of the month or the associated number. This queries the SQL database

- 3 - Add New Actor
        - Allows the user to enter the details of a new actor. The user will be prompted to enter the actor's ID, name, date of birth, gender and country of origin. This modifies the actor table of the SQL database. 

- 4 - View Married Actors
        - Allows the user to enter an actor's ID and if they are married, returns the names and IDs of both married actors. This queries the Neo4J database to find the marriage relationship, and if the relationship exists, queries the SQL database for the actors' names.

- 5 - Add Actor Marriage
        - Allows the user to create a new marriage from the actors in the SQL database. The user is prompted to enter two actor IDs. The SQL database is queried to determine if the actors exist. If they exist, the Neo4J database is queried to determine if either actor is already married. The user is not allowed to create a relationship between two actors who are already married (to themselves or to other actors). Divorced relationships also appear in the database, so it will also be queried to determine if these actors already have nodes, and if not create them. If neither actor is married, the relationship is created along with the nodes, if necessary. 

- 6 - View Studios
        - Allows the user to retrieve all studios (IDs and names) which exist in the SQL database at the time of the query. If any studio is added manually while the programme is running, it will not appear on the list. 

- 7 - Divorce Actors
        - Allows the user to remove a current marriage relationship and replace it with a divorced relationship. The user is prompted to enter an actor's name. The full string must be inputted for the query to execute, although it is case insensitive. The SQL database is queried to return the actor's ID. The Neo4J database is then queried to determine if that actor is currently married. If a relationship exists, it is replaced with a divorced relationship. Finally, the SQL database is queried to retrieve both actors' names and inform the user that they are now divorced. 

- x - Exit Application
        - Allows the user to close the application 

