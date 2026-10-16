import axios from 'axios';

const api = axios.create({
  baseURL: 'http://127.0.0.1:8000/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});



export const scoreJob = (job_description) => {
    return api.post('/scorer', { job_description })
}
export const generateCoverLetter = (job_description) => {
    return api.post('/cover_letter', { job_description })
}
export const upsertPreferences = (preferences) => {
    return api.post('/upsert_preferences', {
        preferences // Sent directly as the JSON body
    })
}
    
export const getPreferences = () => {
    return api.get('/get_preferences')
}
export const sendMessage = (message) => {
    return api.post('/chat', { message })
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

export const chatWithAi = (message) => {
    return api.post("chat", message)
}
   


export default api

