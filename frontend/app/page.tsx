'use client';

import { useState, useEffect } from 'react';
import type { FormEvent } from 'react';

interface AnalysisResult {
  proposal: {
    url: string;
    title: string;
    created_at: string;
  };
  analysis: {
    category_weights: {
      protocol_parameters: number;
      treasury_management: number;
      tokenomics: number;
      protocol_upgrades: number;
      governance_process: number;
      partnerships_integrations: number;
      risk_management: number;
      community_initiatives: number;
    };
    primary_category: string;
    summary: string;
    detailed_evaluation: {
      score: number;
      reasoning: string;
      key_findings: Array<{
        aspect: string;
        analysis: string;
        impact: string;
      }>;
      information_gaps: string[];
      recommendations: string[];
      category: string;
    };
  };
  comment_analysis?: {
    sentiment_score: number;
    summary: string;
    key_points: string[];
    concerns: string[];
    suggestions: string[];
  };
}

export default function Home() {
  const [url, setUrl] = useState('');
  const [includeSentiment, setIncludeSentiment] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [darkMode, setDarkMode] = useState(true);

  useEffect(() => {
    // Check system preference on mount
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    setDarkMode(prefersDark);

    // Listen for system preference changes
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    const handleChange = (e: MediaQueryListEvent) => setDarkMode(e.matches);
    mediaQuery.addEventListener('change', handleChange);

    // Set initial dark mode class
    document.documentElement.classList.toggle('dark', prefersDark);

    return () => mediaQuery.removeEventListener('change', handleChange);
  }, []);

  useEffect(() => {
    document.documentElement.classList.toggle('dark', darkMode);
  }, [darkMode]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await fetch('http://localhost:8000/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          url,
          include_sentiment: includeSentiment,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to analyze proposal');
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      console.error('Analysis error:', err);
      setError('Failed to connect to the analysis server. Make sure the backend is running.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={`min-h-screen transition-colors duration-200 ${
      darkMode ? 'dark bg-dark-bg' : 'bg-gray-50'
    }`}>
      <div className="container mx-auto px-4 py-8 max-w-4xl">
        <div className="flex justify-between items-center mb-8">
          <h1 className={`text-4xl font-bold tracking-tight ${
            darkMode ? 'text-white' : 'text-gray-900'
          }`}>
            Governance Proposal Analyzer
          </h1>
          <button
            onClick={() => setDarkMode(!darkMode)}
            className={`inline-flex items-center px-4 py-2 rounded-lg text-sm font-medium shadow-sm transition-colors ${
              darkMode 
                ? 'bg-dark-card text-gray-300 hover:bg-gray-700 border border-dark-border' 
                : 'bg-white text-gray-700 hover:bg-gray-50 border border-gray-300'
            }`}
          >
            {darkMode ? '☀️ Light Mode' : '🌙 Dark Mode'}
          </button>
        </div>

        <div className={`rounded-xl shadow-lg p-6 mb-8 ${
          darkMode ? 'bg-dark-card border border-dark-border' : 'bg-white'
        }`}>
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label className={`block text-sm font-medium mb-2 ${
                darkMode ? 'text-gray-200' : 'text-gray-700'
              }`}>
                Proposal URL
                <input
                  type="text"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  placeholder="Enter the URL of the governance proposal"
                  className={`mt-1 block w-full rounded-lg shadow-sm text-sm ${
                    darkMode 
                      ? 'bg-gray-800 border-gray-700 text-white placeholder-gray-400' 
                      : 'bg-white border-gray-300 text-gray-900 placeholder-gray-500'
                  } focus:ring-2 focus:ring-blue-500 focus:border-transparent`}
                />
              </label>
            </div>

            <div className="flex items-center">
              <label className={`flex items-center gap-2 text-sm ${
                darkMode ? 'text-gray-200' : 'text-gray-700'
              }`}>
                <input
                  type="checkbox"
                  checked={includeSentiment}
                  onChange={(e) => setIncludeSentiment(e.target.checked)}
                  className={`rounded shadow-sm ${
                    darkMode 
                      ? 'bg-gray-800 border-gray-700' 
                      : 'bg-white border-gray-300'
                  } text-blue-600 focus:ring-blue-500`}
                />
                Include sentiment analysis
              </label>
            </div>

            <button
              type="submit"
              disabled={loading}
              className={`w-full flex justify-center py-3 px-4 rounded-lg text-sm font-semibold shadow-sm transition-all ${
                darkMode
                  ? 'bg-blue-600 text-white hover:bg-blue-700 disabled:bg-gray-700'
                  : 'bg-blue-600 text-white hover:bg-blue-700 disabled:bg-gray-300'
              } disabled:cursor-not-allowed transform hover:scale-[1.02] active:scale-[0.98]`}
            >
              {loading ? (
                <span className="flex items-center gap-2">
                  <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  Analyzing...
                </span>
              ) : 'Analyze Proposal'}
            </button>
          </form>
        </div>

        {error && (
          <div className={`rounded-lg p-4 mb-6 ${
            darkMode 
              ? 'bg-red-900/30 text-red-200 border border-red-800' 
              : 'bg-red-50 text-red-700 border border-red-200'
          }`}>
            <p className="text-sm font-medium">{error}</p>
          </div>
        )}

        {result && (
          <div className="space-y-6">
            <div className={`rounded-xl shadow-lg p-6 ${
              darkMode 
                ? 'bg-dark-card border border-dark-border' 
                : 'bg-white'
            }`}>
              <h2 className={`text-2xl font-bold mb-6 ${
                darkMode ? 'text-white' : 'text-gray-900'
              }`}>
                Analysis Results
              </h2>
              
              <div className="space-y-6">
                <div>
                  <h3 className={`text-lg font-semibold mb-2 ${
                    darkMode ? 'text-gray-200' : 'text-gray-700'
                  }`}>
                    Proposal Details
                  </h3>
                  <p className={`${darkMode ? 'text-gray-300' : 'text-gray-600'}`}>
                    <strong>Title:</strong> {result.proposal.title}
                  </p>
                  <p className={`${darkMode ? 'text-gray-300' : 'text-gray-600'}`}>
                    <strong>URL:</strong> {result.proposal.url}
                  </p>
                </div>

                <div>
                  <h3 className={`text-lg font-semibold mb-2 ${
                    darkMode ? 'text-gray-200' : 'text-gray-700'
                  }`}>
                    Primary Category
                  </h3>
                  <p className={`${darkMode ? 'text-gray-300' : 'text-gray-600'}`}>
                    {result.analysis.primary_category}
                  </p>
                </div>

                <div>
                  <h3 className={`text-lg font-semibold mb-2 ${
                    darkMode ? 'text-gray-200' : 'text-gray-700'
                  }`}>
                    Summary
                  </h3>
                  <p className={`${darkMode ? 'text-gray-300' : 'text-gray-600'}`}>
                    {result.analysis.summary}
                  </p>
                </div>

                <div>
                  <h3 className={`text-lg font-semibold mb-4 ${
                    darkMode ? 'text-gray-200' : 'text-gray-700'
                  }`}>
                    Category Weights
                  </h3>
                  <div className="grid gap-3">
                    {Object.entries(result.analysis.category_weights)
                      .map(([category, weight]) => (
                        <div key={category} className={`flex justify-between items-center p-3 rounded-lg ${
                          darkMode ? 'bg-gray-800' : 'bg-gray-50'
                        }`}>
                          <span className={`capitalize font-medium ${
                            darkMode ? 'text-gray-200' : 'text-gray-700'
                          }`}>
                            {category.replace(/_/g, ' ')}
                          </span>
                          <span className={`font-mono ${
                            darkMode ? 'text-blue-400' : 'text-blue-600'
                          }`}>
                            {weight.toFixed(2)}
                          </span>
                        </div>
                      ))}
                  </div>
                </div>

                <div>
                  <h3 className={`text-lg font-semibold mb-4 ${
                    darkMode ? 'text-gray-200' : 'text-gray-700'
                  }`}>
                    Detailed Evaluation
                  </h3>
                  <div className="space-y-4">
                    <div>
                      <h4 className={`text-md font-medium mb-2 ${
                        darkMode ? 'text-gray-200' : 'text-gray-700'
                      }`}>
                        Score: {result.analysis.detailed_evaluation.score.toFixed(2)}
                      </h4>
                      <p className={`${darkMode ? 'text-gray-300' : 'text-gray-600'}`}>
                        {result.analysis.detailed_evaluation.reasoning}
                      </p>
                    </div>

                    <div>
                      <h4 className={`text-md font-medium mb-2 ${
                        darkMode ? 'text-gray-200' : 'text-gray-700'
                      }`}>
                        Key Findings
                      </h4>
                      <div className="space-y-3">
                        {result.analysis.detailed_evaluation.key_findings.map((finding, index) => (
                          <div key={index} className={`p-3 rounded-lg ${
                            darkMode ? 'bg-gray-800' : 'bg-gray-50'
                          }`}>
                            <p className={`font-medium ${
                              darkMode ? 'text-gray-200' : 'text-gray-700'
                            }`}>
                              {finding.aspect}
                            </p>
                            <p className={`mt-1 ${darkMode ? 'text-gray-300' : 'text-gray-600'}`}>
                              {finding.analysis}
                            </p>
                            <p className={`mt-1 ${darkMode ? 'text-gray-300' : 'text-gray-600'}`}>
                              <strong>Impact:</strong> {finding.impact}
                            </p>
                          </div>
                        ))}
                      </div>
                    </div>

                    <div>
                      <h4 className={`text-md font-medium mb-2 ${
                        darkMode ? 'text-gray-200' : 'text-gray-700'
                      }`}>
                        Information Gaps
                      </h4>
                      <ul className={`list-disc pl-5 space-y-1 ${
                        darkMode ? 'text-gray-300' : 'text-gray-600'
                      }`}>
                        {result.analysis.detailed_evaluation.information_gaps.map((gap, index) => (
                          <li key={index}>{gap}</li>
                        ))}
                      </ul>
                    </div>

                    <div>
                      <h4 className={`text-md font-medium mb-2 ${
                        darkMode ? 'text-gray-200' : 'text-gray-700'
                      }`}>
                        Recommendations
                      </h4>
                      <ul className={`list-disc pl-5 space-y-1 ${
                        darkMode ? 'text-gray-300' : 'text-gray-600'
                      }`}>
                        {result.analysis.detailed_evaluation.recommendations.map((rec, index) => (
                          <li key={index}>{rec}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {result.comment_analysis && (
              <div className={`rounded-xl shadow-lg p-6 ${
                darkMode 
                  ? 'bg-dark-card border border-dark-border' 
                  : 'bg-white'
              }`}>
                <h2 className={`text-2xl font-bold mb-6 ${
                  darkMode ? 'text-white' : 'text-gray-900'
                }`}>
                  Comment Analysis
                </h2>
                
                <div className="space-y-6">
                  <div>
                    <h3 className={`text-lg font-semibold mb-2 ${
                      darkMode ? 'text-gray-200' : 'text-gray-700'
                    }`}>
                      Overall Sentiment
                    </h3>
                    <div className="flex items-center gap-2">
                      <div className={`w-full h-2 rounded-full ${
                        darkMode ? 'bg-gray-700' : 'bg-gray-200'
                      }`}>
                        <div 
                          className={`h-full rounded-full ${
                            result.comment_analysis.sentiment_score >= 0 
                              ? 'bg-green-500' 
                              : 'bg-red-500'
                          }`}
                          style={{ 
                            width: `${Math.abs(result.comment_analysis.sentiment_score) * 100}%`,
                            marginLeft: result.comment_analysis.sentiment_score < 0 ? 'auto' : '0'
                          }}
                        />
                      </div>
                      <span className={`text-sm ${
                        darkMode ? 'text-gray-300' : 'text-gray-600'
                      }`}>
                        {result.comment_analysis.sentiment_score.toFixed(2)}
                      </span>
                    </div>
                  </div>

                  <div>
                    <h3 className={`text-lg font-semibold mb-2 ${
                      darkMode ? 'text-gray-200' : 'text-gray-700'
                    }`}>
                      Summary
                    </h3>
                    <p className={`${darkMode ? 'text-gray-300' : 'text-gray-600'}`}>
                      {result.comment_analysis.summary}
                    </p>
                  </div>

                  <div>
                    <h3 className={`text-lg font-semibold mb-2 ${
                      darkMode ? 'text-gray-200' : 'text-gray-700'
                    }`}>
                      Key Points
                    </h3>
                    <ul className={`list-disc list-inside space-y-1 ${
                      darkMode ? 'text-gray-300' : 'text-gray-600'
                    }`}>
                      {result.comment_analysis.key_points.map((point, index) => (
                        <li key={index}>{point}</li>
                      ))}
                    </ul>
                  </div>

                  <div>
                    <h3 className={`text-lg font-semibold mb-2 ${
                      darkMode ? 'text-gray-200' : 'text-gray-700'
                    }`}>
                      Concerns
                    </h3>
                    <ul className={`list-disc list-inside space-y-1 ${
                      darkMode ? 'text-gray-300' : 'text-gray-600'
                    }`}>
                      {result.comment_analysis.concerns.map((concern, index) => (
                        <li key={index}>{concern}</li>
                      ))}
                    </ul>
                  </div>

                  <div>
                    <h3 className={`text-lg font-semibold mb-2 ${
                      darkMode ? 'text-gray-200' : 'text-gray-700'
                    }`}>
                      Suggestions
                    </h3>
                    <ul className={`list-disc list-inside space-y-1 ${
                      darkMode ? 'text-gray-300' : 'text-gray-600'
                    }`}>
                      {result.comment_analysis.suggestions.map((suggestion, index) => (
                        <li key={index}>{suggestion}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
} 