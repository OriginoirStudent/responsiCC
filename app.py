from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import psycopg2  # Ganti import dari mysql.connector menjadi psycopg2

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Kelas model pengguna
class User(UserMixin):
    def __init__(self, user_id, username, password):
        self.id = user_id
        self.username = username
        self.password = password

# Daftar karyawan (simulasikan database)
users = [
    User(1, 'admin', 'password123'),
    # Tambahkan karyawan lain jika diperlukan
]

# Konfigurasi database
conn = psycopg2.connect(
    host="localhost",  # Ganti host, port, user, password, dan database sesuai dengan konfigurasi PostgreSQL Anda
    port="5432",
    user="your_postgresql_user",
    password="your_postgresql_password",
    database="cafe_menu"
)
cursor = conn.cursor()

# Tabel menu
cursor.execute("CREATE TABLE IF NOT EXISTS menu (id SERIAL PRIMARY KEY, nama VARCHAR(255), harga INT)")

# Tabel pesanan
cursor.execute("CREATE TABLE IF NOT EXISTS pesanan (id SERIAL PRIMARY KEY, nomor_meja INT, menu_id INT, FOREIGN KEY (menu_id) REFERENCES menu(id))")

@login_manager.user_loader
def load_user(user_id):
    return next((user for user in users if user.id == int(user_id)), None)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = next((user for user in users if user.username == username and user.password == password), None)
        if user:
            login_user(user)
            return redirect(url_for('karyawan_menu'))
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/karyawan/tambah_menu', methods=['POST'])
def tambah_menu():
    if request.method == 'POST':
        nama = request.form['nama']
        harga = request.form['harga']
        cursor.execute("INSERT INTO menu (nama, harga) VALUES (%s, %s)", (nama, harga))
        conn.commit()
    return redirect(url_for('karyawan_menu'))

@app.route('/pelanggan/<int:nomor_meja>')
def pelanggan(nomor_meja):
    cursor.execute("SELECT * FROM menu")
    menu = cursor.fetchall()
    return render_template('pelanggan.html', menu=menu, nomor_meja=nomor_meja)

@app.route('/pelanggan/pesan', methods=['POST'])
def pesan():
    if request.method == 'POST':
        nomor_meja = request.form['nomor_meja']
        menu_id = request.form['menu_id']
        cursor.execute("INSERT INTO pesanan (nomor_meja, menu_id) VALUES (%s, %s)", (nomor_meja, menu_id))
        conn.commit()
    return redirect(url_for('pelanggan', nomor_meja=nomor_meja))

@app.route('/karyawan/menu', methods=['GET', 'POST'])
@login_required
def karyawan_menu():
    if request.method == 'POST':
        nama = request.form['nama']
        harga = request.form['harga']
        cursor.execute("INSERT INTO menu (nama, harga) VALUES (%s, %s)", (nama, harga))
        conn.commit()
        flash('Menu berhasil ditambahkan.', 'success')
    cursor.execute("SELECT * FROM menu")
    menu = cursor.fetchall()
    return render_template('karyawan_menu.html', menu=menu)

@app.route('/karyawan/menu/edit/<int:menu_id>', methods=['GET', 'POST'])
@login_required
def edit_menu(menu_id):
    if request.method == 'POST':
        nama = request.form['nama']
        harga = request.form['harga']
        cursor.execute("UPDATE menu SET nama = %s, harga = %s WHERE id = %s", (nama, harga, menu_id))
        conn.commit()
        flash('Menu berhasil diubah.', 'success')
        return redirect(url_for('karyawan_menu'))
    cursor.execute("SELECT * FROM menu WHERE id = %s", (menu_id,))
    menu = cursor.fetchone()
    if menu is None:
        flash('Menu tidak ditemukan.', 'danger')
        return redirect(url_for('karyawan_menu'))
    return render_template('edit_menu.html', menu=menu)

@app.route('/karyawan/menu/delete/<int:menu_id>', methods=['POST'])
@login_required
def delete_menu(menu_id):
    cursor.execute("DELETE FROM menu WHERE id = %s", (menu_id,))
    conn.commit()
    flash('Menu berhasil dihapus.', 'success')
    return redirect(url_for('karyawan_menu'))

if __name__ == '__main__':
    app.run(debug=False)
