import { useState, useEffect } from 'react'
import { getRecordsCount, getPreferences, upsertPreferences } from '../services/api'

export default function Dashboard() {
    const [count, setCount] = useState(0)
    const [preferences, setPreferences] = useState('Not set yet')
    const [newPreferences, setNewPreferences] = useState('')

    useEffect(() => {
        getRecordsCount()
            .then((res) => setCount(res.data))
            .catch(err => console.error(err))
        
        getPreferences()
            .then(res => {
                setPreferences(res.data?.preferences ?? 'Not set yet')
            })
            .catch(err => console.error(err))
    }, [])

    const handleSavePreferences = () => {
        alert('Preferences update coming soon!')
        // upsertPreferences(newPreferences)
        //     .then(() => {
        //         console.log("Saving preferences:", newPreferences)
        //         setPreferences(newPreferences)
        //         alert('Preferences saved!')
        //     })
        //     .catch(err => console.error(err))
    }

    return (
        <div className="page-inner">
            <section className="hero-panel panel reveal">
                <div className="hero-copy">
                    <div className="eyebrow">Personal career office</div>
                    <h1>Stay steady. <em>Move forward.</em></h1>
                    <p>Sumud turns your experience into clearer applications, stronger matches, and better conversations.</p>
                </div>
                <div className="hero-number">
                    <strong>{String(count).padStart(2, '0')}</strong>
                    <span>Knowledge units</span>
                </div>
            </section>

            <div className="stats-grid">
                <section className="stat-card panel reveal">
                    <p className="stat-label">Documents stored</p>
                    <p className="stat-value green">{count}</p>
                    <p className="stat-detail">Ready for contextual scoring</p>
                </section>
                <section className="stat-card panel reveal">
                    <p className="stat-label">Current profile signal</p>
                    <p className="stat-value" style={{ fontSize: '18px', lineHeight: 1.25 }}>
                        {preferences === 'Not set yet' ? 'Profile preferences open' : preferences}
                    </p>
                </section>
            </div>

            <section className="field-panel panel reveal">
                <h2>Career preferences</h2>
                <textarea
                    className="text-field"
                    style={{ minHeight: '112px', padding: '16px' }}
                    placeholder="Remote, full-time, Berlin, open to relocation..."
                    value={newPreferences}
                    onChange={(e) => setNewPreferences(e.target.value)}
                />
                <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '12px' }}>
                    <button onClick={handleSavePreferences} className="primary-button">Save preferences</button>
                </div>
            </section>
        </div>
    )
}