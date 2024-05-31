from flask import Blueprint, render_template, request, redirect, url_for
import pyodbc
from faker import Faker
from werkzeug.security import check_password_hash
from website.templates.database import Hastalar
from website.templates.database import Hasta_Bilgileri
from website.templates.database import Randevu_Bilgileri
from website.templates.database import Doktor_Bilgileri
from website.templates.database import Yonetici
from website.templates.database import get_specialization_list
from website.templates.database import get_doctor_by_id
from website.templates.database import hastane_isimleri

auth = Blueprint('auth', __name__)
fake = Faker("tr_TR")

connection = pyodbc.connect(
    "Driver={SQL Server};"
    "Server=YOURDATABASE\\SQLEXPRESS;"
    "Database=hastane;"
    "Trusted_Connection=yes;"
)
cursor = connection.cursor()

def paging(sorgu, sayfa, sayfa_sinir):
    basla = (sayfa - 1) * sayfa_sinir
    return sorgu[basla: basla + sayfa_sinir]

def get_doctors_by_specialization(specialization):
    sql = "SELECT doktorID, isim, soy_isim FROM Doktorlar WHERE uzmanlik_alani = ?"
    cursor.execute(sql, (specialization))
    return cursor.fetchall()

@auth.route('/adminlogin', methods = ["POST", "GET"])
def admin_login():
    if request.method == "POST":
        admin_id = request.form['adminid']
        admin_password = request.form['adminpassword']
        adm_sorgu = "SELECT COUNT(1) FROM Yoneticiler WHERE yoneticiID = ?"
        cursor.execute(adm_sorgu, (admin_id,))
        adm_exists = cursor.fetchone()[0]
        if adm_exists:
            adm_pass_sorgu = "SELECT sifre FROM Yoneticiler WHERE yoneticiID = ?"
            cursor.execute(adm_pass_sorgu, (admin_id))
            hash_exists = cursor.fetchone()[0]
            if check_password_hash(hash_exists, admin_password):
                return redirect(url_for('auth.admin', adm_id =admin_id))
            else:
                return render_template("adminlogin.html", error="Yanlış şifre!")
        else:
            return render_template("adminlogin.html", error="Yanlış ID!")
    else:
        return render_template("adminlogin.html")

@auth.route('/doctorlogin', methods = ["POST", "GET"])
def doctor_login():
    if request.method == "POST":
        doctor_id = request.form['doctorid']
        dok_sorgu = "SELECT COUNT(1) FROM Doktorlar WHERE doktorID = ?"
        cursor.execute(dok_sorgu, (doctor_id,))
        dok_exists = cursor.fetchone()[0]
        if dok_exists:
            return redirect(url_for('auth.doctor', doc_id =doctor_id))
        else:
            return render_template("doctorlogin.html", error="Yanlış ID!")
    else:
        return render_template("doctorlogin.html")

@auth.route('/patientlogin', methods = ["POST", "GET"])
def patient_login():
    if request.method == "POST":
        patient_id = request.form['patientid']
        pat_sorgu = "SELECT COUNT(1) FROM Hastalar WHERE hastaID = ?"
        cursor.execute(pat_sorgu, (patient_id))
        pat_exists = cursor.fetchone()[0]
        if pat_exists:
            return redirect(url_for('auth.patient', pat_id = patient_id))
        else:
            return render_template("patientlogin.html", error="Yanlış ID!")
    else:
        return render_template("patientlogin.html")

@auth.route('/adminpage')
def admin_page():
    return render_template('adminpage.html')

@auth.route('/logout')
def logout():
    return render_template("homepage.html")

@auth.route('/sign-up', methods = ["POST", "GET"])
def sign_up():
    if request.method == "POST":
        new_patient_id = request.form['patientid']
        new_patient_name = request.form['patientname']
        new_patient_surname = request.form['patientsurname']
        new_patient_birthdate = request.form['patientbirthdate']
        new_patient_gender = request.form['gender']
        new_patient_number = request.form['patientnumber']
        new_patient_address = request.form['patientaddress']
        Hastalar.hasta_ekle(new_patient_id, new_patient_name, new_patient_surname, new_patient_birthdate, new_patient_gender, new_patient_number, new_patient_address)
        return render_template("patientlogin.html")
    else:
        return render_template("sign_up.html")

@auth.route('/admin/<int:adm_id>')
def admin(adm_id):
    doktor_listesi = Doktor_Bilgileri.doktor_goruntule()
    return render_template('adminpage.html', adm_id=adm_id, doktor_listesi=doktor_listesi)

@auth.route('/doctor/<int:doc_id>')
def doctor(doc_id):
    hasta_listesi = Hasta_Bilgileri.hasta_goruntule(doc_id)
    return render_template('doctorpage.html', doc_id=doc_id, hasta_listesi=hasta_listesi)

