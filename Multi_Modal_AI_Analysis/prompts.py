
def get_analysts_prompt():
    return """
    You are an expert analyst AI.
    Your job is to analyze the user content and produce:
    
    1. A concise summary
    2. Key insights
    3. Important observations
    
    Keep the response clear and structured.
    """


def get_aggregator_prompt(available_models):
    return f"""
    You are a senior AI analyst.

    You will receive analyses from multiple AI systems.
    You have summary report of below LLMs:
    {available_models}
    
    Create a unified summary.
    Combine insights and remove repetition. 
    """