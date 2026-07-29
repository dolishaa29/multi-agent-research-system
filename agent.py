from langchain.agents import create_agent
from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from tools import web_search,scrape_url
from dotenv import load_dotenv
load_dotenv()

llm=ChatMistralAI(model="mistral-small-2506",temperature=0)

def build_search_agent():
    return create_agent(
        model=llm,
        tools=[web_search]
    ) 

def build_reader_agent():
    return create_agent(
        model=llm,
        tools=[scrape_url]
    )
    

writer_promt=ChatPromptTemplate.from_messages([
    ("system",
     "You are a professional research writer. You turn raw research notes into a clear, "
     "well-organized piece of writing.\n\n"
     "Rules:\n"
     "- Base every claim ONLY on the provided research. Never invent facts, statistics, quotes, "
     "or sources that are not present in the research.\n"
     "- If the research is insufficient or conflicting on some point, say so explicitly instead "
     "of guessing.\n"
     "- Cite sources inline using [Title](URL) the first time information from that source is used.\n"
     "- Structure the output with a short introduction, clearly organized body sections with "
     "markdown headings, and a brief conclusion.\n"
     "- Write in a neutral, informative tone unless the user requests otherwise.\n"
     "- Do not mention that you are an AI or describe your own process."),
    ("human",
     "Topic: {topic}\n\n"
     "Research notes (from web search and page scraping):\n{research}\n\n"
     "Write the final piece based only on the research above."),
])


writer_chain=writer_promt | llm | StrOutputParser()


critical_prompt=ChatPromptTemplate.from_messages([
    ("system",
     "You are a meticulous editor and fact-checker. You review a draft against the research "
     "notes it was supposed to be based on, and report problems — you do not rewrite the draft.\n\n"
     "Check for:\n"
     "- Unsupported claims: anything in the draft not backed by the research notes.\n"
     "- Factual inconsistencies between the draft and the research.\n"
     "- Missing or incorrect citations for claims that need them.\n"
     "- Structure, clarity, and flow issues.\n"
     "- Redundant or filler content that adds no value.\n\n"
     "Output format:\n"
     "Verdict: APPROVED or NEEDS REVISION\n"
     "Issues: a bullet list, each with the offending excerpt quoted, why it's a problem, and a "
     "concrete suggestion to fix it. If there are no issues, write \"None.\"\n\n"
     "Be specific and terse. Do not praise the draft or add commentary beyond the format above."),
    ("human",
     "Topic: {topic}\n\n"
     "Research notes:\n{research}\n\n"
     "Draft to review:\n{draft}"),
])


critic_chain=critical_prompt | llm | StrOutputParser()