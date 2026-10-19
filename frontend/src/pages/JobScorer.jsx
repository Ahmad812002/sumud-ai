import { useState } from 'react'
import { scoreJob, generateCoverLetter } from '../services/api'
import { Spinner } from './Spinner'


// Score circle component
function ScoreCircle({ score }) {
    const color = score >= 80 ? '#007A3D' : score >= 60 ? '#C8102E' : '#A0A0A0'
    return (
        <div className="flex flex-col items-center justify-center w-28 h-28 rounded-full border-4"
             style={{ borderColor: color }}>
            <span className="text-3xl font-bold text-white">{score}</span>
            <span className="text-xs text-[#A0A0A0]">/ 100</span>
        </div>
    )
}

export default function JobScorer() {
    const [jobDescription, setJobDescription] = useState('')
    const [scorerResult, setScorerResult] = useState(null)
    const [coverLetter, setCoverLetter] = useState(null)
    const [loadingScore, setLoadingScore] = useState(false)
    const [loadingCover, setLoadingCover] = useState(false)
    const [editableLetter, setEditableLetter] = useState('')

    const handleScore = async () => {
        if (jobDescription.trim().length < 50) {
            alert('Please paste a full job description.')
            return
        }
        try {
            setLoadingScore(true)
            setScorerResult(null)
            setCoverLetter(null)
            const res = await scoreJob(jobDescription)
            console.log(res.data)
            setScorerResult(res.data)
        } catch (err) {
            console.error(err)
            alert('Scoring failed. Make sure the backend is running.')
        } finally {
            setLoadingScore(false)
        }
    }

    const handleGenerateCoverLetter = async () => {
        try {
            setLoadingCover(true)
            const res = await generateCoverLetter(jobDescription,
                scorerResult.fit_category,
                scorerResult.matching_points, 
                scorerResult.gaps,
                scorerResult.profile_chunks,
                scorerResult.reasoning
            )
            const letter = res.data
            
            setCoverLetter(letter)
            setEditableLetter(
                `${letter.opening}\n\n${letter.middle}\n\n${letter.gap}\n\n${letter.closing}`
            )
        } catch (err) {
            console.error(err)
            alert('Cover letter generation failed.')
        } finally {
            setLoadingCover(false)
        }
    }

    return (
        <div className="text-white p-6 max-w-6xl mx-auto overflow-y-auto translate-y-0">

            {/* Header */}
            <h1 className="text-2xl font-bold mb-1">Job Scorer</h1>
            <p className="text-[#A0A0A0] text-sm mb-6">
                Paste a job description to see how well it matches your profile.
            </p>

            {/* Input Section */}
            <div className="bg-[#2A2A2A] rounded-xl p-6 border border-[#2E2E2E] mb-6 h-auto">
                <textarea
                    className="w-full h-60 bg-[#1A1A1A] text-white border border-[#2E2E2E] rounded-lg p-4 text-sm resize-none focus:outline-none focus:border-[#C8102E] transition-colors"
                    rows={6}
                    placeholder="Paste the full job description here..."
                    value={jobDescription}
                    onChange={(e) => setJobDescription(e.target.value)}
                />
                <button
                    onClick={handleScore}
                    disabled={loadingScore}
                    className=" bg-[#C8102E] hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed text-white px-8 py-2.5 rounded-lg text-sm font-medium transition-colors"
                >
                    {loadingScore ? 'Scoring...' : 'Score This Job'}
                </button>
            </div>

            {/* Loading */}
            {loadingScore && <Spinner />}

            {/* Results */}
            {scorerResult && (
                <div className="bg-[#2A2A2A] rounded-xl p-6 border border-[#2E2E2E] mb-6 animate-fade-in">
                    
                    {/* Score Header */}
                    <div className="flex items-center gap-6 mb-6 pb-6 border-b border-[#2E2E2E]">
                        <ScoreCircle score={scorerResult.fit_score} />
                        <div>
                            <p className="text-[#A0A0A0] text-xs mb-1">Fit Category</p>
                            <p className="text-xl font-bold text-white">
                                {scorerResult.fit_category}
                            </p>
                            <p className="text-[#A0A0A0] text-sm mt-1">
                                {scorerResult.reasoning}
                            </p>
                        </div>
                    </div>

                    {/* Matching Points */}
                    <div className="mb-4">
                        <h3 className="text-sm font-semibold text-[#007A3D] mb-2">
                            ✓ Matching Points
                        </h3>
                        <ul className="space-y-1">
                            {scorerResult.matching_points.map((point, i) => (
                                <li key={i} className="text-sm text-[#A0A0A0] flex gap-2">
                                    <span className="text-[#007A3D]">•</span>
                                    {point}
                                </li>
                            ))}
                        </ul>
                    </div>

                    {/* Gaps */}
                    {scorerResult.gaps.length > 0 && (
                        <div className="mb-6">
                            <h3 className="text-sm font-semibold text-[#C8102E] mb-2">
                                ✗ Gaps
                            </h3>
                            <ul className="space-y-1">
                                {scorerResult.gaps.map((gap, i) => (
                                    <li key={i} className="text-sm text-[#A0A0A0] flex gap-2">
                                        <span className="text-[#C8102E]">•</span>
                                        {gap}
                                    </li>
                                ))}
                            </ul>
                        </div>
                    )}

                    {/* Generate Cover Letter Button */}
                    <button
                        onClick={handleGenerateCoverLetter}
                        disabled={loadingCover}
                        className="w-full bg-[#007A3D] hover:bg-green-800 disabled:opacity-50 disabled:cursor-not-allowed text-white py-3 rounded-lg text-sm font-medium transition-colors"
                    >
                        {loadingCover ? 'Generating...' : 'Generate Cover Letter'}
                    </button>
                </div>
            )}

            {/* Cover Letter Loading */}
            {loadingCover && <Spinner />}

            {/* Cover Letter Result */}
            {coverLetter && (
                <div className="bg-[#2A2A2A] rounded-xl p-6 border border-[#2E2E2E]">
                    <div className="flex justify-between items-center mb-4">
                        <h2 className="text-lg font-semibold">Cover Letter</h2>
                        <span className="text-xs text-[#A0A0A0]">You can edit below</span>
                    </div>
                    <textarea
                        className="w-full bg-[#1A1A1A] text-white border border-[#2E2E2E] rounded-lg p-4 text-sm resize-none focus:outline-none focus:border-[#C8102E] leading-relaxed"
                        rows={16}
                        value={editableLetter}
                        onChange={(e) => setEditableLetter(e.target.value)}
                    />
                    <div className="flex gap-3 mt-4">
                        <button
                            onClick={() => navigator.clipboard.writeText(editableLetter)}
                            className="flex-1 border border-[#2E2E2E] hover:border-white text-white py-2.5 rounded-lg text-sm transition-colors"
                        >
                            Copy to Clipboard
                        </button>
                        <button
                            className="flex-1 bg-[#C8102E] hover:bg-red-700 text-white py-2.5 rounded-lg text-sm transition-colors"
                            onClick={() => alert('PDF download coming soon!')}
                        >
                            Download PDF
                        </button>
                    </div>
                </div>
            )}

        </div>
    )
}