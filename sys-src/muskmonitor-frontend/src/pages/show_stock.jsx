import React from 'react';
//import ShowStock from '../components/ShowStock.jsx';
import ShowStock from '../components/ShowStock_historical.jsx';
import HamburgerMenu from '../components/HamburgerMenu.jsx';

function ShowStockPage() {
  return (
    <div>
      <HamburgerMenu />
      <ShowStock />
    </div>
  );
}

export default ShowStockPage;