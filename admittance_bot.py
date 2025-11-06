import requests
from bs4 import BeautifulSoup
from difflib import get_close_matches
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from urllib.parse import quote


admittance_model = ChatOllama(model="llama3.2")

# dictionary of faculties
faculty_links = {
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

programme_urls = {
    "licenta": "https://admitere.unitbv.ro/informatii-licenta/{faculty_slug}/conditii-de-admitere.html",
    "master": "https://admitere.unitbv.ro/informatii-masterat/{faculty_slug}/conditii-de-admitere.html"
}

# get the detect_faculty method be assisted by AI
# 1. look at the iser input "tell me about admission at the faculty of economical sciences"
# 2. detect the faculty in the user input
# let the ai look at the faculty_links

"""
deci, modific link-urile sa fie gen .unitbv.ro/ro/" 
iar dupa, ma uit la elementul cu clasa "moduleTitle  heading-style-2 visible visible-first" 
si la child elements la inner text si parse together
ca sa obtin slug-ul de facultate
"""
# get the link and parse "" to the link and use it for the next step


def detect_faculty(user_input: str):
    # Detect the most probable faculty mentioned in user_input using Ollama
    # and return the corresponding name and link
    prompt = f"""
    The following is a list of faculties:

    {', '.join(faculty_links.keys())}

    Based on the user's input: "{user_input}"
    Return only the most probable faculty name from the list above.
    """

    try:
        # Call Ollama model
        response = ollama.generate(
            model="qwen",
            prompt=prompt,
        )

        # Extract text result
        ai_text = response.get("response", "").strip()

        # Try to find the best match using fuzzy string matching
        matches = get_close_matches(ai_text, faculty_links.keys(), n=1, cutoff=0.4)

        if matches:
            best_match = matches[0]
            return {best_match: faculty_links[best_match]}
        else:
            # Try a fallback: match from user input directly
            fallback = get_close_matches(user_input, faculty_links.keys(), n=1, cutoff=0.4)
            if fallback:
                best_match = fallback[0]
                return {best_match: faculty_links[best_match]}
            return {"error": "No matching faculty found."}

    except ollama.ResponseError as e:
        return {"error": f"Ollama Error: {e.error}"}
    except Exception as e:
        return {"error": f"Unexpected error: {e}"}

# detect_faculty("how can I get admitted into faculty of economical sciences?")
# OUTPUT:
# {'Faculty of Economics and Business Administration': 'https://econ.unitbv.ro/ro/'}

def get_faculty_name(faculty_url):
    response = requests.get(faculty_url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')

    # Use CSS selector for flexible class matching
    element = soup.select_one('h2.moduleTitle.heading-style-2.visible.visible-first')

    if element:
        combined_text = ' '.join(span.get_text(strip=True) for span in element.find_all('span'))
        return combined_text.strip()
    return None

def slugify_faculty_name(name: str):
    return name.lower().replace(" ", "-").replace("ș", "s").replace("ț", "t").replace("ă", "a")

def detect_programme(user_input: str):
    if "master" in user_input.lower():
        return "master"
    return "licenta"

def get_html(url: str):
    res = requests.get(url)
    res.raise_for_status()
    return BeautifulSoup(res.text, "html.parser")

def parse_case_1(soup):
    headings = soup.select(".accordion .heading-style-4.visible.visible-first")
    collapse_section = soup.select_one("#collapse_146_16")
    text_parts = []
    for h in headings:
        text_parts.append(h.get_text(strip=True))
    if collapse_section:
        for p in collapse_section.select("p"):
            text_parts.append(p.get_text(strip=True))
    return "\n".join(text_parts)

def parse_case_2(soup):
    paragraphs = soup.select(".item_fulltext > p")
    return "\n".join(p.get_text(strip=True) for p in paragraphs)

def summarize_text(text: str):
    prompt = f"Summarize this admission information clearly and concisely:\n\n{text}"
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
    )
    return completion.choices[0].message.content

# ---------------------------------------------------------------------------------------
""" 
def university_agent(user_input: str):
    faculty_dict = detect_faculty(user_input)
    faculty_url = (list(faculty_dict.values()))[0]
    faculty_slug = slugify_faculty_name(get_faculty_name(faculty_url))
    detect_programme(user_input)

    url = programme_urls[programme].format(faculty_slug=faculty_slug)

    soup = get_html(url)
    item_fulltext = soup.select_one(".item_fulltext")

    if item_fulltext.select_one(".accordion"):
        extracted_text = parse_case_1(item_fulltext)
    else:
        extracted_text = parse_case_2(item_fulltext)

    summary = summarize_text(extracted_text)
    return summary
#----------------------------------------------------------------
"""

# In admittance_bot.py, replace the current university_agent function with this:

# --- (Existing utility functions remain above) ---

def admittance_agent_wrapper(user_input: str, admittance_agent_chain):
    """
    1. Detects faculty and program (licenta/master) from user input.
    2. Scrapes the relevant admission criteria page.
    3. Extracts the text from the criteria page.
    4. Invokes the LangChain 'admittance_agent_chain' with the user input
       and the extracted text as context.
    """
    # --- 1. Detect Faculty and Program ---
    faculty_dict = detect_faculty(user_input)
    # Check for error in faculty detection
    if "error" in faculty_dict:
        return faculty_dict["error"]
        
    faculty_url = (list(faculty_dict.values()))[0]
    
    # --- 2. Get Faculty Slug and Program Type ---
    # NOTE: get_faculty_name is needed for slug, but it scrapes the faculty's homepage, not the admission page.
    # If get_faculty_name fails, the script will raise an error (good practice to handle it).
    try:
        faculty_name = get_faculty_name(faculty_url)
        if not faculty_name:
            return "Could not determine the full faculty name for slug generation."
    except requests.RequestException as e:
        return f"Error accessing faculty URL for name extraction: {e}"

    faculty_slug = slugify_faculty_name(faculty_name)
    programme = detect_programme(user_input) # "licenta" or "master"

    # --- 3. Construct URL and Scrape ---
    # URL will look like: https://admitere.unitbv.ro/informatii-licenta/facultatea-de-stiinte-economice/conditii-de-
    try:
        url = programme_urls[programme].format(faculty_slug=faculty_slug)
        soup = get_html(url)
    except requests.RequestException as e:
        return f"Error accessing admission URL ({url}): {e}. The faculty or program might not be available or the URL format has changed."
    except KeyError:
        return f"Unknown program type: {programme}"

    # --- 4. Extract Text ---
    item_fulltext = soup.select_one(".item_fulltext")
    if not item_fulltext:
         return "Could not find the main content on the admission page."

    if item_fulltext.select_one(".accordion"):
        extracted_text = parse_case_1(item_fulltext)
    else:
        extracted_text = parse_case_2(item_fulltext)
        
    if not extracted_text:
        return "Could not extract admission criteria text from the page."

    # --- 5. Invoke LangChain Agent ---
    # The LangChain agent expects the *admission criteria document text* to be
    # part of the prompt's context, as defined in your template's instructions.
    
    # We will pass the full extracted text as a 'document' or 'context'
    # and the original user input as the 'prompt'.
    # Your prompt template only takes {prompt}, so we must modify the template slightly 
    # to include the document text for the LLM to work with.

    # TEMPORARY: For your current `admittance_agent` structure (which only takes {prompt}), 
    # we must inject the document into the prompt string.
    # The agent will treat the combined string as the {prompt} variable.
    
    # Recommended approach (needs *template modification*):
    # final_prompt = {"prompt": user_input, "document": extracted_text}
    
    # Workaround for your *current* template:
    final_prompt_for_llm = f"DOCUMENT (Admission Criteria):\n\n---\n{extracted_text}\n---\n\nUSER QUESTION: {user_input}"
    
    # The agent *always* returns a String via StrOutputParser
    summary = admittance_agent_chain.invoke({
        "prompt": final_prompt_for_llm # Pass the prepared context
    })
    
    return summary

#----------------------------------------------------------------