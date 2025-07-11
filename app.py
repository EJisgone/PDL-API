import streamlit as st
import requests

st.set_page_config(page_title="People Data Search", page_icon="🔍", layout="centered")

# ---- Custom PDL-Themed CSS Styling ----
st.markdown("""
    <style>
    body {
        font-family: 'Segoe UI', sans-serif;
    }
    .reportview-container {
        padding: 2rem;
    }
    .candidate-card {
        background-color: #ffffff;
        border: 1px solid #e1e3e8;
        border-radius: 14px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 8px rgba(0,0,0,0.04);
        color: #1a1a1a;
    }
    .candidate-header {
        font-size: 1.3rem;
        font-weight: 600;
        color: #16294C;
        margin-bottom: 0.5rem;
    }
    .field-label {
        font-weight: 600;
        color: #555;
    }
    .stButton>button {
        background-color: #2C5AFF;
        color: #ffffff;
        border: none;
        padding: 0.6rem 1.2rem;
        border-radius: 8px;
        font-size: 1rem;
        margin-top: 0.5rem;
    }
    .stButton>button:hover {
        background-color: #244bcc;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🔍 People Data Search")
st.caption("Find professionals across the globe based on structured job role data. Powered by People Data Labs.")

# --- Secure API Key
API_KEY = st.secrets["PDL"]["API_KEY"]

# --- Canonical job_title_role values
VALID_ROLES = [
    "advisory", "analyst", "creative", "education", "engineering", "finance", "fulfillment",
    "health", "hospitality", "human_resources", "legal", "manufacturing", "marketing",
    "operations", "partnerships", "product", "professional_service", "public_service",
    "research", "sales", "sales_engineering", "support", "trade", "unemployed"
]

# --- Sidebar Filters
with st.sidebar:
    st.header("🔧 Filters")
    selected_role = st.selectbox("Role", VALID_ROLES, index=VALID_ROLES.index("engineering"))
    num_results = st.slider("Results", 1, 50, 5)
    search_btn = st.button("🔍 Search Candidates")

# --- Perform API Call
if search_btn:
    st.info(f"🔎 Searching for `{selected_role}` candidates...")

    payload = {
        "query": {
            "bool": {
                "must": [
                    {"term": {"job_title_role": selected_role}}
                ]
            }
        },
        "size": num_results
    }

    headers = {
        "Content-Type": "application/json",
        "X-Api-Key": API_KEY
    }

    try:
        response = requests.post(
            "https://api.peopledatalabs.com/v5/person/search",
            headers=headers,
            json=payload
        )
        result = response.json()

        if response.status_code != 200:
            st.error(f"❌ API Error: {result.get('message', result)}")
        else:
            people = result.get("data", [])
            if not people:
                st.warning("⚠️ No candidates found for this role.")
            else:
                st.success(f"✅ Found {len(people)} candidate(s)")

                for person in people:
                    name = person.get("full_name", "N/A")
                    job = person.get("job_title", "N/A")
                    email = person.get("email", "N/A")
                    loc = person.get("location", {}).get("name", "N/A")
                    exp = person.get("experience", [])
                    company = exp[0].get("company", "N/A") if exp else "N/A"

                    st.markdown(f"""
                    <div class="candidate-card">
                        <div class="candidate-header">{name}</div>
                        <div><span class="field-label">Role:</span> {job}</div>
                        <div><span class="field-label">Company:</span> {company}</div>
                        <div><span class="field-label">Location:</span> {loc}</div>
                        <div><span class="field-label">Email:</span> {email}</div>
                    </div>
                    """, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"🚨 Request failed: {str(e)}")
