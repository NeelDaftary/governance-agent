from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from .proposal_analyzer import ProposalAnalyzer
from .sentiment_analyzer import SentimentAnalyzer
from .discourse_parser import DiscourseParser
from typing import Optional

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalyzeRequest(BaseModel):
    url: str
    include_sentiment: Optional[bool] = False

class SentimentRequest(BaseModel):
    comments: list[dict]

@app.post("/analyze")
async def analyze_proposal(request: AnalyzeRequest):
    try:
        # Parse the proposal from the URL
        parser = DiscourseParser()
        proposal_details = parser.parse_proposal(request.url)
        
        # Analyze proposal
        analyzer = ProposalAnalyzer()
        result = analyzer.analyze_proposal(proposal_details)
        
        # Add sentiment analysis if requested
        if request.include_sentiment:
            sentiment_analyzer = SentimentAnalyzer()
            sentiment_result = sentiment_analyzer.analyze_all_comments(proposal_details.get('comments', []))
            result['sentiment_analysis'] = sentiment_result
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/sentiment")
async def analyze_sentiment(request: SentimentRequest):
    try:
        sentiment_analyzer = SentimentAnalyzer()
        result = sentiment_analyzer.analyze_all_comments(request.comments)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 