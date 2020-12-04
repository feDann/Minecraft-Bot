import telebot
import subprocess
import json
import os
from threading import Thread , Lock

from queue import Queue, Empty


process = None
q = None
t = None

cwd =  os.path.dirname(os.path.realpath(__file__))
config_path = os.path.join(cwd,'config.json')

with open(config_path) as configFile:
    config = json.load(configFile)


def enqueue_output(out, queue):
    for line in iter(out.readline, b''):
        queue.put(line)


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
                process = subprocess.Popen(['java', *args , '-jar' , jarName , 'nogui'],stdin=subprocess.PIPE, stdout=subprocess.PIPE,stderr=subprocess.PIPE , cwd=serverDir)                     
                q = Queue()
                t = Thread(target=enqueue_output, args=(process.stdout, q))
                t.daemon = True
                t.start()            
            else:
                bot.reply_to(message, "the server is already up tyoe  /output to view the stdout or /stop to stop the server")
    except Exception  as e:
        print('Error in start ' + str(e)) 

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
                process = None
                t = None
                q = None
                bot.reply_to(message, 'Server Stopped, type /start to start the server')
    except Exception  as e:
        print('Error in stop ' + str(e))
        bot.reply_to(message, 'Unable to stop the server. Try again /stop or contact admin') 


@bot.message_handler(commands=['output','o'])
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
                    bot.reply_to(message, 'No output yet!')
                else:
                    string = ''.join(out)
                    numoftime = len(string)//4096 + 1 #has to split the message if its too long
                    for i in range(1,numoftime +1):
                        part = out[len(out)//numoftime*(i-1):len(out)//numoftime*i]
                        bot.reply_to(message,''.join(part))
    except Exception  as e:
        print('Error in info ' + str(e)) 



@bot.message_handler(commands=['command' , 'c'])
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
                    bot.reply_to(message, 'Command executed!Type /output to see the output')
                else:
                    bot.reply_to(message, 'Unable to use this command right now, /stop the server and /start again')
    except Exception  as e:
        print('Error in command ' + str(e))   
        


@bot.message_handler(commands=['reload_config'])
def fetch_whitelist(message):
    global config
    try:
        if message.from_user.username in config['whitelist']:
            with open(config_path) as configFile:
                config = json.load(configFile)
            bot.reply_to(message, 'Config File reloaded')
    except Exception  as e:
        print('Error during reload config command ' + str(e))



@bot.message_handler(commands=['ping'])
def info_server(message):
    try:
        if message.from_user.username in config['whitelist']:
            bot.reply_to(message , 'pong')
    except Exception  as e:
        print('Error during ping command ' + str(e))


bot.polling()