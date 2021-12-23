import requests, psycopg2
from flask import Flask, render_template, request, redirect

app = Flask(__name__)

conn = psycopg2.connect(database="service_db",
                        user="postgres",
                        password="6654",
                        host="localhost",
                        port="5432")

cursor = conn.cursor()

@app.route('/login/', methods=['GET'])
def index():
    return render_template('login.html')

@app.route('/login/', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        if request.form.get("login"):
            username = request.form.get('username')
            password = request.form.get('password')
            if not(username and password):
                return render_template("account.html", exception = 'You have to complete all fields')
            cursor.execute("SELECT * FROM service.users WHERE login=%s AND password=%s", (str(username), str(password)))
            records = list(cursor.fetchall())
            if not records:
                return render_template("account.html", exception = 'Wrong username or password')
            return render_template('account.html', full_name = records[0][1], login = records[0][2], password = records[0][3])
        elif request.form.get("registration"):
            return redirect("/registration/")

    return render_template('login.html')

@app.route('/registration/', methods=['POST', 'GET'])
def registration():
    if request.method == 'POST':
        name = request.form.get('name')
        login = request.form.get('login')
        password = request.form.get('password')
        if not(name and login and password):
            return render_template('error.html', text='You have to complete all fields')
        else:
            cursor.execute("SELECT * FROM service.users WHERE login=%s", (str(login)))
            records = list(cursor.fetchall())
            if records:
                return render_template('error.html', text='Account does already exist')
            else:
                cursor.execute('INSERT INTO service.users (full_name, login, password) VALUES (%s, %s, %s);',
                               (str(name), str(login), str(password)))
                conn.commit()

                return redirect('/login/')

    return render_template('registration.html')

if __name__ == '__main__':
    app.run(debug=True)
