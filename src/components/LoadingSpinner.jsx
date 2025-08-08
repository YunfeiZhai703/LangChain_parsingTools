import React from 'react'
import './LoadingSpinner.css'

function LoadingSpinner() {
  return (
    <div className="message assistant">
      <div className="message-avatar assistant">🤖</div>
      <div className="message-content loading-content">
        <div className="spinner"></div>
        <p>Analyzing your file... This may take a few moments.</p>
      </div>
    </div>
  )
}

export default LoadingSpinner 