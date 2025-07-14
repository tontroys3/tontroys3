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

# Database setup
def init_database():
    """Initialize SQLite database with required tables"""
    conn = sqlite3.connect('db/streamflow.db')
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
    conn.close()

# Initialize database
init_database()

# Authentication functions
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, hash_password):
    return hash_password == hashlib.sha256(password.encode()).hexdigest()

def create_user(username, email, password):
    conn = sqlite3.connect('db/streamflow.db')
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
    finally:
        conn.close()

def authenticate_user(username, password):
    conn = sqlite3.connect('db/streamflow.db')
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT id, username, email, password_hash FROM users WHERE username = ?",
        (username,)
    )
    user = cursor.fetchone()
    conn.close()
    
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
    st.title("🎥 StreamFlow - Login")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### Login to your account")
        
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            login_button = st.form_submit_button("Login")
            
            if login_button:
                if username and password:
                    user = authenticate_user(username, password)
                    if user:
                        st.session_state.user = user
                        st.session_state.page = 'dashboard'
                        st.rerun()
                    else:
                        st.error("Invalid username or password")
                else:
                    st.error("Please enter both username and password")
        
        st.markdown("---")
        st.markdown("### Don't have an account?")
        if st.button("Create Account"):
            st.session_state.page = 'register'
            st.rerun()

# Registration page
def register_page():
    st.title("🎥 StreamFlow - Register")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### Create your account")
        
        with st.form("register_form"):
            username = st.text_input("Username")
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            register_button = st.form_submit_button("Register")
            
            if register_button:
                if username and email and password and confirm_password:
                    if password == confirm_password:
                        if create_user(username, email, password):
                            st.success("Account created successfully! Please login.")
                            st.session_state.page = 'login'
                            st.rerun()
                        else:
                            st.error("Username or email already exists")
                    else:
                        st.error("Passwords do not match")
                else:
                    st.error("Please fill in all fields")
        
        st.markdown("---")
        if st.button("Back to Login"):
            st.session_state.page = 'login'
            st.rerun()

# Dashboard
def dashboard_page():
    st.title(f"🎥 StreamFlow Dashboard - Welcome {st.session_state.user['username']}!")
    
    # Sidebar
    with st.sidebar:
        st.markdown(f"### Welcome, {st.session_state.user['username']}!")
        
        if st.button("Dashboard"):
            st.session_state.page = 'dashboard'
            st.rerun()
        
        if st.button("Video Gallery"):
            st.session_state.page = 'gallery'
            st.rerun()
        
        if st.button("Live Streams"):
            st.session_state.page = 'streams'
            st.rerun()
        
        if st.button("Settings"):
            st.session_state.page = 'settings'
            st.rerun()
        
        st.markdown("---")
        if st.button("Logout"):
            st.session_state.user = None
            st.session_state.page = 'login'
            st.rerun()
    
    # Main content
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Videos", get_user_video_count())
    
    with col2:
        st.metric("Active Streams", get_user_stream_count())
    
    with col3:
        st.metric("Total Streams", get_user_total_streams())
    
    st.markdown("---")
    
    # Recent activity
    st.subheader("Recent Activity")
    recent_streams = get_recent_streams()
    if recent_streams:
        df = pd.DataFrame(recent_streams, columns=['Title', 'Platform', 'Status', 'Created'])
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No recent activity")

# Video Gallery
def gallery_page():
    st.title("🎬 Video Gallery")
    
    # Upload video
    st.subheader("Upload New Video")
    uploaded_file = st.file_uploader("Choose a video file", type=['mp4', 'mov', 'avi', 'mkv'])
    
    if uploaded_file is not None:
        # Create uploads directory if it doesn't exist
        os.makedirs('public/uploads/videos', exist_ok=True)
        
        # Save uploaded file
        file_path = f"public/uploads/videos/{uploaded_file.name}"
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Save to database
        save_video_to_db(uploaded_file.name, file_path)
        st.success(f"Video '{uploaded_file.name}' uploaded successfully!")
    
    st.markdown("---")
    
    # Display videos
    st.subheader("Your Videos")
    videos = get_user_videos()
    
    if videos:
        for video in videos:
            col1, col2, col3 = st.columns([1, 3, 1])
            
            with col1:
                st.write(f"**{video[2]}**")  # original_name
            
            with col2:
                st.write(f"Uploaded: {video[6]}")  # created_at
            
            with col3:
                if st.button(f"Delete", key=f"delete_{video[0]}"):
                    delete_video(video[0])
                    st.rerun()
    else:
        st.info("No videos uploaded yet")

