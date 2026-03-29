import { BrowserRouter, Route, Routes } from "react-router-dom";
import { VisualPreferencesProvider } from "./context/VisualPreferencesContext";
import { Landing } from "./pages/Landing";
import { Login } from "./pages/Login";
import { VoiceCircle } from "./pages/VoiceCircle";

export default function App() {
  return (
    <VisualPreferencesProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route path="/login" element={<Login />} />
          <Route path="/voice" element={<VoiceCircle />} />
        </Routes>
      </BrowserRouter>
    </VisualPreferencesProvider>
  );
}
