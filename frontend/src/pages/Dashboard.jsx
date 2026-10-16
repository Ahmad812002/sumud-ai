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
        <div className="text-white p-6">
            
            {/* Welcome Section */}
            <div className="bg-[#2A2A2A] rounded-xl p-6 mb-6 border border-[#2E2E2E]">
                <h1 className="text-3xl font-bold text-[#007A3D] mb-2">
                    Be Sumud in your life.
                </h1>
                <p className="text-[#A0A0A0] text-sm leading-relaxed">
                    Sumud AI is your personal career coach — helping you find the right job, 
                    score your fit, and generate tailored cover letters using your own data.
                    I built this while actively searching for a job myself.
                </p>
                <p className="text-[#A0A0A0] text-sm mt-2">
                    Feedback welcome: 
                    <a href="mailto:ahmad812002@gmail.com" 
                       className="text-[#C8102E] ml-1 hover:underline">
                        ahmad812002@gmail.com
                    </a>
                </p>
            </div>

            {/* Stats Row */}
            <div className="grid grid-cols-2 gap-4 mb-6">
                <div className="bg-[#2A2A2A] rounded-xl p-4 border border-[#2E2E2E]">
                    <p className="text-[#A0A0A0] text-xs mb-1">Documents Stored</p>
                    <p className="text-3xl font-bold text-[#007A3D]">{count}</p>
                </div>
                <div className="bg-[#2A2A2A] rounded-xl p-4 border border-[#2E2E2E]">
                    <p className="text-[#A0A0A0] text-xs mb-1">Preferences</p>
                    <p className="text-sm text-white">
                        {preferences}
                    </p>
                </div>
            </div>

            {/* Preferences Section */}
            <div className="bg-[#2A2A2A] rounded-xl p-6 border border-[#2E2E2E]">
                <h2 className="text-lg font-semibold mb-4">Update Preferences</h2>
                <textarea
                    className="w-full bg-[#1A1A1A] text-white border border-[#2E2E2E] rounded-lg p-3 text-sm resize-none focus:outline-none focus:border-[#C8102E]"
                    rows={3}
                    placeholder="e.g. remote, full-time, Germany, open to relocation..."
                    value={newPreferences}
                    onChange={(e) => setNewPreferences(e.target.value)}
                />
                <button
                    onClick={handleSavePreferences}
                    className="mt-3 bg-[#C8102E] hover:bg-red-700 text-white px-6 py-2 rounded-lg text-sm transition-colors"
                >
                    Save Preferences
                </button>
            </div>

        </div>
    )
}