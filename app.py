  
#Python libraries that we need to import for our bot
import MySQLdb
from MySQLdb import Error
import random, os, csv, re
import pandas as pd
from flask import Flask, request
from pymessenger.bot import Bot
from datetime import datetime, timedelta

app = Flask(__name__)

#ACCESS_TOKEN = os.environ['ACCESS_TOKEN']
#VERIFY_TOKEN = os.environ['VERIFY_TOKEN']
#CLEARDB_DATABASE_URL = os.environ['CLEARDB_DATABASE_URL']
#HORARIO_DESLIGAMENTO = os.environ['HORARIO_DESLIGAMENTO']

ACCESS_TOKEN = 'EAADzIkX32oYBADPjMYhnky8mJGBSkjkMrIhnp1LJlCH87clxngeX0I0bunswYBP8gZAPWc6Unm2dSR1yULve7exKRsNI0pgZAotscdOsxObR6mEQVv55mpHbepb3qQpn0eJu83ZBVUN9fM4GvVgVflurQ0f8YccvtTTaZBvIAHa1IuZAlkCqZBCwFXOllZAk1gZD'
VERIFY_TOKEN = 'TESTINGTOKEN'
CLEARDB_DATABASE_URL = 'mysql://b8cd7b592349c7:67006c83@us-cdbr-east-03.cleardb.com/heroku_0c2e37b2ea952c5?reconnect=true'
HORARIO_DESLIGAMENTO = 24

bot = Bot(ACCESS_TOKEN)


#We will receive messages that Facebook sends our bot at this endpoint 
@app.route("/", methods=['GET', 'POST'])
def receive_message():
    
    host, user, passwd, db = URL_bd(CLEARDB_DATABASE_URL)
    
    try:
        con = MySQLdb.connect(host="us-cdbr-east-03.cleardb.com", user="b8cd7b592349c7", passwd="67006c83", db="heroku_0c2e37b2ea952c5")
        #con = MySQLdb.connect(host="host", user="user", passwd="passwd", db="db")
        cursor = con.cursor()
        cursor.execute("SELECT * FROM excluidos")
        
        ID_LIST = {}
        for linha in cursor.fetchall():
            ID_LIST['{}'.format(linha[0])] = {"horario":linha[1]}
        
    except Error as e:
        ID_LIST = {}
        con = False
        print("Erro ao acessar tabela MySQL", e)  
    
    
    if request.method == 'GET':
        """Before allowing people to message your bot, Facebook has implemented a verify token
        that confirms all requests that your bot receives came from Facebook.""" 
        token_sent = request.args.get("hub.verify_token")

        
        return verify_fb_token(token_sent)
    #if the request was not get, it must be POST and we can just proceed with sending a message back to user
    else:
        
        output = request.get_json()
                
        if('is_echo' in output['entry'][0]['messaging'][0]['message']):
            inp = open("input.txt",'w')
            
            
            echo_messenge = str(output['entry'][0]['messaging'][0]['message']['text'])
            recipient_id = str(output['entry'][0]['messaging'][0]['recipient']['id'])
            
            if(get_message_itself(echo_messenge) == 1):
                pass
            elif(get_message_itself(echo_messenge) == 2):
                pass
            else:
                try:
                    comando_update = "UPDATE excluidos SET horario_excluido='{0}' WHERE id_excluido={1}".format(datetime.now(), recipient_id)
                    cursor.execute(comando_update)
                except:
                    ID_LIST[recipient_id] = {'horario': str(datetime.now())}
                
        else:
            # get whatever message a user sent the bot
            for event in output['entry']:
                messaging = event['messaging']
                for message in messaging:
    
                    if message.get('message'):
                        #Facebook Messenger ID for user so we know where to send response back to
                        recipient_id = message['sender']['id']
                        
                        if message['message'].get('text'):
                            response_sent_text = get_message(str(message['message'].get('text')), bd = con)
                            #OUT = open("outputs.txt", 'w')
                            #OUT.writelines(str(message["message"]) + '\n')
                            
                            list_id(recipient_id, response_sent_text, ID_LIST, bd = con)
                            
                            try:
                                # Efetua um commit no banco de dados.
                                con.commit()
                                # Finaliza a conexão
                                con.close()
                            except:
                                pass
                                        
                        #if user sends us a GIF, photo,video, or any other non-text item
                        if message['message'].get('attachments'):
                            #response_sent_nontext = get_message()
                            #send_message(recipient_id, response_sent_nontext)
                            pass
                    
    return "Message Processed"


def verify_fb_token(token_sent):
    #take token sent by facebook and verify it matches the verify token you sent
    #if they match, allow the request, else return an error 
    if token_sent == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return 'Invalid verification token'
    
def get_message_itself(text):

    caso_1 = 'Oi, tudo bem?  Eu sou Jarvis, a inteligência artificial do gabinete do Amom. Vi que você quer mandar uma demanda pra gente. É isso mesmo? Se for, pode preencher o formulário no link https://forms.gle/WDdANuUVKvf7GjwJ8, por favor? O seu protocolo vai ser gerado automaticamente depois que enviar o formulário. Geralmente alguém da equipe de gabinete responde em menos de 10 minutos :)'         
    caso_2 =  'Oi, tudo bem? Eu sou Jarvis, a inteligência artificial do gabinete do Amom. Nós respondemos todo mundo, mas levamos um tempo, pois são muitas mensagens. Fica tranquilo, um membro da equipe vai te responder :)'   
    
    if(str(text) == caso_1):
        return 1
    elif(str(text) == caso_2):
        return 2
    else:
        return False


