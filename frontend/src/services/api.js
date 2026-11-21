import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});



export const scoreJob = (job_description) => {
    return api.post('/scorer', { job_description })
}
export const generateCoverLetter = (job_description, fitCategory, matchingPoints, softSkills, profileChunks, reasoning) => {
    return api.post('/cover_letter', { 
        job_description,
        fit_category: fitCategory,
        matching_points: matchingPoints,
        soft_skills: softSkills,
        profile_chunks: profileChunks,
        reasoning
    })
}
export const upsertPreferences = (preferences) => {
    return api.post('/upsert_preferences', {
        preferences // Sent directly as the JSON body
    })
}
    
export const getPreferences = () => {
    return api.get('/get_preferences')
}
export const chatWithAi = (message) => {
    return api.post('/chat', { message })
}

export const streamChatWithAi = async (message, onDelta, onDone, onError) => {
    const baseURL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api/v1'

    const response = await fetch(`${baseURL}/chat/stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message }),
    })

    if (!response.ok) {
        throw new Error(`Chat request failed with status ${response.status}`)
    }

    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const events = buffer.split('\n\n')
        buffer = events.pop() || ''

        for (const event of events) {
            const line = event.split('\n').find(item => item.startsWith('data: '))
            if (!line) continue

            const data = line.slice(6)
            if (data === '[DONE]') {
                onDone?.()
                return
            }

            try {
                const payload = JSON.parse(data)
                if (payload.error) {
                    onError?.(payload.error)
                    return
                }
                if (payload.delta) onDelta(payload.delta)
            } catch {
                onError?.('Invalid stream response')
                return
            }
        }
    }

    onDone?.()
}

export const getDocuments = () => {
    return api.get('/get_documents')
}
export const getRecordsCount  = () =>{
    return api.get('/get_records_count')
}

export const ingestCV = (file) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post('/upload_cv', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
    })
}

export const ingestDocument = (file) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post('/ingest_document', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
    })
}

export const getCV = () => {
    return api.get("/get_cv")
}


export default api