# Live Streams
def streams_page():
    st.title("📺 Live Streams")
    
    # Create new stream
    st.subheader("Create New Stream")
    
    with st.form("stream_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            title = st.text_input("Stream Title")
            platform = st.selectbox("Platform", ["YouTube", "Facebook", "Twitch", "TikTok", "Instagram"])
        
        with col2:
            stream_key = st.text_input("Stream Key", type="password")
            video_id = st.selectbox("Select Video", get_video_options())
        
        scheduled_time = st.datetime_input("Schedule Time (Optional)")
        
        submit_button = st.form_submit_button("Create Stream")
        
        if submit_button:
            if title and platform and stream_key:
                create_stream(title, platform, stream_key, video_id, scheduled_time)
                st.success("Stream created successfully!")
                st.rerun()
            else:
                st.error("Please fill in all required fields")
    
    st.markdown("---")
    
    # Display streams
    st.subheader("Your Streams")
    streams = get_user_streams()
    
    if streams:
        for stream in streams:
            with st.expander(f"{stream[2]} - {stream[3]} ({stream[5]})"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Title:** {stream[2]}")
                    st.write(f"**Platform:** {stream[3]}")
                    st.write(f"**Status:** {stream[5]}")
                
                with col2:
                    if stream[6]:  # scheduled_time
                        st.write(f"**Scheduled:** {stream[6]}")
                    st.write(f"**Created:** {stream[7]}")
                
                # Action buttons
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button(f"Start Stream", key=f"start_{stream[0]}"):
                        update_stream_status(stream[0], 'active')
                        st.success("Stream started!")
                        st.rerun()
                
                with col2:
                    if st.button(f"Stop Stream", key=f"stop_{stream[0]}"):
                        update_stream_status(stream[0], 'stopped')
                        st.success("Stream stopped!")
                        st.rerun()
                
                with col3:
                    if st.button(f"Delete Stream", key=f"delete_stream_{stream[0]}"):
                        delete_stream(stream[0])
                        st.success("Stream deleted!")
                        st.rerun()
    else:
        st.info("No streams created yet")

# Settings
def settings_page():
    st.title("⚙️ Settings")
    
    user = st.session_state.user
    
    st.subheader("Account Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.text_input("Username", value=user['username'], disabled=True)
        st.text_input("Email", value=user['email'], disabled=True)
    
    with col2:
        st.info("To change your username or email, please contact support.")
    
    st.markdown("---")
    
    st.subheader("Change Password")
    
    with st.form("password_form"):
        current_password = st.text_input("Current Password", type="password")
        new_password = st.text_input("New Password", type="password")
        confirm_password = st.text_input("Confirm New Password", type="password")
        
        if st.form_submit_button("Update Password"):
            if current_password and new_password and confirm_password:
                if new_password == confirm_password:
                    if verify_current_password(user['id'], current_password):
                        update_password(user['id'], new_password)
                        st.success("Password updated successfully!")
                    else:
                        st.error("Current password is incorrect")
                else:
                    st.error("New passwords do not match")
            else:
                st.error("Please fill in all fields")

# Database helper functions
def get_user_video_count():
    conn = sqlite3.connect('db/streamflow.db')
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM videos WHERE user_id = ?", (st.session_state.user['id'],))
    count = cursor.fetchone()[0]
    conn.close()
    return count

def get_user_stream_count():
    conn = sqlite3.connect('db/streamflow.db')
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM streams WHERE user_id = ? AND status = 'active'", (st.session_state.user['id'],))
    count = cursor.fetchone()[0]
    conn.close()
    return count

def get_user_total_streams():
    conn = sqlite3.connect('db/streamflow.db')
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM streams WHERE user_id = ?", (st.session_state.user['id'],))
    count = cursor.fetchone()[0]
    conn.close()
    return count

def get_recent_streams():
    conn = sqlite3.connect('db/streamflow.db')
    cursor = conn.cursor()
    cursor.execute(
        "SELECT title, platform, status, created_at FROM streams WHERE user_id = ? ORDER BY created_at DESC LIMIT 5",
        (st.session_state.user['id'],)
    )
    streams = cursor.fetchall()
    conn.close()
    return streams

def save_video_to_db(filename, file_path):
    conn = sqlite3.connect('db/streamflow.db')
    cursor = conn.cursor()
    
    file_size = os.path.getsize(file_path)
    
    cursor.execute(
        "INSERT INTO videos (user_id, filename, original_name, file_path, file_size) VALUES (?, ?, ?, ?, ?)",
        (st.session_state.user['id'], filename, filename, file_path, file_size)
    )
    conn.commit()
    conn.close()

def get_user_videos():
    conn = sqlite3.connect('db/streamflow.db')
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM videos WHERE user_id = ? ORDER BY created_at DESC",
        (st.session_state.user['id'],)
    )
    videos = cursor.fetchall()
    conn.close()
    return videos

def delete_video(video_id):
    conn = sqlite3.connect('db/streamflow.db')
    cursor = conn.cursor()
    
    # Get file path before deletion
    cursor.execute("SELECT file_path FROM videos WHERE id = ?", (video_id,))
    result = cursor.fetchone()
    
    if result:
        file_path = result[0]
        # Delete file from filesystem
        if os.path.exists(file_path):
            os.remove(file_path)
        
        # Delete from database
        cursor.execute("DELETE FROM videos WHERE id = ?", (video_id,))
        conn.commit()
    
    conn.close()

def get_video_options():
    videos = get_user_videos()
    options = [("None", None)]
    for video in videos:
        options.append((video[3], video[0]))  # (original_name, id)
    return options

def create_stream(title, platform, stream_key, video_id, scheduled_time):
    conn = sqlite3.connect('db/streamflow.db')
    cursor = conn.cursor()
    
    cursor.execute(
        "INSERT INTO streams (user_id, title, platform, stream_key, video_id, scheduled_time) VALUES (?, ?, ?, ?, ?, ?)",
        (st.session_state.user['id'], title, platform, stream_key, video_id, scheduled_time)
    )
    conn.commit()
    conn.close()

def get_user_streams():
    conn = sqlite3.connect('db/streamflow.db')
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM streams WHERE user_id = ? ORDER BY created_at DESC",
        (st.session_state.user['id'],)
    )
    streams = cursor.fetchall()
    conn.close()
    return streams

def update_stream_status(stream_id, status):
    conn = sqlite3.connect('db/streamflow.db')
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE streams SET status = ? WHERE id = ?",
        (status, stream_id)
    )
    conn.commit()
    conn.close()

def delete_stream(stream_id):
    conn = sqlite3.connect('db/streamflow.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM streams WHERE id = ?", (stream_id,))
    conn.commit()
    conn.close()

def verify_current_password(user_id, password):
    conn = sqlite3.connect('db/streamflow.db')
    cursor = conn.cursor()
    cursor.execute("SELECT password_hash FROM users WHERE id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return verify_password(password, result[0])
    return False

def update_password(user_id, new_password):
    conn = sqlite3.connect('db/streamflow.db')
    cursor = conn.cursor()
    password_hash = hash_password(new_password)
    cursor.execute(
        "UPDATE users SET password_hash = ? WHERE id = ?",
        (password_hash, user_id)
    )
    conn.commit()
    conn.close()

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