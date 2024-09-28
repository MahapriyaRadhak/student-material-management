from flask import Flask,flash, render_template, request,url_for,redirect,Response,session,send_file,send_from_directory
from flask_mysqldb import MySQL
from functools import wraps
from werkzeug.utils import secure_filename


import os
import csv
import random

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(APP_ROOT, 'static', 'UPLOAD_FOLDER')

UPLOAD_FOLDER='static/images'
FILE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf', 'text'}

app=Flask(__name__)
app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER']='root'
app.config['MYSQL_PASSWORD']=''
app.config['MYSQL_DB']='db_course'
app.config['MYSQL_CURSORCLASS']='DictCursor'
app.config['UPLOAD_FOLDER']=UPLOAD_FOLDER

mysql=MySQL(app)

def allowed_extensions(file_name):
    return '.' in file_name and file_name.rsplit('.',1)[1].lower() in FILE_EXTENSIONS

@app.route("/")
@app.route("/index")
def index():
	return render_template("index.html")
 
@app.route("/admin",methods=['POST','GET'])
def admin():
    if request.method=='POST':
        if request.form["submit"]=="Login":
            a=request.form["uname"]
            b=request.form["password"]
            cur=mysql.connection.cursor()
            cur.execute("select * from tbl_admin where aname=%s and apass=%s",(a,b))
            data=cur.fetchone()
            if data:
                session['logged_in']=True
                session['aid']=data["aid"]
                session['aname']=data["aname"]
                session['apass']=data["apass"]
                return redirect('admin_login')
    return render_template("admin.html")

def is_logged_in(f):
	@wraps(f)
	def wrap(*args,**kwargs):
		if 'logged_in' in session:
			return f(*args,**kwargs)
		else:
			flash('Unauthorized, Please Login','danger')
			return redirect(url_for('home'))
	return wrap  
        
@app.route("/admin_login",methods=['POST','GET'])
def admin_login():
    return render_template("admin_login.html")
    
@app.route("/admin_department",methods=['POST','GET'])
def admin_department():
    if request.method=='POST':
        if request.form["submit"]=="ADD":
            a=request.form["udep"]
            b=request.form["uyear"]
            c=request.form["usem"]
            cur=mysql.connection.cursor()
            cur.execute("INSERT INTO tbl_department(dept,dyear,dsem) values(%s,%s,%s)" ,(a,b,c))
            mysql.connection.commit()
            cur.close()
    cur=mysql.connection.cursor()
    cur.execute("select * from tbl_department")
    data=cur.fetchall()	
    cur.close()
    return render_template("admin_department.html",datas=data)
    
@app.route("/admin_staff", methods=['POST', 'GET'])
def admin_staff():
    if request.method=='POST':
        if request.form["submit"]=="ADD":
            a=request.form["uname"]
            b=request.form["did"]
            c=request.form["uemail"] 
            d=request.form["uphone"] 
            file=request.files["file"]
            if file and allowed_extensions(file.filename):
                filename, file_extension = os.path.splitext(file.filename)
                new_filename = secure_filename(str(random.randint(10000,99999))+"."+file_extension)
                file.save(os.path.join(UPLOAD_FOLDER, new_filename)) 
            cur=mysql.connection.cursor()
            cur.execute("INSERT INTO tbl_staff(sname,did,semail,sphone,simage) values(%s,%s,%s,%s,%s)" ,(a,b,c,d,new_filename))
            mysql.connection.commit()
            cur.close()
    cur=mysql.connection.cursor()
    cur.execute("select * from tbl_staff")
    data=cur.fetchall()
    cur.close()
    cur=mysql.connection.cursor()
    cur.execute("select * from tbl_department")
    data1=cur.fetchall()
    cur.close()
    return render_template("admin_staff.html",datas=data,dept=data1)

    
@app.route("/admin_viewstudent",methods=['POST','GET'])
def admin_viewstudent():
    cur=mysql.connection.cursor()
    cur.execute("select * from tbl_student a inner join tbl_department d on a.did=d.did")
    data=cur.fetchall()	
    return render_template("admin_viewstudent.html",datas=data)

