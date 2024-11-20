import { useNavigate } from "react-router-dom";

function show_stock() {
  let navigate = useNavigate();

  navigate("/show_tweets");
}
