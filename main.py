from tkinter import *
from interface import BudgetGUI
import database as db

def main():
    # Create the main window
    root = Tk()

    # Initialize the database
    db.create_tables()

    # Create and start the UI
    app = BudgetGUI(root)

    # Start the application
    app.run()

if __name__ == "__main__":
    main()