@auth.route('/patient/<int:pat_id>')
def patient(pat_id):
    randevu_listesi = Randevu_Bilgileri.randevu_goruntule(pat_id)
    return render_template('patientpage.html', pat_id=pat_id, randevu_listesi=randevu_listesi)

@auth.route('/appointment', methods=['GET', 'POST'])
def appointment():
    if request.method == 'POST':
        patient_id = request.form['patientid']
        pat_sorgu = "SELECT COUNT(1) FROM Hastalar WHERE hastaID = ?"
        cursor.execute(pat_sorgu, (patient_id))
        pat_exists = cursor.fetchone()[0]
        if pat_exists:
            return redirect(url_for('auth.appointmentpage', pat_id=patient_id))
        else:
            return render_template("appointment.html", error="Yanlış ID!")
    else:
        return render_template('appointment.html')

@auth.route('/appointmentpage/<int:pat_id>', methods=['GET', 'POST'])
def appointmentpage(pat_id):
    if request.method == 'POST':
        specialization = request.form['specialization']
        doctor_id = request.form['doctorid']
        appointment_date = request.form['appointmentdate']
        appointment_time = request.form['appointmenttime']
        randevu_id = fake.random_int(100,200)
        sql = "INSERT INTO Randevular (randevuID,hastaID, doktorID, randevu_tarihi, randevu_saati) VALUES (?, ?, ?, ?, ?)"
        cursor.execute(sql, (randevu_id, pat_id, doctor_id, appointment_date, appointment_time))
        connection.commit()
        return redirect(url_for('auth.success', specialization=specialization, doctor_id=doctor_id, appointment_date=appointment_date, appointment_time=appointment_time))
    else:
        specialization = request.args.get('specialization')
        doctors = get_doctors_by_specialization(specialization) if specialization else []
        specialization_list = get_specialization_list()
        return render_template('appointmentpage.html', pat_id=pat_id, doctors=doctors, specialization=specialization, specialization_list=specialization_list)

@auth.route('/success')
def success():
    specialization = request.args.get('specialization')
    doctor_id = request.args.get('doctor_id')
    appointment_date = request.args.get('appointment_date')
    appointment_time = request.args.get('appointment_time')
    doctor = get_doctor_by_id(doctor_id)
    return render_template('success.html', specialization=specialization, doctor=doctor, appointment_date=appointment_date, appointment_time=appointment_time)

@auth.route('/update_doctor/<int:doctor_id>', methods=['GET', 'POST'])
def update_doctor(doctor_id):
    if request.method == 'GET':
        doctor = get_doctor_by_id(doctor_id)
        uzmanlik_alanlari = get_specialization_list()
        return render_template('update_doctor.html', doctor=doctor, uzmanlik_alanlari=uzmanlik_alanlari, hastane_isimleri=hastane_isimleri)
    elif request.method == 'POST':
        new_docname = request.form['isim']
        new_docsurname = request.form['soy_isim']
        new_speciality = request.form['uzmanlik_alani']
        new_hospital = request.form['calistigi_hastane']
        sql = "UPDATE Doktorlar SET isim = ?, soy_isim = ?, uzmanlik_alani = ?, calistigi_hastane = ? WHERE doktorID = ?"
        cursor.execute(sql, (new_docname, new_docsurname, new_speciality, new_hospital, doctor_id))
        connection.commit()
        return redirect(url_for('auth.doctor', doc_id=doctor_id))

@auth.route('/update_patient/<int:pat_id>', methods=['GET', 'POST'])
def update_patient(pat_id):
    if request.method == 'POST':
        new_name = request.form['isim']
        new_surname = request.form['soy_isim']
        new_birthdate = request.form['dogum_tarihi']
        new_gender = request.form['cinsiyet']
        new_number = request.form['numara']
        new_address = request.form['adres']
        sql = "UPDATE Hastalar SET isim = ?, soy_isim = ?, dogum_tarihi = ?, cinsiyet = ?, numara = ?, adres = ? WHERE hastaID = ?"
        cursor.execute(sql, (new_name, new_surname, new_birthdate, new_gender, new_number, new_address, pat_id))
        connection.commit()
        return redirect(url_for('auth.patient', pat_id=pat_id))
    else:
        sql = "SELECT * FROM Hastalar WHERE hastaID = ?"
        cursor.execute(sql, (pat_id,))
        patient = cursor.fetchone()
        return render_template('update_patient.html', patient=patient)

