from flask import Flask, render_template, request, redirect, url_for, flash, Response
import os
import numpy as np
import sqlite3
import cvzone.SerialModule
from cvzone.HandTrackingModule import HandDetector
import cv2
from time import sleep

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('db/al_jazari.db')
    conn.row_factory = sqlite3.Row
    return conn

menu = ['home', 'functions', 'move the hand'
#, 'check connection', 'report issue'
 ]

@app.context_processor
def inject_enumerate():
    return dict(enumerate=enumerate)

@app.context_processor
def inject_bool():
    return dict(bool=bool)

@app.context_processor
def inject_zip():
    return dict(zip=zip)

@app.route("/")
@app.route("/home")
def home():
    active = 'home'
    page_name = "Hello World"

    conn = get_db_connection()

    query = conn.execute('''
        SELECT * FROM models;
    ''').fetchall()

    conn.close()

    return render_template(
        "index.html",
        page_name=page_name,
        query=query
    )

@app.route("/functions")
def functions():
    conn = get_db_connection()

    query = conn.execute('''
        SELECT f.id, f.name, m.name, "default" FROM functions AS f
        INNER JOIN models AS m
        ON f.model_id = m.id;
    ''').fetchall()

    query_len = conn.execute('SELECT count(id) FROM functions;').fetchall()[0][0]

    conn.close()
    active = 'functions'

    return render_template(
        'functions/functions.html',
        page_name="Functions",
        menu_template=menu,
        active=active,
        query = query,
        query_len=query_len
    )

@app.route("/functions/<int:id>")
def function_settings(id):
    active = 'functions'
    moves_table_header = [
        'number of move',
        'finger name',
        'wait time (sec)',
        'number of motor',
        'motor id',
    ]

    function_titles = [
        'function id',
        'function name',
        'model id',
        'model name',
        'is default function?'
    ]

    conn = get_db_connection()

    function_detailes = conn.execute('''
        SELECT f.id, f.name, m.id, m.name, "default"
        FROM functions AS f
        INNER JOIN models AS m
        ON f.model_id = m.id
        WHERE f.id = {};
    '''.format(id)).fetchall()

    query = conn.execute('''
        SELECT  move_num, m.name, wait_time_in_seconds, motor_num_in_the_model, motor_id
        FROM functions_moves AS fm
            INNER JOIN motors as m
            ON fm.motor_id = m.id
        WHERE function_id = {};
    '''.format(id)).fetchall()

    conn.close()

    return render_template(
        'functions/function_settings.html',
        page_name="Functions Settings",
        function_titles=function_titles,
        function_detailes=list(function_detailes)[0],
        moves_table_header=moves_table_header,
        menu_template=menu,
        active=active,
        query = query,
    )

@app.route("/functions/<int:id>/edit", methods=['GET', 'POST'])
def edit_function(id):
    active = 'functions'
    moves_table_header = [
        'number of move',
        'finger name',
        'wait time (sec)',
    ]

    function_titles = [
        'function id',
        'function name',
        'model id',
        'model name',
        'is default function?'
    ]

    conn = get_db_connection()
    is_defualt = conn.execute('SELECT "default" FROM functions WHERE id = ?', str(id)).fetchall()[0][0]
    if int(is_defualt):
        conn.close()
        return redirect(url_for('function_settings', id=id))

    function_detailes = conn.execute('''
        SELECT f.id, f.name, m.id, m.name, "default"
        FROM functions AS f
        INNER JOIN models AS m
        ON f.model_id = m.id
        WHERE f.id = {};
    '''.format(id)).fetchall()



    query = conn.execute('''
        SELECT move_num, m.name, wait_time_in_seconds, motor_num_in_the_model, motor_id
        FROM functions_moves AS fm
            INNER JOIN motors as m
            ON fm.motor_id = m.id
        WHERE function_id = {};
    '''.format(id)).fetchall()

    motors = conn.execute('''
        SELECT id, name, motor_num_in_the_model FROM motors
        WHERE model_id = 1;
    ''').fetchall()

    conn.close()

    if request.method == 'POST':

        with get_db_connection() as conn:
            conn.execute('''
                DELETE FROM functions_moves WHERE function_id = {};
            '''.format(id)).fetchall()

            values = []
            count = 1
            num = 0
            for key in request.form.keys():
                key_lst = key.split("_")      

                if key_lst[0] == "finger":
                    values = [id, request.form.get(key, type=int), count]
                    num = key_lst[1]

                elif key_lst[0] == "waitTime" and key_lst[1] == num:
                    values.append(request.form.get(key, type=float))
                    conn.execute('''
                        insert into functions_moves (function_id, motor_id, move_num, wait_time_in_seconds) values
                        (?, ?, ?, ?)
                    ''', values).fetchall()

                    count += 1

        return redirect(url_for('function_settings', id=id))






    return render_template(
        'functions/edit_function.html',
        page_name="Functions Settings",
        function_titles=function_titles,
        function_detailes=list(function_detailes)[0],
        moves_table_header=moves_table_header,
        menu_template=menu,
        active=active,
        query = query,
        motors = motors,
        # dic = request.form
    )
