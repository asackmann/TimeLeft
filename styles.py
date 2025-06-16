# styles.py
# This module contains CSS styles for the Streamlit app.

def get_styles():
    return """
    <style>
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            max-width: 1200px;
            margin: auto;
        }
        .kpi-card {
            background: #1e1e1e; /* Dark background */
            border-radius: 12px;
            padding: 1.5rem 1rem;
            margin-bottom: 1rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.3);
            text-align: center;
            color: #ffffff; /* Light text for contrast */
        }
        .insight-card {
            background: #2a2a2a; /* Slightly lighter dark */
            border-radius: 10px;
            padding: 1rem 1.5rem;
            margin-bottom: 0.7rem;
            box-shadow: 0 1px 4px rgba(0,0,0,0.3);
            font-size: 1.1rem;
            color: #ffffff;
        }
    </style>
    """
