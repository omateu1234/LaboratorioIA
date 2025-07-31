import tkinter as tk # Aún necesario para constantes como tk.END, tk.NORMAL, tk.DISABLED
import customtkinter
from gpt4all import GPT4All
import sys # Para manejar la salida si el modelo no carga

# --- Configuración del modelo GPT4All ---
model_name = "Meta-Llama-3-8B-Instruct.Q4_0.gguf"
model_path = r"C:\Users\Oscar\AppData\Local\nomic.ai\GPT4All"

model = None # Inicializamos el modelo como None
try:
    # Intentar cargar el modelo
    model = GPT4All(model_name, model_path=model_path)
    print("Modelo GPT4All cargado exitosamente.")
    initial_status_message = "¡Modelo IA cargado! Haz una pregunta."
except Exception as e:
    # Capturar cualquier error durante la carga del modelo
    print(f"Error al cargar el modelo GPT4All: {e}", file=sys.stderr)
    initial_status_message = f"Error al cargar el modelo IA: {e}. Funcionalidad de IA deshabilitada."
    # No es necesario salir, la UI seguirá funcionando, pero el bot no responderá.

# --- Funcionalidad del Chatbot ---
def send_message():
    user_input = entry.get()
    if user_input.strip() == "": 
        return

    # Mostrar mensaje del usuario
    chat_log.configure(state=tk.NORMAL) # Habilitar para escribir
    chat_log.insert(tk.END, "Tú: " + user_input + "\n")
    chat_log.configure(state=tk.DISABLED) 
    entry.delete(0, tk.END) # Limpiar el campo de entrada

    # Asegurarse de que el mensaje del usuario se muestre antes de generar la respuesta
    root.update_idletasks() # Actualiza la interfaz para mostrar el mensaje de usuario inmediatamente

    if model is None: # Si el modelo no cargó, solo muestra un mensaje de error
        chat_log.configure(state=tk.NORMAL)
        chat_log.insert(tk.END, "Bot: El modelo IA no está disponible. No se puede generar una respuesta.\n")
        chat_log.configure(state=tk.DISABLED)
        chat_log.yview(tk.END) # Desplazar al final
        return

    # Generar respuesta del bot
    try:
        # Usamos chat_session para mejor gestión del contexto de la conversación
        with model.chat_session():
            # Puedes ajustar max_tokens y temp (temperatura para la creatividad)
            response = model.generate(prompt=user_input, max_tokens=100, temp=0.7)
    except Exception as e:
        response = f"Error al generar respuesta del IA: {e}"
        print(f"Error en GPT4All al generar: {e}", file=sys.stderr)

    # Mostrar respuesta del bot
    chat_log.configure(state=tk.NORMAL)
    chat_log.insert(tk.END, "Bot: " + response + "\n")
    chat_log.configure(state=tk.DISABLED)
    chat_log.yview(tk.END) # Desplazar automáticamente al final

# --- Configuración de la Interfaz Gráfica con CustomTkinter ---
# Configurar el modo de apariencia y el tema de color
customtkinter.set_appearance_mode("System")  # Opciones: "System", "Dark", "Light"
customtkinter.set_default_color_theme("blue")  # Opciones: "blue", "dark-blue", "green"

# Crear la ventana principal de CustomTkinter
root = customtkinter.CTk() 
root.title("Chatbot IA Local")
root.geometry("650x550") # Un poco más grande para mejor visualización

# Área de registro del chat (Textbox de CustomTkinter)
# Quitamos width y height fijos para que pack(fill, expand) lo maneje
chat_log = customtkinter.CTkTextbox(root, state=tk.DISABLED, wrap="word")
chat_log.pack(padx=10, pady=10, fill="both", expand=True) # Muy importante fill="both" y expand=True

# Mostrar el mensaje de estado inicial
chat_log.configure(state=tk.NORMAL)
chat_log.insert(tk.END, initial_status_message + "\n\n")
chat_log.configure(state=tk.DISABLED)
chat_log.yview(tk.END)

# Marco para la entrada de texto y el botón
input_frame = customtkinter.CTkFrame(root)
input_frame.pack(padx=10, pady=(0, 10), fill="x") # pady=(0,10) en el frame es suficiente

# Campo de entrada de texto para el usuario (Entry de CustomTkinter)
entry = customtkinter.CTkEntry(input_frame, placeholder_text="Escribe tu mensaje aquí...", width=450)
entry.pack(side=tk.LEFT, padx=(10, 5), pady=10, fill="x", expand=True) # pady=10 dentro del frame

# Vincular la tecla Enter para enviar el mensaje
entry.bind("<Return>", lambda event=None: send_message())

# Botón de envío (Button de CustomTkinter)
send_button = customtkinter.CTkButton(input_frame, text="Enviar", command=send_message, width=90) # Ajustado un poco el ancho
send_button.pack(side=tk.LEFT, padx=(5, 10), pady=10)

# Función para cerrar el modelo de GPT4All al cerrar la ventana
def on_closing():
    if model: # Solo intentar cerrar si el modelo se cargó exitosamente
        print("Cerrando modelo GPT4All...")
        model.close()
    root.destroy()

# Asignar la función on_closing al evento de cerrar la ventana
root.protocol("WM_DELETE_WINDOW", on_closing)

# Iniciar el bucle principal de la aplicación
root.mainloop()