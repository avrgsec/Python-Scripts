import feedparser
import requests
import time
from dateutil import parser
import sys
import datetime
import json

# --- Constants & Classes ---
class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    GREEN = '\033[92m'
    BLUE = '\033[94m'

# --- YOUR FULL AND CORRECT SOURCES LIST ---
SOURCES = [
    {"name": "Krebs on Security", "url": "https://krebsonsecurity.com/feed/", "type": "rss"},
    {"name": "The Hacker News", "url": "https://feeds.feedburner.com/TheHackersNews", "type": "rss"}, # Corrected URL
    {"name": "Greynoise Intelligence", "url": "https://www.greynoise.io/blog/rss.xml", "type": "rss"},
    {"name": "Google Threat Intelligence", "url": "https://feeds.feedburner.com/threatintelligence/pvexyqv7v0v", "type": "rss"},
    {"name": "CISA KEV Catalog", "url": "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json", "type": "json_cisa"}
]

motd_art = r"""
   / \   \ \   / /  |  _ \   / ___|
  / _ \   \ \_/ /   | |_) | | |  _
 / ___ \   \   /    |  _ <  | |_| |
/_/   \_\   \_/     |_| \_\  \____|

"""

# Function to make the text print to screen with a delay of 0.01 for epic-ness
def slow_text(text, delay=0.01):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()

# Fetches content from a URL using custom UA to avoid errors. Returns raw text for later parsing, otherwise return error dict
def fetch_url_content(url):
    try:
        browser_user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        headers = {'User-Agent': browser_user_agent}
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            return response.text
        else:
            return {"error": f"Failed with status code {response.status_code}"}
    except requests.exceptions.RequestException as e:
        return {"error": f"A network connection error occurred: {e}"}

# Takes a single entry from feedparser object (XML) and return formatted report string
def process_rss_entry(entry):
    report_line = ""
    try:
        title = entry.title
        link = entry.link
        try:
            messy_date = entry.published
            parsed_date = parser.parse(messy_date)
            clean_date = parsed_date.strftime("%Y-%m-%d")
        except AttributeError:
            clean_date = "No date provided"
        report_line += f"\n{Colors.BLUE}Published:{Colors.RESET} {clean_date}\n"
        report_line += f"{Colors.BLUE}Title:{Colors.RESET} {Colors.BOLD}{title}{Colors.RESET}\n"
        report_line += f"{Colors.BLUE}Link:{Colors.RESET} {link}\n"
    except AttributeError:
        report_line += "Could not parse this RSS entry.\n"
    return report_line

# Takes a single vulnerability dictionary from CISA Json and return a formatted string
def process_cisa_vulnerability(vulnerability):
    report_line = ""
    try:
        cve_id = vulnerability.get('cveID', 'N/A')
        name = vulnerability.get('vulnerabilityName', 'N/A')
        date_added = vulnerability.get('dateAdded', 'N/A')
        report_line += f"\n{Colors.BLUE}Date Added:{Colors.RESET} {date_added}\n"
        report_line += f"{Colors.BLUE}CVE ID:{Colors.RESET} {Colors.BOLD}{cve_id}{Colors.RESET}\n"
        report_line += f"{Colors.BLUE}Name:{Colors.RESET} {name}\n"
    except Exception:
        report_line += "Could not parse this CISA vulnerability entry.\n"
    return report_line

# Prints the MOTD and Welcome Message
print(f"{Colors.GREEN}{motd_art}{Colors.RESET}")
slow_text(f"{Colors.BOLD}Welcome back, Chris. Here is your daily digest!{Colors.RESET}")
print("-------------------------------------------")
now = datetime.datetime.now()
formatted_time = now.strftime("%A, %B %d, %Y - %I:%M %p")
slow_text(f"{Colors.BLUE}Login time: {formatted_time}{Colors.RESET}")
print("-------------------------------------------")
time.sleep(1)

# Fetch data and build report string
final_report_string = ""
for source in SOURCES:
    name = source["name"]
    url = source["url"]
    source_type = source["type"]

    final_report_string += f"\n{Colors.GREEN}{Colors.BOLD}--- Latest from {name} ---{Colors.RESET}\n"
    
    content = fetch_url_content(url)
    
    if isinstance(content, dict) and 'error' in content:
        # Handle errors from the fetcher
        final_report_string += f"Failed to fetch content from the source: {content['error']}\n"
        continue

    if content:
        if source_type == "rss":
            feed = feedparser.parse(content)
            if feed and feed.entries:
                for entry in feed.entries[:3]:
                    # Delegate formatting to RSS func
                    final_report_string += process_rss_entry(entry)
            else:
                final_report_string += "Could not parse the RSS content.\n"

        elif source_type == "json_cisa":
            try:
                data = json.loads(content)
                vulnerabilities = data.get('vulnerabilities', [])
                if vulnerabilities:
                    for vuln in vulnerabilities[:10]:
                        # Delegate formatting to the CISA func
                        final_report_string += process_cisa_vulnerability(vuln)
                else:
                    final_report_string += "No vulnerabilities found in the data.\n"
            except json.JSONDecodeError:
                final_report_string += "Failed to parse JSON content from the source.\n"
    else:
        final_report_string += "Failed to fetch content from the source (Empty Response).\n"

# Present the Final Report
slow_text(final_report_string)

