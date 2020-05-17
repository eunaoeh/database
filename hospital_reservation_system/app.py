from flask import Flask, request, render_template, redirect, url_for
import pymysql
import csv
import urllib.request as ul
import xmltodict
import json
import datetime
from haversine import haversine

app = Flask(__name__)
conn = pymysql.connect(host='localhost', user='root', password='2017030482', db='dr_hyu', charset="utf8")
cnt_user_clinic = cnt_user_phar = 0
default_phar = default_clinic = 5

def DBconnection():
    sql = "SELECT COUNT(*) FROM USER"
    cur = conn.cursor()
    cur.execute(sql)
    res = cur.fetchall()[0][0]

    if res == 0:
        try:
            f = open("customers.csv", 'r', encoding='utf-8')
            if f != None:
                rdr = csv.reader(f)
                header = next(rdr)
                for line in rdr:
                    cur.execute("INSERT IGNORE INTO user (name, phone, local, domain, passwd, lat, lng) VALUES ('{}','{}', '{}', '{}', '{}', '{}', '{}')".format(line[0], line[1], line[2], line[3], line[4], float(line[6]), float(line[7])))
                    conn.commit()
        except Exception as ex:
            print(ex)
    
        print("initial DB set FINISHED")

def getData():
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM CLINIC")
    cnt = cur.fetchall()[0][0]
    if cnt == 0:
        OpenAPI_Clinic(0, 5)

    cur.execute("SELECT * FROM pharmacy")
    res = cur.fetchall()

    if len(res) == 0:
        OpenAPI_Pharmacy(0, 5)

def OpenAPI_Clinic(first, second):
    hanyang = (37.5585146, 127.0331892)
    cur = conn.cursor()
    for i in range(1, 101):
        URL = "http://apis.data.go.kr/B552657/HsptlAsembySearchService/getHsptlBassInfoInqire?serviceKey=pmxTNo7r3bisQw121DLdNQRyKuuird7xfX3MUhAqJWwH9H2UZ6D%2FqPZsyEgsegkEJStT4YTfcLVkWipJKnVElA%3D%3D&numOfRows=100&pageNo={}".format(i)
        request = ul.Request(URL)
        response = ul.urlopen(request)
        rescode = response.getcode()

        if rescode == 200:
            result_data = response.read()
            rD = xmltodict.parse(result_data)
            rDJ = json.dumps(rD)
            rDD = json.loads(rDJ)
            tdata = rDD["response"]['body']['items']['item']

            for j in range(100):
                data = tdata[j]
                if 'wgs84Lat' not in data.keys() or 'wgs84Lon' not in data.keys():
                    continue
                else:
                    place = (float(data['wgs84Lat']), float(data['wgs84Lon']))
                    if haversine(hanyang, place) <= second and haversine(hanyang,place) > first:
                        if 'dutyTime1s' not in data.keys():
                            data['dutyTime1s'] = data['dutyTime1c'] = '0000'
                        if 'dutyTime2s' not in data.keys():
                            data['dutyTime2s'] = data['dutyTime2c'] = '0000'
                        if 'dutyTime3s' not in data.keys():
                            data['dutyTime3s'] = data['dutyTime3c'] = '0000'
                        if 'dutyTime4s' not in data.keys():
                            data['dutyTime4s'] = data['dutyTime4c'] = '0000'
                        if 'dutyTime5s' not in data.keys():
                            data['dutyTime5s'] = data['dutyTime5c'] = '0000'
                        if 'dutyTime6s' not in data.keys():
                            data['dutyTime6s'] = data['dutyTime6c'] = '0000'
                        if 'dutyTime7s' not in data.keys():
                            data['dutyTime7s'] = data['dutyTime7c'] = '0000'
                            
                        sql = '''INSERT IGNORE INTO CLINIC (name, hpid, lat, lng, treatment, dutyTime1s,
                                    dutyTime1c, dutyTime2s, dutyTime2c, dutyTime3s, dutyTime3c, dutyTime4s,
                                    dutyTime4c, dutyTime5s, dutyTime5c, dutyTime6s, dutyTime6c, dutyTime7s, dutyTime7c, address)
                                    VALUES ("{}","{}",{},{},"{}",{},{},{},{},{},{},{},{},{},{},{},{},{},{},"{}")'''.format(
                                    data['dutyName'], data['hpid'], data['wgs84Lat'], data['wgs84Lon'], data['dgidIdName'],
                                    data['dutyTime1s'], data['dutyTime1c'], data['dutyTime2s'], data['dutyTime2c'],
                                    data['dutyTime3s'], data['dutyTime3c'], data['dutyTime4s'], data['dutyTime4c'],
                                    data['dutyTime5s'], data['dutyTime5c'], data['dutyTime6s'], data['dutyTime6c'],
                                    data['dutyTime7s'], data['dutyTime7c'], data['dutyAddr'])
                        cur.execute(sql)
                        conn.commit()
    cur.close()

def OpenAPI_Pharmacy(first, second):
    hanyang = (37.5585146, 127.0331892)
    cur = conn.cursor()
    for i in range(1,101):
        URL = "http://apis.data.go.kr/B552657/ErmctInsttInfoInqireService/getParmacyListInfoInqire?serviceKey=pmxTNo7r3bisQw121DLdNQRyKuuird7xfX3MUhAqJWwH9H2UZ6D%2FqPZsyEgsegkEJStT4YTfcLVkWipJKnVElA%3D%3D&numOfRows=100&pageNo={}".format(i)
        request = ul.Request(URL)
        response = ul.urlopen(request)
        rescode = response.getcode()

        if rescode == 200:
            result_data = response.read()
            rD = xmltodict.parse(result_data)
            rDJ = json.dumps(rD)
            rDD = json.loads(rDJ)
            tdata = rDD["response"]['body']['items']['item']

            for j in range(100):
                data = tdata[j]
                if 'wgs84Lat' not in data.keys() or 'wgs84Lon' not in data.keys():
                    continue
                else:
                    place = (float(data['wgs84Lat']), float(data['wgs84Lon']))
                    if haversine(hanyang, place) <= second and haversine(hanyang,place) > first:
                        sql = "INSERT IGNORE into pharmacy (name, hpid, lat, lng, address) VALUES ('{}','{}','{}','{}','{}')".format(data['dutyName'],data['hpid'], data['wgs84Lat'], data['wgs84Lon'], data['dutyAddr'])
                        cur.execute(sql)
                        conn.commit() 
    cur.close()

