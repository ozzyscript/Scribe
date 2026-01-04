
from phi.agent.agent import Agent
from phi.model.groq.groq import Groq
from phi.tools.duckduckgo import DuckDuckGo
from phi.tools.googlesearch import GoogleSearch
from phi.tools.wikipedia import WikipediaTools
from dotenv import load_dotenv
import datetime, time
import sys
load_dotenv()
import json


# Add date/time/title for tracking
now = datetime.datetime.now()
title = f"Scribed_{now.strftime('%Y-%m-%d_%H-%M')}"


NOTES_FILE_PATH = "/home/ozirx/OZiRX/Tech/PRJs/Scribe/thinking.txt"

# Schema validation to prevent silent corruption 
REQUIRED_KEYS = {
    "Assumptions",
    "Questions",
    "Self-Answers",
    "Verified Answers",
    "Resources",
    "Summary",
    "Recommendations",
    "Date",
    "Title",
    "Tools",
}

def load_file_content(file_path):
    try:
        with open(file_path, "r") as f:
            content = f.read().strip()
            if len(content) < 20:
                print(f"The file doesn't have enough content({len(content)} chars). Please add more notes.")
                sys.exit(1)
            return content

    except FileNotFoundError:
        print(f"No notes found. Please create '{file_path}' with some content.")
    except Exception as e:
        raise RuntimeError(f"Unexpected error {e}") from e




file_content = load_file_content(NOTES_FILE_PATH)





PROMPT = f"""
You are an advanced AI organizing agent with access to DuckDuckGo, Google Search, and Wikipedia.

Your role:
- Analyze brainstorm notes
- Extract structure
- Verify questions using web tools
- Return a clean, machine-readable JSON response

TASKS:
1. Analyze the provided notes as plain text.
2. Extract:
   - Questions
   - Ideas
   - Self-answers (if present)
3. For each extracted question:
   - Use web tools ONLY when external verification is needed
   - Prefer Wikipedia for factual background
   - Prefer search engines for comparisons, jobs, trends, or up-to-date info
4. Synthesize verified answers based on reliable sources.
5. Provide concise recommendations and resources.

INVALID CONTENT HANDLING:
- If the notes are empty, meaningless, or non-textual, return ONLY this JSON object and stop:

  "error": "Invalid or insufficient content"


OUTPUT FORMAT (MANDATORY):
- Return ONE valid JSON object
- No explanations
- No markdown
- No tool logs
- No text outside JSON
- Response MUST start with '{' and end with '}'

JSON SCHEMA (STRICT):

  "Assumptions": "string",
  "Questions": ["string"],
  "Self-Answers": ["string"],
  "Verified Answers": ["string"],
  "Resources": ["string"],
  "Summary": "string",
  "Recommendations": ["string"],
  "Date": "YYYY-MM-DD",
  "Title": "string",
  "Tools": ["string"]


Notes:
\"\"\"{file_content}\"\"\"
"""

INSTRUNCTIONS  = [
"""
Initialization: Confirm that the brainstorm notes are successfully loaded.
If no notes are found, return a clear message indicating the issue.""",
"""
Extraction:
Identify and extract all questions, ideas, and self-answers from the notes.
Categorize the extracted elements into distinct sections for clarity.
""",

"""
Verification:
For each identified question, perform a search using DuckDuckGo, Google Search, and Wikipedia to find accurate and up-to-date answers.
Verify the reliability of the sources and provide a summary of the verified information.
""",
"""
Organization:
Structure the output in a consistent JSON format with clearly defined sections: Your Thoughts, Questions, Self-Answers, Verified Answers,Resources, Summary, Recommendations, Date, and Title.
""",

"""
Formatting:
Ensure that the final output is well-structured and formatted in JSON for easy extraction and further use.
""",

"""
Feedback and Recommendations:
Provide constructive feedback based on the content of the notes.
Offer actionable recommendations and additional resources to help improve or expand on the brainstormed ideas.
"""
]

scribe = Agent(
    name="Scribe",
    model=Groq(id="llama-3.3-70b-versatile"),
    tools=[
    GoogleSearch(),
    DuckDuckGo(),
    WikipediaTools()
    ],
    instructions=INSTRUNCTIONS,
    show_tool_calls=True,
    # markdown=True,

)


# Delay to prevent rate limiting
def safe_agent_run(prompt, retries=3, delay=2):
    for i in range(retries):
        try:
            response = scribe.run(prompt)
            return response
        except Exception as e:
            print(f"Attempt {i+1} failed: {e}")
            time.sleep(delay * (2 ** i))  # Exponential backoff
    raise RuntimeError("All retries failed.")



def parse_and_validate_agent_response(raw_text) -> dict:

    # Handle accidental string-wrapped JSON
    # remove '' around {} if exist 
    if raw_text.startswith("'") and raw_text.endswith("'"):
        raw_text = raw_text[1:-1].strip()

    # Parsing response
    try:
        data = json.loads(raw_text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON returned by agent:\n{e}")

    # Agent level error handling
    if "error" in data:
        raise RuntimeError(f"Agent error:{data["error"]}")

    # Schema validation (set)
    # subtract the keys, what's left is the missing one 
    missing = REQUIRED_KEYS - data.keys()
    if missing:
        raise ValueError(f"A key or more is missing in the ageent response: {missing}")
    
    return data

# print("=================Response =================")
# print(response.content)
# print("============================================")

response = safe_agent_run(PROMPT)

data = parse_and_validate_agent_response(response.content)


print(data["Questions"])
print(data["Recommendations"])# Save output
# with open(f"/home/ozirx/OZiRX/Tech/PRJs/Scribe/{title}.md", "w") as f:
#     f.write(response.content)
#
# print(f"Output saved to {title}.md")

