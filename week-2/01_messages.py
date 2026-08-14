from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage


messages = [
    SystemMessage(content="You explain AI engineering concepts to beginners."),
    HumanMessage(content="What is a prompt template?"),
    AIMessage(content="A prompt template is a reusable structure for prompts."),
    ToolMessage(
        content='{"temperature_c": 29}',
        tool_call_id="example-weather-call-1",
        name="get_weather",
    ),
]

for message in messages:
    print(f"{message.__class__.__name__}")
    print(f"  type: {message.type}")
    print(f"  content: {message.content}")
    print()