@app.route('/')
def main():
    return render_template("main.html")

@app.route('/sign_in', methods=['GET', 'POST'])
def signIn():
    global user, clinic, pharmacy
    user = {}
    clinic = {}
    pharmacy = {} 
    result = ""
    if request.method == 'POST':
        cur = conn.cursor(pymysql.cursors.DictCursor)
        sql = "SELECT * FROM USER WHERE local='{}' AND domain='{}' AND passwd='{}'".format(request.form['local'], request.form['domain'], request.form['passwd'])
        cur.execute(sql)
        user = cur.fetchall()

        if len(user) == 0:
            return render_template("sign_in.html", result="Sign in Failed. Try Again")
        
        user = user[0]

        sql = "SELECT * FROM TYPE WHERE ulocal='{}' AND udomain='{}'".format(user['local'], user['domain'])
        cur.execute(sql)
        userType = cur.fetchall()

        if len(userType) == 0:
            sql = "INSERT INTO TYPE (ulocal, udomain) VALUES ('{}', '{}')".format(user['local'], user['domain'])
            cur.execute(sql)
            conn.commit()
            return render_template("user_type.html")
        
        userType = userType[0]

        if request.form['type'] == 'none':
            return render_template("user_type.html")
        elif request.form['type'] == 'patient' and userType['patient'] == 1:
            return render_template("patient.html", name=user['name'])
        elif request.form['type'] == 'clinic' and userType['clinic'] == 1:
            cur = conn.cursor(pymysql.cursors.DictCursor)
            sql = "SELECT * FROM clinic c WHERE c.hpid=(SELECT cu.cid FROM clinic_user cu WHERE cu.ulocal='{}' AND cu.udomain='{}') and c.name=(SELECT cu.cname FROM clinic_user cu WHERE cu.ulocal='{}' and cu.udomain='{}')".format(request.form['local'], request.form['domain'], request.form['local'], request.form['domain'])
            cur.execute(sql)
            clinic = cur.fetchall()[0]
            OpenTime = ""
            if clinic['dutyTime1s'] != '0':
                OpenTime += " Mon: " + clinic['dutyTime1s'][:-2] + ':' + clinic['dutyTime1s'][-2:] + " ~ " + clinic['dutyTime1c'][:-2] + ':' + clinic['dutyTime1c'][-2:]
            if clinic['dutyTime2s'] != '0':
                OpenTime += "\n Tue: " + clinic['dutyTime2s'][:-2] + ':' + clinic['dutyTime2s'][-2:] + " ~ " + clinic['dutyTime2c'][:-2] + ':' + clinic['dutyTime2c'][-2:]
            if clinic['dutyTime3s'] != '0':
                OpenTime += "\n Wed: " + clinic['dutyTime3s'][:-2] + ':' + clinic['dutyTime3s'][-2:] + " ~ " + clinic['dutyTime3c'][:-2] + ':' + clinic['dutyTime3c'][-2:]
            if clinic['dutyTime4s'] != '0':
                OpenTime += "\n Thu: " + clinic['dutyTime4s'][:-2] + ':' + clinic['dutyTime4s'][-2:] + " ~ " + clinic['dutyTime4c'][:-2] + ':' + clinic['dutyTime4c'][-2:]
            if clinic['dutyTime5s'] != '0':
                OpenTime += "\n Fri: " + clinic['dutyTime5s'][:-2] + ':' + clinic['dutyTime5s'][-2:] + " ~ " + clinic['dutyTime5c'][:-2] + ':' + clinic['dutyTime5c'][-2:]
            if clinic['dutyTime6s'] != '0':
                OpenTime += "\n Sat: " + clinic['dutyTime6s'][:-2] + ':' + clinic['dutyTime6s'][-2:] + " ~ " + clinic['dutyTime6c'][:-2] + ':' + clinic['dutyTime6c'][-2:]
            if clinic['dutyTime7s'] != '0':
                OpenTime += "\n Sun: " + clinic['dutyTime7s'][:-2] + ':' + clinic['dutyTime7s'][-2:] + " ~ " + clinic['dutyTime7c'][:-2] + ':' + clinic['dutyTime7c'][-2:]

            clinic['time'] = OpenTime
            clinic['dis'] = haversine((user['lat'], user['lng']), (clinic['lat'], clinic['lng']))
            return render_template("clinic.html", distance=clinic['dis'],name = clinic['name'], hpid = clinic['hpid'], number=clinic['numDoctor'], treatment=clinic['treatment'], lat=clinic['lat'], lng=clinic['lng'], location=clinic['address'], time=clinic['time'])
        elif request.form['type'] == 'store' and userType['pharmacy'] == 1:
            cur = conn.cursor(pymysql.cursors.DictCursor)
            sql = "SELECT * FROM pharmacy p WHERE p.hpid=(SELECT pu.phid FROM pharmacy_user pu WHERE pu.ulocal='{}' AND pu.udomain='{}') and p.name=(SELECT pu.phname FROM pharmacy_user pu WHERE pu.ulocal='{}' and pu.udomain='{}')".format(user['local'], user['domain'], user['local'], user['domain'])
            cur.execute(sql)
            pharmacy = cur.fetchall()[0]
            return render_template("store.html", name=pharmacy['name'], hpid=pharmacy['hpid'], lat=pharmacy['lat'], lng=pharmacy['lng'], location=pharmacy['address'])
        else:
            result = "Choose Type again"
    return render_template("sign_in.html", result=result)

