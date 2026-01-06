
"""
What is it?
Scribe is an agent that helps you to organize ides, find answers
and prove your assumptions.

How it works?
You brainstorm a topic in Text file, then provide the file path
to the agent.

The agent loads the content, organize it, search internet for 
the given and assumption.

Finally creates a Markdown file and add to it the answers, 
proved assumptions, resources, recommendations and a short summary.

So the final result is a clean well organized file.
"""


from phi.agent.agent import Agent
from phi.model.groq.groq import Groq
from phi.tools.duckduckgo import DuckDuckGo
from phi.tools.googlesearch import GoogleSearch
from phi.tools.wikipedia import WikipediaTools
from dotenv import load_dotenv
import datetime, time
import sys, json, os


load_dotenv()


now = datetime.datetime.now()
datetime_creation = now.strftime('%Y-%m-%d_%H-%M')


NOTES_FILE_PATH = "/home/ozirx/OZiRX/Tech/PRJs/Scribe/thinking.txt"
OUTPUT_FILE_PATH = "/home/ozirx/OZiRX/Tech/PRJs/Scribe"


# ===============================================
#                 Pure Utilities
# ===============================================

def parse_response_content(response):
    try:
        data = json.loads(response)
    except json.JSONDecodeError as e:
        raise ValueError(f"invalid json returned by agent:\n{e}")
    if "error" in data:
        raise RuntimeError(f"Agent error:{data["error"]}")
    return data


def extract_and_format(parsed_resopnse,cat_name):
    content = ""
    for elem in parsed_resopnse[cat_name]:
        content += f"- {elem}\n"
    return content 



# ===============================================
#            Side-effect Utilities
# ===============================================
# A function has side effects if it does anything
# beyond returning a value.


def load_file_content(file_path):
    
    """Load file content and make sure it is not empty"""
    
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


def save_content(file_path:str, file_name:str, content:str):
    proper_name = file_name.replace(" ","_")
    full_path = os.path.join(file_path,f"{proper_name}.md")
    
    # if dirs(folders) not exist create them.
    os.makedirs(file_path, exist_ok=True)


    try:
        with open(f"{full_path}", "w") as f:
            f.write(content)
        print(f"file saved at {full_path}")
    except Exception as e:
        print(f"Failed to save file. Reason:\n {e}")


def safe_agent_run(agent,prompt, retries=3, delay=0.5):

    """ Slow down retries of external API/tools if first 
        try failed, to avoid rate-limiting, temp-ban or IP block.
    """

    for i in range(retries):
        try:
            response = agent.run(prompt)
            return response
        except Exception as e:
            print(f"Attempt {i+1} failed: {e}")
            time.sleep(delay * (2 ** i))  # Exponential backoff
    raise RuntimeError("All retries failed.")


# ===============================================
#            Prompt and Instructions 
# ===============================================
# Notes: 
# The more precise prompt is, the better result you get.
# Instructions: Who the agent is and how it should behave
# Prompt: What the agent should do right now

file_content = load_file_content(NOTES_FILE_PATH)


PROMPT = f"""
You are an expert brainstorm helper assistant.

You have access to the following tools:
["Google Search", "Wikipedia", "DuckDuckGo"]

Use tools ONLY when external knowledge is required to verify facts,
check assumptions, or provide reliable resources.
Do NOT search unnecessarily.

The user provides raw brainstorm notes as plain text.
The notes may be messy, informal, incomplete, or contain assumptions,
questions, spelling mistakes, and mixed ideas.

Your responsibilities:

1. Organize the content into clear ideas without changing the meaning.
2. Correct obvious spelling mistakes ONLY when the meaning is clear.
3. Identify assumptions made by the user (explicit or implicit).
4. For each assumption:
   - State it clearly using this format:
     "Your assumption was: <assumption>"
   - Verify it using reliable sources when needed.
   - Respond with:
     - "Yes, this assumption is correct."
     - OR "No, this assumption is incorrect. The correct information is: <correction>"
5. Identify questions in the notes (explicit or implied).
   - If answering requires external knowledge, use tools.
   - Present answers in a clear question → answer style.
6. Extract and provide helpful resources related to the topic.
   Resources may include:
     - Official websites
     - Trusted articles
     - Books
     - Videos
     - Communities
   Prefer official and well-established sources.
7. Write a short, clear summary of the topic in simple language.
8. Provide practical, realistic recommendations to help the user move forward.
9. Generate a short, clear title that reflects the main topic.

IMPORTANT RULES:
- Do NOT invent facts or questions.
- Do NOT over-correct grammar or rewrite the user's ideas.
- Do NOT include unverified or low-quality resources.
- Keep answers realistic and grounded.
- Maintain a consistent response structure.

Resources rule:
- Do NOT blindly reuse links found in the user's notes.
- If links appear in the notes, treat them as "user-saved links".
- Only include a link in "Resources" if it is relevant, trustworthy,
  and adds value beyond what the user already provided.
- Prefer adding NEW, high-quality resources when possible.
- If no better resources exist, you may include selected user links,
  but only after evaluation.

Summary rule:
- The Summary MUST reflect the final understanding after analysis.
- It should be based on the verified answers and assumption checks,
  NOT a recap of the user's original notes.
- The summary should answer: "What should the user now understand?"

CLARIFICATIONS:
- "Resources" must be curated by you. Do NOT automatically reuse links
  found in the user's notes unless they are evaluated and still useful.
- The "Summary" must summarize the conclusions and insights you produced
  after verification, not the user's raw brainstorm.

INVALID INPUT:
- If the input is meaningless, empty, or non-textual, return ONLY:


  "error": "Invalid or insufficient content"


OUTPUT FORMAT (MANDATORY):
- Return ONE valid JSON object.
- No markdown.
- No explanations.
- No text outside JSON.
- Output MUST start with '{' and end with '}'.

JSON SCHEMA (STRICT):

  "Ideas": ["string"],
  "Assumptions": ["string"],
  "Assumption Checks": ["string"],
  "Questions": ["string"],
  "Verified Answers": ["string"],
  "Resources": ["string"],
  "Summary": ["string"],
  "Recommendations": ["string"],
  "Title": "string",
  "Tools": ["string"]


User brainstorm file content:
\"\"\"{file_content}\"\"\"
"""


