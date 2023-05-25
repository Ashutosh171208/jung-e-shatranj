from flask import Flask, render_template, jsonify, request, redirect, url_for, g
import sqlite3
import json

app = Flask(__name__)

DATABASE = 'leaderboards.db'


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        for i in range(1, 11):
            cursor.execute(f'''
                CREATE TABLE IF NOT EXISTS leaderboard{i} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    points INTEGER
                )
            ''')
        db.commit()


@app.route('/')
def index():
    return render_template('leaderboards.html')


@app.route('/leaderboards')
def leaderboards():
    db = get_db()
    cursor = db.cursor()
    leaderboard_data = []
    for i in range(1, 11):
        cursor.execute(f'SELECT name, points FROM leaderboard{i} ORDER BY points DESC LIMIT 6')
        leaderboard = cursor.fetchall()
        leaderboard_data.append(leaderboard)
    return render_template('leaderboards.html', leaderboards=leaderboard_data)

@app.route('/get_members', methods=['POST'])
def get_members():
    leaderboard = request.form.get('leaderboard')

    db = get_db()
    cursor = db.cursor()

    # Get the members for the selected leaderboard
    cursor.execute(f'SELECT name FROM leaderboard{leaderboard}')
    members = [row[0] for row in cursor.fetchall()]

    return json.dumps(members)


@app.route('/add_member', methods=['GET', 'POST'])
def add_member():
    if request.method == 'POST':
        leaderboard = request.form.get('leaderboard')
        name = request.form.get('name')
        points = request.form.get('points')

        db = get_db()
        cursor = db.cursor()

        # Insert the new member into the specified leaderboard
        cursor.execute(f'INSERT INTO leaderboard{leaderboard} (name, points) VALUES (?, ?)', (name, points))
        db.commit()

        return redirect(url_for('leaderboards'))

    return render_template('add_member.html')

@app.route('/modify_points', methods=['POST'])
def modify_points():
    leaderboard = request.form.get('leaderboard')

    db = get_db()
    cursor = db.cursor()

    # Get the members for the selected leaderboard
    cursor.execute(f'SELECT name FROM leaderboard{leaderboard}')
    members = cursor.fetchall()
    members = [member[0] for member in members]  # Extract the names from the result

    print(f"Leaderboard: {leaderboard}")
    print(f"Members: {members}")

    return render_template('add_member.html', members=members)






@app.route('/delete_member', methods=['POST'])
def delete_member():
    leaderboard = request.form.get('leaderboard')
    name = request.form.get('name')

    db = get_db()
    cursor = db.cursor()

    # Delete the specified member from the leaderboard
    cursor.execute(f'DELETE FROM leaderboard{leaderboard} WHERE name = ?', (name,))
    db.commit()

    return redirect(url_for('leaderboards'))


if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0')
