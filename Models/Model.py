from flask_sqlalchemy import SQLAlchemy
from Controllers import db
  
class Item(db.Model):
    __tablename__ = 'mahasiswa'
    npm = db.Column(db.String(20), primary_key=True)
    nama = db.Column(db.String(100), nullable=False)
    semester = db.Column(db.Integer, nullable=False)
    angkatan = db.Column(db.Integer, nullable=False)
    ipk = db.Column(db.Numeric(4,2), nullable=False)
    nilai = db.Column(db.Integer, nullable=False)
    matkul = db.Column(db.String(100), nullable=False)
    kehadiran = db.Column(db.Integer, nullable=False)
    prestasi = db.Column(db.Integer, nullable=False)
    organisasi = db.Column(db.Integer, nullable=False)

class HasilAHP(db.Model):
    __tablename__ = 'hasil_ahp'
    id = db.Column(db.Integer, primary_key=True)
    npm = db.Column(db.String(20), db.ForeignKey('mahasiswa.npm'))
    
    # Field hasil perhitungan
    ipk_normal = db.Column(db.Float)
    nilai_normal = db.Column(db.Float)
    kehadiran_normal = db.Column(db.Float)
    prestasi_normal = db.Column(db.Float)
    organisasi_normal = db.Column(db.Float)
    skor_akhir = db.Column(db.Float)
    peringkat = db.Column(db.Integer)  
    mahasiswa = db.relationship('Item', backref='hasil_ahp')

@classmethod
def get_all(cls):
    return cls.query.all()   