# -*- coding: utf-8 -*-
"""
import os
import gc
from flask import Flask, render_template, url_for, flash, request, redirect, session
from db_connect import connection
from wtforms import Form, BooleanField, TextField, IntegerField, FormField, PasswordField, FileField, validators,MultipleFileField
from flask_wtf.file import FileField, FileRequired, FileAllowed
from werkzeug.utils import secure_filename
from wtforms.validators import Length
from passlib.hash import sha256_crypt
from MySQLdb import escape_string as thwart
from functools import wraps
"""

import gc
import os
import random
import MySQLdb
from MySQLdb import escape_string as thwart
from datetime import datetime
from functools import wraps
from dbconnect import connection
from flask import (Flask, flash, redirect, render_template, request, session,
                   url_for)
from passlib.hash import sha256_crypt

app = Flask(__name__)
app.secret_key = "Top Secret!!!"

@app.context_processor
def override_url_for():
    return dict(url_for=dated_url_for)


def dated_url_for(endpoint, **values):
    if endpoint == 'static':
        filename = values.get('filename', None)
        if filename:
            file_path = os.path.join(app.root_path,
                                     endpoint, filename)
            values['q'] = int(os.stat(file_path).st_mtime)
    return url_for(endpoint, **values)

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash("Öncelikle giriş yapmalısınız!!!")
            return redirect(url_for('login'))
    return wrap

def admin_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if session.get('admin'):
            return f(*args, **kwargs)
        else:
            flash("Üzgünüz :( Bu sayfa için yetkiniz bulunmamaktadır.")
            return redirect(url_for('homepage'))
    return wrap

@app.route("/")
def homepage():
    return render_template("homepage.html")

@app.route("/login/", methods=['GET', 'POST'])
def login():
    if 'logged_in' in session:
        return render_template("homepage.html")
    elif request.method == "POST":
        c,conn=connection()
        data = c.execute("SELECT * FROM uye WHERE okul_no = (%s)",
                             [thwart(request.form['username'])])
        if data:
            data=c.fetchone()
            username=data[1]
            passwrd=data[2]
            rol=data[3]
            if sha256_crypt.verify(request.form['passwd'],passwrd):
                session['logged_in'] = True
                session['uye_no']=data[0]
                session['name']=data[4]
                if rol==0:
                    session['admin']=True
                else:
                    session['admin']=False
                session['username'] = request.form['username']
                return redirect(url_for("homepage"))
            else:
                gc.collect()
                flash("Giriş Başarısız")
        else:
            gc.collect()
            flash("Giriş Başarısız")
    return render_template("login.html")

@app.route("/logout/")
@login_required
def logout():
    session.clear()
    gc.collect()
    return redirect(url_for('homepage'))

@app.route("/admin/")
@login_required
@admin_required
def admin():
    return render_template("admin_panel.html")

@app.route("/uyeler/")
@login_required
@admin_required
def uyeler():
    c,conn=connection()
    c.execute("SELECT * FROM uye")
    rows=c.fetchall()
    c.execute('SELECT COUNT(*) FROM uye')
    uye_sayisi=c.fetchone()
    c.close()
    conn.close()
    return render_template("uyeler.html",rows=rows,sayi=uye_sayisi[0])

@app.route("/ayrinti/<uye_no>",methods=['GET','POST'])
@login_required
@admin_required
def ayrinti(uye_no=0):
    if request.method == "POST":
        c,conn=connection()
        c.execute("""UPDATE uye SET okul_no='%s',passwrd='%s',ad='%s',soyad='%s',rol='%s' WHERE uye_no='%s'"""%(request.form['okul_no'],sha256_crypt.encrypt((str(request.form['passwd']))),request.form['ad'],request.form['soyad'],request.form['rol'],uye_no))
        conn.commit()
        print(uye_no)
        return uyeler()
    else:
        c,conn=connection()
        c.execute("SELECT * FROM uye WHERE uye_no=(%s)",[thwart(uye_no)])
        data=c.fetchone()
        okul_no=data[1]
        rol=data[3]
        ad=data[4]
        soyad=data[5]
        return render_template("uye-ayrinti.html",okul_no=okul_no,rol=rol,ad=ad,soyad=soyad,uye_no=uye_no)

