import streamlit as st
import requests

st.set_page_config(page_title="Candidate Search", page_icon="🔍")

st.title("🔍 Candidate Search App")
st.write("Search professionals based on normalized job roles using the People Data Labs API")

# Load your API key from secrets
API_KEY = st.secrets["PDL"]["API_KEY"]

# Valid job_title_role values as per PDL docs
VALID_ROLES = [
    "advisory", "analyst", "creative", "education", "engineering", "finance", "fulfillment",
    "health", "hospitality", "human_resources", "legal", "manufacturing", "marketing",
    "operations", "partnerships", "product", "professional_service", "public_service",
    "research", "sales", "sales_engineering", "support", "trade", "unemployed"
]

# UI: Role selector and number of results
selected_role = st.selectbox("Select a role", VALID_ROLES, index=VALID_ROLES.index("engineering"))
num_results = st.slider("Number of candidates to return", 1, 50, 5)

if st.button("Search"):
    st.info(f"Searching for candidates in the role: **{selected_role}**...")

    # Elasticsearch-compatible payload
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
            st.error(f"API Error: {result.get('message', result)}")
        else:
            people = result.get("data", [])
            if not people:
                st.warning("No candidates found for this role.")
            else:
                for person in people:
                    st.subheader(person.get("full_name", "No Name Provided"))
                    st.write(f"**Job Title:** {person.get('job_title', 'N/A')}")
                    location = person.get("location", {}).get("name", "N/A")
                    st.write(f"**Location:** {location}")
                    email = person.get("email", "N/A")
                    st.write(f"**Email:** {email}")
                    experience = person.get("experience", [])
                    if experience:
                        st.write(f"**Company:** {experience[0].get('company', 'N/A')}")
                    st.divider()
    except Exception as e:
        st.error(f"Request failed: {str(e)}")
