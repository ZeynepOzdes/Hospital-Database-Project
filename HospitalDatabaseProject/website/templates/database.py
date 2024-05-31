from faker import Faker
import pyodbc
import random
from werkzeug.security import generate_password_hash

fake = Faker("tr_TR")

connection = pyodbc.connect(
    "Driver={SQL Server};"
    "Server=YOURDATABASE\\SQLEXPRESS;"
    "Database=hastane;"
    "Trusted_Connection=yes;"
)
cursor = connection.cursor()

uzmanlik_alanlari = [
        "Dahiliye", 
        "Cerrahi", 
        "Nöroloji", 
        "Kardiyoloji", 
        "Ortopedi", 
        "Psikiyatri", 
        "Pediatri", 
        "Göz Hastalıkları", 
        "Üroloji", 
        "Radyoloji",
        "Göğüs Hastalıkları",
        "Dermatoloji",
        "Genel Cerrahi",
        "KBB"
    ]
        
hastane_isimleri = [
        "Arnavutköy Devlet Hastanesi",
        "Avcılar Murat Kölük Devlet Hastanesi",
        "Başakşehir Devlet Hastanesi",
        "Bahçelievler Devlet Hastanesi",
        "Bayrampaşa Devlet Hastanesi",
        "Beşiktaş Sait Çiftçi Devlet Hastanesi",
        "Beykoz Devlet Hastanesi",
        "Büyükçekmece Mimar Sinan Devlet Hastanesi",
        "Çatalca İlyas Çokay Devlet Hastanesi",
        "Esenyurt Necmi Kadıoğlu Devlet Hastanesi",
        "Eyüpsultan Devlet Hastanesi",
        "İstinye Devlet Hastanesi",
        "Kağıthane Devlet Hastanesi",
        "Küçükçekmece Kanuni Sultan Süleyman Hastanesi",
        "Maltepe Devlet Hastanesi",
        "Pendik Devlet Hastanesi",
        "Tuzla Devlet Hastanesi",
        "Silivri Devlet Hastanesi",
        "Sultanbeyli Devlet Hastanesi",
        "Şile Devlet Hastanesi",
        "Üsküdar Devlet Hastanesi",
        "Başakşehir Çam ve Sakura Şehir Hastanesi",
        "Kartal Dr. Lütfi Kırdar Şehir Hastanesi",
        "Prof. Dr. Cemil Taşcıoğlu Şehir Hastanesi",
        "Dr. Süleyman Yalçın Şehir Hastanesi",
        "Hospitalist Hastanesi",
        "Haznedar Hastanesi, Bahçelievler",
        "Haznedar Ömür Hastanesi",
        "Hisar Intercontinental Hospital",
        "Hisar Hospital",
        "Hizmet Hastanesi",
        "Huzur Hastanesi",
        "İncirli Hastanesi",
        "İstanbul Diş Hastanesi",
        "Özel İstanbul Hospital",
        "İtalyan Hastanesi",
        "Ota-Jinemed Hospital",
        "John F. Kennedy Hospital",
        "Kadıköy Şifa Hastanesi",
    ]

class Doktorlar:

    def __init__(self, isim, soyisim, uzmanlik_alani, calistigi_hastane):
        self.isim = isim
        self.soyisim = soyisim
        self.uzmanlik_alani = uzmanlik_alani
        self.calistigi_hastane = calistigi_hastane

    @staticmethod
    def fake_doktor():
        existing_ids_doc = set()  

        for _ in range(200):  
            doktor_id = fake.random_int(1000, 9999)

            while doktor_id in existing_ids_doc:
                doktor_id = fake.random_int(1000, 9999)

            existing_ids_doc.add(doktor_id)
            doktor_isim = fake.first_name()
            doktor_soyisim =fake.last_name()
            uzmanlik_a = fake.random_element(uzmanlik_alanlari) 
            hastane_isim = fake.random_element(hastane_isimleri) 
            sql = "INSERT INTO Doktorlar (doktorID, isim, soy_isim, uzmanlik_alani, calistigi_hastane) VALUES (?, ?, ?, ?, ?)"
            cursor.execute(sql, (doktor_id, doktor_isim, doktor_soyisim, uzmanlik_a, hastane_isim))
            connection.commit()

