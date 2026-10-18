import React, { useState, useRef } from 'react'
import html2canvas from 'html2canvas'
import JSZip from 'jszip'
import AdCard from './AdCard'
import adCopyData from '../ad-copy.json'

const ANGLE_CODES = ['All', 'BUSY', 'REVENUE', 'CRM', 'ORG', 'CRINGE', 'PRIVACY']

export default function App() {
  const [selectedFilter, setSelectedFilter] = useState('All')
  const [isDownloading, setIsDownloading] = useState(false)
  const [downloadProgress, setDownloadProgress] = useState('')
  const fullSizeRefs = useRef({})

  const filteredAds = selectedFilter === 'All'
    ? adCopyData
    : adCopyData.filter(ad => ad.angle_code === selectedFilter)

  const handleDownload = async (ads) => {
    setIsDownloading(true)
    setDownloadProgress('Generating images...')

    try {
      const zip = new JSZip()
      
      for (let i = 0; i < ads.length; i++) {
        const ad = ads[i]
        setDownloadProgress(`Rendering ${i + 1}/${ads.length}: ${ad.id}...`)
        
        // Get the full-size element
        const element = fullSizeRefs.current[ad.id]
        if (!element) continue

        // Render to canvas
        const canvas = await html2canvas(element, {
          width: 1080,
          height: 1080,
          scale: 1,
          backgroundColor: null,
          logging: false
        })

        // Convert to blob
        const blob = await new Promise(resolve => canvas.toBlob(resolve, 'image/png'))
        
        // Add to zip
        const filename = `ER-${ad.angle_code}-${String(i + 1).padStart(2, '0')}-${ad.awareness_level}.png`
        zip.file(filename, blob)
      }

      setDownloadProgress('Creating ZIP file...')
      const zipBlob = await zip.generateAsync({ type: 'blob' })
      
      // Download
      const url = URL.createObjectURL(zipBlob)
      const a = document.createElement('a')
      a.href = url
      const date = new Date().toISOString().split('T')[0]
      a.download = `everreach-ads-bulk-${date}.zip`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)

      setDownloadProgress('✓ Download complete!')
      setTimeout(() => {
        setDownloadProgress('')
        setIsDownloading(false)
      }, 2000)
    } catch (error) {
      console.error('Download failed:', error)
      setDownloadProgress('✗ Download failed')
      setIsDownloading(false)
    }
  }

  return (
    <div style={{ padding: '40px 20px' }}>
      <h1 style={{ 
        fontSize: '48px', 
        marginBottom: '10px',
        fontWeight: 'bold'
      }}>
        EverReach Bulk Ad Generator
      </h1>
      <p style={{ 
        fontSize: '18px', 
        marginBottom: '40px',
        color: '#aaa'
      }}>
        {adCopyData.length} Facebook ad creatives • {filteredAds.length} showing
      </p>

      {/* Filter Buttons */}
      <div style={{ 
        display: 'flex', 
        gap: '10px', 
        marginBottom: '30px',
        flexWrap: 'wrap'
      }}>
        {ANGLE_CODES.map(code => (
          <button
            key={code}
            onClick={() => setSelectedFilter(code)}
            style={{
              padding: '12px 24px',
              fontSize: '16px',
              fontWeight: selectedFilter === code ? 'bold' : 'normal',
              backgroundColor: selectedFilter === code ? '#0066ff' : '#333',
              color: '#fff',
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer',
              transition: 'all 0.2s'
            }}
            onMouseOver={e => {
              if (selectedFilter !== code) {
                e.target.style.backgroundColor = '#444'
              }
            }}
            onMouseOut={e => {
              if (selectedFilter !== code) {
                e.target.style.backgroundColor = '#333'
              }
            }}
          >
            {code}
            {code !== 'All' && ` (${adCopyData.filter(ad => ad.angle_code === code).length})`}
          </button>
        ))}
      </div>

      {/* Download Buttons */}
      <div style={{ 
        display: 'flex', 
        gap: '15px', 
        marginBottom: '40px',
        alignItems: 'center'
      }}>
        <button
          onClick={() => handleDownload(adCopyData)}
          disabled={isDownloading}
          style={{
            padding: '16px 32px',
            fontSize: '18px',
            fontWeight: 'bold',
            backgroundColor: isDownloading ? '#666' : '#00cc66',
            color: '#fff',
            border: 'none',
            borderRadius: '8px',
            cursor: isDownloading ? 'not-allowed' : 'pointer',
            transition: 'all 0.2s'
          }}
          onMouseOver={e => {
            if (!isDownloading) e.target.style.backgroundColor = '#00dd77'
          }}
          onMouseOut={e => {
            if (!isDownloading) e.target.style.backgroundColor = '#00cc66'
          }}
        >
          Download All as ZIP ({adCopyData.length})
        </button>

        {selectedFilter !== 'All' && (
          <button
            onClick={() => handleDownload(filteredAds)}
            disabled={isDownloading}
            style={{
              padding: '16px 32px',
              fontSize: '18px',
              fontWeight: 'bold',
              backgroundColor: isDownloading ? '#666' : '#0066ff',
              color: '#fff',
              border: 'none',
              borderRadius: '8px',
              cursor: isDownloading ? 'not-allowed' : 'pointer',
              transition: 'all 0.2s'
            }}
            onMouseOver={e => {
              if (!isDownloading) e.target.style.backgroundColor = '#0077ff'
            }}
            onMouseOut={e => {
              if (!isDownloading) e.target.style.backgroundColor = '#0066ff'
            }}
          >
            Download Selected ({filteredAds.length})
          </button>
        )}

        {downloadProgress && (
          <span style={{ 
            fontSize: '16px', 
            color: downloadProgress.startsWith('✓') ? '#00cc66' : '#aaa'
          }}>
            {downloadProgress}
          </span>
        )}
      </div>

      {/* Preview Grid */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fill, minmax(340px, 1fr))',
        gap: '30px',
        marginBottom: '60px'
      }}>
        {filteredAds.map((ad, index) => (
          <div key={ad.id} style={{
            border: '1px solid #333',
            borderRadius: '8px',
            overflow: 'hidden',
            backgroundColor: '#1a1a1a'
          }}>
            <div style={{ padding: '15px', backgroundColor: '#222' }}>
              <div style={{ 
                fontSize: '14px', 
                fontWeight: 'bold',
                marginBottom: '5px',
                color: '#fff'
              }}>
                {ad.id}
              </div>
              <div style={{ 
                fontSize: '12px', 
                color: '#aaa',
                display: 'flex',
                gap: '10px'
              }}>
                <span style={{
                  backgroundColor: '#333',
                  padding: '2px 8px',
                  borderRadius: '4px'
                }}>
                  {ad.angle_code}
                </span>
                <span style={{
                  backgroundColor: '#333',
                  padding: '2px 8px',
                  borderRadius: '4px'
                }}>
                  {ad.awareness_level}
                </span>
              </div>
            </div>
            <div style={{ 
              display: 'flex', 
              justifyContent: 'center',
              padding: '20px',
              backgroundColor: '#0a0a0a'
            }}>
              <AdCard ad={ad} scale={0.3} />
            </div>
          </div>
        ))}
      </div>

      {/* Hidden full-size cards for rendering */}
      <div style={{ 
        position: 'absolute', 
        left: '-9999px',
        top: '-9999px'
      }}>
        {adCopyData.map(ad => (
          <div 
            key={`full-${ad.id}`}
            ref={el => fullSizeRefs.current[ad.id] = el}
          >
            <AdCard ad={ad} scale={1} />
          </div>
        ))}
      </div>
    </div>
  )
}
