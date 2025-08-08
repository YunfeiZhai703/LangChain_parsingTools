import React, { useState, useRef } from 'react'
import './BottomUpload.css'

function BottomUpload({ onFileUpload, isLoading }) {
  const [isDragOver, setIsDragOver] = useState(false)
  const [selectedFile, setSelectedFile] = useState(null)
  const fileInputRef = useRef(null)

  const handleDragOver = (e) => {
    e.preventDefault()
    setIsDragOver(true)
  }

  const handleDragLeave = (e) => {
    e.preventDefault()
    setIsDragOver(false)
  }

  const handleDrop = (e) => {
    e.preventDefault()
    setIsDragOver(false)
    const files = e.dataTransfer.files
    if (files.length > 0) {
      handleFileSelect(files[0])
    }
  }

  const handleFileSelect = (file) => {
    const allowedExtensions = ['.pdf', '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.xls', '.xlsx', '.xlsm', '.csv']
    const fileExtension = file.name.toLowerCase().substring(file.name.lastIndexOf('.'))
    
    if (!allowedExtensions.includes(fileExtension)) {
      alert('Please select a supported file type (PDF, Image, Excel, or CSV).')
      return
    }
    setSelectedFile(file)
  }

  const handleFileInputChange = (e) => {
    if (e.target.files.length > 0) {
      handleFileSelect(e.target.files[0])
    }
  }

  const handleUpload = () => {
    if (selectedFile && !isLoading) {
      onFileUpload(selectedFile, 'comprehensive') // Default to comprehensive
      setSelectedFile(null)
    }
  }

  return (
    <div className="bottom-upload">
      <div 
        className={`upload-section ${isDragOver ? 'dragover' : ''}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <div className="upload-controls">
          <div className="upload-icon">📄</div>
          <div className="upload-text">
            {selectedFile ? selectedFile.name : 'Drop here or'}
          </div>
          <input 
            type="file" 
            ref={fileInputRef}
            className="file-input" 
            accept=".pdf,.jpg,.jpeg,.png,.gif,.bmp,.tiff,.webp,.xls,.xlsx,.xlsm,.csv"
            onChange={handleFileInputChange}
          />
          <button 
            className="upload-btn" 
            onClick={() => fileInputRef.current?.click()}
          >
            {selectedFile ? 'Choose Another File' : 'Choose File'}
          </button>
          {selectedFile && (
            <button 
              className={`upload-btn upload-btn-primary ${isLoading ? 'disabled' : ''}`}
              onClick={handleUpload}
              disabled={isLoading}
            >
              {isLoading ? 'Analyzing...' : 'Upload & Analyze'}
            </button>
          )}
        </div>
        <div className="supported-files">
          Supports: PDF, Images (JPG, PNG, etc.), Excel, CSV
        </div>
      </div>
    </div>
  )
}

export default BottomUpload 