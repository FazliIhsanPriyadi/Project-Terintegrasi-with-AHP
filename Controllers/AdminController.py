from werkzeug.security import generate_password_hash, check_password_hash
from flask import request, redirect, url_for, flash
from Models.AdminModel import User
from Controllers import db
from flask_login import login_user, logout_user

# Fungsi untuk menangani proses signup
def signup_post():
    if request.method == 'POST':
        username = request.form.get('username').strip()  # Hapus spasi di awal/akhir input
        password = request.form.get('password').strip()

        # Cek jika username sudah ada
        user = User.query.filter_by(username=username).first()
        if user:
            flash("Username sudah terdaftar, silakan coba dengan username lain!", "error")
            return redirect(url_for('signup'))

        # Membuat pengguna baru dan mengenkripsi password
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, password=hashed_password)

        # Menyimpan data pengguna baru ke database
        db.session.add(new_user)
        db.session.commit()

        print(f"User berhasil didaftarkan: {username}")
        print(f"Password (hash): {hashed_password}")

        flash("Pendaftaran berhasil! Silakan login.", "success")
        return redirect(url_for('login'))

# Fungsi untuk menangani proses login
def login_post():
    if request.method == 'POST':
        username = request.form.get('username').strip()
        password = request.form.get('password').strip()

        print(f"Username input: {username}")
        print(f"Password input: {password}")

        # Mencari pengguna berdasarkan username
        user = User.query.filter_by(username=username).first()

        if user is None:
            flash("Username tidak ditemukan.", "error")
            print("User tidak ditemukan!")
            return redirect(url_for('login'))

        print(f"User ditemukan: {user.username}")
        print(f"Password hash dari database: {user.password}")

        # Verifikasi password
        password_check = check_password_hash(user.password, password)
        print(f"Hasil check_password_hash: {password_check}")

        if password_check:
            login_user(user)
            flash("Login berhasil!", "success")
            print("Login sukses!")
            return redirect(url_for('home'))
        else:
            flash("Password salah. Silakan coba lagi.", "error")
            print("Password salah!")
            return redirect(url_for('login'))

# Fungsi logout
def logout():
    logout_user()
    flash("Anda berhasil logout.", "info")
    print("User logout berhasil")
    return redirect(url_for('login'))
