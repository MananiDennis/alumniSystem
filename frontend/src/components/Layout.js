import React, { useState } from "react";
import {
  Box,
  Drawer,
  AppBar,
  Toolbar,
  Typography,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  IconButton,
  Avatar,
  Menu,
  MenuItem,
} from "@mui/material";
import {
  Dashboard,
  People,
  DataUsage,
  Analytics,
  Settings,
  Menu as MenuIcon,
  Logout,
} from "@mui/icons-material";

const Layout = ({ children, user, onLogout, currentPage, onPageChange }) => {
  const [mobileOpen, setMobileOpen] = useState(false);
  const [desktopOpen, setDesktopOpen] = useState(true);
  const [anchorEl, setAnchorEl] = useState(null);

  const menuItems = [
    { text: "Dashboard", icon: <Dashboard />, id: "dashboard" },
    { text: "Alumni", icon: <People />, id: "alumni" },
    { text: "Data Collection", icon: <DataUsage />, id: "collection" },
    { text: "AI Analytics", icon: <Analytics />, id: "analytics" },
    { text: "Settings", icon: <Settings />, id: "settings" },
  ];

  const drawer = (
    <Box
      sx={{
        background: "linear-gradient(180deg, #1a1a1a 0%, #2d2d2d 100%)",
        height: "100%",
        color: "white",
      }}
    >
      <Box
        sx={{
          p: 3,
          textAlign: "center",
          borderBottom: "1px solid rgba(255,255,255,0.1)",
        }}
      >
        <Box
          sx={{
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            gap: 2,
            py: 2,
          }}
        >
          <img
            src="/img/Edith_Cowan_University_Logo.svg"
            alt="Edith Cowan University Logo"
            style={{ height: "50px", width: "auto", maxWidth: "150px" }}
          />
          <Box sx={{ textAlign: "left" }}>
            <Typography variant="h6" fontWeight="bold">
              ECU Alumni
            </Typography>
            <Typography variant="caption" sx={{ opacity: 0.8 }}>
              Tracking System
            </Typography>
          </Box>
        </Box>
      </Box>

      <List sx={{ pt: 2 }}>
        {menuItems.map((item) => (
          <ListItem
            button
            key={item.id}
            selected={currentPage === item.id}
            onClick={() => onPageChange(item.id)}
            sx={{
              mx: 1,
              mb: 1,
              borderRadius: 2,
              bgcolor:
                currentPage === item.id ? "rgba(255,255,255,0.15)" : "inherit",
              "&:hover": { bgcolor: "rgba(255,255,255,0.1)" },
            }}
          >
            <ListItemIcon sx={{ color: "white", minWidth: 40 }}>
              {item.icon}
            </ListItemIcon>
            <ListItemText primary={item.text} />
          </ListItem>
        ))}
      </List>
    </Box>
  );

  return (
    <Box sx={{ display: "flex" }}>
      <AppBar
        position="fixed"
        sx={{
          zIndex: 1201,
          background: "linear-gradient(90deg, #1a1a1a 0%, #2d2d2d 100%)",
          width: desktopOpen ? { sm: `calc(100% - 240px)` } : "100%",
          ml: desktopOpen ? { sm: "240px" } : 0,
          transition: "width 0.3s ease, margin-left 0.3s ease",
        }}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            edge="start"
            onClick={() => {
              if (window.innerWidth >= 600) {
                setDesktopOpen(!desktopOpen);
              } else {
                setMobileOpen(!mobileOpen);
              }
            }}
            sx={{ mr: 2 }}
          >
            <MenuIcon />
          </IconButton>

          <Typography variant="h6" sx={{ flexGrow: 1 }}>
            Alumni Tracking System
          </Typography>

          <Avatar
            sx={{ cursor: "pointer", bgcolor: "rgba(255,255,255,0.15)" }}
            onClick={(e) => setAnchorEl(e.currentTarget)}
          >
            {user?.email?.[0]?.toUpperCase() ||
              user?.name?.[0]?.toUpperCase() ||
              "U"}
          </Avatar>

          <Menu
            anchorEl={anchorEl}
            open={Boolean(anchorEl)}
            onClose={() => setAnchorEl(null)}
          >
            <MenuItem onClick={onLogout}>
              <Logout sx={{ mr: 1 }} /> Logout
            </MenuItem>
          </Menu>
        </Toolbar>
      </AppBar>

      <Drawer
        variant="permanent"
        sx={{
          display: { xs: "none", sm: "block" },
          "& .MuiDrawer-paper": {
            width: 240,
            boxSizing: "border-box",
            transform: desktopOpen ? "translateX(0)" : "translateX(-100%)",
            transition: "transform 0.3s ease",
          },
        }}
        open={desktopOpen}
      >
        {drawer}
      </Drawer>

      <Drawer
        variant="temporary"
        open={mobileOpen}
        onClose={() => setMobileOpen(false)}
        ModalProps={{ keepMounted: true }}
        sx={{
          display: { xs: "block", sm: "none" },
          "& .MuiDrawer-paper": { width: 240, boxSizing: "border-box" },
        }}
      >
        {drawer}
      </Drawer>

      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          width: desktopOpen ? { sm: `calc(100% - 240px)` } : "100%",
          ml: desktopOpen ? { sm: "240px" } : 0,
          mt: "64px",
          transition: "width 0.3s ease, margin-left 0.3s ease",
        }}
      >
        {children}
      </Box>
    </Box>
  );
};

export default Layout;
