from model.Vaccine import Vaccine
from model.Caregiver import Caregiver
from model.Patient import Patient
from util.Util import Util
from db.ConnectionManager import ConnectionManager
import pymssql
import datetime


'''
objects to keep track of the currently logged-in user
Note: it is always true that at most one of currentCaregiver and currentPatient is not null
        since only one user can be logged-in at a time
'''
current_patient = None

current_caregiver = None


def create_patient(tokens):
    """
    TODO: Part 1
    """
    # create_patient <username> <password>
    # check 1: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Create patient failed")
        return

    username = tokens[1]
    password = tokens[2]
    # check 2: check if the username has been taken already
    if username_exists_patient(username):
        print("Username taken, try again")
        return

    salt = Util.generate_salt()
    hash = Util.generate_hash(password, salt)

    # create the patient
    patient = Patient(username, salt=salt, hash=hash)

    # save to caregiver information to our database
    try:
        patient.save_to_db()
    except pymssql.Error as e:
        print("Create patient failed")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Create patient failed")
        print("Error:", e)
        return
    print("Created user", username)
    #pass


def username_exists_patient(username):
    cm = ConnectionManager()
    conn = cm.create_connection()

    select_username = "SELECT * FROM Patients WHERE Username = %s"
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(select_username, username)
        #  returns false if the cursor is not before the first record or if there are no rows in the ResultSet.
        for row in cursor:
            return row['Username'] is not None
    except pymssql.Error as e:
        print("Error occurred when checking username")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when checking username")
        print("Error:", e)
    finally:
        cm.close_connection()
    return False


def create_caregiver(tokens):
    # create_caregiver <username> <password>
    # check 1: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Failed to create user.")
        return

    username = tokens[1]
    password = tokens[2]
    # check 2: check if the username has been taken already
    if username_exists_caregiver(username):
        print("Username taken, try again!")
        return

    salt = Util.generate_salt()
    hash = Util.generate_hash(password, salt)

    # create the caregiver
    caregiver = Caregiver(username, salt=salt, hash=hash)

    # save to caregiver information to our database
    try:
        caregiver.save_to_db()
    except pymssql.Error as e:
        print("Failed to create user.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Failed to create user.")
        print(e)
        return
    print("Created user ", username)


def username_exists_caregiver(username):
    cm = ConnectionManager()
    conn = cm.create_connection()

    select_username = "SELECT * FROM Caregivers WHERE Username = %s"
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(select_username, username)
        #  returns false if the cursor is not before the first record or if there are no rows in the ResultSet.
        for row in cursor:
            return row['Username'] is not None
    except pymssql.Error as e:
        print("Error occurred when checking username")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when checking username")
        print("Error:", e)
    finally:
        cm.close_connection()
    return False


def login_patient(tokens):
    """
    TODO: Part 1
    """
    # login_patient <username> <password>
    # check 1: if someone's already logged-in, they need to log out first
    global current_patient
    if current_patient is not None or current_caregiver is not None:
        print("User already logged in, try again")
        return

    # check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Login patient failed")
        return

    username = tokens[1]
    password = tokens[2]

    patient = None
    try:
        patient = Patient(username, password=password).get()
    except pymssql.Error as e:
        print("Login patient failed")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Login patient failed")
        print("Error:", e)
        return

    # check if the login was successful
    if patient is None:
        print("Login patient failed")
    else:
        print("Logged in as " + username)
        current_patient = patient
    #pass


def login_caregiver(tokens):
    # login_caregiver <username> <password>
    # check 1: if someone's already logged-in, they need to log out first
    global current_caregiver
    if current_caregiver is not None or current_patient is not None:
        print("User already logged in.")
        return

    # check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Login failed.")
        return

    username = tokens[1]
    password = tokens[2]

    caregiver = None
    try:
        caregiver = Caregiver(username, password=password).get()
    except pymssql.Error as e:
        print("Login failed.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Login failed.")
        print("Error:", e)
        return

    # check if the login was successful
    if caregiver is None:
        print("Login failed.")
    else:
        print("Logged in as: " + username)
        current_caregiver = caregiver


