'use client';

import { useState } from 'react';

interface AnalysisResult {
  protocol_parameters: number;
  treasury_management: number;
  tokenomics: number;
  protocol_upgrades: number;
  governance_process: number;
  partnerships_integrations: number;
  risk_management: number;
  community_initiatives: number;
  primary_category: string;
  summary: string;
  sentiment_analysis?: {
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
    <main className="min-h-screen bg-gray-900 text-gray-100">
      <div className="container mx-auto p-4 max-w-4xl">
        <h1 className="text-3xl font-bold mb-6 text-blue-400">Governance Proposal Analyzer</h1>

        <form onSubmit={handleSubmit} className="mb-8">
          <div className="space-y-4">
            <div>
              <label className="block mb-2">
                Proposal URL:
                <input
                  type="text"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  placeholder="Enter proposal URL"
                  className="w-full p-2 mt-1 bg-gray-800 border border-gray-700 rounded text-gray-100 placeholder-gray-500 focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
                />
              </label>
            </div>

            <div>
              <label className="flex items-center gap-2 text-gray-300">
                <input
                  type="checkbox"
                  checked={includeSentiment}
                  onChange={(e) => setIncludeSentiment(e.target.checked)}
                  className="rounded border-gray-700 bg-gray-800 text-blue-500 focus:ring-blue-500"
                />
                Include sentiment analysis
              </label>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:bg-blue-800 disabled:cursor-not-allowed transition-colors"
            >
              {loading ? 'Analyzing...' : 'Analyze'}
            </button>
          </div>
        </form>

        {error && (
          <div className="p-4 mb-4 bg-red-900/50 text-red-200 rounded border border-red-700">
            {error}
          </div>
        )}

        {result && (
          <div className="space-y-6">
            <div className="p-4 bg-gray-800 rounded border border-gray-700">
              <h2 className="text-xl font-semibold mb-4 text-blue-400">Primary Analysis</h2>
              <div className="mb-4">
                <h3 className="font-semibold text-gray-300">Primary Category</h3>
                <p className="text-gray-100">{result.primary_category}</p>
              </div>
              <div className="mb-4">
                <h3 className="font-semibold text-gray-300">Summary</h3>
                <p className="text-gray-100">{result.summary}</p>
              </div>
              <div>
                <h3 className="font-semibold mb-2 text-gray-300">Category Scores</h3>
                <div className="space-y-2">
                  {Object.entries(result)
                    .filter(([key, value]) => 
                      typeof value === 'number' && 
                      !['sum'].includes(key)
                    )
                    .map(([category, score]) => (
                      <div key={category} className="flex justify-between text-gray-100">
                        <span className="capitalize">
                          {category.replace(/_/g, ' ')}
                        </span>
                        <span>{(score as number).toFixed(2)}</span>
                      </div>
                    ))}
                </div>
              </div>
            </div>

            {result.sentiment_analysis && (
              <div className="p-4 bg-gray-800 rounded border border-gray-700">
                <h2 className="text-xl font-semibold mb-4 text-blue-400">Sentiment Analysis</h2>
                
                <div className="mb-4">
                  <h3 className="font-semibold text-gray-300">Sentiment Score</h3>
                  <p className="text-gray-100">{result.sentiment_analysis.sentiment_score.toFixed(2)}</p>
                </div>

                <div className="mb-4">
                  <h3 className="font-semibold text-gray-300">Summary</h3>
                  <p className="text-gray-100">{result.sentiment_analysis.summary}</p>
                </div>

                <div className="mb-4">
                  <h3 className="font-semibold text-gray-300">Key Points</h3>
                  <ul className="list-disc pl-5 text-gray-100 space-y-1">
                    {result.sentiment_analysis.key_points.map((point, i) => (
                      <li key={i}>{point}</li>
                    ))}
                  </ul>
                </div>

                <div className="mb-4">
                  <h3 className="font-semibold text-gray-300">Concerns</h3>
                  <ul className="list-disc pl-5 text-gray-100 space-y-1">
                    {result.sentiment_analysis.concerns.map((concern, i) => (
                      <li key={i}>{concern}</li>
                    ))}
                  </ul>
                </div>

                <div>
                  <h3 className="font-semibold text-gray-300">Suggestions</h3>
                  <ul className="list-disc pl-5 text-gray-100 space-y-1">
                    {result.sentiment_analysis.suggestions.map((suggestion, i) => (
                      <li key={i}>{suggestion}</li>
                    ))}
                  </ul>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </main>
  );
} 