class Hastalar:

    def __init__(self, hid, ad, soyisim, dogum_tarihi, cinsiyet, numara, adres):
        self.hid = hid
        self.ad = ad
        self.soyisim = soyisim
        self.dogum_tarihi = dogum_tarihi
        self.cinsiyet = cinsiyet
        self.numara = numara
        self.adres = adres
        sql = "INSERT INTO Hastalar (hastaID, isim, soy_isim, dogum_tarihi, cinsiyet, numara, adres) VALUES (?, ?, ?, ?, ?, ?, ?)"
        cursor.execute(sql, (hid, ad, soyisim, dogum_tarihi, cinsiyet, numara, adres))
        connection.commit()

    @staticmethod
    def fake_hasta():
        existing_ids_h = set()  

        for _ in range(1000):  
            hasta_id = fake.random_int(1000, 9999)

            while hasta_id in existing_ids_h:
                hasta_id = fake.random_int(1000, 9999)

            existing_ids_h.add(hasta_id)
            hasta_isim = fake.first_name()
            hasta_soyisim = fake.last_name()
            hasta_numara = fake.phone_number() 
            hasta_adres = fake.address()
            hasta_cinsiyet = random.choice(['Kadın', 'Erkek'])
            dogum_tarihi = fake.date_of_birth(minimum_age=15, maximum_age=65)
            dogum_tarihi_sql = dogum_tarihi.strftime('%Y-%m-%d')
            sql = "INSERT INTO Hastalar (hastaID, isim, soy_isim, dogum_tarihi, cinsiyet, numara, adres) VALUES (?, ?, ?, ?, ?, ?, ?)"
            cursor.execute(sql, (hasta_id, hasta_isim, hasta_soyisim, dogum_tarihi_sql, hasta_cinsiyet, hasta_numara, hasta_adres))
            connection.commit()
    
    @staticmethod
    def hasta_ekle(hasta_id, ad, soyisim, dogum_tarihi, cinsiyet, numara, adres):
        sql =  "INSERT INTO Hastalar (hastaID, isim, soy_isim, dogum_tarihi, cinsiyet, numara, adres) VALUES (?, ?, ?, ?, ?, ?, ?)"
        cursor.execute(sql,(hasta_id, ad, soyisim, dogum_tarihi, cinsiyet, numara, adres))
        connection.commit()

class Randevular:

    def __init__(self, randevu_id, hasta_id, doktor_id, randevu_tarihi, randevu_saati):
        self.randevu_id = randevu_id
        self.hasta_id = hasta_id
        self.doktor_id = doktor_id
        self.randevu_tarihi = randevu_tarihi
        self.randevu_saati = randevu_saati

    @staticmethod
    def fake_randevu():

        def hastaid_sec(tablo):
            cursor.execute(f"SELECT hastaID FROM {tablo}")
            idler = cursor.fetchall()
            return random.choice(idler)[0]

        @staticmethod
        def doktorid_sec(tablo):
            cursor.execute(f"SELECT doktorID FROM {tablo}")
            idler = cursor.fetchall()
            return random.choice(idler)[0]  
        existing_ids_r = set()

        for _ in range(1000):  
            hasta_id = hastaid_sec("Hastalar")

            #Geçmiş
            for _ in range(70):
                randevu_id = fake.random_int(1000,199999)

                while randevu_id in existing_ids_r:
                    randevu_id = fake.random_int(1000, 199999)
            
                existing_ids_r.add(randevu_id)
                doktor_id = doktorid_sec("Doktorlar")

                randevu_tarihi = fake.date_this_year()
                randevu_tarihi_sql = randevu_tarihi.strftime('%Y-%m-%d')
                randevu_saati = fake.time()  
                sql = "INSERT INTO Randevular (randevuID, hastaID, doktorID, randevu_tarihi, randevu_saati) VALUES (?, ?, ?, ?, ?)"
                cursor.execute(sql, (randevu_id, hasta_id, doktor_id, randevu_tarihi_sql, randevu_saati))
            
            # Gelecek 
            for _ in range(10):  
                randevu_id = fake.random_int(1000,199999)

                while randevu_id in existing_ids_r:
                    randevu_id = fake.random_int(1000, 199999)
                
                existing_ids_r.add(randevu_id)
                doktor_id = doktorid_sec("Doktorlar")

                randevu_tarihi = fake.date_between(start_date='today', end_date='+40d')  
                randevu_tarihi_sql = randevu_tarihi.strftime('%Y-%m-%d')
                randevu_saati = fake.time()
                sql = "INSERT INTO Randevular (randevuID, hastaID, doktorID, randevu_tarihi, randevu_saati) VALUES (?, ?, ?, ?, ?)"
                cursor.execute(sql, (randevu_id, hasta_id, doktor_id, randevu_tarihi_sql, randevu_saati))
            connection.commit()

