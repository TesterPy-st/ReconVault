// Mock graph data used when the backend is unavailable

export const mockGraphData = {
  nodes: [
    {
      id: '1',
      value: 'malware-c2.example.com',
      type: 'DOMAIN',
      riskLevel: 'CRITICAL',
      riskScore: 0.95,
      confidence: 0.9,
      source: 'VIRUSTOTAL',
      connections: 5,
      size: 20,
      color: '#ff0033',
      metadata: {
        firstSeen: '2024-01-15T10:30:00Z',
        lastSeen: '2024-01-20T14:22:00Z',
        categories: ['malware', 'command-and-control'],
        threatIntel: {
          score: 95,
          sources: ['VT', 'Shodan', 'AlienVault']
        }
      },
      created_at: '2024-01-15T10:30:00Z',
      updated_at: '2024-01-20T14:22:00Z'
    },
    {
      id: '2',
      value: '192.168.1.100',
      type: 'IP_ADDRESS',
      riskLevel: 'HIGH',
      riskScore: 0.75,
      confidence: 0.85,
      source: 'SHODAN',
      connections: 8,
      size: 16,
      color: '#ff6600',
      metadata: {
        geo: { country: 'US', city: 'New York' },
        openPorts: [22, 80, 443, 8080],
        org: 'Suspicious Organization'
      },
      created_at: '2024-01-18T09:15:00Z',
      updated_at: '2024-01-20T12:00:00Z'
    },
    {
      id: '3',
      value: 'phishing@malicious.net',
      type: 'EMAIL',
      riskLevel: 'MEDIUM',
      riskScore: 0.65,
      confidence: 0.8,
      source: 'WEB_SCRAPER',
      connections: 3,
      size: 12,
      color: '#ffaa00',
      metadata: {
        domain: 'malicious.net',
        associatedCampaigns: ['Phish-2024-001'],
        reports: 12
      },
      created_at: '2024-01-16T16:45:00Z',
      updated_at: '2024-01-19T11:30:00Z'
    },
    {
      id: '4',
      value: 'suspicious-user',
      type: 'USERNAME',
      riskLevel: 'LOW',
      riskScore: 0.35,
      confidence: 0.7,
      source: 'SOCIAL_MEDIA',
      connections: 2,
      size: 10,
      color: '#00dd00',
      metadata: {
        platforms: ['Twitter', 'LinkedIn'],
        followers: 1250,
        verified: false
      },
      created_at: '2024-01-17T14:20:00Z',
      updated_at: '2024-01-18T08:45:00Z'
    },
    {
      id: '5',
      value: 'secure-corp.com',
      type: 'DOMAIN',
      riskLevel: 'INFO',
      riskScore: 0.15,
      confidence: 0.95,
      source: 'MANUAL',
      connections: 4,
      size: 8,
      color: '#00d9ff',
      metadata: {
        legitimate: true,
        sslCertificate: true,
        whoisInfo: 'Registered 2020'
      },
      created_at: '2024-01-10T12:00:00Z',
      updated_at: '2024-01-20T16:00:00Z'
    }
  ],
  edges: [
    {
      id: 'e1',
      source: '1',
      target: '2',
      type: 'COMMUNICATES_WITH',
      confidence: 0.9,
      strength: 0.8,
      metadata: {
        protocols: ['HTTP', 'HTTPS'],
        frequency: 'daily',
        dataVolume: '2.3MB'
      },
      created_at: '2024-01-15T10:30:00Z',
      updated_at: '2024-01-20T14:22:00Z'
    },
    {
      id: 'e2',
      source: '2',
      target: '3',
      type: 'OWNS',
      confidence: 0.75,
      strength: 0.6,
      metadata: {
        evidence: ['Email headers', 'Server logs'],
        timeframe: '2024-01-16 to 2024-01-19'
      },
      created_at: '2024-01-16T16:45:00Z',
      updated_at: '2024-01-19T11:30:00Z'
    },
    {
      id: 'e3',
      source: '3',
      target: '4',
      type: 'MENTIONS',
      confidence: 0.6,
      strength: 0.4,
      metadata: {
        platform: 'Twitter',
        mentions: 5,
        sentiment: 'negative'
      },
      created_at: '2024-01-17T14:20:00Z',
      updated_at: '2024-01-18T08:45:00Z'
    },
    {
      id: 'e4',
      source: '5',
      target: '2',
      type: 'PART_OF',
      confidence: 0.85,
      strength: 0.7,
      metadata: {
        relationship: 'infrastructure',
        dnsRecords: ['A', 'MX', 'NS']
      },
      created_at: '2024-01-10T12:00:00Z',
      updated_at: '2024-01-20T16:00:00Z'
    }
  ]
};