@app.route("/uye_sil/<uye_no>/")
@login_required
@admin_required
def uye_sil(uye_no=0):
    c,conn=connection()
    c.execute("DELETE FROM uye WHERE uye_no=(%s)",[uye_no])
    conn.commit()
    return uyeler()

@app.route("/yeni_uye/",methods=['GET','POST'])
@login_required
@admin_required
def yeni_uye():
    if request.method=="POST":
        c,conn=connection()
        pas=sha256_crypt.encrypt(request.form['passwd'])
        c.execute("INSERT into uye (okul_no,passwrd,rol,ad,soyad) values ((%s),(%s),(%s),(%s),(%s))",[request.form['okul_no'],pas,request.form['rol'],request.form['ad'],request.form['soyad']])
        conn.commit()
        return uyeler()
    return render_template("yeni-uye.html")

@app.route('/cekilisler/')
@login_required
def cekilisler():
    c,conn=connection()
    c.execute("SELECT * FROM cekilis")
    rows=c.fetchall()
    c.execute('SELECT COUNT(*) FROM cekilis')
    cekilis_sayisi=c.fetchone()
    c.close()
    conn.close()
    return render_template("cekilisler.html",rows=rows,sayi=cekilis_sayisi[0])

@app.route("/cekilis-ayrinti/<cekilis_no>",methods=['GET','POST'])
@login_required
@admin_required
def cekilis_ayrinti(cekilis_no=0):
    if request.method == "POST":
        c,conn=connection()
        c.execute("""UPDATE cekilis SET cekilis_adi='%s',tarih='%s' WHERE cekilis_no='%s'"""%(request.form['ad'],request.form['tarih'],cekilis_no))
        conn.commit()
        return cekilisler()
    else:
        c,conn=connection()
        c.execute("SELECT * FROM  cekilis WHERE cekilis_no=(%s)",[thwart(cekilis_no)])
        data=c.fetchone()
        c.execute("SELECT COUNT(*) FROM  katilimci WHERE cekilis_no=(%s)",[thwart(cekilis_no)])
        sayi=c.fetchone()[0]
        c.execute("SELECT * FROM  katilimci WHERE cekilis_no=(%s) ORDER BY kazandi_mi DESC",[thwart(cekilis_no)])
        rows=c.fetchall()
        ad=data[1]
        tarih=data[2]
        return render_template("cekilis-ayrinti.html",ad=ad,tarih=tarih,cekilis_no=cekilis_no,rows=rows,sayi=sayi)

@app.route("/cekilis_sil/",methods=['GET','POST'])
@login_required
@admin_required
def cekilis_sil():
    if request.method=="POST":
        c,conn=connection()
        boxs = request.form.getlist("checked")
        for box in boxs:
            c.execute("DELETE FROM katilimci WHERE katilimci_no= (%s)",[box])
        conn.commit()
        return cekilisler()
    return cekilisler()

@app.route("/yeni_cekilis/",methods=['GET','POST'])
@login_required
@admin_required
def yeni_cekilis():
    if request.method=="POST":
        c,conn=connection()
        print(request.form['tarih'])
        c.execute("INSERT INTO cekilis (cekilis_adi,tarih) values ((%s),(%s))",[request.form['ad'],request.form['tarih']])
        conn.commit()
        return cekilisler()
    return render_template("yeni-cekilis.html")

@app.route("/cekilis_kayit/<cekilis_no>",methods=['GET','POST'])
@login_required
def cekilis_kayit(cekilis_no=0):
    c,conn=connection()
    if request.method=="POST":
        columns="(ad,soyad,uyelik,kazandi_mi,cekilis_no,uye_no"
        values="("+request.form['ad']+","+request.form['soyad']+","+request.form['uyelik']+","+'0'+","+cekilis_no+","+str(session['uye_no'])
        values=[request.form['ad'],request.form['soyad'],request.form['uyelik'],'0',cekilis_no,str(session['uye_no'])]
        sayi=5
        bolum=request.form['bolum']
        if(bolum):
            columns+=",bolum"
            values.append(bolum)
            sayi+=1
        sinif=request.form['sinif']
        if(sinif):
            columns+=",sinif"
            values.append(sinif)
            sayi+=1
        telefon=request.form['telefon']
        if(telefon):
            columns+=",telefon"
            values.append(telefon)
            sayi+=1
        mail=request.form['mail']
        if(mail):
            columns+=",mail"
            values.append(mail)
            sayi+=1
        columns+=")"
        c.execute("INSERT INTO katilimci "+columns+" VALUES ((%s)"+",(%s)"*sayi+")",values)
        flash('Kayıt eklenme başarılı')
        return redirect(url_for('cekilis_kayit',cekilis_no=cekilis_no))
    c.execute("SELECT cekilis_adi FROM cekilis WHERE cekilis_no= (%s)",[cekilis_no])
    cekilis_adi=c.fetchone()[0]
    return render_template("yeni-kayit.html",cekilis_no=cekilis_no,cekilis_adi=cekilis_adi)

