from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root:@localhost/library-system"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = "abcd2123445"

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(100), nullable=False)

class Book(db.Model):
    bookid = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    isbn = db.Column(db.String(100), nullable=False)
    no_of_copy = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(100), nullable=False)
    authorid = db.Column(db.String(100), db.ForeignKey("author.authorid"))
    categoryid = db.Column(db.String(100), db.ForeignKey("category.categoryid"))
    rackid = db.Column(db.String(10), db.ForeignKey("rack.rackid"))
    publisherid = db.Column(db.String(100), db.ForeignKey("publisher.publisherid"))

class Author(db.Model):
    authorid = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(100), nullable=False)

class Category(db.Model):
    categoryid = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(100), nullable=False)

class Rack(db.Model):
    rackid = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(100), nullable=False)

class Publisher(db.Model):
    publisherid = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(100), nullable=False)     
class IssuedBook(db.Model):
    issuebookid = db.Column(db.Integer, primary_key=True)
    bookname = db.Column(db.String(100), db.ForeignKey("book.bookid"))
    userid = db.Column(db.Integer, db.ForeignKey("user.id"))
    issue_date = db.Column(db.DateTime, nullable=False)
    due_date = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(100), nullable=False)

@app.route("/")
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        user = User.query.filter_by(email=email, password=password).first()
        if user:
            session["loggedin"] = True
            session["userid"] = user.id
            session["name"] = user.first_name
            session["email"] = user.email
            session["role"] = user.role
            return redirect(url_for("dashboard"))
        else:
            return "Invalid email or password"
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if "loggedin" in session:
        total_books = Book.query.count()
        available_books = Book.query.filter_by(is_available=True).count()
        issued_books = IssuedBook.query.filter_by(return_date=None).count()
        returned_books = IssuedBook.query.filter(IssuedBook.return_date.isnot(None)).count()
        
        return render_template("dashboard.html", 
                               total_books=total_books, 
                               available_books=available_books, 
                               issued_books=issued_books, 
                               returned_books=returned_books)
    return redirect(url_for("login"))

@app.route("/user")
def user():
    if "loggedin" in session:
        users = User.query.all()
        return render_template("users.html", users=users)
    return redirect(url_for("login"))

@app.route("/save_users", methods=["GET", "POST"])
def save_users():
    if "loggedin" in session:
        if request.method == "POST":
            first_name = request.form["first_name"]
            last_name = request.form["last_name"]
            email = request.form["email"]
            role = request.form["role"]
            action = request.form["action"]
            if action == "updateUser":
                userid = request.form["userid"]
                user = User.query.get(userid)
                user.first_name = first_name
                user.last_name = last_name
                user.email = email
                user.role = role
                db.session.commit()
            else:
                user = User(first_name=first_name, last_name=last_name, email=email, role=role)
                db.session.add(user)
                db.session.commit()
            return redirect(url_for("users"))
        return redirect(url_for("users"))
    return redirect(url_for("login"))

@app.route("/edit_users")
def edit_users():
    if "loggedin" in session:
        userid = request.args.get("userid")
        user = User.query.get(userid)
        return render_template("edit_user.html", user=user)
    return redirect(url_for("login"))

@app.route("/view_users")
def view_users():
    if "loggedin" in session:
        userid = request.args.get("userid")
        user = User.query.get(userid)
        return render_template("view_user.html", user=user)
    return redirect(url_for("login"))

@app.route("/password_change")
def password_change():
    if "loggedin" in session:
        changePassUserId = request.args.get("userid")
        return render_template("password_change.html", changePassUserId=changePassUserId)
    return redirect(url_for("login"))

@app.route("/save_password", methods=["POST"])
def save_password():
    if "loggedin" in session:
        password = request.form["password"]
        userid = request.form["userid"]
        user = User.query.get(userid)
        user.password = password
        db.session.commit()
        return redirect(url_for("users"))
    return redirect(url_for("login"))

@app.route("/delete_users", methods=["GET"])
def delete_users():
    if "loggedin" in session:
        userid = request.args.get("userid")
        user = User.query.get(userid)
        db.session.delete(user)
        db.session.commit()
        return redirect(url_for("users"))
    return redirect(url_for("login"))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        userName = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        user = User(first_name=userName, email=email, password=password)
        db.session.add(user)
        db.session.commit()
        return "You have successfully registered!"
    return render_template("register.html")

