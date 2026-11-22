from agent import (
    build_reader_agent,
    build_search_agent,
    critic_chain,
    planner_chain,
    revise_chain,
    writer_chain,
)

MAX_REVISIONS = 2


def message_text(content) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "".join(
            block.get("text", "") if isinstance(block, dict) else str(block)
            for block in content
        )
    return str(content)

def run_research_pipeline(topic: str) -> dict:
    print("Planning research")
    plan = planner_chain.invoke({"topic": topic})

    print("Searching the web")
    search_prompt = (
        f"Research the topic '{topic}' by investigating each of the following "
        "sub-questions. For each one, use the web_search tool to find recent, "
        "reliable, detailed information, and present the results grouped under "
        f"that sub-question.\n\nSub-questions:\n{plan}"
    )
    search_reply = build_search_agent().invoke({"messages": [("user", search_prompt)]})
    search_results = message_text(search_reply["messages"][-1].content)

    print("Reading sources")
    reader_prompt = (
        f"Based on the following search results about '{topic}', pick the most relevant "
        "URLs and scrape them for deeper, detailed information. Summarize what you find "
        f"into clear research notes.\n\nSearch results:\n{search_results}"
    )
    reader_reply = build_reader_agent().invoke({"messages": [("user", reader_prompt)]})
    reader_notes = message_text(reader_reply["messages"][-1].content)

    research = (
        f"--- Research Plan ---\n{plan}\n\n"
        f"--- Search Results ---\n{search_results}\n\n"
        f"--- Detailed Notes ---\n{reader_notes}"
    )
    print("Writing the article")
    article = writer_chain.invoke({"topic": topic, "research": research})

    print("Reviewing the article")
    review = critic_chain.invoke({"topic": topic, "research": research, "draft": article})
    revisions = 0
    while "NEEDS REVISION" in review.upper() and revisions < MAX_REVISIONS:
        revisions += 1
        print(f"Revising the article ({revisions}/{MAX_REVISIONS})")
        article = revise_chain.invoke({
            "topic": topic,
            "research": research,
            "draft": article,
            "issues": review,
        })
        review = critic_chain.invoke({"topic": topic, "research": research, "draft": article})

    return {
        "plan": plan,
        "search_results": search_results,
        "reader_results": reader_notes,
        "research": research,
        "draft": article,
        "article": article,
        "review": review,
        "revisions": revisions,
    }
