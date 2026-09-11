import React, { useState } from 'react';
import { ChevronDown, ChevronUp, Brain, TrendingUp, Newspaper, Flag, Lightbulb } from 'lucide-react';
import type { AIAnalysis } from '../types';

interface AIAnalysisPanelProps {
  analysis: AIAnalysis;
}

export const AIAnalysisPanel: React.FC<AIAnalysisPanelProps> = ({ analysis }) => {
  const [expandedSections, setExpandedSections] = useState<Record<string, boolean>>({
    performance: true,
    news: false,
    political: false,
    sensitivity: false,
    suggestions: true,
  });

  const toggleSection = (section: string) => {
    setExpandedSections(prev => ({ ...prev, [section]: !prev[section] }));
  };

  const getSentimentColor = (score: number) => {
    if (score >= 0.7) return 'bg-success/10 text-success border-success/20';
    if (score >= 0.3) return 'bg-success/5 text-success/80 border-success/10';
    if (score >= -0.3) return 'bg-warning/10 text-warning border-warning/20';
    if (score >= -0.7) return 'bg-danger/5 text-danger/80 border-danger/10';
    return 'bg-danger/10 text-danger border-danger/20';
  };

  const getSentimentLabel = (score: number) => {
    if (score >= 0.7) return 'Very Positive';
    if (score >= 0.3) return 'Positive';
    if (score >= -0.3) return 'Neutral';
    if (score >= -0.7) return 'Negative';
    return 'Very Negative';
  };

  const SectionCard = ({ 
    title, 
    icon, 
    sectionKey, 
    children 
  }: { 
    title: string; 
    icon: React.ReactNode; 
    sectionKey: string; 
    children: React.ReactNode 
  }) => (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
      <button
        onClick={() => toggleSection(sectionKey)}
        className="w-full px-6 py-4 flex items-center justify-between hover:bg-gray-50 transition-colors"
      >
        <div className="flex items-center gap-3">
          <span className="text-primary-500">{icon}</span>
          <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
        </div>
        {expandedSections[sectionKey] ? (
          <ChevronUp className="h-5 w-5 text-gray-400" />
        ) : (
          <ChevronDown className="h-5 w-5 text-gray-400" />
        )}
      </button>
      
      {expandedSections[sectionKey] && (
        <div className="px-6 pb-6 pt-2 border-t border-gray-100">
          {children}
        </div>
      )}
    </div>
  );

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3 mb-6">
        <Brain className="h-8 w-8 text-primary-500" />
        <h2 className="text-2xl font-bold text-gray-900">AI Analysis</h2>
        <div className={`px-3 py-1 rounded-full text-sm font-medium border ${getSentimentColor(analysis.confidence_score)}`}>
          Confidence: {(analysis.confidence_score * 100).toFixed(0)}% ({getSentimentLabel(analysis.confidence_score)})
        </div>
      </div>

      <SectionCard
        title="Performance Summary"
        icon={<TrendingUp className="h-6 w-6" />}
        sectionKey="performance"
      >
        <p className="text-gray-700 leading-relaxed">{analysis.performance_summary}</p>
      </SectionCard>

      <SectionCard
        title="News Impact Analysis"
        icon={<Newspaper className="h-6 w-6" />}
        sectionKey="news"
      >
        <p className="text-gray-700 leading-relaxed">{analysis.news_impact}</p>
      </SectionCard>

      <SectionCard
        title="Political & Regulatory Factors"
        icon={<Flag className="h-6 w-6" />}
        sectionKey="political"
      >
        <p className="text-gray-700 leading-relaxed">{analysis.political_factors}</p>
      </SectionCard>

      <SectionCard
        title="Parameter Sensitivity"
        icon={<Lightbulb className="h-6 w-6" />}
        sectionKey="sensitivity"
      >
        <p className="text-gray-700 leading-relaxed">{analysis.parameter_sensitivity}</p>
      </SectionCard>

      <SectionCard
        title="Actionable Suggestions"
        icon={<Lightbulb className="h-6 w-6" />}
        sectionKey="suggestions"
      >
        <ul className="space-y-3">
          {analysis.suggestions.map((suggestion, index) => (
            <li key={index} className="flex items-start gap-3">
              <span className="flex-shrink-0 w-6 h-6 bg-primary-100 text-primary-600 rounded-full flex items-center justify-center text-sm font-medium">
                {index + 1}
              </span>
              <p className="text-gray-700 flex-1">{suggestion}</p>
            </li>
          ))}
        </ul>
      </SectionCard>
    </div>
  );
};
