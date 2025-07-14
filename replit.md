# StreamFlow v2.0 - Live Streaming Application

## Overview

StreamFlow is now a Streamlit-based live streaming application that enables multi-platform streaming to YouTube, Facebook, and other RTMP-enabled platforms. The application provides video management, scheduled streaming, real-time monitoring, and advanced streaming configuration options.

## User Preferences

Preferred communication style: Simple, everyday language.

## Recent Changes

- **2025-07-14**: Converted from Node.js/Express application to Streamlit web app
- **2025-07-14**: Created streamlit_app.py with full authentication, video management, and streaming functionality
- **2025-07-14**: Maintained SQLite database structure for compatibility
- **2025-07-14**: Application now runs on port 5000 using Streamlit server

## System Architecture

### Backend Architecture
- **Framework**: Express.js web server with EJS templating
- **Database**: SQLite3 for data persistence
- **Video Processing**: FFmpeg for video encoding and streaming
- **Authentication**: Session-based authentication with bcrypt password hashing
- **Security**: CSRF protection, rate limiting, and input validation

### Frontend Architecture
- **Template Engine**: EJS with EJS-mate for layout management
- **Styling**: Custom CSS with responsive design
- **Client-side**: Vanilla JavaScript for interactive components
- **Video Player**: Video.js for video playback

## Key Components

### Models
- **User**: Handles user authentication and profile management
- **Video**: Manages video metadata and file references
- **Stream**: Manages streaming configurations and status

### Services
- **streamingService**: Core FFmpeg streaming functionality with retry logic
- **schedulerService**: Manages scheduled stream execution and duration monitoring
- **systemMonitor**: Real-time system resource monitoring
- **googleDriveService**: Google Drive integration for video imports
- **logger**: Centralized logging to file and console

### Middleware
- **uploadMiddleware**: Handles video file uploads with multer
- **Authentication**: Session-based user authentication
- **Security**: CSRF tokens, rate limiting, input validation

## Data Flow

1. **User Registration/Login**: Users create accounts or authenticate via session management
2. **Video Upload**: Videos uploaded locally or imported from Google Drive
3. **Video Processing**: FFmpeg generates thumbnails and extracts metadata
4. **Stream Configuration**: Users configure RTMP settings and streaming parameters
5. **Stream Execution**: FFmpeg processes video and streams to configured platforms
6. **Monitoring**: Real-time system and stream status monitoring

## External Dependencies

### Core Dependencies
- **@ffmpeg-installer/ffmpeg**: Video processing and streaming
- **googleapis**: Google Drive API integration
- **sqlite3**: Database operations
- **express-session**: Session management
- **multer**: File upload handling
- **bcrypt**: Password hashing
- **systeminformation**: System monitoring

### Security Dependencies
- **csrf**: Cross-site request forgery protection
- **express-rate-limit**: Rate limiting
- **express-validator**: Input validation

## Deployment Strategy

### Requirements
- Node.js v20 or higher
- FFmpeg (system or bundled)
- SQLite3 (included in package)
- VPS/Server with 1+ CPU cores and 1GB+ RAM
- Port 7575 (configurable via environment)

### Installation Options
1. **Automated**: Single-command installation script
2. **Manual**: Step-by-step setup with system dependencies

### Database Setup
- SQLite database auto-created on first run
- Tables for users, videos, and streams created automatically
- Session storage using SQLite store

### Security Configuration
- Session secrets auto-generated
- Environment variables for configuration
- CSRF protection enabled
- Rate limiting configured

### File Storage
- Videos stored in `public/uploads/videos/`
- Thumbnails in `public/uploads/thumbnails/`
- Logs in `logs/app.log`
- Database in `db/streamflow.db`

## Architecture Decisions

### Database Choice: SQLite3
- **Problem**: Need lightweight, serverless database
- **Solution**: SQLite3 for simplicity and zero-configuration
- **Pros**: No server setup, file-based, included in package
- **Cons**: Limited concurrent write performance

### Video Processing: FFmpeg
- **Problem**: Need video encoding and streaming capabilities
- **Solution**: FFmpeg with Node.js wrapper
- **Pros**: Industry standard, comprehensive format support
- **Cons**: Resource intensive, complex configuration

### Authentication: Session-based
- **Problem**: User authentication and state management
- **Solution**: Express sessions with SQLite storage
- **Pros**: Simple implementation, server-side security
- **Cons**: Not suitable for distributed deployments

### File Upload: Multer + Local Storage
- **Problem**: Handle video file uploads
- **Solution**: Multer with disk storage
- **Pros**: Direct file access, simple implementation
- **Cons**: Server storage dependency, no CDN integration