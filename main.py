import vertexai
from vertexai.language_models import ChatModel, InputOutputTextPair
from flask import Flask, render_template, request, jsonify, url_for, redirect, session, flash
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error
from config import DATABASE_CONFIG
from werkzeug.security import generate_password_hash, check_password_hash
import userform
from ia import ChatbotIA


app = Flask(__name__)

app.secret_key = 'luguitoo'
db = mysql.connector.connect(**DATABASE_CONFIG)
cursor = db.cursor()
CORS(app)

# Crea la tabla si es que no existe
create_table_query = """
    CREATE TABLE IF NOT EXISTS user (
        id_user INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(255),
        email VARCHAR(255),
        password VARCHAR(255)
    )
"""
cursor.execute(create_table_query)
db.commit()
chatbot = ChatbotIA()

@app.route('/', methods=['GET', 'POST'])
def login():
    user = userform.User(request.form)
    if request.method == 'POST':
        username = user.username.data
        password = user.password.data
        cursor.execute('SELECT * FROM user WHERE username = %(username)s', {'username': username})
        data = cursor.fetchall()
        if data:
            userdata = data[0]
            if userdata:
                passcheck = userdata[3]
                if check_password_hash(passcheck, password):
                    session['username'] = username
                    return redirect(url_for('bienvenido'))
        flash("Credenciales incorrectas", "error")
    return render_template('login.html', user=user)

@app.route("/get", methods=["POST"])
def chat_vertexai():
    msg = request.form["msg"]
    input_text = msg
    response = chatbot.entrada(input_text)
    return jsonify({"response": response})

@app.route('/bienvenido')
def bienvenido():
    datos = session.get('username')
    if datos is not None:
        print(datos)
        return render_template('chat.html', datos=datos)
    else:
        flash("Usuario no autenticado", "error")
        return redirect(url_for('login'))

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    user = userform.User(request.form)
    if request.method == 'POST' and user.validate():
        password = create_password(user.password.data)
        sql = "SELECT * FROM user WHERE username = %s"
        val = [user.username.data]
        cursor.execute(sql, val)
        data = cursor.fetchall()
        create = True
        if data:
            flash("Usuario existente", "existe_us")
            create = False
        elif not data:
            sql = "SELECT * FROM user WHERE email = %s"
            val = [user.email.data]
            cursor.execute(sql, val)
            coe = cursor.fetchall()
            if coe:
                create = False
                flash("Correo existente", "existe_co")
            elif user.password.data == user.confirmpassword.data and create:
                cursor.execute('INSERT INTO user (username, email, password) VALUES (%s, %s, %s)',
                                 (user.username.data, user.email.data, password))
                db.commit()
                flash("Registro exitoso", "success")
                return redirect(url_for('login'))
            else:
                flash("Error en el registro", "psw")
    return render_template('register.html', user=user)

def create_password(password):
    return generate_password_hash(password)

if __name__ == '__main__':
    app.run(debug=True, port=8080, host='0.0.0.0')
