from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# Connect to the SQLite database
def get_db_connection():
    conn = sqlite3.connect('links.db')
    conn.row_factory = sqlite3.Row
    return conn

# Create the links table if it doesn't exist
def create_table():
    conn = get_db_connection()
    conn.execute('''CREATE TABLE IF NOT EXISTS links
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL,
                  url TEXT NOT NULL,
                  traffic INTEGER DEFAULT 0,
                  UNIQUE(name))''')
    conn.close()

# Homepage
@app.route('/')
def index():
    conn = get_db_connection()
    links = conn.execute('SELECT * FROM links ORDER BY traffic DESC').fetchall()
    conn.close()
    return render_template('index.html', links=links)

# Add a new link
@app.route('/add', methods=['POST'])
def add_link():
    name = request.form['name']
    url = request.form['url']
    
    conn = get_db_connection()
    try:
        conn.execute('INSERT INTO links (name, url) VALUES (?, ?)', (name, url))
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        return render_template('error.html', message='Link name already exists')
    
    conn.close()
    return redirect(url_for('index'))

# Redirect to the link URL
@app.route('/redirect/<int:link_id>')
def redirect_link(link_id):
    conn = get_db_connection()
    link = conn.execute('SELECT * FROM links WHERE id = ?', (link_id,)).fetchone()
    conn.execute('UPDATE links SET traffic = traffic + 1 WHERE id = ?', (link_id,))
    conn.commit()
    conn.close()
    
    return render_template('redirect.html', link=link)

# Rename a link
@app.route('/rename/<int:link_id>', methods=['POST'])
def rename_link(link_id):
    new_name = request.form['new_name']
    
    conn = get_db_connection()
    try:
        conn.execute('UPDATE links SET name = ? WHERE id = ?', (new_name, link_id))
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        return render_template('error.html', message='Link name already exists')
    
    conn.close()
    return redirect(url_for('index'))

# Delete a link
@app.route('/delete/<int:link_id>', methods=['POST'])
def delete_link(link_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM links WHERE id = ?', (link_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

# Error page
@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', message='Page not found')

if __name__ == '__main__':
    create_table()
    app.run()