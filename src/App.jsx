import React, { useState } from 'react'
import Header from './components/Header'
import UploadArea from './components/UploadArea'
import AnalysisOptions from './components/AnalysisOptions'
import ConversationArea from './components/ConversationArea'
import './App.css'

function App() {
  const [conversation, setConversation] = useState([])
  const [isLoading, setIsLoading] = useState(false)
  const [showConversation, setShowConversation] = useState(false)
  const [abortController, setAbortController] = useState(null)

  const handleFileUpload = async (file, analysisType) => {
    // Add user message to conversation
    const userMessage = {
      type: 'user',
      content: {
        fileName: file.name,
        fileSize: (file.size / 1024 / 1024).toFixed(2),
        analysisType
      }
    }

    setConversation(prev => [...prev, userMessage])
    setShowConversation(true)
    setIsLoading(true)

    // Create new AbortController for this request
    const controller = new AbortController()
    setAbortController(controller)

    try {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('analysis_type', analysisType)

      const response = await fetch('/api/analyze-pdf/', {
        method: 'POST',
        body: formData,
        signal: controller.signal
      })

      const data = await response.json()

      if (data.error) {
        const errorMessage = {
          type: 'assistant',
          content: `Error: ${data.error}`,
          isError: true
        }
        setConversation(prev => [...prev, errorMessage])
      } else if (data.analysis && data.analysis.error) {
        const errorMessage = {
          type: 'assistant',
          content: `Error: ${data.analysis.error}`,
          isError: true
        }
        setConversation(prev => [...prev, errorMessage])
      } else {
        const assistantMessage = {
          type: 'assistant',
          content: formatAnalysisResponse(data),
          isError: false
        }
        setConversation(prev => [...prev, assistantMessage])
      }
    } catch (error) {
      if (error.name === 'AbortError') {
        const cancelMessage = {
          type: 'assistant',
          content: '⏹️ Analysis stopped by user.',
          isError: false
        }
        setConversation(prev => [...prev, cancelMessage])
      } else {
        let errorMessage = 'An error occurred while processing the file: ' + error.message
        
        if (error.message.includes('Ollama service crashed')) {
          errorMessage = '❌ Ollama service crashed. Please restart the application and try again.'
        } else if (error.message.includes('Cannot connect to Ollama')) {
          errorMessage = '❌ Cannot connect to Ollama. Please make sure Ollama is running.'
        } else if (error.message.includes('broken pipe')) {
          errorMessage = '❌ Ollama service is not responding. Please restart the application.'
        }

        const errorMsg = {
          type: 'assistant',
          content: errorMessage,
          isError: true
        }
        setConversation(prev => [...prev, errorMsg])
      }
    } finally {
      setIsLoading(false)
      setAbortController(null)
    }
  }

  const handleStopAnalysis = () => {
    if (abortController) {
      abortController.abort()
    }
  }

  const formatAnalysisResponse = (data) => {
    let content = ''
    
    // Add document summary information
    if (data.document_summary) {
      const summary = data.document_summary
      content += '<strong>📋 Document Information:</strong><br>'
      content += `File Type: ${summary.file_type || 'Unknown'}<br>`
      content += `Pages/Sections: ${summary.total_pages || 0}<br>`
      if (summary.sheets) {
        content += `Sheets: ${summary.sheets.join(', ')}<br>`
      }
      if (summary.rows) {
        content += `Rows: ${summary.rows}, Columns: ${summary.columns}<br>`
      }
      if (summary.image_format) {
        content += `Format: ${summary.image_format}<br>`
      }
      content += '<br>'
    }
    
    if (data.analysis) {
      const analysis = data.analysis
      
      if (analysis.analysis_type === 'detailed' && analysis.page_analyses) {
        content += '<strong>📄 Page-by-Page Analysis</strong><br><br>'
        analysis.page_analyses.forEach((page, index) => {
          content += `<strong>Page ${page.page_number || index + 1}:</strong><br>`
          content += `${page.analysis || page.summary || 'No analysis available'}<br><br>`
        })
        
        if (analysis.overall_summary) {
          content += '<strong>📊 Overall Summary:</strong><br>'
          content += `${analysis.overall_summary.analysis || analysis.overall_summary.summary}<br><br>`
        }
      } else if (analysis.analysis_type === 'comprehensive') {
        if (analysis.document_summary) {
          content += '<strong>🧠 Document Analysis:</strong><br>'
          content += `${analysis.document_summary.document_summary || analysis.document_summary.analysis || analysis.document_summary.summary}<br><br>`
        }
      } else {
        content += '<strong>🧠 AI Analysis:</strong><br>'
        content += `${analysis.analysis || analysis.summary}<br><br>`
      }
    }
    
    return content || 'Analysis completed successfully!'
  }

  return (
    <div className="app">
      <Header />
      
      {!showConversation ? (
        <div className="main-content">
          <UploadArea onFileUpload={handleFileUpload} isLoading={isLoading} />
          <AnalysisOptions />
        </div>
      ) : (
        <>
          <ConversationArea 
            conversation={conversation} 
            isLoading={isLoading}
            onFileUpload={handleFileUpload}
            onStopAnalysis={handleStopAnalysis}
          />
        </>
      )}
    </div>
  )
}

export default App 