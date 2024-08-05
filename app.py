from flask import Flask, render_template, request, redirect, url_for
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import sqlite3

app = Flask(__name__)

def send_email(to_email, message, subject="Contact Form Submission"):
    from_email = "Codeoclock.cit@gmail.com"
    from_password = "ckqj xlkg exmb qhxi"
    body = f"{message}"

    email_message = MIMEMultipart()
    email_message["From"] = from_email
    email_message["To"] = to_email
    email_message["Subject"] = subject
    email_message.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(from_email, from_password)
        server.sendmail(from_email, to_email, email_message.as_string())
        server.quit()
        print(f"Email sent to {to_email}")
    except Exception as e:
        print(f"Failed to send email: {e}")

def save_to_db(name, email, phone, message, consent):
    conn = sqlite3.connect('form_submissions.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO submissions (name, email, phone, message, consent)
        VALUES (?, ?, ?, ?, ?)
    ''', (name, email, phone, message, consent))
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/login')
def login_page():
    return render_template("login.html")

@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']
    
    if validate_login(email, password):
        return redirect(url_for('admin_page', logged_in=True))
    else:
        return redirect(url_for('login_page', error="Invalid credentials"))
    
@app.route('/send_email', methods=["POST"])
def handle_send_email():
    try:
        name = request.form['name']
        to_email = request.form['email']
        phone = request.form['phone']
        message = request.form['message']
        consent = 'consent' in request.form
        save_to_db(name, to_email, phone, message, consent)
        send_email(to_email, message)
        return  redirect(url_for('index'))
    except KeyError as e:
        return f"Missing field: {e}", 400


@app.route('/admin')
def admin_page():
    logged_in = request.args.get('logged_in') == 'True'
    if not logged_in:
        return redirect(url_for('login_page', error="Access denied"))

    conn = sqlite3.connect('form_submissions.db')
    c = conn.cursor()
    c.execute('SELECT id, name, email FROM submissions')
    submissions = c.fetchall()
    conn.close()
    return render_template('admin.html', submissions=submissions, logged_in=logged_in)

@app.route('/admin/<int:submission_id>')
def view_submission(submission_id):
    logged_in = request.args.get('logged_in') == 'True'
    if not logged_in:
        return redirect(url_for('login_page', error="Access denied"))

    conn = sqlite3.connect('form_submissions.db')
    c = conn.cursor()
    c.execute('SELECT * FROM submissions WHERE id = ?', (submission_id,))
    submission = c.fetchone()
    conn.close()
    
    if not submission:
        return "Submission not found", 404

    return render_template('submission_details.html', submission=submission, logged_in=logged_in)


@app.route('/reply', methods=['POST'])
def handle_reply():
    try:
        submission_id = int(request.form['submission_id'])
        reply_message = request.form['reply_message']
        
        # Fetch email from submission
        conn = sqlite3.connect('form_submissions.db')
        c = conn.cursor()
        c.execute('SELECT email FROM submissions WHERE id = ?', (submission_id,))
        email = c.fetchone()[0]
        conn.close()

        # Send the reply email
        send_email(email, reply_message, subject="Reply to Your Contact Form Submission")

        return redirect(url_for('admin_page', logged_in=True))
    except Exception as e:
        return f"Failed to send reply: {e}", 400

def validate_login(email, password):
    # Replace this with actual validation logic
    return email == "admin@example.com" and password == "password123"

@app.route('/logout')
def logout():
    return redirect(url_for('login_page'))

if __name__ == "__main__":
    app.run(debug=True)