class Yonetici:

    def __init__(self,yonetici_id, kullanici_adi, sifre):
        self.yonetici_id = yonetici_id
        self.kullanici_adi = kullanici_adi
        self.sifre_hash = generate_password_hash(sifre, method='pbkdf2:sha256', salt_length=16)

    def yonetici_ekle(self):
        cursor.execute("INSERT INTO Yoneticiler (yoneticiID, kullanici_adi, sifre) VALUES (?, ?, ?)",(self.yonetici_id, self.kullanici_adi, self.sifre_hash))
        connection.commit()

    def hasta_cikar(hasta_id):
        sql = "DELETE FROM Hastalar WHERE hastaID = ?"
        cursor.execute(sql, (hasta_id))
        connection.commit()

    def doktor_ekle(doktor_id, isim, soyisim, uzmanlik_alani, calistigi_hastane):
        sql =  "INSERT INTO Doktorlar (doktorID, isim, soy_isim, uzmanlik_alani, calistigi_hastane) VALUES (?, ?, ?, ?, ?)"
        cursor.execute(sql,(doktor_id, isim, soyisim, uzmanlik_alani, calistigi_hastane))
        connection.commit()

    def doktor_cikar(doktor_id):
        sql =  "DELETE FROM Doktorlar WHERE doktorID = ?"
        cursor.execute(sql, (doktor_id))
        connection.commit()

class Hasta_Bilgileri:

    def __init__(self, hid, ad, soyisim, dogum_tarihi, cinsiyet, numara, adres):
        self.hid = hid
        self.ad = ad
        self.soyisim = soyisim
        self.dogum_tarihi = dogum_tarihi
        self.cinsiyet = cinsiyet
        self.numara = numara
        self.adres = adres

    @staticmethod
    def hasta_goruntule(doktor_id):
        sorgu_hastalar = "SELECT * FROM Hastalar WHERE hastaID IN (SELECT hastaID FROM Randevular WHERE Randevular.doktorID = ?)"
        cursor.execute(sorgu_hastalar, (doktor_id))
        sonuc = cursor.fetchall()
        hasta_listesi = []

        for satir in sonuc:
            hasta_bilgileri = Hasta_Bilgileri(satir[0], satir[1], satir[2], satir[3], satir[4], satir[5], satir[6])
            hasta_listesi.append(hasta_bilgileri)
        return hasta_listesi

class Randevu_Bilgileri:

    def __init__(self, randevu_id, hasta_id, doktor_id, dok_ad, dok_soyad, randevu_tarihi, randevu_saati):
        self.randevu_id = randevu_id
        self.hasta_id = hasta_id
        self.doktor_id = doktor_id
        self.dok_ad = dok_ad
        self.dok_soyad = dok_soyad
        self.randevu_tarihi = randevu_tarihi
        self.randevu_saati = randevu_saati
    
    @staticmethod
    def randevu_goruntule(hasta_id):
        sorgu_randevular = "SELECT Randevular.randevuID, Randevular.hastaID, Randevular.doktorID, Doktorlar.isim, Doktorlar.soy_isim, Randevular.randevu_tarihi, Randevular.randevu_saati FROM Randevular INNER JOIN Doktorlar ON Randevular.doktorID = Doktorlar.doktorID WHERE Randevular.hastaID = ?"
        cursor.execute(sorgu_randevular, hasta_id)
        sonuc = cursor.fetchall()
        randevu_listesi = []

        for satir in sonuc:
            randevu_bilgileri = Randevu_Bilgileri(satir[0], satir[1], satir[2], satir[3], satir[4], satir[5], satir[6])
            randevu_listesi.append(randevu_bilgileri)
        return randevu_listesi

class Doktor_Bilgileri:

    def __init__(self, isim, soyisim, uzmanlik_alani, calistigi_hastane):
        self.isim = isim
        self.soyisim = soyisim
        self.uzmanlik_alani = uzmanlik_alani
        self.calistigi_hastane = calistigi_hastane
    
    @staticmethod
    def doktor_goruntule():
        sorgu_doktorlar = "SELECT Doktorlar.doktorID, Doktorlar.isim, Doktorlar.soy_isim, Doktorlar.uzmanlik_alani , Doktorlar.calistigi_hastane FROM Doktorlar"
        cursor.execute(sorgu_doktorlar)
        sonuc = cursor.fetchall()
        doktor_listesi = []

        for satir in sonuc:
            doktor_bilgileri = Doktor_Bilgileri(satir[0], satir[1], satir[2], satir[3])
            doktor_listesi.append(doktor_bilgileri)
        return doktor_listesi

def get_specialization_list():
    return uzmanlik_alanlari 

def get_doctor_by_id(doctor_id):
    sql = "SELECT isim, soy_isim FROM Doktorlar WHERE doktorID = ?"
    cursor.execute(sql, (doctor_id,))
    doctor_data = cursor.fetchone()

    if doctor_data:
        doctor = {
            'isim': doctor_data[0],
            'soy_isim': doctor_data[1]
        }
        return doctor
    else:
        return None


#yonetici1 = Yonetici(1,"admin", "sifre")
#yonetici2 = Yonetici(2,"admin2","sifre")
#yonetici1.yonetici_ekle()
#yonetici2.yonetici_ekle()
#Doktorlar.fake_doktor()
#Hastalar.fake_hasta()
#Randevular.fake_randevu()