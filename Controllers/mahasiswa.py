from Models.Model import Item
from flask import request, redirect, url_for, flash
from Controllers import db

def get_mahasiswa():
    mahasiswa = Item.query.all()  
    return mahasiswa  

def add_mahasiswa():
    if request.method == 'POST':
        npm = request.form.get('npm')
        nama = request.form.get('nama')
        semester = request.form.get('semester')
        angkatan = request.form.get('angkatan')
        ipk = request.form.get('ipk')
        nilai = request.form.get('nilai')
        matkul = request.form.get('matkul')
        kehadiran = request.form.get('kehadiran')
        prestasi = request.form.get('prestasi')
        organisasi = request.form.get('organisasi')

        if not nama or not npm:
            flash("Nama dan NPM harus diisi!", "error")
            return redirect(url_for('tambah_mahasiswa'))

        new_mahasiswa = Item(
            npm=npm,
            nama=nama,
            semester=semester,
            angkatan=angkatan,
            ipk=ipk,
            nilai=nilai,
            matkul=matkul,
            kehadiran=kehadiran,
            prestasi=prestasi,
            organisasi=organisasi
        )
        db.session.add(new_mahasiswa)
        db.session.commit()
        flash("Mahasiswa berhasil ditambahkan!", "success")
        return redirect(url_for('mahasiswa'))

def delete_mahasiswa(npm):
    mahasiswa = Item.query.get(npm)
    if not mahasiswa:
        flash("Mahasiswa tidak ditemukan!", "error")
        return redirect(url_for('mahasiswa'))

    db.session.delete(mahasiswa)
    db.session.commit()
    flash("Mahasiswa berhasil dihapus!", "success")
    return redirect(url_for('mahasiswa'))

def edit_mahasiswa(npm):
    mahasiswa = Item.query.get(npm)
    if request.method == 'POST':
        if mahasiswa:
            mahasiswa.npm = request.form.get('npm')
            mahasiswa.nama = request.form.get('nama')
            mahasiswa.semester = request.form.get('semester')
            mahasiswa.angkatan = request.form.get('angkatan')
            mahasiswa.ipk = request.form.get('ipk')
            mahasiswa.nilai = request.form.get('nilai')
            mahasiswa.matkul = request.form.get('matkul')
            mahasiswa.kehadiran = request.form.get('kehadiran')
            mahasiswa.prestasi = request.form.get('prestasi')
            mahasiswa.organisasi = request.form.get('organisasi')
            
            db.session.commit()
            flash("Mahasiswa berhasil diperbarui!", "success")
            return redirect(url_for('mahasiswa'))
        else:
            flash("Mahasiswa tidak ditemukan!", "danger")
            return redirect(url_for('mahasiswa'))        
    return mahasiswa