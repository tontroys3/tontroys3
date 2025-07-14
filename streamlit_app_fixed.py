import streamlit as st
import sqlite3
import pandas as pd
import hashlib
from datetime import datetime
import os

# Set page config
st.set_page_config(
    page_title="StreamFlow - Live Streaming Platform",
    page_icon="🎥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
def init_session():
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'page' not in st.session_state:
        st.session_state.page = 'login'
    if 'db_initialized' not in st.session_state:
        st.session_state.db_initialized = False
    if 'users' not in st.session_state:
        st.session_state.users = []
    if 'videos' not in st.session_state:
        st.session_state.videos = []
    if 'streams' not in st.session_state:
        st.session_state.streams = []

# Initialize data storage (using session state for cloud compatibility)
def init_data():
    if not st.session_state.db_initialized:
        # Create demo admin user
        admin_user = {
            'id': 1,
            'username': 'admin',
            'email': 'admin@streamflow.com',
            'password_hash': hashlib.sha256('admin123'.encode()).hexdigest(),
            'created_at': datetime.now().isoformat()
        }
        st.session_state.users.append(admin_user)
        st.session_state.db_initialized = True

# Authentication functions
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, hash_password):
    return hash_password == hashlib.sha256(password.encode()).hexdigest()

def create_user(username, email, password):
    # Check if user already exists
    for user in st.session_state.users:
        if user['username'] == username or user['email'] == email:
            return False
    
    # Create new user
    new_user = {
        'id': len(st.session_state.users) + 1,
        'username': username,
        'email': email,
        'password_hash': hash_password(password),
        'created_at': datetime.now().isoformat()
    }
    st.session_state.users.append(new_user)
    return True

def authenticate_user(username, password):
    for user in st.session_state.users:
        if user['username'] == username and verify_password(password, user['password_hash']):
            return {'id': user['id'], 'username': user['username'], 'email': user['email']}
    return None

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
            
        st.markdown("---")
        st.info("**Demo Login:** Username: `admin`, Password: `admin123`")

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
        video_count = len([v for v in st.session_state.videos if v['user_id'] == st.session_state.user['id']])
        st.metric("Total Video", video_count, help="Jumlah video yang telah diupload")
    
    with col2:
        active_streams = len([s for s in st.session_state.streams if s['user_id'] == st.session_state.user['id'] and s['status'] == 'active'])
        st.metric("Stream Aktif", active_streams, help="Jumlah stream yang sedang berjalan")
    
    with col3:
        total_streams = len([s for s in st.session_state.streams if s['user_id'] == st.session_state.user['id']])
        st.metric("Total Stream", total_streams, help="Total stream yang pernah dibuat")
    
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
    user_streams = [s for s in st.session_state.streams if s['user_id'] == st.session_state.user['id']]
    
    if user_streams:
        recent_streams = sorted(user_streams, key=lambda x: x['created_at'], reverse=True)[:5]
        data = []
        for stream in recent_streams:
            data.append([stream['title'], stream['platform'], stream['status'], stream['created_at']])
        
        df = pd.DataFrame(data, columns=['Judul', 'Platform', 'Status', 'Dibuat'])
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
            new_video = {
                'id': len(st.session_state.videos) + 1,
                'user_id': st.session_state.user['id'],
                'filename': uploaded_file.name,
                'original_name': uploaded_file.name,
                'file_path': f"uploads/{uploaded_file.name}",
                'file_size': uploaded_file.size if hasattr(uploaded_file, 'size') else 1024000,
                'created_at': datetime.now().isoformat()
            }
            st.session_state.videos.append(new_video)
            st.success("Video berhasil disimpan!")
            st.rerun()
    
    st.markdown("---")
    
    # Display videos
    st.subheader("📚 Video Anda")
    user_videos = [v for v in st.session_state.videos if v['user_id'] == st.session_state.user['id']]
    
    if user_videos:
        for video in user_videos:
            with st.expander(f"🎥 {video['original_name']}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Nama File:** {video['filename']}")
                    st.write(f"**Ukuran:** {video['file_size']} bytes")
                
                with col2:
                    st.write(f"**Upload:** {video['created_at']}")
                    if st.button(f"Hapus", key=f"delete_{video['id']}"):
                        st.session_state.videos = [v for v in st.session_state.videos if v['id'] != video['id']]
                        st.success("Video dihapus!")
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
            user_videos = [v for v in st.session_state.videos if v['user_id'] == st.session_state.user['id']]
            video_options = ["Tidak ada video"] + [v['original_name'] for v in user_videos]
            selected_video = st.selectbox("Pilih Video", video_options)
        
        scheduled_time = st.datetime_input("Jadwal Stream (Opsional)", value=None)
        
        submit_button = st.form_submit_button("🚀 Buat Stream", use_container_width=True)
        
        if submit_button:
            if title and platform and stream_key:
                video_id = None
                if selected_video != "Tidak ada video":
                    video_id = next((v['id'] for v in user_videos if v['original_name'] == selected_video), None)
                
                new_stream = {
                    'id': len(st.session_state.streams) + 1,
                    'user_id': st.session_state.user['id'],
                    'title': title,
                    'platform': platform,
                    'stream_key': stream_key,
                    'video_id': video_id,
                    'status': 'pending',
                    'scheduled_time': scheduled_time.isoformat() if scheduled_time else None,
                    'created_at': datetime.now().isoformat()
                }
                st.session_state.streams.append(new_stream)
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
    user_streams = [s for s in st.session_state.streams if s['user_id'] == st.session_state.user['id']]
    
    if user_streams:
        for stream in user_streams:
            with st.expander(f"📺 {stream['title']} - {stream['platform']} ({stream['status']})"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Judul:** {stream['title']}")
                    st.write(f"**Platform:** {stream['platform']}")
                    st.write(f"**Status:** {stream['status']}")
                
                with col2:
                    if stream['scheduled_time']:
                        st.write(f"**Jadwal:** {stream['scheduled_time']}")
                    st.write(f"**Dibuat:** {stream['created_at']}")
                
                # Action buttons
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button(f"▶️ Mulai", key=f"start_{stream['id']}"):
                        for i, s in enumerate(st.session_state.streams):
                            if s['id'] == stream['id']:
                                st.session_state.streams[i]['status'] = 'active'
                        st.success("Stream dimulai!")
                        st.rerun()
                
                with col2:
                    if st.button(f"⏹️ Berhenti", key=f"stop_{stream['id']}"):
                        for i, s in enumerate(st.session_state.streams):
                            if s['id'] == stream['id']:
                                st.session_state.streams[i]['status'] = 'stopped'
                        st.success("Stream dihentikan!")
                        st.rerun()
                
                with col3:
                    if st.button(f"🗑️ Hapus", key=f"delete_stream_{stream['id']}"):
                        st.session_state.streams = [s for s in st.session_state.streams if s['id'] != stream['id']]
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
                        # Find user and verify current password
                        user_data = next((u for u in st.session_state.users if u['id'] == user['id']), None)
                        if user_data and verify_password(current_password, user_data['password_hash']):
                            # Update password
                            for i, u in enumerate(st.session_state.users):
                                if u['id'] == user['id']:
                                    st.session_state.users[i]['password_hash'] = hash_password(new_password)
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

# Main app
def main():
    init_session()
    init_data()
    
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