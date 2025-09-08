from app.AI.simple_RAG_agent import Agent

if __name__ == "__main__":
    agent = Agent("docs", "data", "my_collections", "gpt-3.5-turbo", short_memory=True)
    # agent.add_document("peler.pdf", "pdf")
    while True:
        user_input = input("Human: ")
        if user_input == "exit":
            print("bye bye")
            agent.pretty_print()
            break
        agent.execute(
            {"user_message": user_input, "total_token": 0},
            "thread_123",
        )
        print(f"time: {agent.response_time}")
        print(f"token: {agent.token_usage}")

#
