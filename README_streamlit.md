# StreamFlow - Live Streaming Platform

A Streamlit-based live streaming management application for multi-platform streaming.

## Features

- **User Authentication**: Secure login and registration system
- **Video Management**: Upload and manage video files
- **Multi-Platform Streaming**: Support for YouTube, Facebook, Twitch, and more
- **Stream Scheduling**: Schedule streams for future broadcasts
- **Real-time Monitoring**: Track stream status and performance

## Setup for Streamlit.io

1. Fork or clone this repository
2. Make sure `streamlit_app.py` is in the root directory
3. Requirements are automatically installed from `requirements_streamlit.txt`
4. Deploy directly to Streamlit.io

## Files for Deployment

- `streamlit_app.py` - Main application file
- `requirements_streamlit.txt` - Python dependencies
- `README_streamlit.md` - This file

## Usage

1. Create an account on the registration page
2. Upload videos to your gallery
3. Configure streaming platforms with RTMP keys
4. Start live streaming to multiple platforms simultaneously

## Platform Support

- YouTube Live
- Facebook Live
- Twitch
- TikTok Live
- Instagram Live
- Custom RTMP servers

## Requirements

- Python 3.11+
- Streamlit 1.46.1+
- SQLite3 (built-in)
- Pandas for data management
- Requests for API calls
- Pillow for image processing