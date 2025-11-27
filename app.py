import streamlit as st
from modules.auth import Authentication
import base64

# Page configuration
st.set_page_config(
    page_title="Bank Loan Analysis Tool",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
def local_css():
    st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .risk-high {
        color: #ff4b4b;
        font-weight: bold;
    }
    .risk-medium {
        color: #ffa500;
        font-weight: bold;
    }
    .risk-low {
        color: #00cc96;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

def main():
    local_css()
    
    # Initialize session state
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user_info' not in st.session_state:
        st.session_state.user_info = {}
    
    # Authentication
    if not st.session_state.authenticated:
        show_login()
    else:
        show_main_app()

def show_login():
    st.markdown("<h1 class='main-header'>🏦 Bank Loan Analysis Tool</h1>", unsafe_allow_html=True)
    st.markdown("### Kenyan Banking Institution")
    
    col1, col2, col3 = st.columns([1,2,1])
    
    with col2:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            login_button = st.form_submit_button("Login")
            
            if login_button:
                auth = Authentication()
                authenticated, user_info = auth.authenticate(username, password)
                
                if authenticated:
                    st.session_state.authenticated = True
                    st.session_state.user_info = user_info
                    st.success(f"Welcome {user_info['role']}!")
                    st.rerun()
                else:
                    st.error("Invalid username or password")

def show_main_app():
    # Sidebar
    with st.sidebar:
        st.image("https://via.placeholder.com/150x50.png?text=BANK+LOGO", width=150)
        st.write(f"**Role:** {st.session_state.user_info['role']}")
        st.write(f"**Branch:** {st.session_state.user_info['branch']}")
        st.write("---")
        
        if st.button("Logout"):
            st.session_state.authenticated = False
            st.session_state.user_info = {}
            st.rerun()
    
    # Main app continues with pages
    st.markdown("<h1 class='main-header'>Loan Analysis Dashboard</h1>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()