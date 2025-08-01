from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin, current_user
import os
from werkzeug.utils import secure_filename
from PyPDF2 import PdfReader
from fpdf import FPDF

app = Flask(__name__)
app.secret_key = 'your-secret-key'

# Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

users = {'admin': {'password': 'admin123'}}

class User(UserMixin):
    def __init__(self, username):
        self.id = username

@login_manager.user_loader
def load_user(user_id):
    if user_id in users:
        return User(user_id)
    return None

UPLOAD_FOLDER = os.path.expanduser("~/Documents/Sample")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

FONT_PATH = r"C:\Users\User\Desktop\SE_Skill\py\dejavu-fonts-ttf-2.37\ttf\DejaVuSans.ttf"

# Routes
@app.route("/")
def home():
    return render_template("home.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if username in users and users[username]["password"] == password:
            login_user(User(username))
            flash("Logged in successfully.")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid credentials.")
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out.")
    return redirect(url_for("home"))

@app.route("/dashboard")
@login_required
def dashboard():
    pdfs = [f for f in os.listdir(UPLOAD_FOLDER) if f.endswith(".pdf")]
    return render_template("dashboard.html", pdfs=pdfs)

@app.route("/create", methods=["POST"])
@login_required
def create():
    filename = request.form.get("filename", "").strip()
    content = request.form.get("content", "").strip()
    if not filename or not content:
        flash("Both filename and content are required.")
        return redirect(url_for("dashboard"))

    try:
        pdf = FPDF()
        pdf.add_page()
        if os.path.exists(FONT_PATH):
            pdf.add_font("DejaVu", "", FONT_PATH, uni=True)
            pdf.set_font("DejaVu", "", 12)
        else:
            pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, content)
        save_path = os.path.join(UPLOAD_FOLDER, secure_filename(filename) + ".pdf")
        pdf.output(save_path)
        flash("PDF created successfully.")
    except Exception as e:
        flash(f"Error: {e}")
    return redirect(url_for("dashboard"))

@app.route("/upload", methods=["POST"])
@login_required
def upload():
    file = request.files.get("file")
    if file and file.filename.endswith(".pdf"):
        filename = secure_filename(file.filename)
        file.save(os.path.join(UPLOAD_FOLDER, filename))
        flash("PDF uploaded successfully.")
    else:
        flash("Only PDF files allowed.")
    return redirect(url_for("dashboard"))

@app.route("/read/<filename>")
@login_required
def read(filename):
    path = os.path.join(UPLOAD_FOLDER, filename)
    try:
        reader = PdfReader(path)
        content = "\n\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
        return render_template("read.html", filename=filename, content=content)
    except Exception as e:
        flash(f"Error reading file: {e}")
        return redirect(url_for("dashboard"))

@app.route("/delete/<filename>")
@login_required
def delete(filename):
    try:
        os.remove(os.path.join(UPLOAD_FOLDER, filename))
        flash("PDF deleted successfully.")
    except Exception as e:
        flash(f"Error: {e}")
    return redirect(url_for("dashboard"))

if __name__ == "__main__":
    app.run()
