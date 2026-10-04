import React, { useState } from 'react';
import { ChevronDown, ChevronUp, Brain, TrendingUp, Newspaper, Flag, Lightbulb, AlertTriangle } from 'lucide-react';
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
    warnings: false,
  });

  const toggleSection = (section: string) => {
    setExpandedSections(prev => ({ ...prev, [section]: !prev[section] }));
  };

  const getConfidenceColor = (score: number) => {
    if (score >= 0.7) return 'bg-success/10 text-success border-success/20';
    if (score >= 0.4) return 'bg-success/5 text-success/80 border-success/10';
    if (score >= 0.3) return 'bg-warning/10 text-warning border-warning/20';
    return 'bg-danger/10 text-danger border-danger/20';
  };

  const getConfidenceLabel = (score: number) => {
    if (score >= 0.7) return 'High';
    if (score >= 0.4) return 'Moderate';
    if (score >= 0.3) return 'Low';
    return 'Very Low';
  };

  // Renders a string list, or a fallback line when the engine returned none,
  // so a section never collapses into an empty box.
  const BulletList = ({ items, emptyText }: { items: string[]; emptyText: string }) => {
    if (!items || items.length === 0) {
      return <p className="text-gray-500 text-sm italic">{emptyText}</p>;
    }
    return (
      <ul className="space-y-2">
        {items.map((item, index) => (
          <li key={index} className="flex items-start gap-2">
            <span className="flex-shrink-0 w-1.5 h-1.5 rounded-full bg-primary-500 mt-2" />
            <p className="text-gray-700 flex-1">{item}</p>
          </li>
        ))}
      </ul>
    );
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

  const sensitivityEntries = Object.entries(analysis.parameter_sensitivity || {});

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3 mb-6 flex-wrap">
        <Brain className="h-8 w-8 text-primary-500" />
        <h2 className="text-2xl font-bold text-gray-900">AI Analysis</h2>
        <div className={`px-3 py-1 rounded-full text-sm font-medium border ${getConfidenceColor(analysis.confidence_score)}`}>
          Confidence: {(analysis.confidence_score * 100).toFixed(0)}% ({getConfidenceLabel(analysis.confidence_score)})
        </div>
      </div>

      <SectionCard
        title="Performance Summary"
        icon={<TrendingUp className="h-6 w-6" />}
        sectionKey="performance"
      >
        <p className="text-gray-700 leading-relaxed">{analysis.performance_summary}</p>

        <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h4 className="text-sm font-semibold text-gray-700 mb-2">Outperformance Reasons</h4>
            <BulletList items={analysis.outperformance_reasons} emptyText="None identified" />
          </div>
          <div>
            <h4 className="text-sm font-semibold text-gray-700 mb-2">Underperformance Reasons</h4>
            <BulletList items={analysis.underperformance_reasons} emptyText="None identified" />
          </div>
        </div>

        <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h4 className="text-sm font-semibold text-gray-700 mb-2">Strategy Strengths</h4>
            <BulletList items={analysis.strategy_strengths} emptyText="None identified" />
          </div>
          <div>
            <h4 className="text-sm font-semibold text-gray-700 mb-2">Strategy Weaknesses</h4>
            <BulletList items={analysis.strategy_weaknesses} emptyText="None identified" />
          </div>
        </div>
      </SectionCard>

      <SectionCard
        title="News Impact Analysis"
        icon={<Newspaper className="h-6 w-6" />}
        sectionKey="news"
      >
        <p className="text-gray-700 leading-relaxed mb-4">{analysis.sentiment_impact_analysis}</p>
                <h4 className="text-sm font-semibold text-gray-700 mb-2">Key News Events</h4>
                {(!analysis.key_news_events || analysis.key_news_events.length === 0) ? (
                  <p className="text-gray-500 text-sm italic">No key news events identified</p>
                ) : (
                  <ul className="space-y-3">
                    {analysis.key_news_events.map((event, index) => (
                      <li key={index} className="flex items-start gap-2">
                        <span className="flex-shrink-0 w-1.5 h-1.5 rounded-full bg-primary-500 mt-2" />
                        <div>
                          <p className="text-gray-700 font-medium">{event.headline}</p>
                          <p className="text-sm text-gray-500">
                            {event.date} · Sentiment: {event.sentiment_impact}
                          </p>
                        </div>
                      </li>
                    ))}
                  </ul>
                )}
              </SectionCard>

      <SectionCard
        title="Political & Regulatory Factors"
        icon={<Flag className="h-6 w-6" />}
        sectionKey="political"
      >
        <BulletList items={analysis.political_factors} emptyText="No political or regulatory factors detected" />
      </SectionCard>

      <SectionCard
        title="Parameter Sensitivity"
        icon={<Lightbulb className="h-6 w-6" />}
        sectionKey="sensitivity"
      >
        {sensitivityEntries.length === 0 ? (
          <p className="text-gray-500 text-sm italic">No parameter sensitivity data available.</p>
        ) : (
          <ul className="space-y-2">
            {sensitivityEntries.map(([key, value]) => (
              <li key={key} className="flex items-start justify-between gap-4 text-sm">
                <span className="text-gray-600">{key}</span>
                <span className="text-gray-900 font-medium text-right">
                  {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                </span>
              </li>
            ))}
          </ul>
        )}
      </SectionCard>

      <SectionCard
        title="Actionable Suggestions"
        icon={<Lightbulb className="h-6 w-6" />}
        sectionKey="suggestions"
      >
        {(!analysis.suggestions || analysis.suggestions.length === 0) ? (
          <p className="text-gray-500 text-sm italic">No suggestions generated for this run.</p>
        ) : (
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
        )}
      </SectionCard>

      <SectionCard
        title="Risk Warnings"
        icon={<AlertTriangle className="h-6 w-6" />}
        sectionKey="warnings"
      >
        <BulletList items={analysis.risk_warnings} emptyText="No risk warnings flagged" />
      </SectionCard>
    </div>
  );
};