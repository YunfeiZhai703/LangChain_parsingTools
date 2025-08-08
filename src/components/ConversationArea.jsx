import React, { useRef, useEffect, useState } from 'react'
import Message from './Message'
import LoadingSpinner from './LoadingSpinner'
import BottomUpload from './BottomUpload'
import './ConversationArea.css'

function ConversationArea({ conversation, isLoading, onFileUpload, onStopAnalysis }) {
  const conversationEndRef = useRef(null)
  const stopBtnRef = useRef(null)
  const [tooltipPosition, setTooltipPosition] = useState({ x: 0, y: 0 })

  const scrollToBottom = () => {
    conversationEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [conversation])

  const updateTooltipPosition = () => {
    if (stopBtnRef.current) {
      const rect = stopBtnRef.current.getBoundingClientRect()
      setTooltipPosition({
        x: rect.left + rect.width / 2,
        y: rect.top - 8
      })
    }
  }

  const handleMouseEnter = () => {
    updateTooltipPosition()
  }

  return (
    <div className="conversation-area">
      <div className="conversation-messages">
        {conversation.map((message, index) => (
          <Message 
            key={index} 
            message={message}
          />
        ))}
        
        {isLoading && (
          <div className="loading-container">
            <LoadingSpinner />
            <div className="stop-btn-container">
              <button 
                ref={stopBtnRef}
                className="stop-btn" 
                onClick={onStopAnalysis}
                onMouseEnter={handleMouseEnter}
              >
                <div className="stop-icon"></div>
              </button>
              <div 
                className="stop-tooltip"
                style={{
                  left: `${tooltipPosition.x}px`,
                  top: `${tooltipPosition.y}px`
                }}
              >
                Stop Analysis
              </div>
            </div>
          </div>
        )}
        
        <div ref={conversationEndRef} />
      </div>
      
      <BottomUpload onFileUpload={onFileUpload} isLoading={isLoading} />
    </div>
  )
}

export default ConversationArea 