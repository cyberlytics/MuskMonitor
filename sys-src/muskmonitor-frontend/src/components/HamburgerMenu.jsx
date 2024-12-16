import React, { useState } from "react";
import { Link } from "react-router-dom";
import {
  Drawer,
  IconButton,
  List,
  ListItem,
  ListItemText,
} from "@mui/material";
import MenuIcon from "@mui/icons-material/Menu";
import CloseIcon from "@mui/icons-material/Close";
import "./HamburgerMenu.css";

function HamburgerMenu() {
  const [open, setOpen] = useState(false);

  const toggleDrawer = (open) => (event) => {
    if (event.type === 'keydown' && (event.key === 'Tab' || event.key === 'Shift')) {
      return;
    }
    setOpen(open);
  };

  return (
    <div className="hamburger-menu">
      <IconButton edge="start" color="inherit" aria-label="menu" onClick={toggleDrawer(true)}>
        <MenuIcon />
      </IconButton>
      <Drawer anchor="left" open={open} onClose={toggleDrawer(false)}>
        <div
          role="presentation"
          onClick={toggleDrawer(false)}
          onKeyDown={toggleDrawer(false)}
          className="drawer-content"
        >
          <IconButton edge="start" color="inherit" aria-label="close" onClick={toggleDrawer(false)} className="close-button">
            <CloseIcon />
          </IconButton>
          <List>
            <ListItem button component={Link} to="/">
              <ListItemText primary="Home" />
            </ListItem>
            <ListItem button component={Link} to="/show_stock">
              <ListItemText primary="Stock-Price-Prediction" />
            </ListItem>
            <ListItem button component={Link} to="/show_tweets">
              <ListItemText primary="Elon Musk Tweet Feed" />
            </ListItem>
          </List>
        </div>
      </Drawer>
    </div>
  );
}

export default HamburgerMenu;