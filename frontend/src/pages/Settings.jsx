import { useState, useEffect, useRef } from 'react'
import { 
    ingestDocument, getRecordsCount, getCV, upload_CV } from '../services/api'
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
            .then(res => setCvUrl(`${import.meta.env.VITE_BASE_URL}${res.data.cv_url}`))
            .catch(() => setCvUrl(null))  // no CV yet, show upload zone
        getRecordsCount()
            .then(res => setCount(res.data))
            .catch(err => console.error(err))

        const timer = setTimeout(() => {
            setMessage('');
        }, 10000);
        return () => clearTimeout(timer);
        
    }, [message])

    const getMessageColor = (msg) => {
        if (msg.startsWith('✓')) return 'text-[#007A3D]';
        if (msg.startsWith('✗')) return 'text-[#C8102E]';
        if (msg.startsWith('ℹ')) return 'text-yellow-600';
        return 'text-gray-700'; // Default fallback
    };
    

    const ingestFile = async (file) => {
        
        setLoading(true)
        setMessage(null)
        try {
            const res = await ingestDocument(file)
            console.log(res.data)
            
            if(res.data?.message?.includes("ingested successfully")){
                setMessage(`✓ ${file.name} ingested successfully`)
                const res = await getRecordsCount()
                setCount(res.data)
            }

                
        } catch (err) {
            console.log(err.response?.status)
            console.log(err.response?.data?.detail)
            if(err.response?.status === 409) setMessage(`ℹ ${err.response?.data?.detail}`)
            else if (err.response?.status === 401) setMessage(`ℹ ${err.response?.data?.detail}`)
            else if (err.repsonse?.status === 403) setMessage(`ℹ ${err.response?.data?.detail}`)
            else {
                setMessage(`✗ Failed to ingest ${file.name}, ${err.response?.data?.detail}`)
            }
            
        } finally {
            setLoading(false)
        }
    }

    const uploadCV = async (file) => {
        const formData = new FormData()
        formData.append('file', file)
        setCvLoading(true)
        try {
            const uploadRes = await upload_CV(file)

            if(uploadRes.data.message == `A CV with the name ${file.name} is already uploaded.`){
                setMessage(`✗ A CV with the name ${file.name} is already uploaded.`)
                return
            }

            const ingestRes = await ingestDocument(file)
            console.log(ingestRes.data)
            if(ingestRes.data.message.includes("is already ingested.")){
                setMessage(`✗ A document with the name ${file.name} is already ingested.`)
                return
            }
            
            

            setCvUrl(`${import.meta.env.VITE_BASE_URL}${uploadRes.data.cv_url}`)
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
                            <p className="text-[#A0A0A0] text-xs mt-2">
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
                            <p className={`mt-3 text-sm ${ getMessageColor(message) }`}>
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