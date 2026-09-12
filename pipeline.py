from agent import build_reader_agent , build_search_agent, writer_chain, critic_chain, planner_chain

def extract_text(content)->str:
    if isinstance(content,str):
        return content
    if isinstance(content,list):
        return "".join(
            block.get("text","") if isinstance(block,dict) else str(block)
            for block in content
        )
    return str(content)

def run_research_pipeline(topic:str)->dict:
    state={}
    print("\n"+" ="*50)
    print("step0 planner is working")
    print("="*50)

    state["plan"]=planner_chain.invoke({"topic":topic})
    print(state["plan"])

    print("\n"+" ="*50)
    print("step1 agent is working")
    print("="*50)

    search_agent=build_search_agent()
    search_result=search_agent.invoke({
        "messages":[("user",
                    f"Research the topic '{topic}' by investigating each of the following "
                    f"sub-questions. For each one, use the web_search tool to find recent, "
                    f"reliable, detailed information, and present the results grouped under "
                    f"that sub-question.\n\nSub-questions:\n{state['plan']}")]

    })
    state["search_results"]=extract_text(search_result["messages"][-1].content)
    print(state['search_results'])

    print("\n"+" ="*50)
    print("step2 reader agent is working")
    print("="*50)

    reader_agent=build_reader_agent()
    reader_result=reader_agent.invoke({
        "messages":[("user",
                    f"Based on the following search results about '{topic}', pick the most relevant "
                    f"URLs and scrape them for deeper, detailed information. Summarize what you find "
                    f"into clear research notes.\n\nSearch results:\n{state['search_results']}")]
    })
    state["reader_results"]=extract_text(reader_result["messages"][-1].content)
    print(state['reader_results'])

    print("\n"+" ="*50)
    print("combining research")
    print("="*50)

    state["research"]=(
        f"--- Research Plan ---\n{state['plan']}\n\n"
        f"--- Search Results ---\n{state['search_results']}\n\n"
        f"--- Detailed Notes ---\n{state['reader_results']}"
    )
    print(state["research"])

    return state

if __name__=="__main__":
    topic=input("Enter research topic: ")
    run_research_pipeline(topic)