@app.route('/user_type', methods=['GET', 'POST'])
def userType():
    global cnt_user_clinic, user, cnt_user_phar
    if request.method == 'POST':
        cur = conn.cursor()
        type_list = request.form.getlist('type')
        print(type_list)
        if 'clinic' in type_list:
            sql = "INSERT into clinic_user (ulocal, udomain, cid, cname) SELECT '{}', '{}', c.hpid, c.name FROM clinic c LIMIT {}, 1".format(user['local'], user['domain'], cnt_user_clinic)
            cur.execute(sql)
            conn.commit()
            cnt_user_clinic += 1
        if 'pharmacy' in type_list:
            sql = "INSERT into pharmacy_user (ulocal, udomain, phid, phname) SELECT '{}', '{}', ph.hpid, ph.name FROM pharmacy ph LIMIT {}, 1".format(user['local'], user['domain'], cnt_user_phar)
            cur.execute(sql)
            conn.commit()
            cnt_user_phar += 1

        if len(type_list) == 1:
            sql = "UPDATE type SET {}=TRUE WHERE ulocal='{}' AND udomain='{}'".format(type_list[0], user['local'], user['domain'])
        elif len(type_list) == 2:
            sql = "UPDATE type SET {}=TRUE, {}=TRUE WHERE ulocal='{}' AND udomain='{}'".format(type_list[0], type_list[1], user['local'], user['domain'])
        elif len(type_list) == 3:
            sql = "UPDATE type SET {}=TRUE, {}=TRUE, {}=TRUE WHERE ulocal='{}' AND udomain='{}'".format(type_list[0], type_list[1], type_list[2], user['local'], user['domain'])
        elif len(type_list) == 4:
            sql = "UPDATE type SET {}=TRUE, {}=TRUE, {}=TRUE, {}=TRUE WHERE ulocal='{}' AND udomain='{}'".format(type_list[0], type_list[1], type_list[2],type_list[3], user['local'], user['domain'])
        else:
            return render_template("user_type.html", result="CHOOSE AT LEAST ONE")
        cur.execute(sql)
        conn.commit()
        return render_template("page_type.html")
    return render_template("user_type.html", result="")

@app.route('/page_type', methods=['GET', 'POST'])
def pageType():
    global clinic, user, pharmacy
    if request.method == "GET":
        page_type = request.args.get('type')
        if page_type == 'patient':
            return render_template("patient.html", name=user['name'])
        elif page_type == 'clinic':
            cur = conn.cursor(pymysql.cursors.DictCursor)
            sql = "SELECT * FROM clinic c WHERE c.hpid=(SELECT cu.cid FROM clinic_user cu WHERE cu.ulocal='{}' AND cu.udomain='{}') and c.name=(SELECT cu.cname FROM clinic_user cu WHERE cu.ulocal='{}' and cu.udomain='{}')".format(user['local'], user['domain'], user['local'], user['domain'])
            cur.execute(sql)
            clinic = cur.fetchall()[0]
            OpenTime = ""
            if clinic['dutyTime1s'] != '0':
                OpenTime += " Mon: " + clinic['dutyTime1s'][:-2] + ':' + clinic['dutyTime1s'][-2:] + " ~ " + clinic['dutyTime1c'][:-2] + ':' + clinic['dutyTime1c'][-2:]
            if clinic['dutyTime2s'] != '0':
                OpenTime += "\n Tue: " + clinic['dutyTime2s'][:-2] + ':' + clinic['dutyTime2s'][-2:] + " ~ " + clinic['dutyTime2c'][:-2] + ':' + clinic['dutyTime2c'][-2:]
            if clinic['dutyTime3s'] != '0':
                OpenTime += "\n Wed: " + clinic['dutyTime3s'][:-2] + ':' + clinic['dutyTime3s'][-2:] + " ~ " + clinic['dutyTime3c'][:-2] + ':' + clinic['dutyTime3c'][-2:]
            if clinic['dutyTime4s'] != '0':
                OpenTime += "\n Thu: " + clinic['dutyTime4s'][:-2] + ':' + clinic['dutyTime4s'][-2:] + " ~ " + clinic['dutyTime4c'][:-2] + ':' + clinic['dutyTime4c'][-2:]
            if clinic['dutyTime5s'] != '0':
                OpenTime += "\n Fri: " + clinic['dutyTime5s'][:-2] + ':' + clinic['dutyTime5s'][-2:] + " ~ " + clinic['dutyTime5c'][:-2] + ':' + clinic['dutyTime5c'][-2:]
            if clinic['dutyTime6s'] != '0':
                OpenTime += "\n Sat: " + clinic['dutyTime6s'][:-2] + ':' + clinic['dutyTime6s'][-2:] + " ~ " + clinic['dutyTime6c'][:-2] + ':' + clinic['dutyTime6c'][-2:]
            if clinic['dutyTime7s'] != '0':
                OpenTime += "\n Sun: " + clinic['dutyTime7s'][:-2] + ':' + clinic['dutyTime7s'][-2:] + " ~ " + clinic['dutyTime7c'][:-2] + ':' + clinic['dutyTime7c'][-2:]

            clinic['time'] = OpenTime
            clinic['dis'] = haversine((user['lat'], user['lng']), (clinic['lat'], clinic['lng']))
            
            return render_template("clinic.html", distance=clinic['dis'],name=clinic['name'], hpid=clinic['hpid'], number=clinic['numDoctor'], treatment=clinic['treatment'], lat=clinic['lat'], lng=clinic['lng'], location=clinic['address'], time=clinic['time'])
        elif page_type == 'store':
            cur = conn.cursor(pymysql.cursors.DictCursor)
            sql = "SELECT * FROM pharmacy p WHERE p.hpid=(SELECT pu.phid FROM pharmacy_user pu WHERE pu.ulocal='{}' AND pu.udomain='{}') and p.name=(SELECT pu.phname FROM pharmacy_user pu WHERE pu.ulocal='{}' and pu.udomain='{}')".format(user['local'], user['domain'], user['local'], user['domain'])
            cur.execute(sql)
            pharmacy = cur.fetchall()[0]
            return render_template("store.html", name=pharmacy['name'], hpid=pharmacy['hpid'], lat=pharmacy['lat'], lng=pharmacy['lng'], location=pharmacy['address'])

    return render_template("page_type.html")