@app.route("/admin_viewdepartment",methods=['POST','GET'])
def admin_viewdepartment():
    cur=mysql.connection.cursor()
    cur.execute("select * from tbl_department")
    data=cur.fetchall()	
    return render_template("admin_viewdepartment.html",datas=data)
    
@app.route('/delete_department/<string:did>',methods=['POST','GET'])
def delete_department(did):
    cur=mysql.connection.cursor()
    cur.execute("delete from tbl_department where did=%s",(did,))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for("admin_viewdepartment"))
    
@app.route("/admin_viewstaff",methods=['POST','GET'])
def admin_viewstaff():
    cur=mysql.connection.cursor()
    cur.execute("select * from tbl_staff a inner join tbl_department d on a.did=d.did")
    data=cur.fetchall()	
    return render_template("admin_viewstaff.html",datas=data) 

@app.route('/delete_staff/<string:sid>',methods=['POST','GET'])
def delete_staff(sid):
    cur=mysql.connection.cursor()
    cur.execute("delete from tbl_staff where sid=%s",(sid,))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for("admin_viewstaff"))
           
@app.route('/delete_student/<string:stid>',methods=['POST','GET'])
def delete_student(stid):
    cur=mysql.connection.cursor()
    cur.execute("delete from tbl_student where stid=%s",(stid,))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for("admin_viewstudent"))
    
    
@app.route("/admin_viewmaterials", methods=['POST', 'GET'])
def admin_viewmaterials():
    dept = []
    
    if request.method == 'POST':
        if request.form.get("submit") == "Submit":
            a = request.form["did"]
            b = request.form["usem"]
            cur = mysql.connection.cursor()
            cur.execute("SELECT *  FROM tbl_materials m INNER JOIN tbl_staff s ON m.did = s.did INNER JOIN tbl_department d ON m.did = d.did WHERE m.dsem = %s AND m.did = %s",(b,a))
            dept=cur.fetchall()
            cur.close()
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM tbl_department")
    data1 = cur.fetchall()
    cur.close()
    return render_template("admin_viewmaterials.html", status=dept, depta=data1)
    
@app.route("/staff",methods=['POST','GET'])
def staff():
    if request.method=='POST':
        if request.form["submit"]=="Login":
            a=request.form["uname"]
            b=request.form["password"]
            cur=mysql.connection.cursor()
            cur.execute("select * from tbl_staff where sname=%s and semail=%s",(a,b))
            data=cur.fetchone()
            if data:
                session['logged_in']=True
                session['sid']=data["sid"]
                session['sname']=data["sname"]
                session['spass']=data["semail"]
                flash('Login Successfully','success')
                return redirect('staff_login')
            else:
                flash('Invalid Login. Try Again','danger')
    return render_template("staff.html" )
    
@app.route("/staff_login",methods=['POST','GET'])
def staff_login():
    return render_template("staff_login.html")
    
@app.route("/staff_viewprofile",methods=['POST','GET'])
def staff_viewprofile():
    cur=mysql.connection.cursor()
    cur.execute("select * from tbl_staff a inner join tbl_department d on a.did=d.did where a.sid=%s",((session['sid'],)))
    data=cur.fetchall()	
    return render_template("staff_viewprofile.html",datas=data)
    
@app.route("/staff_updatedetails", methods=['POST', 'GET'])
def staff_updatedetails():
    if request.method == 'POST':
        if request.form["submit"] == "Update":
            a = request.form["uname"]
            b = request.form["udept"]  
            c = request.form["uemail"]
            d = request.form["uphone"]
            if b:
                cur = mysql.connection.cursor()
                cur.execute(
                    "UPDATE tbl_staff SET sname=%s, did=%s, semail=%s, sphone=%s WHERE sid=%s",
                    (a, b, c, d, session['sid']))
                mysql.connection.commit()
                cur.close()    
                return redirect(url_for('staff_updatedetails'))
    cur = mysql.connection.cursor()
    cur.execute(" SELECT tbl_staff.sname, tbl_staff.semail, tbl_staff.sphone, tbl_department.did, tbl_department.dept FROM tbl_staff JOIN tbl_department ON tbl_staff.did = tbl_department.did WHERE tbl_staff.sid=%s", (session['sid'],))
    data = cur.fetchone()
    cur.close()
    cur = mysql.connection.cursor()
    cur.execute("SELECT did, dept FROM tbl_department")
    departments = cur.fetchall()
    cur.close()
    return render_template("staff_updatedetails.html", datas=data, departments=departments)
 
