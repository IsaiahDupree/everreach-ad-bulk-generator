import React from 'react'

const COLOR_MAP = {
  BUSY: '#1a1a2e',
  REVENUE: '#2d1b00',
  CRM: '#0d2137',
  ORG: '#1a2d1a',
  CRINGE: '#2d1a2d',
  PRIVACY: '#1a1a1a'
}

export default function AdCard({ ad, scale = 0.3 }) {
  const backgroundColor = COLOR_MAP[ad.angle_code] || '#1a1a1a'
  
  return (
    <div
      className="ad-card"
      style={{
        width: `${1080 * scale}px`,
        height: `${1080 * scale}px`,
        backgroundColor,
        display: 'flex',
        flexDirection: 'column',
        position: 'relative',
        overflow: 'hidden'
      }}
    >
      {/* Headline - top 60% */}
      <div style={{
        flex: '0 0 60%',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: `${60 * scale}px`,
        textAlign: 'center'
      }}>
        <h1 style={{
          fontSize: `${scale === 1 ? 72 : 72 * scale}px`,
          fontWeight: 'bold',
          color: '#ffffff',
          lineHeight: 1.2,
          fontFamily: 'Inter, system-ui, -apple-system, sans-serif',
          margin: 0
        }}>
          {ad.headline}
        </h1>
      </div>

      {/* Body text - 30% */}
      <div style={{
        flex: '0 0 30%',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: `${40 * scale}px ${60 * scale}px`,
        textAlign: 'center'
      }}>
        <p style={{
          fontSize: `${scale === 1 ? 32 : 32 * scale}px`,
          fontWeight: 'normal',
          color: '#ffffff',
          lineHeight: 1.4,
          fontFamily: 'Inter, system-ui, -apple-system, sans-serif',
          margin: 0
        }}>
          {ad.body}
        </p>
      </div>

      {/* Bottom strip - 8% */}
      <div style={{
        flex: '0 0 8%',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: `0 ${60 * scale}px`,
        backgroundColor: 'rgba(0, 0, 0, 0.2)'
      }}>
        <span style={{
          fontSize: `${scale === 1 ? 24 : 24 * scale}px`,
          fontWeight: 'bold',
          color: '#ffffff',
          fontFamily: 'Inter, system-ui, -apple-system, sans-serif'
        }}>
          EverReach
        </span>
        <span style={{
          fontSize: `${scale === 1 ? 18 : 18 * scale}px`,
          fontWeight: 'normal',
          color: '#ffffff',
          fontFamily: 'Inter, system-ui, -apple-system, sans-serif',
          opacity: 0.9
        }}>
          Your network never goes cold.
        </span>
      </div>
    </div>
  )
}
