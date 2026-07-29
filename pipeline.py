from agent import build_reader_agent , build_search_agent, writer_chain, critic_chain

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
    print("step1 agent is working")
    print("="*50)

    search_agent=build_search_agent()
    search_result=search_agent.invoke({
        "messages":[("user",f"Find recent , reliable and detailed information about:{topic}")]

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
    state["reader_results"]=reader_result["messages"][-1].content
    print(state['reader_results'])

    print("\n"+" ="*50)
    print("combining research")
    print("="*50)

    state["research"]=(
        f"--- Search Results ---\n{state['search_results']}\n\n"
        f"--- Detailed Notes ---\n{state['reader_results']}"
    )
    print(state["research"])

    return state

if __name__=="__main__":
    topic=input("Enter research topic: ")
    run_research_pipeline(topic)
