import telebot
import subprocess
import json
import os
from threading import Thread , Lock

from queue import Queue, Empty


lock = Lock()

process = None
q = None
t = None

cwd =  os.getcwd()
config_path = os.path.join(cwd,'config.json')

with open(config_path) as configFile:
    config = json.load(configFile)


def enqueue_output(out, queue):
    for line in iter(out.readline, b''):
        queue.put(line)
    out.close()


def out_log():
    out = []
    decodeLine = True
    while decodeLine:
        try:
            line = q.get_nowait()
        except Empty:
            decodeLine=False
        else:
            out.append(line.decode().replace('[Server thread/INFO]',''))
    return out


bot = telebot.TeleBot(config["bot-token"])



@bot.message_handler(commands=['start' ,'s'])
def start_server(message):
    global process
    global t
    global q
    try:
        if message.from_user.username in config['whitelist']:
            if process is None:
                bot.reply_to(message, "Starting Minecraft Server...")
                args = config['args']
                serverDir = config['server-directory']
                jarName = config['jar-name']  
                process = subprocess.Popen(' '.join(['java', *args , '-jar' , jarName , 'nogui']),stdin=subprocess.PIPE, stdout=subprocess.PIPE,stderr=subprocess.PIPE ,  shell=True, cwd=serverDir)              
                q = Queue()
                t = Thread(target=enqueue_output, args=(process.stdout, q))
                t.daemon = True
                t.start()
            
            else:
                bot.reply_to(message, "the server is already up, type /restart to restart the server , /info to view the stdout or /stop to stop the server")
    except Exception  as e:
        print('Error in start ' + str(e)) 


@bot.message_handler(commands=['info','i'])
def info_server(message):
    global process
    global q
    try:
        if message.from_user.username in config['whitelist']:
            if process is None:
                bot.reply_to(message, "Server is not yet started! Use /start to start the server")
            else:
                out = out_log()
                if not out:
                    bot.reply_to(message, 'No log yet!')
                else:
                    string = ''.join(out)
                    numoftime = len(string)//4096 + 1 #had to split the message if its too long
                    for i in range(1,numoftime +1):
                        part = out[len(out)//numoftime*(i-1):len(out)//numoftime*i]
                        bot.reply_to(message,''.join(part))                       
    except Exception  as e:
        print('Error in info ' + str(e)) 


@bot.message_handler(commands=['stop'])
def stop_server(message):
    global process
    global t
    global q
    try:
        if message.from_user.username in config['whitelist']:
            if process is None:
                bot.reply_to(message, "Server is not yet started! Use /start to start the server")
            else:
                if not process.stdin.closed:           
                    process.stdin.write(b'stop\n')
                    process.stdin.flush()
                    process.communicate()
                    process.terminate()
                else:
                    process.terminate()
                q = None
                t = None
                process = None
                bot.reply_to(message, 'Server Stopped, type /start to start the server')
    except Exception  as e:
        print('Error in stop ' + str(e))
        bot.reply_to(message, 'Unable to stop the server. Try again /stop') 

@bot.message_handler(commands=['help_minecraft'])
def help_command(message):
    global process
    global t
    global q
    try:
        if message.from_user.username in config['whitelist']:
            if process is None:
                bot.reply_to(message, "Server is not yet started! Use /start to start the server")
            elif not process.stdin.closed :           
                process.stdin.write(b'help\n')
                process.stdin.flush()
                bot.reply_to(message, 'Help done, press /info to se result')
            else:
                bot.reply_to(message, 'Unable to use this command right now, /stop the server and /start again')
    except Exception  as e:
        print('Error in help ' + str(e))  


@bot.message_handler(commands=['command'])
def exec_command(message):
    global process
    global t
    global q
    try:
        if message.from_user.username in config['whitelist']:
            if process is None:
                bot.reply_to(message, "Server is not yet started! Use /start to start the server")
            else:            
                command = message.text.replace('/command ' , '')
                if 'stop' in command:
                    bot.reply_to(message,'To stop the server use /stop command!')
                elif not process.stdin.closed :
                    command += "\n"
                    process.stdin.write(command.encode())
                    process.stdin.flush()
                    bot.reply_to(message, 'Command executed!Type /info to see the output')
                else:
                    bot.reply_to(message, 'Unable to use this command right now, /stop the server and /start again')
    except Exception  as e:
        print('Error in command ' + str(e))   
        


@bot.message_handler(commands=['fetch_whitelist'])
def fetch_whitelist(message):
    global config
    try:
        if message.from_user.username in config['whitelist']:
            with open(config_path) as configFile:
                config = json.load(configFile)
            bot.reply_to(message, 'Whitelist updated')
    except Exception  as e:
        print('Error during fetch whitelist command ' + str(e))



@bot.message_handler(commands=['ping'])
def info_server(message):
    try:
        if message.from_user.username in config['whitelist']:
            bot.reply_to(message , 'pong')
    except Exception  as e:
        print('Error during ping command ' + str(e))


bot.polling()