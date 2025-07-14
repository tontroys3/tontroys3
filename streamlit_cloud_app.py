import streamlit as st
import sqlite3
import pandas as pd
import os
from datetime import datetime
import hashlib
import uuid

# Set page config
st.set_page_config(
    page_title="StreamFlow - Live Streaming Platform",
    page_icon="🎥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Database setup for cloud deployment
def init_database():
    """Initialize SQLite database with required tables"""
    # Use in-memory database for cloud deployment
    if 'db_connection' not in st.session_state:
        try:
            st.session_state.db_connection = sqlite3.connect(':memory:', check_same_thread=False)
        except Exception as e:
            st.error(f"Database connection error: {e}")
            return None
    
    conn = st.session_state.db_connection
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            avatar_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create videos table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS videos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            filename TEXT NOT NULL,
            original_name TEXT NOT NULL,
            file_path TEXT NOT NULL,
            thumbnail_path TEXT,
            duration INTEGER,
            file_size INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Create streams table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS streams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            platform TEXT NOT NULL,
            stream_key TEXT NOT NULL,
            video_id INTEGER,
            status TEXT DEFAULT 'pending',
            scheduled_time TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (video_id) REFERENCES videos (id)
        )
    ''')
    
    conn.commit()
    return conn

# Initialize database
if init_database() is None:
    st.error("Failed to initialize database")
    st.stop()

# Authentication functions
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, hash_password):
    return hash_password == hashlib.sha256(password.encode()).hexdigest()

def create_user(username, email, password):
    conn = st.session_state.db_connection
    cursor = conn.cursor()
    password_hash = hash_password(password)
    
    try:
        cursor.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
            (username, email, password_hash)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False

def authenticate_user(username, password):
    conn = st.session_state.db_connection
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT id, username, email, password_hash FROM users WHERE username = ?",
        (username,)
    )
    user = cursor.fetchone()
    
    if user and verify_password(password, user[3]):
        return {'id': user[0], 'username': user[1], 'email': user[2]}
    return None

# Session management
def init_session():
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'page' not in st.session_state:
        st.session_state.page = 'login'

# Login page
def login_page():
    st.title("🎥 StreamFlow - Live Streaming Platform")
    st.markdown("### Welcome to StreamFlow")
    st.info("Demo platform untuk live streaming ke berbagai platform seperti YouTube, Facebook, Twitch, dan lainnya.")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("#### Login ke akun Anda")
        
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Masukkan username")
            password = st.text_input("Password", type="password", placeholder="Masukkan password")
            login_button = st.form_submit_button("Login", use_container_width=True)
            
            if login_button:
                if username and password:
                    user = authenticate_user(username, password)
                    if user:
                        st.session_state.user = user
                        st.session_state.page = 'dashboard'
                        st.rerun()
                    else:
                        st.error("Username atau password salah")
                else:
                    st.error("Silakan masukkan username dan password")
        
        st.markdown("---")
        st.markdown("#### Belum punya akun?")
        if st.button("Daftar Sekarang", use_container_width=True):
            st.session_state.page = 'register'
            st.rerun()

# Registration page
def register_page():
    st.title("🎥 StreamFlow - Daftar Akun")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("#### Buat akun baru")
        
        with st.form("register_form"):
            username = st.text_input("Username", placeholder="Pilih username unik")
            email = st.text_input("Email", placeholder="alamat@email.com")
            password = st.text_input("Password", type="password", placeholder="Minimal 8 karakter")
            confirm_password = st.text_input("Konfirmasi Password", type="password", placeholder="Ulangi password")
            register_button = st.form_submit_button("Daftar", use_container_width=True)
            
            if register_button:
                if username and email and password and confirm_password:
                    if password == confirm_password:
                        if len(password) >= 8:
                            if create_user(username, email, password):
                                st.success("Akun berhasil dibuat! Silakan login.")
                                st.session_state.page = 'login'
                                st.rerun()
                            else:
                                st.error("Username atau email sudah digunakan")
                        else:
                            st.error("Password minimal 8 karakter")
                    else:
                        st.error("Konfirmasi password tidak cocok")
                else:
                    st.error("Silakan isi semua field")
        
        st.markdown("---")
        if st.button("Kembali ke Login", use_container_width=True):
            st.session_state.page = 'login'
            st.rerun()

# Dashboard
def dashboard_page():
    st.title(f"🎥 StreamFlow Dashboard")
    st.markdown(f"### Selamat datang, {st.session_state.user['username']}!")
    
    # Sidebar
    with st.sidebar:
        st.markdown(f"#### Halo, {st.session_state.user['username']}!")
        st.markdown("---")
        
        if st.button("🏠 Dashboard", use_container_width=True):
            st.session_state.page = 'dashboard'
            st.rerun()
        
        if st.button("🎬 Galeri Video", use_container_width=True):
            st.session_state.page = 'gallery'
            st.rerun()
        
        if st.button("📺 Live Streaming", use_container_width=True):
            st.session_state.page = 'streams'
            st.rerun()
        
        if st.button("⚙️ Pengaturan", use_container_width=True):
            st.session_state.page = 'settings'
            st.rerun()
        
        st.markdown("---")
        if st.button("🚪 Keluar", use_container_width=True):
            st.session_state.user = None
            st.session_state.page = 'login'
            st.rerun()
    
    # Main content
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Video", get_user_video_count(), help="Jumlah video yang telah diupload")
    
    with col2:
        st.metric("Stream Aktif", get_user_stream_count(), help="Jumlah stream yang sedang berjalan")
    
    with col3:
        st.metric("Total Stream", get_user_total_streams(), help="Total stream yang pernah dibuat")
    
    st.markdown("---")
    
    # Quick actions
    st.subheader("🚀 Aksi Cepat")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📤 Upload Video", use_container_width=True):
            st.session_state.page = 'gallery'
            st.rerun()
    
    with col2:
        if st.button("🎥 Buat Stream", use_container_width=True):
            st.session_state.page = 'streams'
            st.rerun()
    
    with col3:
        if st.button("📊 Lihat Statistik", use_container_width=True):
            st.info("Fitur statistik akan segera hadir!")
    
    st.markdown("---")
    
    # Recent activity
    st.subheader("📋 Aktivitas Terbaru")
    recent_streams = get_recent_streams()
    if recent_streams:
        df = pd.DataFrame(recent_streams, columns=['Judul', 'Platform', 'Status', 'Dibuat'])
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Belum ada aktivitas terbaru")

# Video Gallery
def gallery_page():
    st.title("🎬 Galeri Video")
    
    # Upload video
    st.subheader("📤 Upload Video Baru")
    uploaded_file = st.file_uploader("Pilih file video", type=['mp4', 'mov', 'avi', 'mkv'])
    
    if uploaded_file is not None:
        st.success(f"Video '{uploaded_file.name}' siap diupload!")
        st.warning("⚠️ Catatan: Pada versi demo ini, file tidak benar-benar tersimpan di server.")
        
        # Simulate saving to database
        if st.button("Simpan Video", use_container_width=True):
            save_video_to_db(uploaded_file.name, f"uploads/{uploaded_file.name}")
            st.success("Video berhasil disimpan ke database!")
            st.rerun()
    
    st.markdown("---")
    
    # Display videos
    st.subheader("📚 Video Anda")
    videos = get_user_videos()
    
    if videos:
        for video in videos:
            with st.expander(f"🎥 {video[2]}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Nama File:** {video[1]}")
                    st.write(f"**Ukuran:** {video[5] if video[5] else 'Unknown'} bytes")
                
                with col2:
                    st.write(f"**Upload:** {video[6]}")
                    if st.button(f"Hapus", key=f"delete_{video[0]}"):
                        delete_video(video[0])
                        st.rerun()
    else:
        st.info("Belum ada video yang diupload")

# Live Streams
def streams_page():
    st.title("📺 Live Streaming")
    
    # Create new stream
    st.subheader("🎥 Buat Stream Baru")
    
    with st.form("stream_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            title = st.text_input("Judul Stream", placeholder="Masukkan judul menarik")
            platform = st.selectbox("Platform", ["YouTube", "Facebook", "Twitch", "TikTok", "Instagram", "Custom RTMP"])
        
        with col2:
            stream_key = st.text_input("Stream Key", type="password", placeholder="Masukkan RTMP stream key")
            video_id = st.selectbox("Pilih Video", get_video_options())
        
        scheduled_time = st.datetime_input("Jadwal Stream (Opsional)", value=None)
        
        submit_button = st.form_submit_button("🚀 Buat Stream", use_container_width=True)
        
        if submit_button:
            if title and platform and stream_key:
                create_stream(title, platform, stream_key, video_id, scheduled_time)
                st.success("Stream berhasil dibuat!")
                st.rerun()
            else:
                st.error("Silakan isi semua field yang diperlukan")
    
    st.markdown("---")
    
    # Info box
    st.info("""
    **💡 Cara Mendapatkan Stream Key:**
    
    - **YouTube:** YouTube Studio → Go Live → Stream Key
    - **Facebook:** Facebook Live → Use Stream Key → Copy Key
    - **Twitch:** Creator Dashboard → Settings → Stream Key
    - **TikTok:** TikTok Live Studio → Get Stream Key
    """)
    
    st.markdown("---")
    
    # Display streams
    st.subheader("📋 Stream Anda")
    streams = get_user_streams()
    
    if streams:
        for stream in streams:
            with st.expander(f"📺 {stream[2]} - {stream[3]} ({stream[5]})"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Judul:** {stream[2]}")
                    st.write(f"**Platform:** {stream[3]}")
                    st.write(f"**Status:** {stream[5]}")
                
                with col2:
                    if stream[6]:  # scheduled_time
                        st.write(f"**Jadwal:** {stream[6]}")
                    st.write(f"**Dibuat:** {stream[7]}")
                
                # Action buttons
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button(f"▶️ Mulai", key=f"start_{stream[0]}"):
                        update_stream_status(stream[0], 'active')
                        st.success("Stream dimulai!")
                        st.rerun()
                
                with col2:
                    if st.button(f"⏹️ Berhenti", key=f"stop_{stream[0]}"):
                        update_stream_status(stream[0], 'stopped')
                        st.success("Stream dihentikan!")
                        st.rerun()
                
                with col3:
                    if st.button(f"🗑️ Hapus", key=f"delete_stream_{stream[0]}"):
                        delete_stream(stream[0])
                        st.success("Stream dihapus!")
                        st.rerun()
    else:
        st.info("Belum ada stream yang dibuat")

# Settings
def settings_page():
    st.title("⚙️ Pengaturan")
    
    user = st.session_state.user
    
    st.subheader("👤 Informasi Akun")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.text_input("Username", value=user['username'], disabled=True)
        st.text_input("Email", value=user['email'], disabled=True)
    
    with col2:
        st.info("Untuk mengubah username atau email, silakan hubungi admin.")
    
    st.markdown("---")
    
    st.subheader("🔐 Ubah Password")
    
    with st.form("password_form"):
        current_password = st.text_input("Password Saat Ini", type="password")
        new_password = st.text_input("Password Baru", type="password")
        confirm_password = st.text_input("Konfirmasi Password Baru", type="password")
        
        if st.form_submit_button("🔄 Update Password", use_container_width=True):
            if current_password and new_password and confirm_password:
                if new_password == confirm_password:
                    if len(new_password) >= 8:
                        if verify_current_password(user['id'], current_password):
                            update_password(user['id'], new_password)
                            st.success("Password berhasil diubah!")
                        else:
                            st.error("Password saat ini salah")
                    else:
                        st.error("Password baru minimal 8 karakter")
                else:
                    st.error("Konfirmasi password tidak cocok")
            else:
                st.error("Silakan isi semua field")
    
    st.markdown("---")
    
    st.subheader("📝 Tentang Aplikasi")
    st.markdown("""
    **StreamFlow v2.0** - Platform Live Streaming Multi-Platform
    
    Fitur utama:
    - Upload dan kelola video
    - Streaming ke berbagai platform
    - Jadwal streaming otomatis
    - Monitoring real-time
    
    Dibuat dengan ❤️ menggunakan Streamlit
    """)

# Database helper functions
def get_user_video_count():
    conn = st.session_state.db_connection
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM videos WHERE user_id = ?", (st.session_state.user['id'],))
    count = cursor.fetchone()[0]
    return count

def get_user_stream_count():
    conn = st.session_state.db_connection
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM streams WHERE user_id = ? AND status = 'active'", (st.session_state.user['id'],))
    count = cursor.fetchone()[0]
    return count

def get_user_total_streams():
    conn = st.session_state.db_connection
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM streams WHERE user_id = ?", (st.session_state.user['id'],))
    count = cursor.fetchone()[0]
    return count

def get_recent_streams():
    conn = st.session_state.db_connection
    cursor = conn.cursor()
    cursor.execute(
        "SELECT title, platform, status, created_at FROM streams WHERE user_id = ? ORDER BY created_at DESC LIMIT 5",
        (st.session_state.user['id'],)
    )
    streams = cursor.fetchall()
    return streams

def save_video_to_db(filename, file_path):
    conn = st.session_state.db_connection
    cursor = conn.cursor()
    
    file_size = 1024 * 1024  # Demo size
    
    cursor.execute(
        "INSERT INTO videos (user_id, filename, original_name, file_path, file_size) VALUES (?, ?, ?, ?, ?)",
        (st.session_state.user['id'], filename, filename, file_path, file_size)
    )
    conn.commit()

def get_user_videos():
    conn = st.session_state.db_connection
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM videos WHERE user_id = ? ORDER BY created_at DESC",
        (st.session_state.user['id'],)
    )
    videos = cursor.fetchall()
    return videos

def delete_video(video_id):
    conn = st.session_state.db_connection
    cursor = conn.cursor()
    cursor.execute("DELETE FROM videos WHERE id = ?", (video_id,))
    conn.commit()

def get_video_options():
    videos = get_user_videos()
    options = [("Tidak ada video", None)]
    for video in videos:
        options.append((video[3], video[0]))  # (original_name, id)
    return options

def create_stream(title, platform, stream_key, video_id, scheduled_time):
    conn = st.session_state.db_connection
    cursor = conn.cursor()
    
    cursor.execute(
        "INSERT INTO streams (user_id, title, platform, stream_key, video_id, scheduled_time) VALUES (?, ?, ?, ?, ?, ?)",
        (st.session_state.user['id'], title, platform, stream_key, video_id, scheduled_time)
    )
    conn.commit()

def get_user_streams():
    conn = st.session_state.db_connection
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM streams WHERE user_id = ? ORDER BY created_at DESC",
        (st.session_state.user['id'],)
    )
    streams = cursor.fetchall()
    return streams

def update_stream_status(stream_id, status):
    conn = st.session_state.db_connection
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE streams SET status = ? WHERE id = ?",
        (status, stream_id)
    )
    conn.commit()

def delete_stream(stream_id):
    conn = st.session_state.db_connection
    cursor = conn.cursor()
    cursor.execute("DELETE FROM streams WHERE id = ?", (stream_id,))
    conn.commit()

def verify_current_password(user_id, password):
    conn = st.session_state.db_connection
    cursor = conn.cursor()
    cursor.execute("SELECT password_hash FROM users WHERE id = ?", (user_id,))
    result = cursor.fetchone()
    
    if result:
        return verify_password(password, result[0])
    return False

def update_password(user_id, new_password):
    conn = st.session_state.db_connection
    cursor = conn.cursor()
    password_hash = hash_password(new_password)
    cursor.execute(
        "UPDATE users SET password_hash = ? WHERE id = ?",
        (password_hash, user_id)
    )
    conn.commit()

# Main app
def main():
    init_session()
    
    if st.session_state.user is None:
        if st.session_state.page == 'register':
            register_page()
        else:
            login_page()
    else:
        if st.session_state.page == 'dashboard':
            dashboard_page()
        elif st.session_state.page == 'gallery':
            gallery_page()
        elif st.session_state.page == 'streams':
            streams_page()
        elif st.session_state.page == 'settings':
            settings_page()
        else:
            dashboard_page()

if __name__ == "__main__":
    main()