@auth.route('/add-patient', methods=['GET', 'POST'])
def add_patient():
    if request.method == 'POST':
        hasta_id = request.form['hastaID']
        ad = request.form['isim']
        soyisim = request.form['soy_isim']
        dogum_tarihi = request.form['dogum_tarihi']
        cinsiyet = request.form['cinsiyet']
        numara = request.form['numara']
        adres = request.form['adres']
        Hastalar.hasta_ekle(hasta_id, ad, soyisim, dogum_tarihi, cinsiyet, numara, adres)
        return redirect(url_for('auth.admin_page'))
    else:
        return render_template('add_patient.html')

@auth.route('/delete-patient', methods=['GET', 'POST'])
def delete_patient():
    if request.method == 'POST':
        hasta_id = request.form['hastaID']
        cursor.execute("SELECT COUNT(1) FROM Randevular WHERE hastaID = ? AND randevu_tarihi >= CONVERT(date, GETDATE())", (hasta_id,))
        active_appointments_count = cursor.fetchone()[0]
        if active_appointments_count > 0:
            error = "Aktif randevusu bulunan bir hastayı silemezsiniz."
            return render_template('delete_patient.html', error=error)
        else:
            cursor.execute("SELECT COUNT(1) FROM Randevular WHERE hastaID = ? AND randevu_tarihi < CONVERT(date, GETDATE())", (hasta_id,))
            past_appointments_count = cursor.fetchone()[0]
            if past_appointments_count > 0:
                cursor.execute("DELETE FROM Randevular WHERE hastaID = ? AND randevu_tarihi < CONVERT(date, GETDATE())", (hasta_id,))
                connection.commit()
            Yonetici.hasta_cikar(hasta_id)
            success = "Hasta başarıyla silindi."
            return render_template('delete_patient.html', success=success)
    else:
        return render_template('delete_patient.html')

@auth.route('/add-doctor', methods=['GET', 'POST'])
def add_doctor():
    if request.method == 'POST':
        doktor_id = request.form['doktorID']
        isim = request.form['isim']
        soyisim = request.form['soy_isim']
        uzmanlik_alani = request.form['uzmanlik_alani']
        calistigi_hastane = request.form['calistigi_hastane']
        Yonetici.doktor_ekle(doktor_id, isim, soyisim, uzmanlik_alani, calistigi_hastane)
        return redirect(url_for('auth.admin_page'))
    else:
        uzmanlik_alanlari = get_specialization_list()
        return render_template('add_doctor.html', uzmanlik_alanlari=uzmanlik_alanlari, hastane_isimleri=hastane_isimleri)

@auth.route('/delete-doctor', methods=['GET', 'POST'])
def delete_doctor():
    if request.method == 'POST':
        doktor_id = request.form['doktorID']
        cursor.execute("SELECT COUNT(1) FROM Randevular WHERE doktorID = ? AND randevu_tarihi >= CONVERT(date, GETDATE())", (doktor_id))
        active_appointments_count = cursor.fetchone()[0]
        if active_appointments_count > 0:
            error = "Aktif randevusu bulunan bir doktoru silemezsiniz."
            return render_template('delete_doctor.html', error=error)
        else:
            cursor.execute("SELECT COUNT(1) FROM Randevular WHERE doktorID = ? AND randevu_tarihi < CONVERT(date, GETDATE())", (doktor_id))
            past_appointments_count = cursor.fetchone()[0]
            if past_appointments_count > 0:
                cursor.execute("DELETE FROM Randevular WHERE doktorID = ?", (doktor_id))
                cursor.execute("DELETE FROM Doktorlar WHERE doktorID = ?", (doktor_id))
                connection.commit()
            else:
                cursor.execute("DELETE FROM Doktorlar WHERE doktorID = ?", (doktor_id))
                connection.commit()
            success = "Doktor başarıyla silindi."
            return render_template('delete_doctor.html', success=success)
    else:
        return render_template('delete_doctor.html')

@auth.route('/doctor_pat/<int:doc_id>', methods=['GET'])
def doctor_pat(doc_id):
    sayfa = request.args.get('page', 1, type=int)
    sayfa_sinir = 20
    hasta_listesi = Hasta_Bilgileri.hasta_goruntule(doc_id)
    total = len(hasta_listesi)
    paginated_list = paging(hasta_listesi, sayfa, sayfa_sinir)
    return render_template('doctor_pat.html', doc_id=doc_id, hasta_listesi=paginated_list, page=sayfa, per_page=sayfa_sinir, total=total)

@auth.route('/pat_appointment/<int:pat_id>', methods=['GET'])
def pat_appointment(pat_id):
    sayfa = request.args.get('page', 1, type=int)
    sayfa_sinir = 25
    randevu_listesi = Randevu_Bilgileri.randevu_goruntule(pat_id)
    total = len(randevu_listesi)
    paginated_list = paging(randevu_listesi, sayfa, sayfa_sinir)
    return render_template('pat_appointment.html', pat_id=pat_id, randevu_listesi=paginated_list, page=sayfa, per_page=sayfa_sinir, total=total)