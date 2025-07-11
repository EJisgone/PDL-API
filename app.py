import streamlit as st
import requests

st.set_page_config(page_title="Candidate Search", page_icon="🔍")

st.title("🔍 Candidate Search App (via People Data Labs)")
st.write("Search professionals based on job title using People Data Labs API")

# Load API key from secrets
API_KEY = st.secrets["PDL"]["API_KEY"]

# Input fields
job_title = st.text_input("Enter Job Title", value="software engineer")
num_results = st.slider("Number of candidates", 1, 50, 5)

if st.button("Search"):
    with st.spinner("Searching candidates..."):
        headers = {
            "Content-Type": "application/json",
            "X-Api-Key": API_KEY
        }

        params = {
            "job_title": [job_title],
            "size": num_results
        }

        try:
            response = requests.post(
                "https://api.peopledatalabs.com/v5/person/search",
                headers=headers,
                json=params
            )
            data = response.json()

            if response.status_code != 200:
                st.error(f"API Error: {data.get('error', 'Unknown error')}")
            else:
                people = data.get("data", [])
                if not people:
                    st.warning("No results found.")
                else:
                    for person in people:
                        st.subheader(person.get("full_name", "Name not available"))
                        st.write(f"**Job Title:** {person.get('job_title', 'N/A')}")
                        st.write(f"**Email:** {person.get('email', 'N/A')}")
                        location = person.get("location", {}).get("name", "N/A")
                        st.write(f"**Location:** {location}")
                        company = person.get("experience", [{}])[0].get("company", "N/A")
                        st.write(f"**Company:** {company}")
                        st.divider()
        except Exception as e:
            st.error(f"Request failed: {str(e)}")