@app.route("/staff_updateprofile",methods=['POST','GET'])
def staff_updateprofile():
    if request.method == 'POST':
        if request.form["submit"] == "Update":
            file = request.files["file"]
            if file and allowed_extensions(file.filename):
                file_extension = os.path.splitext(file.filename)[1]
                new_filename = secure_filename(str(random.randint(10000, 99999)) + file_extension)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], new_filename)) 
                cur = mysql.connection.cursor()
                cur.execute("UPDATE tbl_staff SET simage=%s WHERE sid=%s", (new_filename, session['sid']))
                mysql.connection.commit()
                cur.close()
                return redirect(url_for('staff_updateprofile'))
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM tbl_staff WHERE sid=%s", (session['sid'],))
    data = cur.fetchone()
    cur.close()
    return render_template("staff_updateprofile.html", datas=data)
        
@app.route("/staff_addstudent",methods=['POST','GET'])
def staff_addstudent():
    if request.method=='POST':
        if request.form["submit"]=="ADD":
            e=request.form["uroll"]
            a=request.form["uname"]
            b=request.form["did"]
            c=request.form["uemail"]
            d=request.form["uphone"]
            file=request.files["file"]
            if file and allowed_extensions(file.filename):
                filename, file_extension = os.path.splitext(file.filename)
                new_filename = secure_filename(str(random.randint(10000,99999))+"."+file_extension)
                file.save(os.path.join(UPLOAD_FOLDER, new_filename)) 
                cur=mysql.connection.cursor()
                cur.execute("INSERT INTO tbl_student(strollno,stname,did,stemail,stphone,stimage) values(%s,%s,%s,%s,%s,%s)" ,(e,a,b,c,d,new_filename))
                mysql.connection.commit()
                cur.close()
    cur=mysql.connection.cursor()
    cur.execute("select * from tbl_student")
    data=cur.fetchall()
    cur.close()
    cur=mysql.connection.cursor()
    cur.execute("select * from tbl_department")
    data1=cur.fetchall()
    cur.close()
    return render_template("staff_addstudent.html",datas=data,dept=data1)
    
@app.route("/staff_uploadmaterials", methods=['POST', 'GET'])
def staff_uploadmaterials():
    if request.method == 'POST':
        if request.form.get("submit") == "Upload":
            a = request.form.get("did")
            b = request.form.get("dsem") 
            d= request.form.get("usub")  
            file = request.files.get("file")
            if file and allowed_extensions(file.filename):
                filename, file_extension = os.path.splitext(file.filename)
                new_filename = secure_filename(str(random.randint(10000, 99999)) + file_extension)
                file.save(os.path.join(UPLOAD_FOLDER, new_filename))
                cur = mysql.connection.cursor()
                cur.execute(
                    "INSERT INTO tbl_materials(did, material, sid, dsem,subject) VALUES(%s, %s, %s, %s,%s)",
                    (a, new_filename, session['sid'], b,d))
                mysql.connection.commit()
                cur.close()
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM tbl_materials")
    data = cur.fetchall()
    cur.close()
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM tbl_department")
    data1 = cur.fetchall()
    cur.close()
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM tbl_staff")
    data2 = cur.fetchall()
    cur.close()
    return render_template("staff_uploadmaterials.html", datas=data, dept=data1,status=data2)

@app.route("/staff_viewstudent",methods=['POST','GET'])
def staff_viewstudent():
    cur=mysql.connection.cursor()
    cur.execute("select * from tbl_student a inner join tbl_department d on a.did=d.did where d.did=%s",(session['sid'],))
    data=cur.fetchall()	
    cur.close()
    return render_template("staff_viewstudent.html",datas=data)
 