def search_caregiver_schedule(tokens):
    """
    TODO: Part 2
    """
    global current_patient
    global current_caregiver

    if current_patient is None and current_caregiver is None:
        print("Please login first")
        return

    if len(tokens) != 2:
        print("Please try again")
        return

    cm = ConnectionManager()
    conn = cm.create_connection()

    date = tokens[1]
    date_tokens = date.split("-")
    month = int(date_tokens[0])
    day = int(date_tokens[1])
    year = int(date_tokens[2])

    search_usernames = "SELECT A.Username FROM Availabilities AS A WHERE A.Time = %s ORDER BY A.Username;"
    search_vaccines =  "SELECT V.Name, V.Doses FROM Vaccines AS V;"
    try:
        cursor = conn.cursor(as_dict=True)
        d = datetime.datetime(year, month, day)

        cursor.execute(search_usernames, d)
        for row in cursor:
            print(row['Username'])

        cursor.execute(search_vaccines, d)
        for row in cursor:
            print(row['Name'], row['Doses'])

    except pymssql.Error as e:
        print("Please try again")
        print("Db-Error:", e)
    except Exception as e:
        print("Please try again")
        print("Error:", e)
        return
    finally:
        cm.close_connection()
    #pass


def reserve(tokens):
    """
    TODO: Part 2
    """
    global current_caregiver
    global current_patient
    
    if current_patient is None and current_caregiver is None:
        print("Please login first")
        return

    if current_caregiver is not None:
        print("Please login as a patient")
        return

    if len(tokens) != 3:
        print("Please try again")
        return

    cm = ConnectionManager()
    conn = cm.create_connection()

    date = tokens[1]
    vaccine_name = tokens[2]

    date_tokens = date.split("-")
    month = int(date_tokens[0])
    day = int(date_tokens[1])
    year = int(date_tokens[2])
    d = datetime.datetime(year, month, day)

    try:
        cursor = conn.cursor()
        id_query = "SELECT MAX(AppID) FROM Reservations;"
        cursor.execute(id_query)
        id_result = cursor.fetchone()
        if id_result[0] is None:
            app_id = 1
        else:
            app_id = id_result[0] + 1

        doses_query = "SELECT Doses FROM Vaccines WHERE Name = %s;"
        cursor.execute(doses_query, vaccine_name)
        doses_result = cursor.fetchone()
        if not doses_result or doses_result[0] < 1:
            print("Not enough available doses")
            return

        avail_query = "SELECT Username FROM Availabilities WHERE Time = %s ORDER BY Username;"
        cursor.execute(avail_query, d)
        caregiver_result = cursor.fetchone()
        if not caregiver_result:
            print("No caregiver is available")
            return

        caregiver_username = caregiver_result[0]

        insert_query = "INSERT INTO Reservations (AppID, PatientName, CaregiverName, VaccineName, Time) VALUES (%s, %s, %s, %s, %s);"
        cursor.execute(insert_query, (app_id, current_patient.username, caregiver_username, vaccine_name, d))
        conn.commit()

        delete_query = "DELETE FROM Availabilities WHERE Username = %s AND Time = %s;"
        cursor.execute(delete_query, (caregiver_username, d))
        conn.commit()

        print(f"Appointment ID {app_id}, Caregiver username {caregiver_username}")

        update_query = "UPDATE Vaccines SET Doses = Doses - 1 WHERE Name = %s;"
        cursor.execute(update_query, vaccine_name)
        conn.commit()

    except pymssql.Error as e:
        print("Please try again")
        print("Db-Error:", e)
    except Exception as e:
        print("Please try again")
        print("Error:", e)
        return
    finally:
        cm.close_connection()
    #pass


def upload_availability(tokens):
    #  upload_availability <date>
    #  check 1: check if the current logged-in user is a caregiver
    global current_caregiver
    if current_caregiver is None:
        print("Please login as a caregiver first!")
        return

    # check 2: the length for tokens need to be exactly 2 to include all information (with the operation name)
    if len(tokens) != 2:
        print("Please try again!")
        return

    date = tokens[1]
    # assume input is hyphenated in the format mm-dd-yyyy
    date_tokens = date.split("-")
    month = int(date_tokens[0])
    day = int(date_tokens[1])
    year = int(date_tokens[2])
    try:
        d = datetime.datetime(year, month, day)
        current_caregiver.upload_availability(d)
    except pymssql.Error as e:
        print("Upload Availability Failed")
        print("Db-Error:", e)
        quit()
    except ValueError:
        print("Please enter a valid date!")
        return
    except Exception as e:
        print("Error occurred when uploading availability")
        print("Error:", e)
        return
    print("Availability uploaded!")


