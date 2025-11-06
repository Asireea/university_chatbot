import requests
from bs4 import BeautifulSoup
from difflib import get_close_matches
from urllib.parse import quote
import re

# --- Configuration (Faculty Links) ---

# Dictionary of faculties and their main URLs
FACULTY_LINKS = {
    "Faculty of Product Design and Environment": "https://dpm.unitbv.ro/ro/",
    "Faculty of Electrical Engineering and Computer Science": "https://iesc.unitbv.ro/ro/",
    "Faculty of Furniture Design and Wood Engineering": "https://dmil.unitbv.ro/ro/",
    "Faculty of Mechanical Engineering": "https://mecanica.unitbv.ro/ro/",
    "Faculty of Technology Engineering and Industrial Management": "https://itmi.unitbv.ro/ro/",
    "Faculty of Forestry": "https://silvic.unitbv.ro/ro/",
    "Faculty of Materials Science and Engineering": "https://sim.unitbv.ro/ro/",
    "Faculty of Law": "https://drept.unitbv.ro/ro/ro/",
    "Faculty of Physical Education and Mountain Sports": "https://sport.unitbv.ro/ro/",
    "Faculty of Letters": "https://litere.unitbv.ro/ro/",
    "Faculty of Mathematics and Computer Science": "https://mateinfo.unitbv.ro/ro/",
    "Faculty of Medicine": "https://medicina.unitbv.ro/ro/",
    "Faculty of Music": "https://muzica.unitbv.ro/ro/",
    "Faculty of Psychology and Educational Sciences": "https://psihoedu.unitbv.ro/ro/",
    "Faculty of Sociology and Communication": "https://socio.unitbv.ro/ro/",
    "Faculty of Economics and Business Administration": "https://econ.unitbv.ro/ro/",
    "Faculty of Food and Tourism": "https://at.unitbv.ro/ro/",
    "Faculty of Construction": "https://constructii.unitbv.ro/ro/",
}

# Base URLs for admission pages
PROGRAMME_URLS = {
    "licenta": "https://admitere.unitbv.ro/informatii-licenta/{faculty_slug}/conditii-de-admitere.html",
    "master": "https://admitere.unitbv.ro/informatii-masterat/{faculty_slug}/conditii-de-admitere.html"
}

FACULTY_ALIASES = {
    "economical sciences": "Faculty of Economics and Business Administration",
    "economic sciences": "Faculty of Economics and Business Administration",
    "economy": "Faculty of Economics and Business Administration",
    "informatics": "Faculty of Mathematics and Computer Science",
    "law school": "Faculty of Law",
    "psychology": "Faculty of Psychology and Educational Sciences",
    "medicine": "Faculty of Medicine",
}

FACULTY_SLUGS = {
    "Faculty of Economics and Business Administration": "facultatea-de-stiinte-economice-si-administrarea-afacerilor",
    "Faculty of Medicine": "facultatea-de-medicina",
    "Faculty of Law": "facultatea-de-drept",
    "Faculty of Mathematics and Computer Science": "facultatea-de-matematica-si-informatica",
    "Faculty of Psychology and Educational Sciences": "facultatea-de-psihologie-si-stiintele-educatiei",
    "Faculty of Mechanical Engineering": "facultatea-de-inginerie-mecanica",
    "Faculty of Product Design and Environment": "facultatea-de-design-de-produs-si-mediu",
    "Faculty of Technology Engineering and Industrial Management": "facultatea-de-inginerie-tehnologica-si-management-industrial",
    # TODO: add more as needed
}

# --- Utility Functions ---

def get_html(url: str):
    """Fetches the HTML content of a URL and returns a BeautifulSoup object."""
    res = requests.get(url, timeout=10)
    res.raise_for_status()
    return BeautifulSoup(res.text, "html.parser")

def slugify_faculty_name(name: str):
    """Converts a faculty name into a URL-friendly slug."""
    # Transliteration for Romanian characters
    name = name.lower().replace(" ", "-").replace("ș", "s").replace("ț", "t").replace("ă", "a").replace("î", "i").replace("â", "a")
    # Remove non-alphanumeric characters except hyphens
    name = re.sub(r'[^\w\-]', '', name)
    return name

# --- Detection Functions ---

def detect_faculty(user_input: str) -> dict:
    """
    Improved faculty detection using flexible fuzzy matching.
    Returns: {'Faculty Name': 'url'} or {'error': 'message'}
    """
    text = user_input.lower()

    # Check aliases first
    for alias, faculty_name in FACULTY_ALIASES.items():
        if alias in user_input.lower():
            return {faculty_name: FACULTY_LINKS[faculty_name]}

    # Try to find any faculty keyword within the input
    for name, url in FACULTY_LINKS.items():
        if any(word in text for word in name.lower().split()):
            # Direct substring match wins immediately
            if re.search(rf"\b{name.lower().split()[1]}\b", text):
                return {name: url}

    # Fuzzy fallback: compare shorter faculty labels
    simplified_faculties = {re.sub(r'faculty of ', '', k.lower()): k for k in FACULTY_LINKS.keys()}
    simplified_input = re.sub(r'faculty of ', '', text)

    best_match = get_close_matches(simplified_input, simplified_faculties.keys(), n=1, cutoff=0.3)
    if best_match:
        matched_name = simplified_faculties[best_match[0]]
        return {matched_name: FACULTY_LINKS[matched_name]}

    return {"error": "No matching faculty found."}


