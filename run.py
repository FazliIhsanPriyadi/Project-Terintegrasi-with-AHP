from flask import Flask, render_template, request, redirect, url_for, flash
from Controllers.mahasiswa import db, get_mahasiswa, add_mahasiswa, delete_mahasiswa, edit_mahasiswa
from Controllers.ahp import AHPController
from Controllers.AdminController import signup_post, login_post, logout as logout_user_action, User 
from flask_login import LoginManager, login_user,login_required,logout_user,current_user
from Models.Model import Item, HasilAHP
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

NAV_LINKS = [
    {"name": "Home", "endpoint": "home", "icon": "fa-home"},
    {"name": "Mahasiswa", "endpoint": "mahasiswa", "icon": "fa-users"},
    {"name": "Tambah Mahasiswa", "endpoint": "tambah_mahasiswa", "icon": "fa-user-plus"},
    {"name": "Hasil AHP", "endpoint": "lihat_hasil_ahp", "icon": "fa-calculator"},
    {"name": "Logout", "endpoint": "logout_user", "icon": "fa-sign-out-alt"}
]

# Inisialisasi LoginManager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Redirect ke halaman login jika belum login

# Fungsi untuk memuat pengguna berdasarkan ID (user_loader)
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.context_processor
def inject_nav_links():
    return {"nav_links": NAV_LINKS}

# Inisialisasi controller
ahp_controller = AHPController()

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/mahasiswa', methods=['GET'])
def mahasiswa():
    mahasiswa = get_mahasiswa()
    return render_template('mahasiswa.html', mahasiswa=mahasiswa)

@app.route('/mahasiswa/tambah', methods=['GET', 'POST'])
def tambah_mahasiswa():
    if request.method == 'POST':
        add_mahasiswa()
        return redirect(url_for('mahasiswa'))
    return render_template('tambahmahasiswa.html')

@app.route('/mahasiswa/hapus/<string:npm>')
def hapus_mahasiswa(npm):
    delete_mahasiswa(npm)
    return redirect(url_for('mahasiswa'))

@app.route('/mahasiswa/edit/<string:npm>', methods=['GET', 'POST'])
def ubah_mahasiswa(npm):
    if request.method == 'POST':
        edit_mahasiswa(npm)
        return redirect(url_for('mahasiswa'))
    
    mahasiswa_data = Item.query.get(npm)
    if not mahasiswa_data:
        flash("Mahasiswa tidak ditemukan!", "error")
        return redirect(url_for('mahasiswa'))
    
    return render_template('editmahasiswa.html', mahasiswa=mahasiswa_data)

@app.route('/hitung-ahp')
def hitung_ahp():
    hasil = ahp_controller.hitung_ahp()
    
    if hasil['status'] == 'error':
        flash('Gagal menghitung AHP: ' + hasil['message'], 'error')
    else:
        flash('Perhitungan AHP berhasil dilakukan', 'success')
    
    return redirect(url_for('lihat_hasil_ahp'))

@app.route('/hasil-ahp')
def lihat_hasil_ahp():
    # Ambil hasil AHP dari database
    mahasiswa_terurut = ahp_controller.get_hasil_ahp()
    
    # Dapatkan bobot kriteria
    bobot_kriteria = ahp_controller.get_bobot_kriteria()
    
    return render_template(
        'hasil_ahp.html',
        mahasiswa=mahasiswa_terurut,
        bobot_kriteria=bobot_kriteria
    )

# Rute untuk halaman login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        return login_post()  # Memanggil fungsi controller untuk login
    return render_template('Login.html')  # Pastikan Anda memiliki template Login.html

# Rute untuk halaman signup
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        return signup_post()  # Memanggil fungsi controller untuk signup
    return render_template('Signup.html')  # Pastikan Anda memiliki template Signup.html

# Rute untuk logout
@app.route('/logout')
def logout_user():
    return logout_user_action()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)