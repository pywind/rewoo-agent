import React from 'react';
import { LanguageProvider } from './context/LanguageContext.jsx';
import ChatInterface from './components/ChatInterface.jsx';

function App() {
  return (
    <LanguageProvider>
      <ChatInterface />
    </LanguageProvider>
  );
}

export default App;
