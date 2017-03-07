#!/usr/bin/env python
from flask import Flask, render_template, session, request
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect
import RPi.GPIO as GPIO
import time

# Set this variable to "threading", "eventlet" or "gevent" to test the
# different async modes, or leave it set to None for the application to choose
# the best option based on installed packages.
async_mode = None

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
thread = None


def background_thread():
    """Example of how to send server generated events to clients."""
    count = 0
    while True:
        socketio.sleep(10)
        count += 1
        socketio.emit('my_response',
                      {'data': 'Server generated event', 'count': count},
                      namespace='/test')

def turn_on_light():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(18,GPIO.OUT)

    print "LED on"

    GPIO.output(18,GPIO.HIGH)

    time.sleep(1)

    print "LED off"

    GPIO.output(18,GPIO.LOW)

def set_alarm(hours, minutes):
    from crontab import CronTab
    import os
    
    cwd = os.getcwd()

    cron = CronTab(user=True)
    print('python ' + cwd + '/run_sound.py')
    job = cron.new(command='python ' + cwd + '/run_sound.py')
    job.minute.on(minutes)
    job.hour.on(hours)

    cron.write()

def check_for_alarm(txt_rcvd):
    import re
    time = re.search("(?<=wake me up at )[0-9+:]*")

    if time == '' :
        return False

    hours = int(time[:2])
    minutes = int(time[3:])

    set_alarm(hours, minutes)

def process_text(txt_rcvd):
    
    if txt_rcvd == "turn on the light" :
        turn_on_light()
        return "success"
    elif check_for_alarm(txt_rcvd) :
        return "success"


@app.route('/')
def index():
  return render_template('index.html', async_mode=socketio.async_mode)


@socketio.on('my_event', namespace='/test')
def test_message(message):
    
    response = message['data']

    if not 'first' in message :
        response = process_text(message['data'])

        if not response:
            response = message['data']

    emit('my_response',
         {'data': response})


@socketio.on('my_broadcast_event', namespace='/test')
def test_broadcast_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': message['data'], 'count': session['receive_count']},
         broadcast=True)

@socketio.on('connect', namespace='/test')
def test_connect():
    global thread
    emit('my_response', {'data': 'Connected'})


@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected', request.sid)


if __name__ == '__main__':
    socketio.run(app, debug=True, host="0.0.0.0")
