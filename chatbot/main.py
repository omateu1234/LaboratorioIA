from flask import Flask, render_template, request, jsonify
from gpt4all import GPT4All
import sys

app = Flask(__name__)

model_name = "Meta-Llama-3-8B-Instruct.Q4_0.gguf"
model_path= r"C:\Users\Oscar\AppData\Local\nomic.ai\GPT4All"

llm_model= None

try:
    llm_model = GPT4All(model_name, model_path=model_path)
    print("Modelo GPT4All cargado correctamente.")
except Exception as e:
    print(f"Error al cargar el modelo: {str(e)}", file=sys.stderr)
    print("Funcionalidad de chatbot desactivada.")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/saludar/<nombre>')
def saludar(nombre):
    return f"<h1>Hola {nombre}!</h1> <p>Esta es la página de saludo.</p>"

@app.route('/chat', methods=['POST'])
def chat():
    if llm_model is None:
        return jsonify({'response': 'Funcionalidad de chatbot desactivada.'}), 503
    
    user_message= request.json.get('message') #Aqui esperamos el mensaje del usuario
    if not user_message:
        return jsonify({'response': 'Debes enviar un mensaje.'}), 400
    
    try:
        with llm_model.chat_session():
            bot_response= llm_model.generate(prompt=user_message, max_tokens=100, temp=0.7)
        return jsonify({'response': bot_response})
    except Exception as e:
        print(f"Error al generar respuesta del chatbot: {str(e)}", file=sys.stderr)
        return jsonify({'response': 'Error al generar respuesta del chatbot.'}), 500

if __name__ == '__main__':
    app.run(debug=True)#Reiniciar el servidor cada vez que se modifica el código