# Manage Books
@app.route("/books")
def books():
    if "loggedin" in session:
        books = Book.query.all()
        authors = Author.query.all()
        publishers = Publisher.query.all()
        categories = Category.query.all()
        racks = Rack.query.all()
        return render_template("books.html", books=books,authors=authors,publishers=publishers,categories=categories,racks=racks)
    return redirect(url_for("login"))


@app.route("/save_book", methods=["POST"])
def save_book():
    if "loggedin" in session:
        bookName = request.form["name"]
        isbn = request.form["isbn"]
        no_of_copy = request.form["no_of_copy"]
        author = request.form["author"]
        publisher = request.form["publisher"]
        category = request.form["category"]
        rack = request.form["rack"]
        status = request.form["status"]
        action = request.form["action"]
        if action == "updateBook":
            bookid = request.form["bookid"]
            book = Book.query.get(bookid)
            book.name = bookName
            book.isbn = isbn
            book.no_of_copy = no_of_copy
            book.authorid = author
            book.categoryid = category
            book.publisherid = publisher
            book.rackid = rack
            book.status = status
            db.session.commit()
        else:
            book = Book(name=bookName, isbn=isbn, no_of_copy=no_of_copy, authorid=author, categoryid=category, publisherid=publisher, rackid=rack, status=status)
            db.session.add(book)
            db.session.commit()
        return redirect(url_for("books"))
    return redirect(url_for("login"))

@app.route("/delete_book", methods=["GET"])
def delete_book():
    if "loggedin" in session:
        bookid = request.args.get("bookid")
        book = Book.query.get(bookid)
        db.session.delete(book)
        db.session.commit()
        return redirect(url_for("books"))
    return redirect(url_for("login"))

@app.route("/add_stock", methods=["GET", "POST"])
def add_stock():
    if "loggedin" in session:
        bookid = request.args.get("bookid")
        no_of_stock = request.form["no_of_stock"]
        book = Book.query.get(bookid)
        book.no_of_copy += no_of_stock
        db.session.commit()
        return redirect(url_for("books"))
    return redirect(url_for("login"))

@app.route("/search_book", methods=["POST"])
def search_book():
    if "loggedin" in session:
        search_keyword = request.form["search_keyword"]
        books = Book.query.filter(Book.name.like(f"%{search_keyword}%")).all()
        return render_template("books.html", books=books)
    return redirect(url_for("login"))

@app.route("/view_book")
def view_book():
    if "loggedin" in session:
        bookid = request.args.get("bookid")
        book = Book.query.get(bookid)
        return render_template("view_book.html", book=book)
    return redirect(url_for("login"))

@app.route("/book_status_change", methods=["GET"])
def book_status_change():
    if "loggedin" in session:
        bookid = request.args.get("bookid")
        status = request.args.get("status")
        book = Book.query.get(bookid)
        book.status = status
        db.session.commit()
        return redirect(url_for("books"))
    return redirect(url_for("login"))

# Manage Issues
@app.route('/issue_book', methods=['GET', 'POST'])
def issue_book():
    if "loggedin" in session:
        issues = IssuedBook.query.all()
        users = User.query.all()
        books = Book.query.all()
        return render_template("issue_book.html", issues=issues, users=users, books=books)
    return redirect(url_for("login"))

@app.route("/edit_issue_book")
def edit_issue():
    if "loggedin" in session:
        issueid = request.args.get("issueid")
        issue = IssuedBook.query.get(issueid)
        users = User.query.all()
        books = Book.query.all()
        return render_template("edit_issue_book.html", issue=issue, users=users, books=books)
    return redirect(url_for("login"))

@app.route("/save_issue", methods=["POST"])
def save_issue():
    if "loggedin" in session:
        
            # Fetching data from the form
        bookname = request.form["book"]
        userid = request.form["users"]
        issue_date = request.form["expected_return_date"]
        due_date = request.form["return_date"]
        status = request.form["status"]
        
        # Check if issuebookid is provided (for update scenarios)
        issuebookid = request.form.get("issuebookid")
        
        if issuebookid:
            issue = IssuedBook.query.get(issuebookid)
            if issue:
                # Update existing issue
                issue.bookname = bookname
                issue.userid = userid
                issue.issue_date = issue_date
                issue.due_date = due_date
                issue.status = status
            else:
                return f"Issue ID {issuebookid} not found", 404
        else:
            # Create a new issue record
            issue = IssuedBook(bookname=bookname, userid=userid, issue_date=issue_date, due_date=due_date, status=status)
            db.session.add(issue)
        
        db.session.commit()
        return redirect(url_for("issue_book"))
    return redirect(url_for("login"))

    
