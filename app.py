from flask import Flask, render_template, request, session, url_for, redirect, jsonify, make_response, flash
import pymysql
from werkzeug.utils import secure_filename
from flask_uploads import UploadSet, configure_uploads, IMAGES
import pandas as pd
import os
import numpy as np
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

#########################################################################################################################################
#                                       initializing database and flask authentication
#########################################################################################################################################
def dbConnection():
    connection = pymysql.connect(
        host="cropnew.cncgivpu1i0p.eu-central-1.rds.amazonaws.com", user="root", password="adminadmin", port=3306, database="cropnew")
    return connection


def dbClose():
    dbConnection().close()
    return


app = Flask(__name__)
app.secret_key = 'random string'

app.config['UPLOADED_PHOTOS_DEST'] = 'static/upload/'
photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)
#########################################################################################################################################
#                                               Main initial page
#########################################################################################################################################
@app.route('/index')
def index():
    return render_template('index1.html')
#########################################################################################################################################
#                                                   Index page
#########################################################################################################################################
@app.route('/about')
def about():
    return render_template('about.html')
#########################################################################################################################################
#                                                   User page
#########################################################################################################################################
@app.route('/contact')
def contact():
    return render_template('contact.html')
#########################################################################################################################################
#                                                   User Logout
#########################################################################################################################################
@app.route('/logout')
def logout():
    session.pop('user')
    return redirect(url_for('login'))
#########################################################################################################################################
#                                                   User Registeration
#########################################################################################################################################
@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        try:
            status = ""
            name = request.form.get("Name")
            Email = request.form.get("Email")
            pass1 = request.form.get("pass1")
            con = dbConnection()
            cursor = con.cursor()
            cursor.execute(
                'SELECT * FROM userdetails WHERE email = %s', (Email))
            res = cursor.fetchone()
            #res = 0
            if not res:
                sql = "INSERT INTO userdetails (name, email, password) VALUES (%s, %s, %s)"
                val = (name, Email, pass1)
                print(sql, " ", val)
                cursor.execute(sql, val)
                con.commit()
                status = "success"
                return redirect(url_for('login'))
            else:
                status = "Already available"
            # return status
            return redirect(url_for('index'))
        except:
            print("Exception occured at user registration")
            return redirect(url_for('index'))
        finally:
            dbClose()
    return render_template('register.html')
#########################################################################################################################################
#                                                   User Login
#########################################################################################################################################
@app.route('/', methods=["GET", "POST"])
def login():
    msg = ''
    if request.method == "POST":
        session.pop('user', None)
        mailid = request.form.get("email")
        password = request.form.get("Pas")
        print(mailid, password)
        con = dbConnection()
        cursor = con.cursor()
        result_count = cursor.execute(
            'SELECT * FROM userdetails WHERE email = %s AND password = %s', (mailid, password))
        #a= 'SELECT * FROM userdetails WHERE mobile ='+mobno+'  AND password = '+ password
        # print(a)
        # result_count=cursor.execute(a)
        result = cursor.fetchone()
        if result_count > 0:
            print(result_count)
            session['userid'] = result[0]
            session['user'] = mailid
            return redirect(url_for('index'))
        else:
            print(result_count)
            msg = 'Incorrect username/password!'
            return msg
        # dbClose()
    return render_template('login.html')
#########################################################################################################################################
#                                                      Home page
#########################################################################################################################################
@app.route('/home.html')
def home():
    if 'user' in session:
        return render_template('home.html', user=session['user'])
    return render_template("login.html")
#########################################################################################################################################
#                                                   Plant disease
#########################################################################################################################################
@app.route('/plntds', methods=['GET', 'POST'])
def plntds():
    print('hi')
    if 'user' in session:
        if request.method == "POST":
            # Get the file from post request

            f = request.files['dsfile']

            # Save the file to ./uploads
            basepath = os.path.dirname(__file__)
            file_path = os.path.join(
                basepath, 'static/upload/', secure_filename(f.filename))
            f.save(file_path)
            fname = secure_filename(f.filename)
            # print("printing file name")
            # print(fname)
        
            from os import listdir
            from os.path import isfile, join
            predict_dir_path = file_path
            
            import tensorflow
            from tensorflow.keras.preprocessing import image
            from tensorflow.keras.models import load_model
            model = load_model("VGG_plant.hp5")
            image_size = 224
            img = image.load_img(predict_dir_path,
                                target_size=(image_size, image_size))
            x = image.img_to_array(img)
            # print("printing X#######")
            # print(x)
            # x = x/255
            # x = np.expand_dims(x, axis=0)

            img_4d=x.reshape(1,224,224,3)

            # images = np.vstack([x])

            predictions = model.predict(img_4d)
            print(predictions[0])
            new_pred=np.argmax(predictions[0])
            print("printing classes")
            print(new_pred)
            
            list2 = ['Pepper bell Bacterial_spot','Pepper bell healthy',
                    'Potato Early_blight','Potato healthy','Potato Late_blight',
                    'Tomato Target_Spot','Tomato Tomato mosaic virus',
                    'Tomato Bacterial spot','Tomato Early blight',
                    'Tomato healthy','Tomato Late blight',
                    'Tomato Leaf Mold','Tomato Septoria leaf spot']

            print(list2[new_pred])
            op = str(list2[new_pred])

            return render_template('plant_disease.html', op=op)
        return render_template("plant_disease.html", user=session['user'])
    return render_template("login.html")


if __name__ == "__main__":
    app.run("0.0.0.0")
    #app.run(debug=True)
