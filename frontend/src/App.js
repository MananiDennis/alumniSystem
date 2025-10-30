import React, { useState, useEffect } from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import { ThemeProvider, createTheme } from "@mui/material/styles";
import CssBaseline from "@mui/material/CssBaseline";
import axios from "axios";

// Components
import Layout from "./components/Layout";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import Alumni from "./pages/Alumni";
import Analytics from "./pages/Analytics";
import DataCollection from "./pages/DataCollection";
import Documentation from "./pages/Documentation";
import { api } from "./utils/api";

const theme = createTheme({
  palette: {
    primary: {
      main: "#667eea",
    },
    secondary: {
      main: "#764ba2",
    },
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
  },
  shape: {
    borderRadius: 12,
  },
});

function App() {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);

  useEffect(() => {
    // Check for stored token on app load
    const storedToken = localStorage.getItem("token");
    if (storedToken) {
      // Verify token and get user info
      axios
        .get(api.endpoints.me, {
          headers: { Authorization: `Bearer ${storedToken}` },
        })
        .then((response) => {
          setUser(response.data);
          setToken(storedToken);
        })
        .catch(() => {
          localStorage.removeItem("token");
        });
    }
  }, []);

  const handleLogin = (userData, userToken) => {
    setUser(userData);
    setToken(userToken);
  };

  const handleLogout = () => {
    localStorage.removeItem("token");
    setUser(null);
    setToken(null);
  };

  if (!user) {
    return (
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Router>
          <Routes>
            <Route path="/login" element={<Login onLogin={handleLogin} />} />
            <Route path="*" element={<Navigate to="/login" replace />} />
          </Routes>
        </Router>
      </ThemeProvider>
    );
  }

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Layout user={user} onLogout={handleLogout}>
          <Routes>
            <Route path="/dashboard" element={<Dashboard token={token} />} />
            <Route path="/alumni" element={<Alumni token={token} />} />
            <Route path="/analytics" element={<Analytics token={token} />} />
            <Route path="/data-collection" element={<DataCollection token={token} />} />
            <Route path="/docs" element={<Documentation />} />
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="/login" element={<Navigate to="/dashboard" replace />} />
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </Layout>
      </Router>
    </ThemeProvider>
  );
}

export default App;
