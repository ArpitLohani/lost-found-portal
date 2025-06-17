import os
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from werkzeug.utils import secure_filename
import sqlite3

app = Flask(__name__)
app.secret_key = 'secret'
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# DB setup
def init_db():
    with sqlite3.connect('database.db') as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            description TEXT,
            contact TEXT,
            status TEXT,
            image TEXT,
            approved INTEGER DEFAULT 0
        )''')







# Home with approved items
@app.route('/')
def index():
    conn = sqlite3.connect('database.db')
    items = conn.execute("SELECT * FROM items WHERE approved=1").fetchall()
    conn.close()
    return render_template('index.html', items=items)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/details')
def details():
    return render_template('details.html')






@app.route('/report', methods=['GET', 'POST'])
def report():
    if request.method == 'POST':
        name = request.form['name']
        desc = request.form['description']
        contact = request.form['contact']
        status = request.form['status']
        file = request.files['image']
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        with sqlite3.connect('database.db') as conn:
            conn.execute("INSERT INTO items (name, description, contact, status, image) VALUES (?, ?, ?, ?, ?)",
                         (name, desc, contact, status, filename))
        flash('Item submitted for approval!', 'info')
        return redirect('/')
    return render_template('report.html')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        password = request.form['password']
        if password == 'admin123':
            conn = sqlite3.connect('database.db')
            items = conn.execute("SELECT * FROM items WHERE approved=0").fetchall()
            conn.close()
            return render_template('admin.html', items=items)
        else:
            flash('Wrong password!', 'danger')
            return redirect('/admin')
    return render_template('login.html')

@app.route('/approve/<int:item_id>')
def approve(item_id):
    with sqlite3.connect('database.db') as conn:
        conn.execute("UPDATE items SET approved=1 WHERE id=?", (item_id,))
    flash('Item approved!', 'success')
    return redirect('/admin')

@app.route('/item/<int:item_id>')
def view_item(item_id):
    with sqlite3.connect('database.db') as conn:
        item = conn.execute("SELECT * FROM items WHERE id=?", (item_id,)).fetchone()
    return render_template('view_item.html', item=item)

# Only one main block

    
if __name__ == '__main__':
    init_db()
    app.run(debug=True)