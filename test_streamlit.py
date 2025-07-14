import streamlit as st

st.title("Test Streamlit App")
st.write("This is a test to verify Streamlit is working properly.")

if st.button("Click Me"):
    st.success("Button clicked! Streamlit is working.")
    
st.sidebar.write("Sidebar is working")