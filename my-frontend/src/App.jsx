import { useEffect, useState } from "react";
import "./App.css";

function App() {
  const [message, setMessage] = useState("Loading...");

  useEffect(() => {
    fetch("https://ioss-assessment.onrender.com/")
      .then((res) => res.json())
      .then((data) => setMessage(data.message))
      .catch(() => setMessage("Failed to fetch backend"));
  }, []);

  return (
    <div style={{ textAlign: "center", marginTop: "50px" }}>
      <h1>Frontend + Backend Deployment Test</h1>
      <p>Backend says: {message}</p>
    </div>
  );
}

export default App;
