import pymysql
import pymysql.cursors



def main():
    conn = pymysql.connect(
        host ="localhost",
        user = "root",
        password = "root",
        database = "hospital",
        cursorclass=pymysql.cursors.DictCursor)
    ppsn = input(f'Enter New Patient Details\nPPSN:')
    fname = input(f'Enter New Patient Details\nFirst Name:')
    sname = input(f'Enter New Patient Details\nSurname:')
    add = input(f'Enter New Patient Details\nAddress:')
    docid = input(f'Enter New Patient Details\nDoctor ID:')

    values = (ppsn, fname, sname, add, docid)

    #query_ppsn = "SELECT 1 FROM patient_table WHERE ppsn = %s LIMIT 1"
    #query_docid = "SELECT 1 FROM patient_table WHERE doctorID = %s LIMIT 1"
    query_insert = "INSERT INTO patient_table(ppsn, first_name, surname, address, doctorID) VALUES (%s, %s, %s, %s, %s)"

    try:
       with conn:   
            cursor = conn.cursor()
            cursor.execute(query_insert, values)
            conn.commit()
            print("Insert Successful")

    except pymysql.err.IntegrityError as e:
            error_code = e.args[0]
            error_msg = str(e)

            if (error_code == 1062 and "PRIMARY" in error_msg) or (error_code == 1452 and "doctorID" in error_msg):
                 print("Existing PPSN, or non-existant DoctorID entered")
            else:
                 print("Integrity Error:", e)

    except pymysql.DataError as e:
            error_code = e.args[0]
            print("Invalid value entered for Doctor ID")
   # if not isinstance(docid, int):
       # end_statement =  "Invalid value entered for Doctor ID"

          

           # cursor.execute(query_ppsn, (ppsn,))
           # result_ppsn = cursor.fetchone()

        #cursor.execute(query_docid, (docid,))
      #  result_docid = cursor.fetchone()
        
      #  cursor.execute(query_insert, values)

        #if result_ppsn or result_docid:
           # end_statement2 = "Existing PPSN, or non-existant DoctorID entered"

    #final_statement = " ".join(part for part in [end_statement, end_statement2] if part)
    #print(final_statement)

if __name__ == "__main__":
    main()


