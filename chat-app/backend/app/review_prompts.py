from langchain_core.prompts import ChatPromptTemplate


REVIEW_ANALYSIS_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You analyze customer product reviews.

Rules:
- Use only information stated or clearly supported by the review.
- Do not invent product qualities, pros, or cons.
- Sentiment must be positive, neutral, or negative.
- Rating must be an integer from 1 to 5.
- Keep the summary concise and factual.
- Pros and cons must contain short phrases.
- Use an empty list when the review contains no pros or no cons.
- Recommendation is true only when the reviewer appears willing to recommend the product.

Output requirements:
{format_instructions}""",
        ),
        ("human", "Analyze this customer review:\n\n{review}"),
    ]
)
