#!/usr/bin/env python3
"""
Test Double Sidebar Fix
Simple test to verify no duplicate sidebar elements are created
"""

import streamlit as st
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Test page config
st.set_page_config(
    page_title="Double Sidebar Test",
    page_icon="🔧",
    layout="wide"
)

# Test the problematic functions
try:
    from utils.auth_helpers import show_user_info, enable_dev_auth
    from utils.shared_utils import show_debug_info
    
    st.title("🔧 Double Sidebar Test")
    
    # Test sidebar without conflicts
    with st.sidebar:
        st.header("Test Sidebar")
        st.write("This should be the only sidebar menu")
        
        # Test the fixed functions
        st.markdown("---")
        st.markdown("### Auth Functions Test")
        
        # These should not create additional sidebars
        enable_dev_auth()
        show_user_info()
        
        st.markdown("---")
        st.markdown("### Debug Functions Test")
        
        # This should not create additional sidebars
        show_debug_info()
    
    # Main content
    st.write("✅ If you see only ONE sidebar menu, the fix worked!")
    st.write("❌ If you see TWO sidebar menus, there's still an issue.")
    
    # Instructions
    st.info("""
    **Instructions:**
    1. Look at the left sidebar
    2. Count how many navigation menus you see
    3. There should be only ONE sidebar with all elements inside it
    4. No duplicate 'streamlit app' labels should appear
    """)

except Exception as e:
    st.error(f"Error importing functions: {e}")
    st.write("Check if the sidebar fixes are applied correctly")
