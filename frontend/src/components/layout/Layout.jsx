import { Outlet } from 'react-router-dom'
import Sidebar from './Sidebar'

export default function Layout() {
  return (
    <div className="flex flex-col h-screen bg-[#1A1A1A] ">
      
      {/* Top bar */}
      <div className="flex justify-between items-center px-6 py-3 bg-[#1A1A1A] border-b border-[#2E2E2E] shrink-0">
        <span className="text-white font-bold text-lg">Sumud AI</span>
        <div className="w-9 h-9 rounded-full bg-[#C8102E] flex items-center justify-center text-white text-sm font-bold">
          AJ
        </div>
      </div>

      {/* Body */}
      <div className="flex flex-1 overflow-hidden">
        <Sidebar />
        <main className="flex-1 overflow-y-auto bg-[#242424]">
          <Outlet />
        </main>
      </div>

    </div>
  )
}