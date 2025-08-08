import React from 'react'
import './Message.css'

function Message({ message }) {
  const isUser = message.type === 'user'
  const isError = message.isError

  if (isUser) {
    const analysisTypeDisplay = message.content.analysisType === 'detailed' 
      ? 'Page-by-page Analysis' 
      : 'Full Document Analysis'
    
    // Get file icon and type based on file extension
    const getFileInfo = (fileName) => {
      const extension = fileName.toLowerCase().substring(fileName.lastIndexOf('.'))
      if (extension === '.pdf') return { icon: '📄', type: 'PDF' }
      if (['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'].includes(extension)) return { icon: '🖼️', type: 'Image' }
      if (['.xls', '.xlsx', '.xlsm'].includes(extension)) return { icon: '📊', type: 'Excel' }
      if (extension === '.csv') return { icon: '📋', type: 'CSV' }
      return { icon: '📄', type: 'Document' } // default
    }
    
    const fileInfo = getFileInfo(message.content.fileName)
    
    return (
      <div className="message user">
        <div className="message-avatar user">{fileInfo.icon}</div>
        <div className="message-content">
          <div className="file-info">
            {message.content.fileName} ({message.content.fileSize} MB)
          </div>
          <div>Uploaded document for analysis</div>
          <div className="analysis-method">
            Analysis method: {analysisTypeDisplay}
          </div>
          <div className="analysis-method">
            File type: {fileInfo.type}
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="message assistant">
      <div className="message-avatar assistant">🤖</div>
      <div className={`message-content ${isError ? 'error' : ''}`}>
        <div 
          className="message-text"
          dangerouslySetInnerHTML={{ __html: message.content }}
        />
      </div>
    </div>
  )
}

export default Message 