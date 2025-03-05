import socket
import threading
import queue
import tkinter as tk
from tkinter import scrolledtext, simpledialog

# Cola para comunicación entre hilos
message_queue = queue.Queue()
peer_socket = None
username = ""

# Función para recibir mensajes y pasarlos a la cola
def receive_messages(sock):
    while True:
        try:
            message = sock.recv(1024).decode('utf-8')
            if message:
                message_queue.put(message)  # Poner mensaje en la cola
            else:
                break
        except:
            sock.close()
            break

# Función para enviar mensajes
def send_message():
    message = message_entry.get()
    if message and peer_socket:
        formatted_message = f"{username}: {message}"  # Formato con usuario
        chat_display.insert(tk.END, f"Tú: {message}\n")  # Mostrar en la UI
        chat_display.yview(tk.END)
        message_entry.delete(0, tk.END)
        try:
            peer_socket.send(formatted_message.encode('utf-8'))
        except:
            chat_display.insert(tk.END, "Error al enviar mensaje.\n")

# Función para actualizar la UI con los mensajes recibidos
def update_chat():
    while not message_queue.empty():
        message = message_queue.get()
        chat_display.insert(tk.END, f"{message}\n")
        chat_display.yview(tk.END)
    root.after(100, update_chat)  # Llamar nuevamente después de 100ms

# Iniciar el servidor para recibir conexiones
def start_server(port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('127.0.0.1', port))
    server_socket.listen(5)
    print(f"Escuchando en el puerto {port}...")

    while True:
        client_socket, addr = server_socket.accept()
        print(f"Conectado a {addr}")
        threading.Thread(target=receive_messages, args=(client_socket,)).start()

# Conectar a otro usuario
def connect_to_peer(peer_port):
    global peer_socket
    peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        peer_socket.connect(('127.0.0.1', peer_port))
        chat_display.insert(tk.END, f"Conectado a 127.0.0.1:{peer_port}\n")
        threading.Thread(target=receive_messages, args=(peer_socket,)).start()
    except Exception as e:
        chat_display.insert(tk.END, f"Error al conectar: {e}\n")

# Configurar la interfaz gráfica
root = tk.Tk()
root.title("Chat P2P")

# Solicitar el nombre de usuario
username = simpledialog.askstring("Nombre de usuario", "Ingresa tu nombre:")

# Área de mensajes
chat_display = scrolledtext.ScrolledText(root, width=50, height=20)
chat_display.pack(pady=10)

# Entrada de mensaje
message_entry = tk.Entry(root, width=40)
message_entry.pack(side=tk.LEFT, padx=10)
send_button = tk.Button(root, text="Enviar", command=send_message)
send_button.pack(side=tk.RIGHT, padx=10)

# Obtener los puertos
my_port = int(simpledialog.askstring("Puerto", "Ingresa tu puerto (ej. 55555):"))
threading.Thread(target=start_server, args=(my_port,), daemon=True).start()

peer_port = int(simpledialog.askstring("Puerto", "Ingresa el puerto del otro usuario (ej. 55556):"))
threading.Thread(target=connect_to_peer, args=(peer_port,), daemon=True).start()

# Iniciar el proceso de actualización de UI
root.after(100, update_chat)
root.mainloop()


