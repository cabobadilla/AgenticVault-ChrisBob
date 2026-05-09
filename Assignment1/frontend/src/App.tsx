import { BrowserRouter, Routes, Route } from "react-router-dom"
import Landing from "./pages/Landing"
import ChatKitAgent from "./pages/ChatKitAgent"
import FeedbackAdmin from "./pages/FeedbackAdmin"

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/projects/chatkit-agent" element={<ChatKitAgent />} />
        <Route path="/admin/feedback" element={<FeedbackAdmin />} />
      </Routes>
    </BrowserRouter>
  )
}
