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

with open('config.json') as configFile:
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
        except:
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
                process.stdin.write(b'stop\n')
                process.stdin.flush()
                process.communicate()
                process.terminate()                    
                q = None
                t = None
                process = None
                bot.reply_to(message, 'Server Stopped, type /start to start the server')
    except Exception  as e:
        print('Error in stop ' + str(e)) 

@bot.message_handler(commands=['help_minecraft'])
def help_command(message):
    global process
    global t
    global q
    try:
        if message.from_user.username in config['whitelist']:
            if process is None:
                bot.reply_to(message, "Server is not yet started! Use /start to start the server")
            else:           
                process.stdin.write(b'help\n')
                process.stdin.flush()
                bot.reply_to(message, 'Help done, press /info to se result')
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
                else:
                    command += "\n"
                    process.stdin.write(command.encode())
                    process.stdin.flush()
                    bot.reply_to(message, 'Command executed!Type /info to see the output')
                
    except Exception  as e:
        print('Error in command ' + str(e))   
        




@bot.message_handler(commands=['ping'])
def info_server(message):
    try:
        if message.from_user.username in config['whitelist']:
            bot.reply_to(message , 'pong')
    except Exception  as e:
        print('Error during ping command ' + str(e))


bot.polling()