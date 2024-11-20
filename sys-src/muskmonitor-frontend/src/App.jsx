import { BrowserRouter, Routes, Route } from "react-router-dom";
import "./App.css";

function App() {

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/home" element={<HomeScreen />} />
        <Route path="/gallery" element={<Gallery />} />
        <Route path="/transfer" element={<StyleTransfer />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