@app.route('/create_account', methods=['POST', 'GET'])
def createAccount():
    global cnt_user_clinic, cnt_user_phar
    result = ""
    if request.method == "POST":
        cur = conn.cursor()
        sql = "INSERT INTO USER (name, phone, local, domain, passwd, lat, lng) VALUES ('{}','{}','{}','{}', '{}', {}, {})".format(request.form['name'], request.form['phone'], request.form['local'], request.form['domain'], request.form['passwd'], float(request.form['lat']), float(request.form['lng']))
        cur.execute(sql)
        conn.commit()
        type_list = request.form.getlist('type')

        if 'clinic' in type_list:
            sql = "INSERT into clinic_user (ulocal, udomain, cid, cname) SELECT '{}', '{}', c.hpid, c.name FROM clinic c LIMIT {}, 1".format(request.form['local'], request.form['domain'], cnt_user_clinic)
            cur.execute(sql)
            conn.commit()
            cnt_user_clinic += 1
        if 'pharmacy' in type_list:
            sql = "INSERT into pharmacy_user (ulocal, udomain, phid, phname) SELECT '{}', '{}', ph.hpid, ph.name FROM pharmacy ph LIMIT {}, 1".format(request.form['local'], request.form['domain'], cnt_user_phar)
            cur.execute(sql)
            conn.commit()
            cnt_user_phar += 1 

        if len(type_list) == 0:
            return render_template("create_account.html", result = "Click your user type")
        elif len(type_list) == 1:
            sql = "INSERT INTO TYPE (ulocal, udomain, {}) VALUES ('{}', '{}', TRUE)".format(type_list[0] , request.form['local'], request.form['domain']) 
        elif len(type_list) == 2:
            sql = "INSERT INTO TYPE (ulocal, udomain, {}, {}) VALUES ('{}', '{}', TRUE, TRUE)".format(type_list[0], type_list[1], request.form['local'], request.form['domain'])
        elif len(type_list) == 3:
            sql = "INSERT INTO TYPE (ulocal, udomain, {}, {}, {}) VALUES ('{}', '{}', TRUE, TRUE, TRUE)".format(type_list[0], type_list[1], type_list[2], request.form['local'], request.form['domain'])
        elif len(type_list) == 3:
            sql = "INSERT INTO TYPE (ulocal, udomain, {}, {}, {}, {}) VALUES ('{}', '{}', TRUE, TRUE, TRUE, TRUE)".format(type_list[0], type_list[1], type_list[2],type_list[3], request.form['local'], request.form['domain'])
        cur.execute(sql)
        conn.commit()
        return render_template("create_success.html")
    
    return render_template("create_account.html")

@app.route("/create_success")
def createSuccess():
    return render_template("create_success.html")

@app.route("/clinic")
def clinic():
    global clinic, user
    if len(clinic) == 0:
        return redirect(url_for(signIn))
    cur = conn.cursor(pymysql.cursors.DictCursor)
    sql = "SELECT * FROM clinic c WHERE c.hpid=(SELECT cu.cid FROM clinic_user cu WHERE cu.ulocal='{}' AND cu.udomain='{}') and c.name=(SELECT cu.cname FROM clinic_user cu WHERE cu.ulocal='{}' and cu.udomain='{}')".format(user['local'], user['domain'], user['local'], user['domain'])
    cur.execute(sql)
    clinic = cur.fetchall()[0]
    OpenTime = ""
    if clinic['dutyTime1s'] != '0':
        OpenTime += " Mon: " + clinic['dutyTime1s'][:-2] + ':' + clinic['dutyTime1s'][-2:] + " ~ " + clinic['dutyTime1c'][:-2] + ':' + clinic['dutyTime1c'][-2:]
    if clinic['dutyTime2s'] != '0':
        OpenTime += "\n Tue: " + clinic['dutyTime2s'][:-2] + ':' + clinic['dutyTime2s'][-2:] + " ~ " + clinic['dutyTime2c'][:-2] + ':' + clinic['dutyTime2c'][-2:]
    if clinic['dutyTime3s'] != '0':
        OpenTime += "\n Wed: " + clinic['dutyTime3s'][:-2] + ':' + clinic['dutyTime3s'][-2:] + " ~ " + clinic['dutyTime3c'][:-2] + ':' + clinic['dutyTime3c'][-2:]
    if clinic['dutyTime4s'] != '0':
        OpenTime += "\n Thu: " + clinic['dutyTime4s'][:-2] + ':' + clinic['dutyTime4s'][-2:] + " ~ " + clinic['dutyTime4c'][:-2] + ':' + clinic['dutyTime4c'][-2:]
    if clinic['dutyTime5s'] != '0':
        OpenTime += "\n Fri: " + clinic['dutyTime5s'][:-2] + ':' + clinic['dutyTime5s'][-2:] + " ~ " + clinic['dutyTime5c'][:-2] + ':' + clinic['dutyTime5c'][-2:]
    if clinic['dutyTime6s'] != '0':
        OpenTime += "\n Sat: " + clinic['dutyTime6s'][:-2] + ':' + clinic['dutyTime6s'][-2:] + " ~ " + clinic['dutyTime6c'][:-2] + ':' + clinic['dutyTime6c'][-2:]
    if clinic['dutyTime7s'] != '0':
        OpenTime += "\n Sun: " + clinic['dutyTime7s'][:-2] + ':' + clinic['dutyTime7s'][-2:] + " ~ " + clinic['dutyTime7c'][:-2] + ':' + clinic['dutyTime7c'][-2:]

    clinic['time'] = OpenTime
    clinic['dis'] = haversine((user['lat'], user['lng']), (clinic['lat'], clinic['lng']))
            
    return render_template("clinic.html", distance=clinic['dis'], name = clinic['name'], hpid = clinic['hpid'], number=clinic['numDoctor'], treatment=clinic['treatment'], lat=clinic['lat'], lng=clinic['lng'], location=clinic['address'], time=clinic['time'])

