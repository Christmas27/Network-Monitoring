#!/usr/bin/env python3
"""
Minimal Double Sidebar Reproduction Test
This will help identify the exact cause of the double sidebar issue
"""

import streamlit as st

# Set page config
st.set_page_config(
    page_title="Minimal Sidebar Test",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Minimal pages list
PAGES = ["🏠 Dashboard", "📱 Devices", "🤖 Automation"]

def main():
    """Minimal main function"""
    # Only ONE sidebar context
    with st.sidebar:
        st.markdown("# 🔍 Minimal Test")
        st.markdown("### Navigation")
        
        # Single page selector
        selected_page = st.selectbox(
            "Choose a page",
            PAGES,
            key="minimal_page_selector"
        )
        
        st.markdown("---")
        st.write("This should be the ONLY sidebar")
    
    # Main content
    st.title("🔍 Minimal Double Sidebar Test")
    st.write(f"Selected page: {selected_page}")
    st.success("✅ If you see only ONE sidebar, the issue is in the complex app")
    st.error("❌ If you see TWO sidebars, the issue is fundamental")
    
    # Show HTML structure
    st.markdown("### HTML Debug")
    st.code("""
    Expected HTML structure:
    - Only ONE stSidebarNavLinkContainer
    - Only ONE sidebar with navigation elements
    - No duplicate st-emotion-cache containers for sidebar
    """)

if __name__ == "__main__":
    main()