INSTRUCTIONS = [
    "You are an expert brainstorm helper agent.",
    "Your primary role is to help the user clarify and structure their raw brainstorm notes.",
    "You may use Google Search, DuckDuckGo, and Wikipedia ONLY when external knowledge is required.",
    "Do NOT use tools unnecessarily or by default.",
    "Keep answers realistic, grounded, and concise.",
   """Resources rule (STRICT):
- Only include resources if they add NEW value beyond common knowledge.
- If no high-quality external resource is clearly useful, return an empty list.
- Do NOT include generic sites by default.
""",
"""
Tool selection rules:
- Use Google Search first then DuckDuckGo if needed for specific, up-to-date, or complex queries (like salaries, visa requirements, local regulations).
- Use Wikipedia only for general knowledge, definitions, or historical/contextual info.
- If Wikipedia returns PageError, do not retry infinitely; move on to search engines.
"""
]


# ===============================================
#              Agent Configuration
# ===============================================

AGENT_SCRIBE_CONFIG = {
    "name": "Scribe",
    "model":[
        "llama-3.3-70b-versatile",
        "moonshotai/kimi-k2-instruct-0905",
        "openai/gpt-oss-120b",
    ],
    "tools": [GoogleSearch(), DuckDuckGo(), WikipediaTools()],
    "instructions": INSTRUCTIONS,
}


def agent_scribe(config):
    return Agent(
        name=config["name"],
        model=Groq(id=config["model"][1]),
        tools=config["tools"],
        instructions=config["instructions"],
        show_tool_calls=False,
        markdown=False,

    )

# ===============================================
#           Layout (formatting output) 
# ===============================================

def create_markdown(parsed_response):
    title = parsed_response["Title"]
    ideas = extract_and_format(parsed_response, "Ideas")
    assumptions = extract_and_format(parsed_response, "Assumptions")
    assumptions_checks = extract_and_format(parsed_response, "Assumption Checks")
    questions = extract_and_format(parsed_response, "Questions")
    verified_answers = extract_and_format(parsed_response, "Verified Answers")
    resources = extract_and_format(parsed_response, "Resources")
    recommendations = extract_and_format(parsed_response, "Recommendations")
    summary = parsed_response['Summary']


    result = f"""

#{title}\n
###{datetime_creation}\n
##Ideas\n{ideas}\n\n
##Assumptions\n{assumptions}\n
##Checked Assumptions\n{assumptions_checks}\n\n
##Questions Found\n{questions}\n\n
##Questions Answered\n{verified_answers}\n\n
##Resources\n{resources}\n\n
##Recommendations\n{recommendations}\n\n
##Summary\n{summary}\n
    """
    return result


def main():
    scribe = agent_scribe(AGENT_SCRIBE_CONFIG)
    response = safe_agent_run(scribe,PROMPT)
    response_content = response.content
    parsed_response = parse_response_content(response_content)
    file_name = parsed_response["Title"]
    markdown_content = create_markdown(parsed_response)
    save_content(OUTPUT_FILE_PATH,file_name,markdown_content)

if __name__ == "__main__":
    main()




