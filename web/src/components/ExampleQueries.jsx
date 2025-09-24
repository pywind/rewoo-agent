import React from 'react';
import { Search, Calculator, Globe, BookOpen } from 'lucide-react';

const ExampleQueries = ({ onSelectQuery }) => {
  const examples = [
    {
      icon: <Search className="text-blue-500" size={20} />,
      title: "Research Task",
      query: "Research the latest developments in artificial intelligence and machine learning, including recent breakthroughs and applications",
      category: "Research"
    },
    {
      icon: <Calculator className="text-green-500" size={20} />,
      title: "Mathematical Calculation",
      query: "Calculate the compound interest for an investment of $10,000 at 5% annual interest rate for 10 years",
      category: "Calculation"
    },
    {
      icon: <Globe className="text-purple-500" size={20} />,
      title: "Web Search",
      query: "Find information about the current weather trends and climate change impacts in Southeast Asia",
      category: "Search"
    },
    {
      icon: <BookOpen className="text-orange-500" size={20} />,
      title: "Knowledge Query",
      query: "Explain the concept of quantum computing and its potential applications in cryptography",
      category: "Knowledge"
    }
  ];

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold text-gray-700 mb-4">Try these examples:</h3>
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