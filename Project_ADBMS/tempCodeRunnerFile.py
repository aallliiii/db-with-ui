from database_man import DatabaseManager

def main():
    database = DatabaseManager()
    while True:
        print("\nMain Menu:")
        print("1. Create a new database")
        print("2. Use an existing database")
        print("3. Delete an existing database")
        print("4. Exit")
        choice = input("Enter your choice: ")

        if choice == "1":
            database.create_database()
        elif choice == "2":
            db_name = database.use_database()
            if db_name:
                database.table_menu()
        elif choice == "3":
            database.delete_database()
        elif choice == "4":
            print("Exiting the program. Goodbye!")
            break
        else:
            print("Invalid choice! Please try again.")

if __name__ == "__main__":
    main()
