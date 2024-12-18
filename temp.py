# Fetch Confluence page content
def fetch_confluence_page():
    api_url = f"{confluence_url}/rest/api/content/{page_id}?expand=body.storage"
    response = requests.get(api_url, auth=HTTPBasicAuth(username, password))
    
    if response.status_code == 200:
        data = response.json()
        page_content = data.get("body", {}).get("storage", {}).get("value", "")
        return page_content
    else:
        print(f"Failed to fetch Confluence page. Status code: {response.status_code}")
        print(f"Response: {response.text}")
        return None

# Fetch Jira data using JQL
def fetch_jira_data(jql):
    api_url = f"{jira_url}/rest/api/2/search"
    params = {"jql": jql}
    response = requests.get(api_url, auth=HTTPBasicAuth(username, password), params=params)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch Jira data. Status code: {response.status_code}")
        print(f"Response: {response.text}")
        return None

# Main function
def main():
    # Fetch and parse Confluence page content
    content = fetch_confluence_page()
    if content:
        # Use BeautifulSoup to parse HTML and find Jira macros
        soup = BeautifulSoup(content, "html.parser")
        jira_macros = soup.find_all("ac:structured-macro", {"ac:name": "jira"})
        
        for i, macro in enumerate(jira_macros, start=1):
            jql = macro.find("ac:parameter", {"ac:name": "jql"}).text
            print(f"Jira Macro {i}: JQL Query: {jql}")
            
            # Fetch data from Jira
            jira_data = fetch_jira_data(jql)
            if jira_data:
                print(f"Jira Data for Macro {i}: {jira_data}")
            else:
                print(f"No data retrieved for Jira Macro {i}.")

if __name__ == "__main__":
    main()