@app.route("/clinic_reserve_list")
def clinic_reserve_list():
    global clinic
    cur = conn.cursor(pymysql.cursors.DictCursor)
    sql = "SELECT pname, pnumber, date, time from clinic_reserve where cname='{}' and cid='{}'".format(clinic['name'], clinic['hpid'])
    cur.execute(sql)
    result = cur.fetchall()
    List = ""
    for res in result:
        List += "Name: " + res['pname'] + " Phone: " + res['pnumber'] + " Date: " + res['date'].strftime('%Y-%m-%d') + " Time: " + str(res['time'])
        List += '\n'
    return render_template("clinic_reserve_list.html", name=clinic['name'], hpid=clinic['hpid'], list=List)

@app.route("/treat_patient", methods=['POST','GET'])
def clinic_treat():
    global clinic
    cur = conn.cursor(pymysql.cursors.DictCursor)
    sql = "SELECT pname, pnumber, date, time from clinic_reserve where cname='{}' and cid='{}'".format(clinic['name'], clinic['hpid'])
    cur.execute(sql)
    result = cur.fetchall()
    List = ""
    for res in result:
        List += "Name: " + res['pname'] + " Phone: " + res['pnumber'] + " Date: " + res['date'].strftime('%Y-%m-%d') + " Time: " + str(res['time'])
        List += '\n'
    return render_template("treat_patient.html", name=clinic['name'], hpid=clinic['hpid'], list=List)

@app.route("/clinic_prescribe", methods=['POST','GET'])
def clinic_prescribe():
    global clinic, user
    cur = conn.cursor(pymysql.cursors.DictCursor)
    if request.method == "POST":
        pname = request.form['Name']
        pnumber = request.form['Phone']
        date = datetime.datetime(int(request.form['year']), int(request.form['mon']), int(request.form['date']), int(request.form['hour']), int(request.form['min']))
        medicine = request.form['medicine']
        timeDosage = request.form['timeDosage']
        dayDosage = request.form['dayDosage']
        total = request.form['total']

        sql = "INSERT into prescription (date, clinic, pname, pnumber, medicine, timeDosage, dayDosage, totalDosage) VALUES ('{}', '{}', '{}', '{}', '{}', {}, {}, {})".format(date, clinic['name'], pname, pnumber, medicine, timeDosage, dayDosage, total)
        cur.execute(sql)
        conn.commit()

        sql = "SELECT date from clinic_reserve where pname='{}' and pnumber='{}' and cname='{}' and cid='{}'".format(pname, pnumber, clinic['name'], clinic['hpid'])

        cur.execute(sql)
        tmpdate = cur.fetchall()[0] #check the day seperately

        sql = "INSERT into clinic_complete (pname, pnumber, date, cname, cid, ulocal, udomain) VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}')".format(pname, pnumber, tmpdate['date'], clinic['name'], clinic['hpid'], user['local'], user['domain'])
        cur.execute(sql)
        conn.commit()

        sql = "DELETE FROM clinic_reserve where pname='{}' and pnumber='{}' and cname='{}' and cid='{}'".format(pname, pnumber, clinic['name'], clinic['hpid'])
        cur.execute(sql)
        conn.commit()

        return render_template("clinic_prescribe.html", total=total, dosage=timeDosage, daydosage=dayDosage, clinic=clinic['name'], medicine=medicine, date=date.strftime("%Y %m %d %H %m"), pname=pname, pnumber=pnumber, name=clinic['name'], hpid=clinic['hpid'])

@app.route("/clinic_list_all", methods=["POST", "GET"])
def clinic_list_all():
    global clinic, user
    cur = conn.cursor(pymysql.cursors.DictCursor)
    if request.method == "POST":
        pname = request.form['Name']
        pnumber = request.form['Phone']
        date = datetime.datetime(int(request.form['year']), int(request.form['mon']), int(request.form['date']))
       
        sql = "SELECT * from clinic_complete where ulocal='{}' and udomain='{}' and pname='{}' and pnumber='{}' and date='{}'".format(user['local'], user['domain'], pname, pnumber, date)
        cur.execute(sql)
        result = cur.fetchall()
        line = ""
        if len(result) != 0:
            result = result[0]
            line += "Name: " + result['pname'] + "\nPhone: " + result['pnumber'] + "\nDate: " + result['date'].strftime('%Y %m %d')
        line += '\n'
        return render_template("clinic_list_all.html", result=line, name=clinic['name'], hpid=clinic['hpid'])

    sql = "SELECT pname, pnumber, date from clinic_complete where ulocal='{}' and udomain='{}'".format(user['local'], user['domain'])
    cur.execute(sql)
    result = cur.fetchall()
    List = ""
    for res in result:
        List += "Name: " + res['pname'] + " Phone: " + res['pnumber'] + " Date: " + res['date'].strftime('%Y %m %d')
        List += '\n'
    return render_template("clinic_list_all.html", name=clinic['name'], hpid=clinic['hpid'], list=List)

@app.route("/patient")
def patient():
    global user
    if len(user) == 0:
        return redirect(url_for(signIn))
    return render_template("patient.html", name=user['name'])