@app.route("/functions/new_function", methods=['GET', 'POST'])
def new_function():
    active = 'functions'
    conn = get_db_connection()
    models = conn.execute('SELECT * FROM models').fetchall()
    conn.close()

    if request.method == 'POST':
        fnc = request.form.get('function_name', type=str)
        mod = request.form.get('model_id', type=int)

        if not fnc:
            flash('Title is required!')
        elif not mod:
            flash('Content is required!')
        else:
            conn = get_db_connection()
            conn.execute('INSERT INTO functions(name, model_id, "default") values (?, ?, \'0\');',
                            (fnc.title(), mod))
            conn.commit()
            conn.close()

        return redirect(url_for('functions'))

    return render_template(
        'functions/new_function.html',
        page_name="Create A New Function",
        menu_template=menu,
        active=active,
        models=models
    )

@app.route("/hand-moving")
def move_the_hand():
    return render_template(
        'hand-move.html',
        menu_template=menu,
        active='move the hand',
    )

@app.route("/hand-moving/camera")
def vid():
    return render_template(
        'vid.html',
        menu_template=menu,
        active='move the hand',
    )

@app.route("/hand-moving/camera/live-vid")
def video_feed():
    cap = cv2.VideoCapture(0)
    detector = HandDetector(detectionCon=0.8, maxHands=1)
    mySerial = cvzone.SerialModule.SerialObject("com13", 9600, 1)

    def gen_frames():  
        while True:
            success, frame = cap.read()
            hands, frame = detector.findHands(frame)
            if hands:                             
                hand1 = hands[0]
                lmList1 = hand1["lmList"]
                bbox1 = hand1["bbox"]
                centerPoint1 = hand1["center"]
                handType1 = hand1["type"]
                fingers1 = detector.fingersUp(hand1)
                mySerial.sendData(fingers1)


            # cv2.imshow("Image", img)
            # cv2.waitKey(1)
            if not success:
                break
            else:
                ret, buffer = cv2.imencode('.jpg', frame)
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result

    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route("/hand-moving/functions")
@app.route("/hand-moving/functions?message=<message>")
def move_using_function(message=""):
    conn = get_db_connection()

    query = conn.execute('''
        SELECT f.id, f.name, m.name, "default" FROM functions AS f
        INNER JOIN models AS m
        ON f.model_id = m.id;
    ''').fetchall()

    query_len = conn.execute('SELECT count(id) FROM functions;').fetchall()[0][0]

    conn.close()
    active = 'move the hand'

    return render_template(
        'functions/move_using_function.html',
        page_name="Choose Your Function",
        menu_template=menu,
        active=active,
        query = query,
        query_len=query_len,
        message=message
    )

@app.route("/hand-moving/functions/<int:function_id>?function_name=<function_name>")
def move_using_id_function(function_id, function_name=""):
    mySerial = cvzone.SerialModule.SerialObject("com13", 9600, 1)
    fingers = [0, 0, 0, 0, 0]

    conn = get_db_connection()

    query = conn.execute('''
        SELECT  motor_num_in_the_model, wait_time_in_seconds
        FROM functions_moves AS fm
            INNER JOIN motors as m
            ON fm.motor_id = m.id
        WHERE function_id = {};
    '''.format(function_id)).fetchall()

    conn.close()

    for index, seconds in query:
        fingers[index] = 1
        mySerial.sendData(fingers)
        print(fingers)
        sleep(seconds)

    return redirect(url_for('move_using_function', message=function_name))

# @app.route("/<link>")
# def page(link):
#     page_name = link.replace("-", " ")
#     active = page_name
#     return render_template(
#         "index.html",
#         page_name=page_name,
#         menu_template=menu,
#         active=active
#     )


if __name__ == '__main__':
    app.run(port=5000, debug=True)
