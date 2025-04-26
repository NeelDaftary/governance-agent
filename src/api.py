from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, List
import logging
from src.proposal_analyzer import ProposalAnalyzer
from src.sentiment_analyzer import SentimentAnalyzer
from src.discourse_parser import DiscourseParser
from src.evaluator_agents import EvaluatorAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    comments: List[Dict]

class KeyFinding(BaseModel):
    aspect: str
    analysis: str
    impact: str

class DetailedEvaluation(BaseModel):
    score: float
    reasoning: str
    key_findings: List[KeyFinding]
    information_gaps: List[str]
    recommendations: List[str]

class Analysis(BaseModel):
    category_weights: Dict[str, float]
    primary_category: str
    summary: str
    detailed_evaluation: DetailedEvaluation

class Proposal(BaseModel):
    url: str
    title: str
    created_at: str

class CommentAnalysis(BaseModel):
    sentiment_score: float
    summary: str
    key_points: List[str]
    concerns: List[str]
    suggestions: List[str]

class AnalysisResponse(BaseModel):
    proposal: Proposal
    analysis: Analysis
    comment_analysis: Optional[CommentAnalysis] = None

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_proposal(request: AnalyzeRequest):
    """
    Analyze a governance proposal from the provided URL.
    
    Args:
        request: Contains the proposal URL and whether to include sentiment analysis
        
    Returns:
        AnalysisResponse: Detailed analysis of the proposal including category weights,
                         detailed evaluation, and optional sentiment analysis
    """
    try:
        logger.info(f"Starting analysis for URL: {request.url}")
        
        # Parse the proposal from the URL
        try:
            parser = DiscourseParser()
            proposal_data = parser.parse_proposal(request.url)
            logger.info("Successfully parsed proposal data")
        except Exception as e:
            logger.error(f"Error parsing proposal: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Error parsing proposal: {str(e)}")
        
        # Analyze proposal content and determine category
        try:
            analyzer = ProposalAnalyzer()
            analysis_results = analyzer.analyze_proposal({
                'title': proposal_data['title'],
                'content': proposal_data['content']
            })
            logger.info("Successfully analyzed proposal")
        except Exception as e:
            logger.error(f"Error analyzing proposal: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error analyzing proposal: {str(e)}")
        
        # Extract category scores and get primary category
        try:
            category_weights = {
                k: v for k, v in analysis_results.items() 
                if k not in ['sum', 'primary_category', 'summary']
            }
            primary_category = analysis_results.get('primary_category')
            
            # Get detailed evaluation from specialized agent
            evaluator = EvaluatorAgent()
            detailed_evaluation = evaluator.evaluate_proposal(primary_category, proposal_data)
            logger.info("Successfully generated detailed evaluation")
        except Exception as e:
            logger.error(f"Error generating evaluation: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error generating evaluation: {str(e)}")
        
        # Prepare the response
        result = {
            "proposal": {
                "url": request.url,
                "title": proposal_data['title'],
                "created_at": proposal_data['created_at']
            },
            "analysis": {
                "category_weights": category_weights,
                "primary_category": primary_category,
                "summary": analysis_results.get('summary', ''),
                "detailed_evaluation": {
                    "score": detailed_evaluation.get('score', 0.0),
                    "reasoning": detailed_evaluation.get('reasoning', ''),
                    "key_findings": detailed_evaluation.get('key_findings', []),
                    "information_gaps": detailed_evaluation.get('information_gaps', []),
                    "recommendations": detailed_evaluation.get('recommendations', [])
                }
            }
        }
        
        # Add sentiment analysis if requested
        if request.include_sentiment and proposal_data.get('comments'):
            try:
                sentiment_analyzer = SentimentAnalyzer()
                sentiment_result = sentiment_analyzer.analyze_all_comments(
                    proposal_data['comments'],
                    analysis_results['summary']  # Pass the proposal summary as context
                )
                result['comment_analysis'] = sentiment_result
                logger.info("Successfully completed sentiment analysis")
            except Exception as e:
                logger.error(f"Error in sentiment analysis: {str(e)}")
                # Don't fail the whole request if sentiment analysis fails
                pass
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@app.post("/sentiment")
async def analyze_sentiment(request: SentimentRequest):
    """
    Analyze sentiment of comments independently.
    
    Args:
        request: List of comments to analyze
        
    Returns:
        dict: Sentiment analysis results including score, summary, and key points
    """
    try:
        sentiment_analyzer = SentimentAnalyzer()
        result = sentiment_analyzer.analyze_all_comments(request.comments)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 