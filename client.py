# Create server parameters for stdio connection
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import asyncio
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
from langchain_mistralai import ChatMistralAI
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize the Mistral AI model
model = ChatMistralAI(
    model="mistral-small-latest",
    temperature=0.4,
    api_key=os.getenv("MISTRAL_API_KEY")  # Ensure the API key is loaded
)

# Define server parameters
server_params = StdioServerParameters(
    command="python",
    args=["C:\\Users\\Raghu\\Downloads\\ProofOfConcept\\customcopilot\\main.py"],  # Path to your server script
)

async def run_agent():
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                print("Client session initialized successfully.")


                tools = await load_mcp_tools(session)
                print("Tools loaded successfully.")

                agent = create_react_agent(model, tools)

                while True:
                    query = input("Enter the query (or type 'exit' to quit): ")
                    if query.lower() == 'exit':
                        print("Exiting...")
                        break

        
                    agent_response = await agent.ainvoke({"messages": query})

                    
                    messages = agent_response.get("messages", [])
                    if len(messages) > 3:
                        print("Agent response:", messages[3].content)
                    elif messages:
                        print("Agent response (fallback):", messages[-1].content)
                    else:
                        print("Agent returned no messages.")
    except Exception as e:
        print(f"Error during client execution: {e}")
        raise
    finally:
        print("Client execution complete.")

if __name__ == "__main__":
    asyncio.run(run_agent())