@app.route("/register_most_visited", methods=['POST', 'GET'])
def register_favorite():
    global user
    cur = conn.cursor(pymysql.cursors.DictCursor)
    sql = "SELECT name, hpid, address from clinic"
    cur.execute(sql)
    result = cur.fetchall()
    List = ""
    for res in result:
        List += "Name: " + res['name'] + " ID: " + res['hpid'] + " Location: " + res['address']
        List += '\n'

    sql = "SELECT cname, cid from patient_favorite where pname='{}' and pnumber='{}'".format(user['name'], user['phone'])
    cur.execute(sql)
    result = cur.fetchall()
    favor = ""
    for res in result:
        favor += "Name: " + res['cname'] + " ID: " + res['cid']
        favor += '\n'
    
    if request.method == "POST":
        cname = request.form['cname']
        cid = request.form['cid']
        sql = "INSERT into patient_favorite (pname, pnumber, cid, cname) VALUES ('{}','{}','{}','{}')".format(user['name'], user['phone'], cid, cname)
        cur.execute(sql)
        conn.commit()
        line = "Register {} {} as your favorite clinic".format(cname, cid)
        cur.close()
        return render_template("register_most_visited.html", favor=favor, list=List, result=line, name=user['name'])
    cur.close()
    return render_template("register_most_visited.html", favor=favor, list=List, name=user['name'])

@app.route("/recent_clinic", methods=['GET'])
def recent_clinic():
    global user
    cur = conn.cursor(pymysql.cursors.DictCursor)
    sql = "SELECT c.cid, c.cname, p.date from clinic_user c, clinic_complete p WHERE c.ulocal=p.ulocal and p.udomain=c.udomain and p.pnumber='{}' order by p.date desc".format(user['phone'])
    cur.execute(sql)
    result = cur.fetchall()
    List = ""

    for res in result:
        List += "Date: " + res['date'].strftime("%Y-%m-%d") + " Name: " + res['cname'] + " ID: " + res['cid']
        List += '\n'
    cur.close()
    return render_template("recent_clinic.html", list=List, name=user['name'])

@app.route("/search_clinic", methods=['POST', 'GET'])
def search_clinic():
    global default_clinic, user
    if request.method == "POST":
        dis = request.form['dis']
        wdis = request.form['wdis']
        if dis != "":
            dis = float(dis)
            cur = conn.cursor(pymysql.cursors.DictCursor)
            sql = "SELECT name, hpid, address, lng, lat from clinic;"
            cur.execute(sql)
            result = cur.fetchall()
            tmp = []
            mine= (user['lat'], user['lng'])
            for res in result:
                place = (res['lat'], res['lng'])
                if haversine(mine, place) <= dis:
                    res['distance'] = haversine(mine, place)
                    tmp.append(res)
            List = ""
            for res in tmp:
                List += "Name: " + res['name'] + " ID: " + res['hpid'] + " Location: " + res['address'] + " Distance: " + str(res['distance'])
                List += '\n'
            cur.close()
            return render_template("search_clinic.html", result=List, name=user['name'])
        elif wdis != "":
            wdis = float(wdis)
            OpenAPI_Clinic(5, wdis)
            default_clinic = wdis
            return render_template("search_clinic.html", result="More clinics are added into the database", name=user['name'])

    return render_template("search_clinic.html", name=user['name'])    

@app.route("/search_clinic_type", methods=['POST', 'GET'])
def search_clinic_type():
    List = "내과 소아청소년과 신경과 정신건강의학과 피부과 외과 흉부외과 정형외과 신경외과 성형외과 산부인과 안과 이비인후과 비뇨기과 재활의학과\n마취통증의학과 영상의학과 치료방사선과 임상병리과 해부병리과 가정의학과 핵의학과 응급의학과 치과 구강악안면외과"
    cur = conn.cursor(pymysql.cursors.DictCursor)
    if request.method == "POST":
        depart = request.form['depart']
        sql = "SELECT name, hpid, address, treatment from clinic"
        cur.execute(sql)
        result = cur.fetchall()
        tmp = []
        for res in result:
            if depart in res['treatment']:
                tmp.append(res)
        
        line = ""
        for res in tmp:
            line += "Name: " + res['name'] + " ID: " + res['hpid'] + " Location: " + res['address'] + "\nMedical Department: " + res['treatment']
            line += '\n'
        return render_template("search_clinic_type.html", list=List, result=line)

    return render_template("search_clinic_type.html", list=List)

@app.route("/search_clinic_name", methods=['POST', 'GET'])
def search_clinic_name():
    cur = conn.cursor(pymysql.cursors.DictCursor)
    sql = "SELECT name, hpid, address from clinic"
    cur.execute(sql)
    result = cur.fetchall()
    tmp = ""
    for res in result:
        tmp += "Name: " + res['name'] + " ID: " + res['hpid'] + " Location: " + res['address']
        tmp += '\n'
    if request.method == "POST":
        cname = request.form['cname']
        sql = "SELECT name, hpid, address from clinic where name='{}'".format(cname)
        cur.execute(sql)
        result = cur.fetchall()
        List = ""
        for res in result:
            List += "Name: " + res['name'] + " ID: " + res['hpid'] + " Location: " + res['address']
            List += '\n'
        return render_template("search_clinic_name.html", list=tmp, result=List, name=user['name'])
    return render_template("search_clinic_name.html", list=tmp, name=user['name'])

@app.route("/search_clinic_map", methods=['POST', 'GET'])
def search_map():
    if request.method == 'POST':
        cname = request.form['cname']
        cid = request.form['cid']
        cur = conn.cursor(pymysql.cursors.DictCursor)
        sql = "select lat, lng from clinic where name='{}' and hpid='{}'".format(cname, cid)
        cur.execute(sql)
        result = cur.fetchall()[0]
        cur.close()
        return render_template("map.html", lat = result['lat'], lng = result['lng'], name=cname, id=cid)

    cur = conn.cursor(pymysql.cursors.DictCursor)
    sql = "select name, hpid, address from clinic"
    cur.execute(sql)
    result = cur.fetchall()
    line = ""
    for res in result:
        line += 'Name: ' + res['name'] + " ID: " + res['hpid'] + " Location: " + res['hpid']
        line += '\n'
    cur.close()
    return render_template("search_clinic_map.html", list=line)

