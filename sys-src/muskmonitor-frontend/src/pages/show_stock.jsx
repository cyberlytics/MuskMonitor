import React from 'react';
import ShowStock from '../components/ShowStock_combined.jsx';
import HamburgerMenu from '../components/HamburgerMenu.jsx';
import './ShowStockPage.css'; // Importiere die CSS-Datei für die Stile

function ShowStockPage() {
  return (
    <div className="stock-page">
      <HamburgerMenu />
      <div className="content">
        <ShowStock />
      </div>
    </div>
  );
}

export default ShowStockPage;