def get_message(text, bd = False):
    '''
    expressoes_chaves = { 'quero mandar uma demanda': ['demanda'],
                          'tenho uma denúncia': ['denúncia', 'denuncia'],
                          'gostaria de denunciar': ['denunciar'],
                          'quero mandar uma sugestão': ['sugestão', 'sugestao'],
                          'quero fazer uma reclamação': ['reclamação', 'reclamacao', 'reclamaçao', 'reclamacão']
    }
    '''
    
    
    expressoes_chaves = expressoes_chaves_func(bd)
        
    
    for expressoes in expressoes_chaves:
        for palavras_chaves in expressoes_chaves[expressoes]:
            
            if(palavras_chaves.lower() in text.lower()):
                caso = 1
                frase_padrao = 'Oi, tudo bem?  Eu sou Jarvis, a inteligência artificial do gabinete do Amom. Vi que você quer mandar uma demanda pra gente. É isso mesmo? Se for, pode preencher o formulário no link https://forms.gle/WDdANuUVKvf7GjwJ8, por favor? O seu protocolo vai ser gerado automaticamente depois que enviar o formulário. Geralmente alguém da equipe de gabinete responde em menos de 10 minutos :)'
                return (frase_padrao, caso)
        
    else:
        frase_padrao = 'Oi, tudo bem? Eu sou Jarvis, a inteligência artificial do gabinete do Amom. Nós respondemos todo mundo, mas levamos um tempo, pois são muitas mensagens. Fica tranquilo, um membro da equipe vai te responder :)'
        caso = 2
        return (frase_padrao, caso)
    

#uses PyMessenger to send response to user
def send_message(recipient_id, response):
    #sends user the text message provided via input response parameter
    bot.send_text_message(recipient_id, response)
    return "success"

def URL_bd(URL):
    paramet = re.split('[(:/#?@]', URL)
    
    host = paramet[5]
    user = paramet[3]
    passwd = paramet[4]
    db = paramet[6]
    
    return (host, user, passwd, db)

def list_id(recipient_id, response_sent_text, id_list, bd = False):

    if(bd):
        cursor = bd.cursor()
    
    if(recipient_id not in id_list):
        print("User não está na lista")
                        
        if(response_sent_text[1] == 1):
            send_message(recipient_id, response_sent_text[0])
            
        else:
            send_message(recipient_id, response_sent_text[0])
            
            comando_update = "INSERT INTO excluidos (id_excluido, horario_excluido) VALUE ({0}, '{1}')".format(recipient_id, str(datetime.now()))
            
            try:
                cursor.execute(comando_update)
            except:
                
                ID_LIST[recipient_id] = {'horario': str(datetime.now())}
                print("A conecção com o banco de dados deu errado!")
                
            
                        
    else:
        print("User está na lista")
        
        if(datetime.strptime(id_list[recipient_id]['horario'], '%Y-%m-%d %H:%M:%S.%f') + timedelta(seconds= 3600*HORARIO_DESLIGAMENTO) < datetime.now()):
                            
            if(response_sent_text[1] == 2):
                send_message(recipient_id, response_sent_text[0])
                
                comando_update = "UPDATE excluidos SET horario_excluido='{0}' WHERE id_excluido={1}".format(datetime.now(), recipient_id)
                
                try:
                    cursor.execute(comando_update)
                except:
                    ID_LIST[recipient_id] = {'horario': str(datetime.now())}
                    print("A conecção com o banco de dados deu errado!")
                                
        if(response_sent_text[1] == 1):
            send_message(recipient_id, response_sent_text[0])
            
    
    return id_list

def expressoes_chaves_func(bd = False):
    if(bd):
        try:
            cursor = bd.cursor()
            cursor.execute("SELECT * FROM expressoeschaves")

            
            expressoes_chaves_lista = []
            for row in cursor.fetchall():
                expressao_chave, variacao = row[0], row[1]
                
                if(expressao_chave not in expressoes_chaves_lista):
                    expressoes_chaves_lista.append(expressao_chave)
            
            expressoes_chaves = {}
            for expressao in expressoes_chaves_lista:
                seleciona = "SELECT variacao FROM expressoeschaves WHERE expressoes_chaves ='{}'".format(expressao)
                cursor.execute(seleciona)
                resultado = cursor.fetchall()
                
                expressoes_chaves[expressao] = [x[0] for x in resultado]
            
            return expressoes_chaves    
                
            
        except Error as e:
            print("Erro ao acessar tabela MySQL", e)  
    else:
        expressoes_chaves = { 'Quero enviar uma demanda': ['quero enviar uma demanda', 'quero enviar demanda,'  'quero manda demanda', 'quero mandar uma demanda'],
                          'Quero fazer uma reclamação': ['quero enviar uma reclamação', 'quero mandar uma reclamação'],
                          'Quero fazer uma solicitação': ['quero enviar uma solicitação', 'quero enviar solicitação',  'quero manda solicitação', 'quero mandar uma solicitação'],
                          'Quero fazer uma sugestão': ['quero enviar uma sugestão', 'quero enviar sugestão',  'quero manda sugestão', 'quero mandar uma sugestão'],
                          'Quero fazer uma denúncia': ['quero enviar uma denúncia', 'quero enviar denúncia',  'quero manda denúncia', 'quero mandar uma denúncia'] 
        }
        return expressao_chaves
        

if __name__ == "__main__":
    app.run()
  