import numpy as np
from decimal import Decimal
from flask import jsonify
from Models.Model import Item, HasilAHP
from Controllers import db

class AHPController:
    def __init__(self):
        self.kriteria = ['ipk', 'nilai', 'kehadiran', 'prestasi', 'organisasi']
        self.skala_penilaian = {
            'ipk': {'min': 0.0, 'max': 4.0, 'pembagi': Decimal('4')},
            'nilai': {'min': 0, 'max': 100, 'pembagi': Decimal('100')},
            'kehadiran': {'min': 0, 'max': 100, 'pembagi': Decimal('100')},
            'prestasi': {'min': 0, 'max': 3, 'pembagi': Decimal('3')},
            'organisasi': {'min': 0, 'max': 3, 'pembagi': Decimal('3')}
        }
        
    def hitung_ahp(self):
        """
        Menghitung peringkat mahasiswa menggunakan metode AHP dan menyimpan hasil ke database
        """
        try:
            # Ambil data mahasiswa dari database
            data_mahasiswa = Item.query.all()
            
            if not data_mahasiswa:
                return {'status': 'error', 'message': 'Tidak ada data mahasiswa'}
            
            # 1. Membuat matriks perbandingan berpasangan
            matriks_perbandingan = self._buat_matriks_perbandingan()
            
            # 2. Normalisasi matriks perbandingan
            matriks_normalisasi = self._normalisasi_matriks(matriks_perbandingan)
            
            # 3. Hitung bobot kriteria
            bobot_kriteria = self._hitung_bobot_kriteria(matriks_normalisasi)
            
            # 4. Normalisasi data mahasiswa dan hitung skor
            hasil_akhir = self._proses_data_mahasiswa(data_mahasiswa, bobot_kriteria)
            
            return {
                'status': 'sukses',
                'bobot_kriteria': bobot_kriteria,
                'hasil_akhir': hasil_akhir
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def _buat_matriks_perbandingan(self):
        """
        Membuat matriks perbandingan berpasangan untuk kriteria
        """
        matriks = np.array([
            [1,    2,   3,   4,   5],   # IPK
            [0.5,  1,   2,   3,   4],   # Nilai
            [1/3, 0.5,  1,   2,   3],   # Kehadiran
            [0.25, 1/3, 0.5, 1,   2],   # Prestasi
            [0.2, 0.25, 1/3, 0.5, 1]    # Organisasi
        ], dtype=np.float64)
        return matriks
    
    def _normalisasi_matriks(self, matriks):
        """
        Normalisasi matriks perbandingan dengan membagi setiap kolom dengan total kolom
        """
        total_kolom = np.sum(matriks, axis=0)
        matriks_normalisasi = matriks / total_kolom
        return matriks_normalisasi
    
    def _hitung_bobot_kriteria(self, matriks_normalisasi):
        """
        Menghitung bobot kriteria dengan mengambil rata-rata setiap baris
        """
        bobot = np.mean(matriks_normalisasi, axis=1)
        
        # Konversi ke dictionary dengan nama kriteria
        bobot_kriteria = {}
        for i, kriteria in enumerate(self.kriteria):
            bobot_kriteria[kriteria] = float(bobot[i])
            
        return bobot_kriteria
    
    def _proses_data_mahasiswa(self, data_mahasiswa, bobot_kriteria):
        """
        Proses data mahasiswa: normalisasi, hitung skor, simpan ke database, dan kembalikan hasil
        """
        # Hapus hasil AHP sebelumnya
        HasilAHP.query.delete()
        db.session.commit()
        
        hasil = []
        
        for mhs in data_mahasiswa:
            # Pastikan nilai kehadiran tidak None
            kehadiran = mhs.kehadiran if mhs.kehadiran is not None else 0
            
            # Normalisasi data
            ipk_normal = float(mhs.ipk / self.skala_penilaian['ipk']['pembagi'])
            nilai_normal = float(mhs.nilai / self.skala_penilaian['nilai']['pembagi'])
            kehadiran_normal = float(kehadiran / self.skala_penilaian['kehadiran']['pembagi'])
            prestasi_normal = float(mhs.prestasi / self.skala_penilaian['prestasi']['pembagi'])
            organisasi_normal = float(mhs.organisasi / self.skala_penilaian['organisasi']['pembagi'])
            
            # Hitung skor akhir
            skor = (
                ipk_normal * float(bobot_kriteria['ipk']) +
                nilai_normal * float(bobot_kriteria['nilai']) +
                kehadiran_normal * float(bobot_kriteria['kehadiran']) +
                prestasi_normal * float(bobot_kriteria['prestasi']) +
                organisasi_normal * float(bobot_kriteria['organisasi'])
            )
            
            # Simpan ke database
            hasil_ahp = HasilAHP(
                npm=mhs.npm,
                ipk_normal=Decimal(str(ipk_normal)),
                nilai_normal=Decimal(str(nilai_normal)),
                kehadiran_normal=Decimal(str(kehadiran_normal)),
                prestasi_normal=Decimal(str(prestasi_normal)),
                organisasi_normal=Decimal(str(organisasi_normal)),
                skor_akhir=Decimal(str(skor))
            )
            
            db.session.add(hasil_ahp)
            hasil.append({
                'npm': mhs.npm,
                'nama': mhs.nama,
                'kehadiran': kehadiran,  # Simpan nilai asli kehadiran
                'skor': skor,
                'peringkat': 0
            })
        
        db.session.commit()
        
        # Urutkan berdasarkan skor tertinggi
        hasil.sort(key=lambda x: x['skor'], reverse=True)
        
        # Update peringkat di database
        for i, item in enumerate(hasil):
            item['peringkat'] = i + 1
            HasilAHP.query.filter_by(npm=item['npm']).update({'peringkat': i + 1})
        
        db.session.commit()
            
        return hasil
    
    def get_hasil_ahp(self):
        """
        Mengambil hasil perhitungan AHP dari database dengan join tabel mahasiswa
        """
        hasil = db.session.query(
            Item.npm,
            Item.nama,
            Item.ipk,
            Item.nilai,
            Item.kehadiran,  # Pastikan field kehadiran diambil
            HasilAHP.skor_akhir,
            HasilAHP.peringkat
        ).join(
            HasilAHP, Item.npm == HasilAHP.npm
        ).order_by(
            HasilAHP.peringkat
        ).all()
        
        # Konversi hasil query
        hasil_terkonversi = []
        for row in hasil:
            hasil_terkonversi.append({
                'npm': row.npm,
                'nama': row.nama,
                'ipk': float(row.ipk) if row.ipk is not None else 0.0,
                'nilai': float(row.nilai) if row.nilai is not None else 0.0,
                'kehadiran': float(row.kehadiran) if row.kehadiran is not None else 0.0,
                'skor_akhir': float(row.skor_akhir) if row.skor_akhir is not None else 0.0,
                'peringkat': row.peringkat if row.peringkat is not None else 0
            })
        
        return hasil_terkonversi
    
    def get_bobot_kriteria(self):
        """
        Mengambil bobot kriteria yang sudah dihitung
        """
        return {
            'ipk': 0.35,
            'nilai': 0.25,
            'kehadiran': 0.20,
            'prestasi': 0.12,
            'organisasi': 0.08
        }