import React, { useState } from 'react'
import './AnalysisOptions.css'

function AnalysisOptions() {
  const [selectedOption, setSelectedOption] = useState('comprehensive')

  return (
    <div className="analysis-options">
      <div className="option-item">
        <input 
          type="radio" 
          id="detailed" 
          name="analysisType" 
          value="detailed"
          checked={selectedOption === 'detailed'}
          onChange={(e) => setSelectedOption(e.target.value)}
        />
        <label htmlFor="detailed">Page-by-page Analysis</label>
      </div>
      <div className="option-item">
        <input 
          type="radio" 
          id="comprehensive" 
          name="analysisType" 
          value="comprehensive"
          checked={selectedOption === 'comprehensive'}
          onChange={(e) => setSelectedOption(e.target.value)}
        />
        <label htmlFor="comprehensive">Full Document Analysis</label>
      </div>
    </div>
  )
}

export default AnalysisOptions 