@app.route("/search_pharmacy", methods=['POST', 'GET'])
def search_pharmacy():
    global default_phar
    if request.method == "POST":
        dis = request.form['dis']
        wdis = request.form['wdis']
        if dis != "":
            dis = float(dis)
            cur = conn.cursor(pymysql.cursors.DictCursor)
            sql = "SELECT name, hpid, address, lng, lat from pharmacy;"
            cur.execute(sql)
            result = cur.fetchall()
            tmp = []
            mine= (user['lat'], user['lng'])
            for res in result:
                place = (res['lat'], res['lng'])
                if haversine(mine, place) <= dis:
                    res['distance'] = haversine(mine, place)
                    tmp.append(res)
            List = ""
            for res in tmp:
                List += "Name: " + res['name'] + " ID: " + res['hpid'] + " Location: " + res['address'] + " Distance: " + str(res['distance'])
                List += '\n'
            cur.close()
            return render_template("search_pharmacy.html", result=List, name=user['name'])
        elif wdis != "":
            wdis = float(wdis)
            OpenAPI_Pharmacy(5, wdis)
            default_phar = wdis
            return render_template("search_pharmacy.html", result="More pharmacies are added into the database", name=user['name'])

    return render_template("search_pharmacy.html", name=user['name'])  


@app.route("/reserve_clinic", methods=['POST', 'GET'])
def reserve_clinic():
    global user
    cur = conn.cursor(pymysql.cursors.DictCursor)
    if request.method=='POST':
        pname = request.form['pname']
        pnumber = request.form['pnumber']
        cname = request.form['cname']
        cid = request.form['cid']
        date = datetime.date(int(request.form['year']), int(request.form['mon']), int(request.form['date']))
        time = datetime.time(int(request.form['hour']), int(request.form['min']), 0)

        sql = "INSERT into clinic_reserve (pname, pnumber, cname, cid, date, time) values ('{}', '{}', '{}', '{}', '{}', '{}')".format(pname, pnumber, cname, cid, date, time)
        cur.execute(sql)
        conn.commit()
        return render_template("reserve_clinic.html", name=user['name'],result="Reservation is completed!")

    sql = "SELECT * from clinic"
    cur.execute(sql)
    result = cur.fetchall()
    
    List = ""
    for res in result:
        OpenTime = ""
        if res['dutyTime1s'] != '0':
            OpenTime += " Mon: " + res['dutyTime1s'][:-2] + ':' + res['dutyTime1s'][-2:] + " ~ " + res['dutyTime1c'][:-2] + ':' + res['dutyTime1c'][-2:]
        if res['dutyTime2s'] != '0':
            OpenTime += "\n Tue: " + res['dutyTime2s'][:-2] + ':' + res['dutyTime2s'][-2:] + " ~ " + res['dutyTime2c'][:-2] + ':' + res['dutyTime2c'][-2:]
        if res['dutyTime3s'] != '0':
            OpenTime += "\n Wed: " + res['dutyTime3s'][:-2] + ':' + res['dutyTime3s'][-2:] + " ~ " + res['dutyTime3c'][:-2] + ':' + res['dutyTime3c'][-2:]
        if res['dutyTime4s'] != '0':
            OpenTime += "\n Thu: " + res['dutyTime4s'][:-2] + ':' + res['dutyTime4s'][-2:] + " ~ " + res['dutyTime4c'][:-2] + ':' + res['dutyTime4c'][-2:]
        if res['dutyTime5s'] != '0':
            OpenTime += "\n Fri: " + res['dutyTime5s'][:-2] + ':' + res['dutyTime5s'][-2:] + " ~ " + res['dutyTime5c'][:-2] + ':' + res['dutyTime5c'][-2:]
        if res['dutyTime6s'] != '0':
            OpenTime += "\n Sat: " + res['dutyTime6s'][:-2] + ':' + res['dutyTime6s'][-2:] + " ~ " + res['dutyTime6c'][:-2] + ':' + res['dutyTime6c'][-2:]
        if res['dutyTime7s'] != '0':
            OpenTime += "\n Sun: " + res['dutyTime7s'][:-2] + ':' + res['dutyTime7s'][-2:] + " ~ " + res['dutyTime7c'][:-2] + ':' + res['dutyTime7c'][-2:]    
        
        List += "Name: " + res['name'] + " ID: " + res['hpid'] + " Location: " + res['address'] + " Open Time: \n" + OpenTime
        List += '\n'
    
    return render_template("reserve_clinic.html", name=user['name'], list=List)

@app.route("/reserve_pharmacy", methods=['POST', 'GET'])
def reserve_pharmacy():
    global user
    cur = conn.cursor(pymysql.cursors.DictCursor)
    if request.method=='POST':
        pname = request.form['pname']
        pnumber = request.form['pnumber']
        phname = request.form['phname']
        phid = request.form['phid']
        cname = request.form['cname']

        sql = "INSERT into pharmacy_reserve (pname, pnumber, phname, phid, cname) values ('{}', '{}', '{}', '{}', '{}')".format(pname, pnumber, phname, phid, cname)
        cur.execute(sql)
        conn.commit()

        sql = "Update Prescription set pharmacy='{}' where pname='{}' and pnumber='{}' and clinic='{}'".format(phname,pname,pnumber,cname)
        cur.execute(sql)
        conn.commit()

        return render_template("reserve_pharmacy.html", result="Reservation is completed!")

    sql = "SELECT * from pharmacy"
    cur.execute(sql)
    result = cur.fetchall()
    
    List = ""
    for res in result:
        List += "Name: " + res['name'] + " ID: " + res['hpid'] + " Location: " + res['address']
        List += '\n'

    sql = "SELECT * from prescription where pnumber='{}' and pharmacy is null".format(user['phone'])
    cur.execute(sql)
    result = cur.fetchall()
    
    List2 = ""
    for res in result:
        List2 += "Name: " + res['clinic'] + " ID: " + res['date'].strftime("%Y-%m-%d")
        List2 += '\n'
    
    return render_template("reserve_pharmacy.html", pre=List2, list=List, name=user['name'])

