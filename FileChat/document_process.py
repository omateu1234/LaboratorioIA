import os
import pandas as pd
from gpt4all import GPT4All
import PyPDF2

""" Este es un programa que revisa tus archivos de la carpeta que desees, los fragmenta y mediante un algoritmo de palabras claves obtiene el contexto de los archivos,
    para posteriormente poder hacer consultas a un chatbot sobre el contenido de estos"""


""" CONFIGURACIÓN """
PATH= "C:/Users/Oscar/OneDrive/Documentos"  #Ruta de documentos
TAMANIO_FRAGMENTO= 200                      #Tamaño máximo de los fragmentos
SOBREPOSICION= 20                           #Caracteres de sobreposición para cada fragmento para dar contexto
model_name = "Meta-Llama-3-8B-Instruct.Q4_0.gguf"
model_path= r"C:\Users\Oscar\AppData\Local\nomic.ai\GPT4All"

""" Cargamos el modelo """
print("Cargando el modelo")
try:
    llm= GPT4All(model_name ,model_path=model_path, allow_download=False)
    print("Modelo llama cargado")
except Exception as e:
    print("Error al cargas el modelo {e}")
    llm= None

#Funcion para cargar archivos
def load_documents(ruta_carpeta):
    """ Carga los archivos .txt y devuelve su contenido """
    documentos=[]
    for archivo in os.listdir(ruta_carpeta):
        ruta_completa= os.path.join(ruta_carpeta, archivo)
        if archivo.endswith(".txt"):
            try:        
                with open(ruta_completa, 'r' , encoding='utf-8') as f:
                    contenido= f.read()
                    documentos.append({"nombre_archivo": archivo , "contenido": contenido})    
            except Exception as e:
                print(f"Error al leer el archivo {archivo}: {e}")
                
        elif archivo.endswith(".pdf"):
            try:
                with open(ruta_completa, 'rb')as f:
                    lector_pdf= PyPDF2.PdfReader(f)
                    contenido= ""
                    for pagina in lector_pdf.pages:
                        contenido+=pagina.extract_text() + "\n" #Añadimos el contenido 
                        
                    if contenido.strip(): #Nos aseguramos de que no este vacio
                        documentos.append({"nombre_archivo": archivo , "contenido": contenido})
                    else:
                        print("El documento {archivo} esta vacio")
            except PyPDF2.errors.PdfReadError:
                print("Error de lectura para {archivo}")
            except Exception as e:
                print("Error inesperado al leer {archivo}")
                
    print(f"Se cargaron {len(documentos)} documentos en la carpeta {ruta_carpeta}.")
    return documentos
    

#Funcion para fragmentar documentos
def separate_document(contenido, id_documento, tamanio_fragmento, sobreposicion):
    """ Dividimos el texto en fragmentos mas pequeños """
    fragmentos=[]
    texto_len=len(contenido)
    i=0
    id_fragmento=0
    
    while i < texto_len:
        final_fragmento=min(i + tamanio_fragmento, texto_len)
        fragmento=contenido[i:final_fragmento].strip()
        if fragmento :
            fragmentos.append({
                "id_fragmento": f"{id_documento}_chunk_{id_fragmento}",
                "contenido": fragmento,
                "documento_origen": id_documento
            })
            id_fragmento +=1
            
        #Calcular el siguiente punto de inicio
        if (final_fragmento== texto_len): #Significa que llegamos al final
            break
        else:
            i +=(tamanio_fragmento - sobreposicion)
            if i < 0:    #Evitamos los indices negativos si el fragmento es pequeño
                i=0
    print(f"  ->Documento {id_documento} fragmentado en {len(fragmentos)} trozos")

    return fragmentos

def search_relevant_fragments(pregunta, df_fragmentos, top_n=3):
    """ Vamos a buscar las partes más relevantes del usuario buscando en el DataFrame basado en palabras clave """
    pregunta_low= pregunta.lower()
    #obtenemos una lista con las palabras clave limpias
    palabras_clave= [palabra.strip() for palabra in pregunta_low.split() if palabra.strip()]
    
    if not palabras_clave:
        return[]
    
    resultados=[]
    for i, row in df_fragmentos.iterrows():
        #setteamos los fragmentos
        contenido_fragmento= row['contenido'].lower()
        puntuacion=0
        
        #Contamos las palabras claves que hay y se repiten en cada fragmento
        for palabra in palabras_clave:
            if palabra in contenido_fragmento:
                puntuacion +=1
    
        if(puntuacion > 0):
            resultados.append({
                "id_fragmento": row['id_fragmento'],
                "contenido": row['contenido'],
                "documento_origen": row['documento_origen'],
                "puntuacion": puntuacion
            })
            
    #Ordenamos los resultados
    resultados_ordenados= sorted(resultados, key=lambda x: x['puntuacion'], reverse=True)
    
    return resultados_ordenados[:top_n]