def cancel(tokens):
    """
    TODO: Extra Credit - Cancel Appointment
    """
    global current_caregiver
    global current_patient

    if current_caregiver is None and current_patient is None:
        print("Please login first")
        return

    if len(tokens) != 2:
        print("Please try again")
        return

    app_id = tokens[1]

    try:
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor(as_dict=True)

        if current_caregiver:
            search_caregiver = "SELECT * FROM Reservations WHERE AppID = %s AND CaregiverName = %s;"
            cursor.execute(search_caregiver, (app_id, current_caregiver.username))
        elif current_patient:
            search_patient = "SELECT * FROM Reservations WHERE AppID = %s AND PatientName = %s;"
            cursor.execute(search_patient, (app_id, current_patient.username))
        
        appointment = cursor.fetchone()
        if not appointment:
            print("Appointment doesn't exist")
            return
        vaccine_name = appointment["VaccineName"]
        caregiver_name = appointment["CaregiverName"]
        d = appointment["Time"]

        delete_query = "DELETE FROM Reservations WHERE AppID = %s;"
        cursor.execute(delete_query, (app_id,))

        add_query = "INSERT INTO Availabilities VALUES (%s, %s);"
        cursor.execute(add_query, (d, caregiver_name))

        update_query = "UPDATE Vaccines SET Doses = Doses + 1 WHERE Name = %s;"
        cursor.execute(update_query, (vaccine_name,))
        conn.commit()
        print(f"Appointment {app_id} canceled")

    except pymssql.Error as e:
        print("Please try again")
        print("Db-Error:", e)
    except Exception as e:
        print("Please try again")
        print("Error:", e)
        return
    finally:
        cm.close_connection()
    #pass


'''
def strong_password(password):
    """
    TODO: Extra Credit - Password
    """
    uppercase = False
    lowercase = False
    letter = False
    number = False
    special = False

    if len(password) < 8:
        print("At least 8 characters")
        return False

    special_characters = ['!', '@', '#', '?']

    for digit in password:
        if digit.isupper():
            uppercase = True
        if digit.islower():
            lowercase = True
        if digit.isalpha():
            letter = True
        if digit.isnumeric():
            number = True
        if digit in special_characters:
            special = True

    if not (uppercase and lowercase):
        print("A mixture of both uppercase and lowercase letters")
        return False

    if not (letter and number):
        print("A mixture of letters and numbers")
        return False

    if not special:
        print("Inclusion of at least one special character, from “!”, “@”, “#”, “?”")
        return False

    return True
'''


def add_doses(tokens):
    #  add_doses <vaccine> <number>
    #  check 1: check if the current logged-in user is a caregiver
    global current_caregiver
    if current_caregiver is None:
        print("Please login as a caregiver first!")
        return

    #  check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Please try again!")
        return

    vaccine_name = tokens[1]
    doses = int(tokens[2])
    vaccine = None
    try:
        vaccine = Vaccine(vaccine_name, doses).get()
    except pymssql.Error as e:
        print("Error occurred when adding doses")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when adding doses")
        print("Error:", e)
        return

    # if the vaccine is not found in the database, add a new (vaccine, doses) entry.
    # else, update the existing entry by adding the new doses
    if vaccine is None:
        vaccine = Vaccine(vaccine_name, doses)
        try:
            vaccine.save_to_db()
        except pymssql.Error as e:
            print("Error occurred when adding doses")
            print("Db-Error:", e)
            quit()
        except Exception as e:
            print("Error occurred when adding doses")
            print("Error:", e)
            return
    else:
        # if the vaccine is not null, meaning that the vaccine already exists in our table
        try:
            vaccine.increase_available_doses(doses)
        except pymssql.Error as e:
            print("Error occurred when adding doses")
            print("Db-Error:", e)
            quit()
        except Exception as e:
            print("Error occurred when adding doses")
            print("Error:", e)
            return
    print("Doses updated!")