def get_faculty_name(faculty_url):
    """
    Scrapes the faculty's main page to find the official title used for the slug.
    """
    try:
        soup = get_html(faculty_url)
    except requests.RequestException:
        return None

    # Use CSS selector for flexible class matching
    # Targeting the main title element on the faculty's page
    element = soup.select_one('h2.moduleTitle.heading-style-2.visible.visible-first')

    if element:
        # Concatenate text from all spans within the title
        combined_text = ' '.join(span.get_text(strip=True) for span in element.find_all('span'))
        return combined_text.strip()
        
    # Fallback to the key name if scraping the page title fails
    # NOTE: This fallback is less reliable for accurate slug generation
    return None

def detect_programme(user_input: str) -> str:
    """Detects if the user is asking about 'master' or defaults to 'licenta'."""
    if "master" in user_input.lower() or "masterat" in user_input.lower():
        return "master"
    return "licenta"

# --- Parsing Functions ---

def parse_case_1(soup):
    """Parses admission criteria using accordion structure."""
    headings = soup.select(".accordion .heading-style-4.visible.visible-first")
    # Specific ID selector might be too fragile. Use a more general approach if possible,
    # but based on the original code, we rely on finding the main text under a specific ID
    # or finding a common collapsible section.
    
    # Targeting the first collapsible text section within the item_fulltext
    collapse_section = soup.select_one(".item_fulltext .collapse.in") or soup.select_one(".item_fulltext .collapse")
    
    text_parts = []
    for h in headings:
        text_parts.append(f"HEADER: {h.get_text(strip=True)}")
        
    if collapse_section:
        for p in collapse_section.select("p, ul, ol, div"): # Include more tags for thorough extraction
            text_parts.append(p.get_text(strip=True))
            
    return "\n".join(filter(None, text_parts)) # Filter empty strings


def parse_case_2(soup):
    """Parses admission criteria using simple paragraph structure."""
    # Find all top-level paragraphs within the main content
    paragraphs = soup.select(".item_fulltext > p, .item_fulltext > ul, .item_fulltext > ol, .item_fulltext > div")
    return "\n".join(p.get_text(strip=True) for p in paragraphs)

# --- Main Orchestration Function ---

def get_admission_criteria_text(user_input: str) -> dict:
    """
    Orchestrates the scraping process to fetch raw admission criteria text.
    Returns: {'text': '...', 'metadata': {...}} or {'error': '...'}
    """

    # 1. Detection
    faculty_dict = detect_faculty(user_input)
    if "error" in faculty_dict:
        return faculty_dict

    faculty_name = list(faculty_dict.keys())[0]
    faculty_url_base = faculty_dict[faculty_name]
    programme = detect_programme(user_input)

    # 2. Determine faculty slug
    try:
        # ✅ Check if we already have a hardcoded correct slug
        if faculty_name in FACULTY_SLUGS:
            faculty_slug = FACULTY_SLUGS[faculty_name]
        else:
            # Try to scrape the faculty homepage for its proper Romanian name
            name_for_slug = get_faculty_name(faculty_url_base)
            if not name_for_slug:
                name_for_slug = faculty_name  # fallback to dictionary key
            faculty_slug = slugify_faculty_name(name_for_slug)

        # Construct the admission URL
        url = PROGRAMME_URLS[programme].format(faculty_slug=faculty_slug)

    except Exception as e:
        return {"error": f"Error during URL construction: {e}"}

    # 3. Scraping and Extraction
    try:
        soup = get_html(url)

        # Sometimes 404 pages still render HTML, so detect that
        if "404" in soup.text or "Not Found" in soup.text:
            return {"error": f"The page at {url} was not found (404). Check if the slug '{faculty_slug}' is correct."}

        # More flexible content selector
        item_fulltext = (
            soup.select_one(".item_fulltext")
            or soup.select_one(".blog-content")
            or soup.select_one("article")
            or soup.select_one(".content")
        )

        if not item_fulltext:
            return {"error": f"Could not find admission details at {url}. The page structure may have changed, or the slug '{faculty_slug}' is incorrect for the '{programme}' program."}

        # Determine the parsing case
        if item_fulltext.select_one(".accordion"):
            extracted_text = parse_case_1(item_fulltext)
        else:
            extracted_text = parse_case_2(item_fulltext)

        if not extracted_text:
            return {"error": f"Scraping succeeded, but no text was extracted from the main content section for {faculty_name} ({programme})."}

        return {
            "text": extracted_text,
            "metadata": {
                "faculty": faculty_name,
                "program": programme,
                "source_url": url,
            },
        }

    except requests.RequestException as e:
        return {"error": f"Failed to access the admission page at {url}. Error: {e}"}
    except Exception as e:
        return {"error": f"An unexpected error occurred during parsing: {e}"}


#----------------------------------------------------------------