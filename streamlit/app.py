import streamlit as st
from database.db_manager import DatabaseManager
from utils.patterns import process_patterns


# Initialize database manager
db_path    = r"/workspace/qgi\trojan 2.0\data\database\patterns_database.db"
db_manager = DatabaseManager(db_path)


# Streamlit page configuration
st.set_page_config(page_title = "Pattern Viewer", layout = "wide")


# Pagination settings
page_size   = 20
page_number = st.number_input("Page number", min_value = 1, value = 1, step = 1)
offset      = (page_number - 1) * page_size


# Fetch and process patterns
rows     = db_manager.fetch_patterns(offset = offset, limit = page_size)
patterns = process_patterns(rows)


# Display patterns
for pattern in patterns:
    st.write(pattern)  # You can format this as you like for better display


# Placeholder for pagination (if needed)
if len(patterns) == page_size:
    st.button("Next Page", on_click = lambda: page_number + 1)
