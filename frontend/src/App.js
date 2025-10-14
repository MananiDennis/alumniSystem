import React, { useState, useEffect } from "react";
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
  const [currentPage, setCurrentPage] = useState("dashboard");

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
    setCurrentPage("dashboard");
  };

  const renderPage = () => {
    switch (currentPage) {
      case "dashboard":
        return <Dashboard token={token} />;
      case "alumni":
        return <Alumni token={token} />;
      case "analytics":
        return <Analytics token={token} />;
      case "collection":
        return <DataCollection token={token} />;
      default:
        return <Dashboard token={token} />;
    }
  };

  if (!user) {
    return (
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Login onLogin={handleLogin} />
      </ThemeProvider>
    );
  }

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Layout
        currentPage={currentPage}
        onPageChange={setCurrentPage}
        user={user}
        onLogout={handleLogout}
      >
        {renderPage()}
      </Layout>
    </ThemeProvider>
  );
}

export default App;
