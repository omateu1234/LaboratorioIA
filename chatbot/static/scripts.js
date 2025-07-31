document.addEventListener('DOMContentLoaded', () => {
        const userInput= document.getElementById('user-input');
        const sendButton = document.getElementById('send-button');
        const chatLog = document.getElementById('chat-log');

        const appendMessage= (sender, message) => {
            const messageDiv= document.createElement('div');
            messageDiv.classList.add('message');

            if(sender === 'user') {
                messageDiv.classList.add('user-message');
                messageDiv.textContent= `Tú: ${message}`
        } else{
            messageDiv.classList.add('bot-message');
            messageDiv.textContent= `Bot: ${message}`
        }
        chatLog.appendChild(messageDiv);
        chatLog.scrollTop = chatLog.scrollHeight;
        };

        const sendMessage = async () => {
            const message = userInput.value.trim();
            if(message== ''){
                return;
            }

            appendMessage('user', message);
            userInput.value='';
            sendButton.disabled= true;
            userInput.disabled= true;

            try{
                const response= await fetch('/chat', {
                    method: 'POST',
                    headers:{
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({message: message})
                });

                const data= await response.json();
                if(response.ok){
                    appendMessage('bot', data.response); //Muestra la respuesta del bot
                } else{
                    appendMessage('error', `Error: ${data.response || 'No se pudo obtener la respuesta'} `);
                }
            }catch( error){
            console.error(error);
            appendMessage('bot', 'Error de conexion, Intentalo de nuevo')
        }finally{
            sendButton.disabled= false;
            userInput.disabled= false;
            userInput.focus();
        }
    };

    //Evento para enviar el mensaje 
    sendButton.addEventListener('click', sendMessage);
    userInput.addEventListener('keypress', (e) => {
        if(e.key=== 'Enter'){
            sendMessage();
        }
    })
});