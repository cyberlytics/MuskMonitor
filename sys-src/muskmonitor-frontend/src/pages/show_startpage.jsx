import React from 'react';
import { Link } from 'react-router-dom';
import './ShowStartPage.css';
import HamburgerMenu from '../components/HamburgerMenu.jsx';
import elonFace1 from '../assets/elon_face_2.png'; // Importiere das Bild
import elonFace2 from '../assets/elon_face.png'; // Importiere das Bild

function ShowStartPage() {
  return (
    <div className="start-page">
      <HamburgerMenu />
      <h1>Wilkommen auf dem MuskMonitor</h1>
      <div className="image-container">
        <img src={elonFace1} alt="Elon Musk 1" className="elon-image-left left-image" />
        <img src={elonFace2} alt="Elon Musk 2" className="elon-image-right right-image" />
      </div>
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