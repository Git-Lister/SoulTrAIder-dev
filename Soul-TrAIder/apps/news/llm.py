"""
Placeholder for LLM sentiment analysis.
Will integrate with Ollama.
"""
def analyze_article(article_id):
    """
    Send article to local LLM and store sentiment per instrument.
    """
    import ollama  # will be installed

    from apps.core.models import Instrument

    from .models import NewsArticle, NewsImpact
    
    article = NewsArticle.objects.get(id=article_id)
    instruments = Instrument.objects.all()
    
    prompt = f"""
    Analyze this news article for relevance to the following investments:
    {', '.join([i.ticker for i in instruments])}
    
    Article: {article.title}\n{article.content}
    
    For each, return sentiment (-1 to 1) and brief explanation.
    """
    
    response = ollama.chat(model='llama3', messages=[{'role': 'user', 'content': prompt}])
    # Parse response and store NewsImpact objects
    # ...