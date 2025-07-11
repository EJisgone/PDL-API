import streamlit as st
import requests

st.set_page_config(page_title="People Data Search", page_icon="🔍", layout="centered")

# ---- Custom Styling ----
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
    a {
        color: #2C5AFF;
        text-decoration: none;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🔍 People Data Search")
st.caption("Find professionals globally using structured job role data — powered by People Data Labs.")

# --- API Key
API_KEY = st.secrets["PDL"]["API_KEY"]

# --- Valid Roles
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

# --- Search
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
                st.warning("⚠️ No candidates found.")
            else:
                st.success(f"✅ Found {len(people)} candidate(s)")

                for person in people:
                    name = person.get("full_name", "N/A")
                    job = person.get("job_title", "N/A")
                    email = person.get("email", "N/A")
                    loc = person.get("location", {}).get("name", "N/A")

                    # Company extraction
                    exp = person.get("experience", [])
                    company_data = exp[0].get("company", {}) if exp else {}
                    get_safe = lambda d, k: d.get(k, "N/A")
                    get_nested = lambda d, path: get_safe(d.get(path[0], {}) if isinstance(d, dict) else {}, path[1]) if len(path) == 2 else "N/A"

                    company_name = get_safe(company_data, "name")
                    company_size = get_safe(company_data, "size")
                    company_founded = get_safe(company_data, "founded")
                    company_industry = get_safe(company_data, "industry")
                    company_website = get_safe(company_data, "website")
                    company_linkedin = get_safe(company_data, "linkedin_url")
                    company_facebook = get_safe(company_data, "facebook_url")
                    company_twitter = get_safe(company_data, "twitter_url")

                    # Location subfields
                    location = company_data.get("location", {})
                    loc_name = get_safe(location, "name")
                    street = get_safe(location, "street_address")
                    line2 = get_safe(location, "address_line_2")
                    postal = get_safe(location, "postal_code")
                    city = get_safe(location, "locality")
                    region = get_safe(location, "region")
                    country = get_safe(location, "country")

                    # Render profile card
                    st.markdown(f"""
                    <div class="candidate-card">
                        <div class="candidate-header">{name}</div>
                        <div><span class="field-label">Role:</span> {job}</div>
                        <div><span class="field-label">Email:</span> {email}</div>
                        <div><span class="field-label">Location:</span> {loc}</div>

                        <div style="margin-top: 1rem;"><span class="field-label">🏢 Company Details</span></div>
                        <div><span class="field-label">Name:</span> {company_name}</div>
                        <div><span class="field-label">Industry:</span> {company_industry}</div>
                        <div><span class="field-label">Size:</span> {company_size}</div>
                        <div><span class="field-label">Founded:</span> {company_founded}</div>
                        <div><span class="field-label">Website:</span> <a href="https://{company_website}" target="_blank">{company_website}</a></div>
                        <div><span class="field-label">LinkedIn:</span> <a href="https://{company_linkedin}" target="_blank">{company_linkedin}</a></div>
                        <div><span class="field-label">Facebook:</span> <a href="https://{company_facebook}" target="_blank">{company_facebook}</a></div>
                        <div><span class="field-label">Twitter:</span> <a href="https://{company_twitter}" target="_blank">{company_twitter}</a></div>

                        <div style="margin-top: 0.5rem;"><span class="field-label">📍 Address</span></div>
                        <div><span class="field-label">Street:</span> {street}, {line2}</div>
                        <div><span class="field-label">City:</span> {city}</div>
                        <div><span class="field-label">Region:</span> {region}</div>
                        <div><span class="field-label">Country:</span> {country}</div>
                        <div><span class="field-label">Postal Code:</span> {postal}</div>
                        <div><span class="field-label">Geo:</span> {get_safe(location, "geo")}</div>
                    </div>
                    """, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"🚨 Request failed: {str(e)}")