def generate_answer_ia(pregunta, fragmentos_contexto):
    """ Generamos la respuesta con el modelo llama, basado en la pregunta y los fragmentos """
    if llm is None:
        return "Lo siento, el modelo no se ha podido cargar"
    
    #Construiremos el prompt
    contexto_str=""
    if fragmentos_contexto:
        contexto_str="Información de contexto:\n"
        for i,f in enumerate(fragmentos_contexto):
            contexto_str+= f"[{f['documento_origen']}_Chunk_{i+1}]: {f['contenido']}\n"
    else:
        contexto_str="No hay información de contexto disponible"
    
    prompt=f"""{contexto_str}

**Pregunta**: {pregunta}

**Instrucción**: Basado **solamente** en la "Información de Contexto" proporcionada, responde a la "Pregunta" de forma concisa. 
Si la respuesta no está explícitamente contenida en la información, responde "No tengo suficiente información para responder a esa pregunta basándome en los documentos 
proporcionados.". No añadas comentarios ni justificaciones adicionales. Ve directo al grano."""
    
    print("\n--- Enviando al modelo llama ----")
    try:
        #Aqui interactuamos con el modelo
        respuesta=llm.generate(prompt, max_tokens=200, temp=0.7)
        return respuesta.strip()
    except Exception as e:
        return f"Error al generar la respuesta {e}"
    
""" Metodo main para generar la respuesta mediante IA """
def main():
    documentos= load_documents(PATH)
    
    fragmentos_totales=[]
    
    for documento in documentos:
        fragmentos_doc= separate_document(documento["contenido"], documento["nombre_archivo"], TAMANIO_FRAGMENTO, SOBREPOSICION)
        fragmentos_totales.extend(fragmentos_doc)
    
    #Pasamos los fragmentos a PANDA
    df_fragmentos= pd.DataFrame(fragmentos_totales)
    
    print("\n--- Vista previa de los fragmentos")
    print(df_fragmentos.head())
    print(f"\nTotal de fragmentos procesados: {len(df_fragmentos)}")
    
    #Demostracion Chatbot
    print("\n --- Tu chatbot RAG esta listo")
    print("Escribe 'salir' para acabar la conversación")
    
    while True:
        pregunta_usuario=input("\n Tu pregunta:")
        if pregunta_usuario.lower() == 'salir':
            print("Saliendo")
            break
    
        #Recuperamos los fragmentos
        fragmetos_encontrados= search_relevant_fragments(pregunta_usuario,df_fragmentos, top_n=3)
        
        if fragmetos_encontrados:
            print(f"Se encontraron {len(fragmetos_encontrados)} fragmentos relevantes")
            
            respuesta_llama=generate_answer_ia(pregunta_usuario, fragmetos_encontrados)
            print("\nRespuesta de la IA")
            print(respuesta_llama)
        else:
            print("\nNo se encontraron fragmentos relevantes en tus documentos")
            print("Respuesta de la IA sin contexto:")
            respuesta_fallida=generate_answer_ia(pregunta_usuario, [])
            print(respuesta_fallida)
            
    return df_fragmentos
    
    
            

if __name__ == "__main__":
    df_our_fragments= main()
        
""" Proceso Principal usado para usar el algoritmo de busqueda """
""" def main():
    documentos=load_documents(PATH)
    
    fragmentos_totales=[]
    for documento in documentos:
        fragmentos_doc= separate_document(documento["contenido"], documento["nombre_archivo"], TAMANIO_FRAGMENTO, SOBREPOSICION)
        fragmentos_totales.extend(fragmentos_doc)
        
    
    #Convertimos los fragmentos en panda
    df_fragmentos= pd.DataFrame(fragmentos_totales)
    
    print("Vista previa de los fragmentos (Primeras 5 lineas)")
    print(df_fragmentos.head())
    
    df_fragmentos.to_csv("fragmetos_documentos.csv", index=False, encoding='utf-8')
    
    pregunta_usuario=input("Escribe tu pregunta:")
    
    fragmentos_encontrados= search_relevant_fragments(pregunta_usuario, df_fragmentos, top_n=3)
    
    if fragmentos_encontrados:
        print(f"Se Encontraron {len(fragmentos_encontrados)} fragmentos relevantes")
        for i,frag in enumerate(fragmentos_encontrados):
            print(f"--- Fragmento {i+1} (Puntuacion : {frag['puntuacion']}, Origen: {frag['documento_origen']})---")
            print(frag['contenido'])
            print("-"*40)
    else:
        print("No se encontraron trozos relevantes")
    
    return df_fragmentos """
        