@app.route("/delete_issue", methods=["GET"])
def delete_issue():
    if "loggedin" in session:
        issuebookid = request.args.get("issuebookid")
        issue = IssuedBook.query.get(issuebookid)
        db.session.delete(issue)
        db.session.commit()
        return redirect(url_for("issue_book"))
    return redirect(url_for("login"))

@app.route("/view_issue")
def view_issue():
    if "loggedin" in session:
        issueid = request.args.get("issueid")
        issue = IssuedBook.query.get(issueid)
        return render_template("issue_book.html", issue=issue)
    return redirect(url_for("login"))

@app.route("/search_issue", methods=["POST"])
def search_issue():
    if "loggedin" in session:
        search_keyword = request.form["search_keyword"]
        issues = IssuedBook.query.filter(IssuedBook.issue_date.like(f"%{search_keyword}%")).all()
        return render_template("issue_book.html", issues=issues)
    return redirect(url_for("login"))

# Manage Users
@app.route("/users")
def users():
    if "loggedin" in session:
        users = User.query.all()
        return render_template("users.html", users=users)
    return redirect(url_for("login"))

@app.route("/add_user", methods=["GET", "POST"])
def add_user():
    if "loggedin" in session:
        if request.method == "POST":
            userName = request.form["userName"]
            userEmail = request.form["userEmail"]
            userContact = request.form["userContact"]
            userRole = request.form["userRole"]
            user = User(name=userName, email=userEmail, contact=userContact, role=userRole)
            db.session.add(user)
            db.session.commit()
            return redirect(url_for("users"))
        return render_template("add_user.html")
    return redirect(url_for("login"))

@app.route("/edit_user")
def edit_user():
    if "loggedin" in session:
        userid = request.args.get("userid")
        user = User.query.get(userid)
        return render_template("edit_user.html", user=user)
    return redirect(url_for("login"))

@app.route("/save_user", methods=["POST"])
def save_user():
    if "loggedin" in session:
        userid = request.form["userid"]
        userName = request.form["userName"]
        userEmail = request.form["userEmail"]
        userContact = request.form["userContact"]
        userRole = request.form["userRole"]
        if userid == "":
            user = User(name=userName, email=userEmail, contact=userContact, role=userRole)
            db.session.add(user)
        else:
            user = User.query.get(userid)
            user.name = userName
            user.email = userEmail
            user.contact = userContact
            user.role = userRole
        db.session.commit()
        return redirect(url_for("users"))
    return redirect(url_for("login"))

@app.route("/delete_user", methods=["GET"])
def delete_user():
    if "loggedin" in session:
        userid = request.args.get("userid")
        user = User.query.get(userid)
        db.session.delete(user)
        db.session.commit()
        return redirect(url_for("users"))
    return redirect(url_for("login"))

@app.route("/view_user")
def view_user():
    if "loggedin" in session:
        userid = request.args.get("userid")
        user = User.query.get(userid)
        return render_template("view_user.html", user=user)
    return redirect(url_for("login"))
# Manage Category
@app.route("/category", methods=["GET", "POST"])
def category():
    if "loggedin" in session:
        categories = Category.query.all()
        return render_template("category.html", categories=categories)
    return redirect(url_for("login"))

@app.route("/saveCategory", methods=["POST"])
def saveCategory():
    if "loggedin" in session:
        name = request.form["name"]
        status = request.form["status"]
        action = request.form["action"]
        
        if action == "updateCategory":
            categoryid = request.form["categoryid"]
            category = Category.query.get(categoryid)
            category.name = name
            category.status = status
        else:
            category = Category(name=name, status=status)
            db.session.add(category)
        
        db.session.commit()
        return redirect(url_for("category"))
    return redirect(url_for("login"))

@app.route("/editCategory")
def editCategory():
    if "loggedin" in session:
        categoryid = request.args.get("categoryid")
        category = Category.query.get(categoryid)
        return render_template("edit_category.html", category=category)
    return redirect(url_for("login"))

