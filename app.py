from flask import Flask, render_template, request, redirect, url_for, flash
import psycopg2
from psycopg2.extras import RealDictCursor
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

import time  

def get_db_connection():
    db_url = os.getenv('DATABASE_URL')
    
    while True:
        try:
            conn = psycopg2.connect(db_url)
            return conn
        except psycopg2.OperationalError as e:
            print(f"DataBase is unavailable ({e}). Try again over 2 sec...")
            time.sleep(2)


@app.route('/')
def index():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute('SELECT * FROM contacts ORDER BY id')
    contacts = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('index.html', contacts=contacts)

@app.route('/add', methods=['POST'])
def add_contact():
    full_name = request.form['full_name']
    phone_number = request.form['phone_number']
    note = request.form['note']
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        'INSERT INTO contacts (full_name, phone_number, note) VALUES (%s, %s, %s)',
        (full_name, phone_number, note)
    )
    conn.commit()
    cur.close()
    conn.close()
    flash('Contact was successfully added!')
    return redirect(url_for('index'))

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_contact(id):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    if request.method == 'POST':
        full_name = request.form['full_name']
        phone_number = request.form['phone_number']
        note = request.form['note']
        
        cur.execute(
            'UPDATE contacts SET full_name=%s, phone_number=%s, note=%s WHERE id=%s',
            (full_name, phone_number, note, id)
        )
        conn.commit()
        flash('Contact was successfully updated!')
        return redirect(url_for('index'))
    
    cur.execute('SELECT * FROM contacts WHERE id=%s', (id,))
    contact = cur.fetchone()
    cur.close()
    conn.close()
    return render_template('edit.html', contact=contact)

@app.route('/delete/<int:id>')
def delete_contact(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM contacts WHERE id=%s', (id,))
    conn.commit()
    cur.close()
    conn.close()
    flash('Contact was deleted!')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
