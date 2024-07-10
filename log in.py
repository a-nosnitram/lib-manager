import mysql.connector
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QApplication, QMessageBox, QTableWidgetItem, QPushButton, QTableWidget, QComboBox
from PyQt5.QtCore import Qt

# Connecting to the database
def connection():
    conn = mysql.connector.connect(
        host="localhost",  # server
        port=3306,  # predefined port
        user="root",  # name of the user
        password="",
        database="database school"
    )
    return conn

#--------------------------------------------------------------------------------------------------------------------

# Function to check if the user exists in the database
def check_user(Id, password):
    conn = connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM student WHERE Id=%s AND password=%s AND role='librarian'", (Id, password))
    user = cursor.fetchone()
    conn.close()
    return user

# Function to handle the login button click event
def handle_login():
    Id = window.username_input.text()
    password = window.password_input.text()
    user = check_user(Id, password)
    if user is None:
        # Show error message if the user is not found in the database
        QMessageBox.critical(window, "error", "Invalid username or password")
    else:
        # Show success message and proceed to the main library window
        QMessageBox.information(window, "success", "Login successful")
        open_library_window()
        window.close()

#-------------------------------------------------------------------------------------------------------------------

def update_book(new_value, row, col):
    isbn = library_window.book_list.item(row, 0).text()  # Get ISBN value from the first column
    column_name = library_window.book_list.horizontalHeaderItem(col).text()  # Get the column name
    update_book_in_db(isbn, column_name, new_value)
    QMessageBox.information(library_window, "Success", "Book availability updated successfully")
    display_books()

def delete_book(row):
    isbn_item = library_window.book_list.item(row, 0)
    isbn = isbn_item.text()

    conn = connection()
    cursor = conn.cursor()
    query = "DELETE FROM books WHERE ISBN=%s"
    cursor.execute(query, (isbn,))
    conn.commit()
    conn.close()

    display_books()

def insert_book():
    isbn = library_window.isbn.text()
    name = library_window.name.text()
    author = library_window.author.text()
    year = library_window.year.text()
    description = library_window.description.text()

    conn = connection()
    cursor = conn.cursor()
    query = "INSERT INTO books (ISBN, name, author, year, description) VALUES (%s, %s, %s, %s, %s)"
    cursor.execute(query, (isbn, name, author, year, description))
    conn.commit()
    conn.close()

    display_books()

    library_window.isbn.clear()
    library_window.name.clear()
    library_window.author.clear()
    library_window.year.clear()
    library_window.description.clear()

def open_library_window():
    global library_window
    library_window = loadUi("library.ui")

    library_window.insert_button.clicked.connect(insert_book)

    library_window.show()

    display_books()

def display_books():
    library_window.book_list.clearContents()

    conn = connection()
    cursor = conn.cursor()
    query = "SELECT * FROM books"
    cursor.execute(query)
    books = cursor.fetchall()
    conn.close()

    library_window.book_list.setRowCount(len(books))
    library_window.book_list.setColumnCount(7)

    headers = ["ISBN", "name", "author", "year", "availability", "description", " "]
    library_window.book_list.setHorizontalHeaderLabels(headers)

    for row, book in enumerate(books):
        for col, value in enumerate(book):
            if col == 4:
                combo_box = QComboBox()
                combo_box.addItems(["Available", "Borrowed"])
                combo_box.setCurrentText(value)
                combo_box.currentTextChanged.connect(lambda text, r=row, c=col: update_book(text, r, c))
                library_window.book_list.setCellWidget(row, col, combo_box)
            else:
                item = QTableWidgetItem(str(value))
                library_window.book_list.setItem(row, col, item)

        delete_button = QPushButton("Delete")
        delete_button.clicked.connect(lambda _, r=row: delete_book(r))
        library_window.book_list.setCellWidget(row, 6, delete_button)

        # Allow editing in other columns
        for col in range(6):
            item = library_window.book_list.item(row, col)
            if item is not None:
                item.setFlags(item.flags() | Qt.ItemIsEditable)

    library_window.book_list.cellChanged.connect(update_database)

#-------------------------------------------------------------------------------------------------------------------

def update_database(row, col):
    item = library_window.book_list.item(row, col)
    if item is not None:
        new_value = item.text()
        isbn = library_window.book_list.item(row, 0).text()
        column_name = library_window.book_list.horizontalHeaderItem(col).text()
        update_book_in_db(isbn, column_name, new_value)

def update_book_in_db(isbn, column_name, new_value):
    conn = connection()
    cursor = conn.cursor()

    query = f"UPDATE books SET {column_name} = %s WHERE ISBN = %s"
    values = (str(new_value), str(isbn))

    cursor.execute(query, values)

    conn.commit()
    conn.close()

#------------------------------------------------------------------------------------------------------------------

app = QApplication([])
window = loadUi("login.ui")

window.login_button.clicked.connect(handle_login)

window.show()
app.exec_()
