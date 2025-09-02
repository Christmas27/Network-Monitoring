#!/usr/bin/env python3
"""
Styling Configuration for Network Monitoring Dashboard
Centralized CSS and styling definitions
"""

import streamlit as st

def apply_custom_css():
    """Apply custom CSS styling to the Streamlit app"""
    st.markdown("""
    <style>
        .main-header {
            font-size: 2.5rem;
            text-align: center;
            color: #1f77b4;
            margin-bottom: 1rem;
            font-weight: bold;
        }
        .metric-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 1.5rem;
            border-radius: 10px;
            color: white;
            text-align: center;
            margin: 0.5rem 0;
        }
        .success-card {
            background: linear-gradient(135deg, #56ab2f 0%, #a8e6cf 100%);
            color: white;
        }
        .warning-card {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
        }
        .info-card {
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            color: white;
        }
        .error-card {
            background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
            color: white;
        }
        .sidebar .sidebar-content {
            background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 2px;
        }
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            padding: 0px 24px;
            background-color: #2e3440;
            border-radius: 4px 4px 0px 0px;
            color: #d8dee9 !important;
            font-weight: 500;
        }
        .stTabs [aria-selected="true"] {
            background-color: #1f77b4;
            color: white !important;
            font-weight: 600;
        }
        .stTabs [data-baseweb="tab"]:hover {
            background-color: #4c566a;
            color: white !important;
        }
        /* Fix selectbox and form elements - Comprehensive Override */
        .stSelectbox > div > div {
            background-color: #3b4252 !important;
            color: #d8dee9 !important;
            border: 1px solid #4c566a !important;
        }
        .stSelectbox label {
            color: #d8dee9 !important;
            font-weight: 500;
        }
        
        /* Target all selectbox elements more specifically */
        div[data-testid="stSelectbox"] > div > div {
            background-color: #3b4252 !important;
            color: #d8dee9 !important;
        }
        
        /* Fix the actual dropdown menu */
        div[data-baseweb="select"] {
            background-color: #3b4252 !important;
        }
        div[data-baseweb="select"] > div {
            background-color: #3b4252 !important;
            color: #d8dee9 !important;
        }
        div[data-baseweb="select"] span {
            color: #d8dee9 !important;
        }
        
        /* Fix dropdown options list */
        ul[role="listbox"] {
            background-color: #2e3440 !important;
            border: 1px solid #4c566a !important;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3) !important;
        }
        li[role="option"] {
            background-color: #2e3440 !important;
            color: #d8dee9 !important;
            padding: 8px 12px !important;
        }
        li[role="option"]:hover {
            background-color: #5e81ac !important;
            color: white !important;
        }
        li[role="option"][aria-selected="true"] {
            background-color: #1f77b4 !important;
            color: white !important;
        }
        
        /* Force override for any remaining white text */
        .stSelectbox * {
            color: #d8dee9 !important;
        }
        
        /* Additional overrides for stubborn elements */
        div[data-baseweb="select"] div[role="combobox"] {
            background-color: #3b4252 !important;
            color: #d8dee9 !important;
        }
        
        /* Menu dropdown styling */
        div[data-baseweb="menu"] {
            background-color: #2e3440 !important;
            border: 1px solid #4c566a !important;
        }
        div[data-baseweb="menu"] ul {
            background-color: #2e3440 !important;
        }
        div[data-baseweb="menu"] li {
            background-color: #2e3440 !important;
            color: #d8dee9 !important;
        }
        div[data-baseweb="menu"] li:hover {
            background-color: #5e81ac !important;
            color: white !important;
        }
        /* Dropdown menu styling */
        ul[role="listbox"] {
            background-color: #2e3440 !important;
            border: 1px solid #4c566a !important;
        }
        li[role="option"] {
            background-color: #2e3440 !important;
            color: #d8dee9 !important;
        }
        li[role="option"]:hover {
            background-color: #4c566a !important;
            color: white !important;
        }
        /* Improve expander visibility */
        .streamlit-expanderHeader {
            background-color: #2e3440;
            color: #d8dee9 !important;
            font-weight: 500;
        }
        /* Better button contrast */
        .stButton > button {
            background-color: #5e81ac;
            color: white;
            border: none;
            font-weight: 500;
        }
        .stButton > button:hover {
            background-color: #81a1c1;
            color: white;
        }
        
        /* Additional selectbox text visibility fixes */
        .stSelectbox span[title] {
            color: #d8dee9 !important;
        }
        .stSelectbox div[role="combobox"] span {
            color: #d8dee9 !important;
        }
    </style>

    <script>
    // JavaScript to ensure dropdown is always visible
    setTimeout(function() {
        function fixDropdowns() {
            // Fix all selectboxes
            document.querySelectorAll('[data-baseweb="select"]').forEach(function(select) {
                select.style.backgroundColor = '#3b4252';
                select.style.color = '#d8dee9';
                
                // Fix all spans inside selectbox
                select.querySelectorAll('span').forEach(function(span) {
                    span.style.color = '#d8dee9';
                });
            });
            
            // Fix dropdown menus
            document.querySelectorAll('[role="listbox"], [data-baseweb="menu"]').forEach(function(menu) {
                menu.style.backgroundColor = '#2e3440';
                menu.style.border = '1px solid #4c566a';
                
                menu.querySelectorAll('[role="option"], li').forEach(function(option) {
                    option.style.backgroundColor = '#2e3440';
                    option.style.color = '#d8dee9';
                    option.addEventListener('mouseenter', function() {
                        this.style.backgroundColor = '#5e81ac';
                        this.style.color = 'white';
                    });
                    option.addEventListener('mouseleave', function() {
                        this.style.backgroundColor = '#2e3440';
                        this.style.color = '#d8dee9';
                    });
                });
            });
        }
        
        // Apply immediately
        fixDropdowns();
        
        // Apply when new elements are added
        new MutationObserver(fixDropdowns).observe(document.body, {
            childList: true,
            subtree: true
        });
        
        // Apply every 500ms to catch dynamic elements
        setInterval(fixDropdowns, 500);
    }, 1000);
    </script>
    """, unsafe_allow_html=True)

def get_metric_card_style(card_type="default"):
    """Get CSS class for metric card types"""
    card_styles = {
        "default": "metric-card",
        "success": "metric-card success-card",
        "warning": "metric-card warning-card", 
        "info": "metric-card info-card",
        "error": "metric-card error-card"
    }
    return card_styles.get(card_type, "metric-card")