@app.route("/delete_category", methods=["GET"])
def delete_category():
    if "loggedin" in session:
        categoryid = request.args.get("categoryid")
        category = Category.query.get(categoryid)
        db.session.delete(category)
        db.session.commit()
        return redirect(url_for("category"))
    return redirect(url_for("login"))

# Manage Author
@app.route("/author", methods=["GET", "POST"])
def author():
    if "loggedin" in session:
        authors = Author.query.all()
        return render_template("author.html", authors=authors)
    return redirect(url_for("login"))

@app.route("/saveAuthor", methods=["POST"])
def saveAuthor():
    if "loggedin" in session:
        name = request.form["name"]
        status = request.form["status"]
        action = request.form["action"]
        
        if action == "updateAuthor":
            authorid = request.form["authorid"]
            author = Author.query.get(authorid)
            author.name = name
            author.status = status
        else:
            author = Author(name=name, status=status)
            db.session.add(author)
        
        db.session.commit()
        return redirect(url_for("author"))
    return redirect(url_for("login"))

@app.route("/editAuthor")
def editAuthor():
    if "loggedin" in session:
        authorid = request.args.get("authorid")
        author = Author.query.get(authorid)
        return render_template("edit_author.html", author=author)
    return redirect(url_for("login"))

@app.route("/delete_author", methods=["GET"])
def delete_author():
    if "loggedin" in session:
        authorid = request.args.get("authorid")
        author = Author.query.get(authorid)
        db.session.delete(author)
        db.session.commit()
        return redirect(url_for("author"))
    return redirect(url_for("login"))

# Manage Publisher
@app.route("/publisher", methods=["GET", "POST"])
def publisher():
    if "loggedin" in session:
        publishers = Publisher.query.all()
        return render_template("publisher.html", publishers=publishers)
    return redirect(url_for("login"))

@app.route("/savePublisher", methods=["POST"])
def savePublisher():
    if "loggedin" in session:
        name = request.form["name"]
        status = request.form["status"]
        action = request.form["action"]
        
        if action == "updatePublisher":
            publisherid = request.form["publisherid"]
            publisher = Publisher.query.get(publisherid)
            publisher.name = name
            publisher.status = status
        else:
            publisher = Publisher(name=name, status=status)
            db.session.add(publisher)
        
        db.session.commit()
        return redirect(url_for("publisher"))
    return redirect(url_for("login"))

@app.route("/editPublisher")
def editPublisher():
    if "loggedin" in session:
        publisherid = request.args.get("publisherid")
        publisher = Publisher.query.get(publisherid)
        return render_template("edit_publisher.html", publisher=publisher)
    return redirect(url_for("login"))

@app.route("/delete_publisher", methods=["GET"])
def delete_publisher():
    if "loggedin" in session:
        publisherid = request.args.get("publisherid")
        publisher = Publisher.query.get(publisherid)
        db.session.delete(publisher)
        db.session.commit()
        return redirect(url_for("publisher"))
    return redirect(url_for("login"))

# Manage Rack
@app.route("/rack", methods=["GET", "POST"])
def rack():
    if "loggedin" in session:
        racks = Rack.query.all()
        return render_template("rack.html", racks=racks)
    return redirect(url_for("login"))

@app.route("/saveRack", methods=["POST"])
def saveRack():
    if "loggedin" in session:
        name = request.form["name"]
        status = request.form["status"]
        action = request.form["action"]
        
        if action == "updateRack":
            rackid = request.form["rackid"]
            rack = Rack.query.get(rackid)
            rack.name = name
            rack.status = status
        else:
            rack = Rack(name=name, status=status)
            db.session.add(rack)
        
        db.session.commit()
        return redirect(url_for("rack"))
    return redirect(url_for("login"))

@app.route("/editRack")
def editRack():
    if "loggedin" in session:
        rackid = request.args.get("rackid")
        rack = Rack.query.get(rackid)
        return render_template("edit_rack.html", rack=rack)
    return redirect(url_for("login"))

@app.route("/delete_rack", methods=["GET"])
def delete_rack():
    if "loggedin" in session:
        rackid = request.args.get("rackid")
        rack = Rack.query.get(rackid)
        db.session.delete(rack)
        db.session.commit()
        return redirect(url_for("rack"))
    return redirect(url_for("login"))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# Error Handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template("404.html"), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template("500.html"), 500

# Start the server
if __name__ == "__main__":
    app.run(debug=True)