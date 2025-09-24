import React from 'react';
import { Search, Calculator, Globe, BookOpen } from 'lucide-react';
import { useTranslation } from '../hooks/useTranslation.js';

const ExampleQueries = ({ onSelectQuery }) => {
  const t = useTranslation();
  
  const examples = [
    {
      icon: <Search className="text-blue-500" size={20} />,
      title: t('example_research_title'),
      query: t('example_research_query'),
      category: t('example_research_category')
    },
    {
      icon: <Calculator className="text-green-500" size={20} />,
      title: t('example_calculation_title'),
      query: t('example_calculation_query'),
      category: t('example_calculation_category')
    },
    {
      icon: <Globe className="text-purple-500" size={20} />,
      title: t('example_search_title'),
      query: t('example_search_query'),
      category: t('example_search_category')
    },
    {
      icon: <BookOpen className="text-orange-500" size={20} />,
      title: t('example_knowledge_title'),
      query: t('example_knowledge_query'),
      category: t('example_knowledge_category')
    }
  ];

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold text-gray-700 mb-4">{t('try_examples')}</h3>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {examples.map((example, index) => (
          <div
            key={index}
            onClick={() => onSelectQuery(example.query)}
            className="p-4 border border-gray-200 rounded-lg hover:border-blue-300 hover:shadow-md transition-all cursor-pointer bg-white"
          >
            <div className="flex items-start space-x-3">
              <div className="flex-shrink-0 mt-1">
                {example.icon}
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="text-sm font-medium text-gray-900">{example.title}</h4>
                  <span className="text-xs px-2 py-1 bg-gray-100 text-gray-600 rounded-full">
                    {example.category}
                  </span>
                </div>
                <p className="text-sm text-gray-600 line-clamp-3">
                  {example.query}
                </p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ExampleQueries;