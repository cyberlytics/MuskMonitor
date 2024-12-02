import { useNavigate } from "react-router-dom";

export default function Home() {
  let navigate = useNavigate();
  function handleTweetClick() {
    navigate("/tweets");
  }
  function handleStockClick() {}
  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        minHeight: "100vh",
        minWidth: "100vw",
        backgroundImage: "url('MuskMonitor.png')",
        backgroundSize: "cover",
        backgroundPosition: "center",
      }}
    >
      <div style={{ textAlign: "center", padding: "20px" }}>
        <button onClick={handleTweetClick}>Weiter zu Tweets</button>
        <button onClick={handleStockClick}>Weiter zu Stock Preise</button>
      </div>
    </div>
  );
}
