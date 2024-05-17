import os
import json
from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_mail import Mail, Message
from flask_socketio import SocketIO
from waitress import serve  # Importa el servidor Waitress

app = Flask(__name__, template_folder='templates')
socketio = SocketIO(app)

# Configuración de Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'cuentafalsa97a@gmail.com'
app.config['MAIL_PASSWORD'] = 'midj ddua fkcb dwjj'

mail = Mail(app)

PORT = 3000
archivo_noti = 'notifications.json'

# Función para enviar actualizaciones a los clientes conectados
def send_update(data):
    socketio.emit('update', data)

# Función para cargar las notificaciones desde el archivo
def load_notifications_from_file():
    if os.path.exists(archivo_noti) and os.path.getsize(archivo_noti) > 0:
        with open(archivo_noti, 'r') as file:
            return json.load(file)
    else:
        return []

# Función para guardar las notificaciones en el archivo
def save_notifications_to_file(notifications):
    with open(archivo_noti, 'w') as file:
        json.dump(notifications, file)

# Lista para almacenar las notificaciones recibidas
notifications = load_notifications_from_file()

# Ruta principal, redirige a la vista de notificaciones
@app.route('/')
def index():
    return redirect(url_for('show_notifications'))

# Ruta para el punto final del Webhook
@app.route('/webhook/update_data', methods=['POST'])
def update_data():
    # Procesar la notificación del Webhook
    data = request.json

    # Agregar la notificación a la lista
    notifications.append(data)

    # Guardar las notificaciones en el archivo
    save_notifications_to_file(notifications)

    # Enviar actualizaciones a los clientes conectados
    send_update(data)

    # Verificar si la solicitud incluye un mensaje de error
    if 'error' in data:
        # Agregar la notificación de error
        error_message = f'Error al procesar la notificación del Webhook: {data["error"]}'
        notifications.append({'error': error_message})

        # Enviar correo electrónico
        send_email(data)

    # Responder al proveedor de inventario con un código de estado 200 (OK)
    return jsonify({'message': 'Registro actualizado correctamente'}), 200

# Función para enviar correo electrónico a múltiples destinatarios
def send_email(data):
    subject = 'Notificación del Webhook'
    message = json.dumps(data, ensure_ascii=False, indent=4)  # Para permitir caracteres especiales

    # Lista de destinatarios de correo electrónico
    recipients = ['tuiiyoparatodalavida@gmail.com', 'erickfabri_01@hotmail.com', 'jeffersond044@gmail.com', 'andysisalema9@gmail.com']

    msg = Message(subject, sender='cuentafalsa97a@gmail.com', recipients=recipients)

    # Puedes elegir enviar el correo electrónico en formato HTML o texto plano
    msg.body = message  # Para texto plano
    # msg.html = html_message  # Para HTML

    try:
        mail.send(msg)
    except Exception as e:
        print(f'Error al enviar correo electrónico: {str(e)}')

# Ruta para mostrar las notificaciones recibidas
@app.route('/notifications', methods=['GET'])
def show_notifications():
    return render_template('notifications.html', notifications=notifications)

# Ruta para mostrar las notificaciones recibidas en formato JSON
@app.route('/notifications_json', methods=['GET'])
def show_notifications_json():
    return jsonify(notifications)

# Ejecutar el servidor directamente al iniciar el script
if __name__ == '__main__':
    serve(app, host='127.0.0.1', port=3000)