def show_appointments(tokens):
    """
    TODO: Part 2
    """
    global current_caregiver
    global current_patient

    if len(tokens) != 1:
        print("Please try again")
        return

    if current_caregiver is None and current_patient is None:
        print("Please login first")
        return

    cm = ConnectionManager()
    conn = cm.create_connection()

    try:
        cursor = conn.cursor(as_dict=True)
        if current_patient is not None:
            patient_query = "SELECT AppID, VaccineName, Time, CaregiverName FROM Reservations WHERE PatientName = %s ORDER BY AppID;"
            cursor.execute(patient_query, current_patient.username)
        elif current_caregiver is not None:
            caregiver_query = "SELECT AppID, VaccineName, Time, PatientName FROM Reservations WHERE CaregiverName = %s ORDER BY AppID;"
            cursor.execute(caregiver_query, current_caregiver.username)

        appointments = cursor.fetchall()
        if not appointments:
            print("No scheduled appointments")
            return

        for row in appointments:
            appointment_id = row['AppID']
            vaccine_name = row['VaccineName']
            appointment_date = row['Time']

            year = appointment_date.year
            month = f"{appointment_date.month:02d}"
            day = f"{appointment_date.day:02d}"
            formatted_date = f"{month}-{day}-{year}"

            username = row['PatientName'] if current_caregiver is not None else row['CaregiverName']
            print(f"{appointment_id} {vaccine_name} {formatted_date} {username}")

    except pymssql.Error as e:
        print("Please try again")
        print("Db-Error:", e)
    except Exception as e:
        print("Please try again")
        print("Error:", e)
        return
    finally:
        cm.close_connection()
    #pass


def logout(tokens):
    """
    TODO: Part 2
    """
    global current_caregiver
    global current_patient

    if len(tokens) != 1:
        print("Please try again")
        return

    if current_caregiver is None and current_patient is None:
        print("Please login first")
        return
    else:
        try:
            current_caregiver = None
            current_patient = None
            print("Successfully logged out")
            return
        except pymssql.Error as e:
            print("Please try again", e)
        except Exception as e:
            print("Please try again", e)
    #pass


def start():
    stop = False
    while not stop:
        print()
        print(" *** Please enter one of the following commands *** ")
        print("> create_patient <username> <password>")  # //TODO: implement create_patient (Part 1)
        print("> create_caregiver <username> <password>")
        print("> login_patient <username> <password>")  # // TODO: implement login_patient (Part 1)
        print("> login_caregiver <username> <password>")
        print("> search_caregiver_schedule <date>")  # // TODO: implement search_caregiver_schedule (Part 2)
        print("> reserve <date> <vaccine>")  # // TODO: implement reserve (Part 2)
        print("> upload_availability <date>")
        print("> cancel <appointment_id>")  # // TODO: implement cancel (extra credit)
        print("> add_doses <vaccine> <number>")
        print("> show_appointments")  # // TODO: implement show_appointments (Part 2)
        print("> logout")  # // TODO: implement logout (Part 2)
        print("> Quit")
        print()

        response = ""
        print("> ", end='')

        try:
            response = str(input())
        except ValueError:
            print("Please try again!")
            break

        response = response.lower()
        tokens = response.split(" ")
        if len(tokens) == 0:
            ValueError("Please try again!")
            continue
        operation = tokens[0]
        if operation == "create_patient":
            create_patient(tokens)
        elif operation == "create_caregiver":
            create_caregiver(tokens)
        elif operation == "login_patient":
            login_patient(tokens)
        elif operation == "login_caregiver":
            login_caregiver(tokens)
        elif operation == "search_caregiver_schedule":
            search_caregiver_schedule(tokens)
        elif operation == "reserve":
            reserve(tokens)
        elif operation == "upload_availability":
            upload_availability(tokens)
        elif operation == "cancel":
            cancel(tokens)
        elif operation == "add_doses":
            add_doses(tokens)
        elif operation == "show_appointments":
            show_appointments(tokens)
        elif operation == "logout":
            logout(tokens)
        elif operation == "quit":
            print("Bye!")
            stop = True
        else:
            print("Invalid operation name!")


if __name__ == "__main__":
    '''
    // pre-define the three types of authorized vaccines
    // note: it's a poor practice to hard-code these values, but we will do this ]
    // for the simplicity of this assignment
    // and then construct a map of vaccineName -> vaccineObject
    '''

    # start command line
    print()
    print("Welcome to the COVID-19 Vaccine Reservation Scheduling Application!")

    start()