@app.route("/student",methods=['POST','GET'])
def student():
     if request.method=='POST':
        if request.form["submit"]=="Login":
            a=request.form["uname"]
            b=request.form["password"]
            cur=mysql.connection.cursor()
            cur.execute("select * from tbl_student where stname=%s and stemail=%s",(a,b))
            data=cur.fetchone()
            if data:
                session['logged_in']=True
                session['stid']=data["stid"]
                session['stname']=data["stname"]
                session['stpass']=data["stemail"]
                flash('Login Successfully','success')
                return redirect('student_login')
            else:
                flash('Invalid Login. Try Again','danger')
     return render_template("student.html" )

@app.route("/student_login",methods=['POST','GET'])
def student_login():
    return render_template("student_login.html")
    
@app.route("/student_viewprofile",methods=['POST','GET'])
def student_viewprofile():
    cur=mysql.connection.cursor()
    cur.execute("select * from tbl_student a inner join tbl_department d on a.did=d.did where a.stid=%s",(session["stid"],))
    data=cur.fetchall()	
    return render_template("student_viewprofile.html",datas=data)

@app.route("/student_updatedetails", methods=['POST', 'GET'])
def student_updatedetails():
    if request.method == 'POST':
        if request.form["submit"] == "Update":
            a = request.form["uroll"]
            b = request.form["uname"]
            c = request.form["udept"]  # Department ID
            d = request.form["uemail"]
            e = request.form["uphone"]
            stid = session.get("stid")
            if stid:
                cur = mysql.connection.cursor()
                cur.execute(" UPDATE tbl_student SET strollno = %s, stname = %s, did = %s, stemail = %s, stphone = %s WHERE stid = %s ", (a, b, c, d, e, stid))
                mysql.connection.commit()
                cur.close()
                return redirect(url_for('student_updatedetails'))
    cur = mysql.connection.cursor()
    cur.execute(" SELECT a.strollno, a.stname, a.stemail, a.stphone, a.did, d.dept  FROM tbl_student a INNER JOIN tbl_department d ON a.did = d.did WHERE a.stid = %s", (session.get("stid"),))
    data = cur.fetchone()
    cur.execute("SELECT did, dept FROM tbl_department")
    departments = cur.fetchall()
    cur.close()
    return render_template("student_updatedetails.html", datas=data, departments=departments)

@app.route("/student_updateprofile", methods=['POST', 'GET'])
def student_updateprofile():
    if request.method == 'POST':
        if request.form["submit"] == "Update":
            file = request.files["file"]
            if file and allowed_extensions(file.filename):
                file_extension = os.path.splitext(file.filename)[1]
                new_filename = secure_filename(str(random.randint(10000, 99999)) + file_extension)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], new_filename)) 
                cur = mysql.connection.cursor()
                cur.execute("UPDATE tbl_student SET stimage=%s WHERE stid=%s", (new_filename, session["stid"]))
                mysql.connection.commit()
                cur.close()
                return redirect(url_for('student_updateprofile'))
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM tbl_student WHERE stid=%s", (session["stid"],))
    data = cur.fetchone()
    cur.close()
    return render_template("student_updateprofile.html", datas=data)

@app.route("/student_downloadmaterials", methods=['POST', 'GET'])
def student_downloadmaterials():
    cur = mysql.connection.cursor()
    cur.execute(" SELECT * FROM tbl_materials m INNER JOIN tbl_department d ON m.did = d.did INNER JOIN tbl_student s ON s.did = d.did WHERE s.stid = %s", (session["stid"],))
    data = cur.fetchall()
    cur.close()
    return render_template("student_downloadmaterials.html", datas=data)
    
@app.route('/Logout')
def Logout():
    session.clear()
    return redirect(url_for("admin"))
    
@app.route("/download/<path:filename>",methods=['POST', 'GET'])
def download(filename):
    uploads = os.path.join(UPLOAD_FOLDER)
    return send_from_directory(uploads,filename, as_attachment=True)
    
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for("home"))

    
if __name__=='__main__':
    app.secret_key='secret123'
    app.run(debug=True)