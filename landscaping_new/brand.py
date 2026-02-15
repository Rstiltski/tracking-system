"""
Brand Styling Module

Contains branding elements and global CSS for the landscaping management system.
Following the architecture rules, this provides consistent styling across the application.
"""
from __future__ import annotations

def get_global_css() -> str:
    """
    Get the global CSS styles for the application.
    
    Returns:
        String containing CSS styles
    """
    css = """
    /* Global Styles for Landscaping Management System */
    
    /* Brand Colors */
    :root {
        --primary-color: #2e7d32;        /* Forest Green */
        --primary-light: #60ad5e;        /* Light Green */
        --primary-dark: #005005;         /* Dark Green */
        --secondary-color: #ffb300;      /* Amber */
        --accent-color: #0288d1;         /* Light Blue */
        
        --background-color: #f5f7fa;
        --surface-color: #ffffff;
        --text-primary: #212121;
        --text-secondary: #757575;
        --border-color: #e0e0e0;
        --success-color: #4caf50;
        --warning-color: #ff9800;
        --error-color: #f44336;
        --info-color: #2196f3;
    }
    
    /* Apply brand colors to Streamlit elements */
    .stApp {
        background-color: var(--background-color);
    }
    
    /* Header styling */
    header {
        background-color: var(--primary-color) !important;
        border-bottom: 1px solid var(--border-color);
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-image: linear-gradient(180deg, var(--primary-color) 0%, var(--primary-light) 100%);
        color: white;
    }
    
    /* Button styling */
    button {
        border-radius: 4px !important;
        text-transform: none !important;
    }
    
    .stButton>button {
        background-color: var(--primary-color) !important;
        color: white !important;
        border: 1px solid var(--primary-color) !important;
    }
    
    .stButton>button:hover {
        background-color: var(--primary-dark) !important;
        border: 1px solid var(--primary-dark) !important;
    }
    
    /* Form elements */
    .stSelectbox>div>div, .stTextInput>div>div, .stTextArea>div>div, .stNumberInput>div>div {
        border: 1px solid var(--border-color) !important;
        border-radius: 4px !important;
    }
    
    /* Data frames */
    .stDataFrame {
        border: 1px solid var(--border-color) !important;
        border-radius: 4px !important;
    }
    
    /* Success, warning, error, info boxes */
    .stSuccess {
        border-color: var(--success-color) !important;
        background-color: rgba(76, 175, 80, 0.1) !important;
    }
    
    .stWarning {
        border-color: var(--warning-color) !important;
        background-color: rgba(255, 152, 0, 0.1) !important;
    }
    
    .stError {
        border-color: var(--error-color) !important;
        background-color: rgba(244, 67, 54, 0.1) !important;
    }
    
    .stInfo {
        border-color: var(--info-color) !important;
        background-color: rgba(33, 150, 243, 0.1) !important;
    }
    
    /* Custom card styling */
    .card {
        background: var(--surface-color);
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border: 1px solid var(--border-color);
    }
    
    /* Custom header styling */
    .app-header {
        background-color: var(--primary-color);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        text-align: center;
    }
    
    /* Responsive adjustments */
    @media (max-width: 768px) {
        .app-header h1 {
            font-size: 1.5rem;
        }
    }
    """
    return css

def get_company_info() -> dict:
    """
    Get company information for branding purposes.
    
    Returns:
        Dictionary containing company information
    """
    return {
        "name": "GreenThumb Landscaping",
        "tagline": "Transforming Spaces, Naturally",
        "contact_email": "info@greenthumblandscape.com",
        "phone": "(555) 123-LAWN",
        "address": "123 Garden Way, Landscape City, LC 12345",
        "logo_url": "/assets/logo.png"  # Placeholder
    }

def get_page_title(page_name: str) -> str:
    """
    Get a branded page title.
    
    Args:
        page_name: Name of the page
        
    Returns:
        Formatted page title with branding
    """
    company_info = get_company_info()
    return f"{page_name} - {company_info['name']}"

def get_footer_text() -> str:
    """
    Get branded footer text.
    
    Returns:
        Footer text with copyright and contact information
    """
    company_info = get_company_info()
    year = __import__('datetime').datetime.now().year
    return f"© {year} {company_info['name']}. {company_info['tagline']}. Contact: {company_info['contact_email']}"