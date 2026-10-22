import { useState, useEffect, useRef } from 'react'
import { ingestDocument, getRecordsCount, ingestCV, getCV } from '../services/api'
import axios from 'axios'

function Spinner() {
    return (
        <div className="flex items-center justify-center py-4">
            <div className="w-6 h-6 border-4 border-[#C8102E] border-t-transparent rounded-full animate-spin" />
        </div>
    )
}

export default function Settings() {
    const [count, setCount] = useState(0)
    const [loading, setLoading] = useState(false)
    const [cvLoading, setCvLoading] = useState(false)
    const [message, setMessage] = useState(null)
    const [cvUrl, setCvUrl] = useState(null)
    const [dragging, setDragging] = useState(false)
    const fileInputRef = useRef(null)
    const cvInputRef = useRef(null)

    useEffect(() => {
        getCV()
            .then(res => setCvUrl(`${import.meta.env.PORT}${res.data.cv_url}`))
            .catch(() => setCvUrl(null))  // no CV yet, show upload zone
        getRecordsCount()
            .then(res => setCount(res.data))
            .catch(err => console.error(err))
    }, [])

    const ingestFile = async (file) => {
        
        setLoading(true)
        setMessage(null)
        
        try {
            const res = await ingestDocument(file)
            if(res.data.message){
                setMessage(`✓ ${file.name} ingested successfully`)
                const res = await getRecordsCount()
                setCount(res.data)
            }
                
        } catch (err) {
            setMessage(`✗ Failed to ingest ${file.name}`)
            console.error(err)
        } finally {
            setLoading(false)
        }
    }

    const uploadCV = async (file) => {
        const formData = new FormData()
        formData.append('file', file)
        setCvLoading(true)
        try {
            const res = await ingestCV(file)
            

            setCvUrl(`${import.meta.env.PORT}${res.data.cv_url}`)
        } catch (err) {
            console.error(err)
            alert('CV upload failed')
        } finally {
            setCvLoading(false)
        }
    }

    // Drag and drop handlers
    const handleDragOver = (e) => {
        e.preventDefault()
        setDragging(true)
    }

    const handleDragLeave = () => setDragging(false)

    const handleDrop = (e) => {
        e.preventDefault()
        setDragging(false)
        const file = e.dataTransfer.files[0]
        if (file) ingestFile(file)
    }

    const handleFileSelect = (e) => {
        const file = e.target.files[0]
        if (file) ingestFile(file)
    }

    const handleCvSelect = (e) => {
        const file = e.target.files[0]
        if (file) uploadCV(file)
    }

    return (
        <div className="text-white p-6 max-w-6xl mx-auto">
            
            <h1 className="text-2xl font-bold mb-1">Settings</h1>
            <p className="text-[#A0A0A0] text-sm mb-6">
                Manage your knowledge base and CV.
            </p>

            <div className="grid grid-cols-2 gap-6">

                {/* Left Column */}
                <div className="space-y-6">

                    {/* Stats */}
                    <div className="bg-[#2A2A2A] rounded-xl p-5 border border-[#2E2E2E]">
                        <h2 className="text-sm font-semibold text-[#A0A0A0] mb-3">
                            KNOWLEDGE BASE
                        </h2>
                        <div className="flex items-center gap-3">
                            <span className="text-4xl font-bold text-[#007A3D]">{count}</span>
                            <span className="text-[#A0A0A0] text-sm">chunks stored</span>
                        </div>
                    </div>

                    {/* Document Upload — Drag and Drop */}
                    <div className="bg-[#2A2A2A] rounded-xl p-5 border border-[#2E2E2E]">
                        <h2 className="text-sm font-semibold text-[#A0A0A0] mb-3">
                            ADD DOCUMENT
                        </h2>

                        {/* Drop Zone */}
                        <div
                            onDragOver={handleDragOver}
                            onDragLeave={handleDragLeave}
                            onDrop={handleDrop}
                            onClick={() => fileInputRef.current.click()}
                            className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-colors
                                ${dragging 
                                    ? 'border-[#C8102E] bg-[#C8102E]/10' 
                                    : 'border-[#2E2E2E] hover:border-[#C8102E]/50'
                                }`}
                        >
                            <p className="text-[#A0A0A0] text-sm mb-1">
                                Drag & drop a file here
                            </p>
                            <p className="text-[#A0A0A0] text-xs">
                                or click to browse
                            </p>
                            <p className="text-[#2E2E2E] text-xs mt-2">
                                PDF, TXT, DOCX, MD
                            </p>
                        </div>

                        <input
                            ref={fileInputRef}
                            type="file"
                            accept=".pdf,.txt,.docx,.md"
                            className="hidden"
                            onChange={handleFileSelect}
                        />

                        {loading && <Spinner />}

                        {message && (
                            <p className={`mt-3 text-sm ${
                                message.startsWith('✓') 
                                    ? 'text-[#007A3D]' 
                                    : 'text-[#C8102E]'
                            }`}>
                                {message}
                            </p>
                        )}
                    </div>
                </div>

                {/* Right Column — CV */}
                <div className="bg-[#2A2A2A] rounded-xl p-5 border border-[#2E2E2E]">
                    <h2 className="text-sm font-semibold text-[#A0A0A0] mb-3">
                        YOUR CV
                    </h2>

                    {cvUrl ? (
                        <div>
                            <iframe
                                src={cvUrl}
                                className="w-full h-80 rounded-lg border border-[#2E2E2E] mb-3"
                                title="Your CV"
                            />
                            <button
                                onClick={() => cvInputRef.current.click()}
                                className="w-full border border-[#2E2E2E] hover:border-white text-[#A0A0A0] hover:text-white py-2 rounded-lg text-sm transition-colors"
                            >
                                Replace CV
                            </button>
                        </div>
                    ) : (
                        <div
                            onClick={() => cvInputRef.current.click()}
                            className="border-2 border-dashed border-[#2E2E2E] hover:border-[#007A3D]/50 rounded-xl p-8 text-center cursor-pointer transition-colors h-80 flex flex-col items-center justify-center"
                        >
                            {cvLoading ? <Spinner /> : (
                                <>
                                    <p className="text-[#A0A0A0] text-sm mb-1">
                                        Upload your CV
                                    </p>
                                    <p className="text-[#A0A0A0] text-xs">
                                        PDF only — displayed as preview
                                    </p>
                                </>
                            )}
                        </div>
                    )}

                    <input
                        ref={cvInputRef}
                        type="file"
                        accept=".pdf"
                        className="hidden"
                        onChange={handleCvSelect}
                    />
                </div>
            </div>
        </div>
    )
}