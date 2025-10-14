import React, { useState, useEffect } from "react";
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  Paper,
  LinearProgress,
  Chip,
} from "@mui/material";
import { People, LinkedIn, Business, TrendingUp } from "@mui/icons-material";
import axios from "axios";
import { api } from "../utils/api";

const Dashboard = () => {
  const [stats, setStats] = useState({});
  const [recentAlumni, setRecentAlumni] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      const [statsRes, recentRes] = await Promise.all([
        axios.get(api.endpoints.stats),
        axios.get(api.endpoints.recent + "?limit=5"),
      ]);

      setStats(statsRes.data);
      setRecentAlumni(recentRes.data);
    } catch (error) {
      console.error("Error loading dashboard:", error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <LinearProgress />;

  return (
    <Box>
      <Typography
        variant="h4"
        sx={{ mb: 4, fontWeight: "bold", color: "#333" }}
      >
        Dashboard Overview
      </Typography>

      {/* Stats Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card
            sx={{
              borderRadius: 3,
              background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
              color: "white",
            }}
          >
            <CardContent>
              <Box
                sx={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                }}
              >
                <Box>
                  <Typography variant="h4" fontWeight="bold">
                    {stats.total_alumni || 0}
                  </Typography>
                  <Typography variant="body2" sx={{ opacity: 0.9 }}>
                    Total Alumni
                  </Typography>
                </Box>
                <People sx={{ fontSize: 40, opacity: 0.8 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card
            sx={{
              borderRadius: 3,
              background: "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)",
              color: "white",
            }}
          >
            <CardContent>
              <Box
                sx={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                }}
              >
                <Box>
                  <Typography variant="h4" fontWeight="bold">
                    {stats.with_linkedin || 0}
                  </Typography>
                  <Typography variant="body2" sx={{ opacity: 0.9 }}>
                    With LinkedIn
                  </Typography>
                </Box>
                <LinkedIn sx={{ fontSize: 40, opacity: 0.8 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card
            sx={{
              borderRadius: 3,
              background: "linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)",
              color: "white",
            }}
          >
            <CardContent>
              <Box
                sx={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                }}
              >
                <Box>
                  <Typography variant="h4" fontWeight="bold">
                    {stats.with_current_job || 0}
                  </Typography>
                  <Typography variant="body2" sx={{ opacity: 0.9 }}>
                    With Current Job
                  </Typography>
                </Box>
                <Business sx={{ fontSize: 40, opacity: 0.8 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card
            sx={{
              borderRadius: 3,
              background: "linear-gradient(135deg, #fa709a 0%, #fee140 100%)",
              color: "white",
            }}
          >
            <CardContent>
              <Box
                sx={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                }}
              >
                <Box>
                  <Typography variant="h4" fontWeight="bold">
                    {((stats.average_confidence || 0) * 100).toFixed(0)}%
                  </Typography>
                  <Typography variant="body2" sx={{ opacity: 0.9 }}>
                    Avg Confidence
                  </Typography>
                </Box>
                <TrendingUp sx={{ fontSize: 40, opacity: 0.8 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Recent Alumni */}
      <Paper sx={{ p: 3, borderRadius: 3 }}>
        <Typography variant="h6" sx={{ mb: 2, fontWeight: "bold" }}>
          Recently Added Alumni
        </Typography>

        {recentAlumni.length === 0 ? (
          <Typography color="text.secondary">No recent alumni found</Typography>
        ) : (
          <Box>
            {recentAlumni.map((alumni) => (
              <Box
                key={alumni.id}
                sx={{
                  p: 2,
                  mb: 2,
                  bgcolor: "grey.50",
                  borderRadius: 2,
                  border: "1px solid",
                  borderColor: "grey.200",
                }}
              >
                <Box
                  sx={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                  }}
                >
                  <Box>
                    <Typography variant="subtitle1" fontWeight="bold">
                      {alumni.name}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {alumni.current_job
                        ? `${alumni.current_job.title} at ${alumni.current_job.company}`
                        : "No current job info"}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {alumni.location} • Added{" "}
                      {new Date(alumni.last_updated).toLocaleDateString()}
                    </Typography>
                  </Box>
                  <Box sx={{ textAlign: "right" }}>
                    {alumni.industry && (
                      <Chip
                        label={alumni.industry}
                        size="small"
                        sx={{ mb: 1, display: "block" }}
                      />
                    )}
                    <Chip
                      label={`${(alumni.confidence_score * 100).toFixed(0)}%`}
                      size="small"
                      color={
                        alumni.confidence_score > 0.7 ? "success" : "warning"
                      }
                    />
                  </Box>
                </Box>
              </Box>
            ))}
          </Box>
        )}
      </Paper>
    </Box>
  );
};

export default Dashboard;
