import { BrowserRouter, Route, Routes } from "react-router-dom";
import { VisualPreferencesProvider } from "./context/VisualPreferencesContext";
import { AccessibilityPage } from "./pages/AccessibilityPage";
import { Company } from "./pages/Company";
import { Landing } from "./pages/Landing";
import { Login } from "./pages/Login";
import { Product } from "./pages/Product";
import { VoiceCircle } from "./pages/VoiceCircle";

export default function App() {
  return (
    <VisualPreferencesProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route path="/product" element={<Product />} />
          <Route path="/company" element={<Company />} />
          <Route path="/accessibility" element={<AccessibilityPage />} />
          <Route path="/login" element={<Login />} />
          <Route path="/voice" element={<VoiceCircle />} />
        </Routes>
      </BrowserRouter>
    </VisualPreferencesProvider>
  );
}
