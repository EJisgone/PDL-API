import streamlit as st
import requests

st.set_page_config(page_title="Candidate Search", page_icon="🔍")

st.title("🔍 Candidate Search App")
st.write("Search professionals based on job title using People Data Labs API")

# Load your API key securely from Streamlit secrets
API_KEY = st.secrets["PDL"]["API_KEY"]

# Input fields
job_title = st.text_input("Enter Job Title", value="developer")
num_results = st.slider("Number of candidates to return", 1, 50, 5)

if st.button("Search"):
    st.info("Sending request to People Data Labs API...")
    
    # Proper Elasticsearch query format
    payload = {
        "query": {
            "bool": {
                "must": [
                    {"term": {"job_title_role": job_title.lower()}}  # Role must be lowercase term
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
                st.warning("No candidates found.")
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