@app.route("/prescription_result", methods=['POST', 'GET'])
def prescription_result():
    cur = conn.cursor(pymysql.cursors.DictCursor)
    if request.method=='POST':
        clinic = request.form['clinic']
        pharmacy = request.form['pharmacy']
        date = datetime.datetime(int(request.form['year']), int(request.form['mon']), int(request.form['date']), int(request.form['hour']), int(request.form['min']))

        sql = "select * from prescription where clinic='{}' and date='{}'".format(clinic, date)
        cur.execute(sql)
        result = cur.fetchall()
        for res in result:
            pname = res['pname']
            pnumber = res['pnumber']
            date = res['date']
            clinic = res['clinic']
            medicine = res['medicine']
            dosage = res['timeDosage']
            daydosage = res['dayDosage']
            total = res['totalDosage']
            pharmacy = res['pharmacy']
            pdate = res['prescriptedDay']
            extra = res['extra']
            presult = res['result']
            if presult == 1:
                presult = "Checking"
            elif presult == 2:
                presult = "Available"
            elif presult == 3:
                presult = "Unavailable"
            return render_template("prescription_result.html", extra=extra, pname=pname, pnumber=pnumber, date=date, clinic=clinic, medicine=medicine, dosage=dosage, daydosage=daydosage, total=total, pharmacy=pharmacy, pdate=pdate, result=presult)

    sql = "SELECT p.date, p.result, p.pharmacy, p.clinic from prescription p where p.pname='{}' and p.pnumber='{}' order by p.date desc".format(user['name'], user['phone'])
    cur.execute(sql)
    result = cur.fetchall()
    
    List = ""
    for res in result:
        tmp = ""
        if res['result'] == 1:
            tmp = "Checking"
        elif res['result'] == 2:
            tmp = "Available"
        elif res['result'] == 3:
            tmp = "Unavailabe"
        else:
            tmp = "Not Reserve Pharmacy Yet"
        if res['pharmacy'] == None:
            res['pharmacy'] = ""
        List += "Result: " + tmp + " Date: " + res['date'].strftime("%Y-%m-%d, %H:%M") + " Clinic Name: " + res['clinic'] + " Pharmacy: " + res['pharmacy']
        List += '\n'
    
    return render_template("prescription_result.html", list=List)    


@app.route("/store")
def pharmacy():
    global pharmacy
    if len(pharmacy) == 0:
        return redirect(url_for(signIn))
    return render_template("store.html", name=pharmacy['name'], hpid=pharmacy['hpid'])

@app.route("/pharmacy_reserve_list", methods=['GET'])
def pharmacy_reserve_list():
    global user, pharmacy
    cur = conn.cursor(pymysql.cursors.DictCursor)

    sql = "SELECT * from prescription where pharmacy='{}' and result=1".format(pharmacy['name'])
    cur.execute(sql)
    result = cur.fetchall()
    List = ""
    for res in result:
        List += "Name: " + res['pname'] + " Phone: " + res['pnumber'] + " Clinic: "+res['clinic'] + " Date: "+res['date'].strftime("%Y-%m-%d-%H-%M") + " Medicine: " + res['medicine'] + " Dosage Per Time: " + str(res['timeDosage']) + " Dosage Per Day: " +str(res['dayDosage']) + " Total Dosage: " + str(res['totalDosage'])
        List += '\n'
    
    return render_template("pharmacy_reserve_list.html", list=List)

@app.route("/prescribe_patient", methods=['GET', 'POST'])
def prescribe_patient():
    global pharmacy, user
    result = ""
    cur = conn.cursor(pymysql.cursors.DictCursor)
    if request.method == "POST":
        pname = request.form['pname']
        pnumber = request.form['pnumber']
        cname = request.form['cname']
        if request.form['year'] != "":
            date = datetime.datetime(int(request.form['year']), int(request.form['mon']), int(request.form['date']), int(request.form['hour']), int(request.form['min']))
        result = int(request.form['type'])
        extra = request.form['extra']
        if result == 2:
            sql = "UPDATE prescription set pharmacy='{}', prescriptedDay='{}',result={}, extra='{}' WHERE pname='{}' and pnumber='{}' and result=1 and clinic='{}'".format(pharmacy['name'],date,2,extra, pname, pnumber, cname)
            cur.execute(sql)
            conn.commit()
            result = "Prescription is completed"
        elif result == 3:
            sql = "UPDATE prescription set result=3, pharmacy='{}' where pname='{}' and pnumber='{}' and clinic='{}'".format(pharmacy['name'], pname,pnumber, cname)
            cur.execute(sql)
            conn.commit()
            result = "Prescription is completed"
        
        sql = "DELETE FROM pharmacy_reserve where pname='{}' and pnumber='{}' and phname='{}' and phid='{}' and cname='{}'".format(pname, pnumber, pharmacy['name'], pharmacy['hpid'], cname)
        cur.execute(sql)
        conn.commit()

        return render_template("prescribe_patient.html", result=result)
    
    sql = "SELECT pname, pnumber,cname from pharmacy_reserve pr where phname='{}' and phid='{}'".format(pharmacy['name'], pharmacy['hpid'])
    cur.execute(sql)
    result = cur.fetchall()
    List = ""
    for res in result:
        List += "Name: " + res['pname'] + " Phone: " + res['pnumber'] + " Clinic: " + res['cname']
        List += '\n'
    return render_template("prescribe_patient.html", list=List)

if __name__ == "__main__":
    user = {}
    clinic = {}
    pharmacy = {}

    DBconnection()
    getData()
    app.run("127.0.0.1", port=9999, debug=True)