@app.route("/cekilis/",methods=['GET','POST'])
@login_required
@admin_required
def cekilis():
    c,conn=connection()
    if request.method=="POST":
        kisi=request.form['sayi']
        hediye=request.form['hediye']
        cekilis_no=request.form['cekilis_no']
        c.execute("SELECT * FROM katilimci WHERE cekilis_no= (%s) AND kazandi_mi=0",[cekilis_no])
        sonuc=c.fetchall()
        c.execute("SELECT COUNT(*) FROM katilimci WHERE cekilis_no= (%s)",[cekilis_no])
        sayi=c.fetchone()[0]
        sonuc=random.sample(sonuc, int(kisi))
        for row in sonuc:
            print(row[10])
            c.execute("UPDATE katilimci SET kazandi_mi=1, hediye= (%s) WHERE katilimci_no= (%s)",[hediye,row[0]])
        conn.commit()
        return render_template("cekilis.html",sonuc=sonuc,sayi=sayi)
    c.execute("SELECT * FROM cekilis")
    rows=c.fetchall()
    c.execute("SELECT count(*) FROM katilimci")
    sayi=c.fetchone()[0]
    return render_template("cekilis.html",rows=rows,sayi=sayi)

@app.route("/setup112/")
def setup112():
    c,conn=connection()
    c.execute("SET FOREIGN_KEY_CHECKS=0")
    conn.commit()
    c.execute("DROP TABLE IF EXISTS uye")
    conn.commit()
    c.execute("DROP TABLE IF EXISTS cekilis")
    conn.commit()
    c.execute("DROP TABLE IF EXISTS katilimci")
    conn.commit()
    c.execute("SET FOREIGN_KEY_CHECKS=1")
    conn.commit()
    c.execute("CREATE TABLE uye (uye_no INT AUTO_INCREMENT PRIMARY KEY,okul_no varchar(10) UNIQUE,passwrd LONGTEXT NOT NULL,rol TINYINT NOT NULL,ad nvarchar(30) NOT NULL,soyad nvarchar(30) NOT NULL,CONSTRAINT uc_okul_no UNIQUE (okul_no));")
    conn.commit()
    c.execute("CREATE TABLE cekilis (cekilis_no INT AUTO_INCREMENT PRIMARY KEY,cekilis_adi NVARCHAR(20),tarih DATE);")
    conn.commit()
    c.execute("CREATE TABLE katilimci (katilimci_no INT AUTO_INCREMENT PRIMARY KEY,ad NVARCHAR(30) NOT NULL,soyad NVARCHAR(30) NOT NULL,bolum NVARCHAR(50),sinif TINYINT,uyelik BOOLEAN NOT NULL,telefon NVARCHAR(12),mail NVARCHAR(50),cekilis_no INT,uye_no INT,kazandi_mi BOOLEAN NOT NULL,hediye NVARCHAR(50),CONSTRAINT fk_cekilis_katilimci FOREIGN KEY (cekilis_no) REFERENCES cekilis(cekilis_no),CONSTRAINT fk_uye_katilimci FOREIGN KEY (uye_no) REFERENCES uye(uye_no));")
    conn.commit()
    c.execute("INSERT into uye (okul_no,passwrd,rol,ad,soyad) values ('172114023','"+sha256_crypt.encrypt((str('3548788')))+"','0','Eren','ŞAHAN')")
    conn.commit()
    flash('İşlem Başarı ile Gerçekleşti')
    return homepage()

if __name__ == '__main__':
    app.run(debug=True)
