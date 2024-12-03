import React from 'react';
import { Link } from 'react-router-dom';
import './ShowStartPage.css'; // Importiere die CSS-Datei für die Stile
import HamburgerMenu from '../components/HamburgerMenu.jsx'; // Importiere das HamburgerMenu-Komponente

function ShowStartPage() {
  return (
    <div className="start-page">
      <h1>Wilkommen auf dem MuskMonitor</h1>
      <div className="button-container">
        <Link to="/show_stock" className="button">
          Stock-Price-Prediction
        </Link>
        <Link to="/show_tweets" className="button">
          Elon Musk Tweet Feed
        </Link>
      </div>
    </div>
  );
}

export default ShowStartPage;