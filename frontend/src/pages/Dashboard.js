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
import {
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  AreaChart,
  Area,
} from "recharts";
import axios from "axios";
import { api } from "../utils/api";

const Dashboard = () => {
  const [stats, setStats] = useState({});
  const [analytics, setAnalytics] = useState({});
  const [recentAlumni, setRecentAlumni] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      // Fetch main stats
      const statsRes = await axios.get(api.endpoints.stats);
      const statsData = statsRes.data;
      setStats(statsData);

      // Fetch additional analytics data
      const [industriesRes, locationsRes, companiesRes, recentRes] =
        await Promise.all([
          axios.get(api.endpoints.industries),
          axios.get(api.endpoints.locations),
          axios.get(api.endpoints.companies),
          axios.get(api.endpoints.recent),
        ]);

      // Transform industry distribution for pie chart
      const industryData = Object.entries(
        industriesRes.data.industries || {}
      ).map(([name, value], index) => ({
        name,
        value,
        color: [
          "#8884d8",
          "#82ca9d",
          "#ffc658",
          "#ff7c7c",
          "#8dd1e1",
          "#d084d0",
        ][index % 6],
      }));

      // Transform location distribution for bar chart
      const locationData = Object.entries(
        locationsRes.data.locations || {}
      ).map(([location, count]) => ({
        location,
        count,
      }));

      // Mock graduation years data (this would need a backend endpoint)
      const graduationYears = [
        { year: "2018", count: 45 },
        { year: "2019", count: 52 },
        { year: "2020", count: 38 },
        { year: "2021", count: 41 },
        { year: "2022", count: 35 },
        { year: "2023", count: 28 },
      ];

      // Mock confidence trend (this would need a backend endpoint)
      const confidenceTrend = [
        { month: "Jan", confidence: 0.75 },
        { month: "Feb", confidence: 0.78 },
        { month: "Mar", confidence: 0.82 },
        { month: "Apr", confidence: 0.79 },
        { month: "May", confidence: 0.85 },
        { month: "Jun", confidence: 0.88 },
      ];

      // Calculate employment status from backend data
      const totalAlumni = statsData.total_alumni || 0;
      const withCurrentJob = statsData.with_current_job || 0;
      const withLinkedIn = statsData.with_linkedin || 0;
      const unemployed = totalAlumni - withCurrentJob;
      const unknown = totalAlumni - withLinkedIn;

      const jobStatusData = [
        {
          name: "Employed",
          value: Math.round((withCurrentJob / totalAlumni) * 100),
          color: "#4caf50",
        },
        {
          name: "Unemployed",
          value: Math.round((unemployed / totalAlumni) * 100),
          color: "#f44336",
        },
        {
          name: "Unknown",
          value: Math.round((unknown / totalAlumni) * 100),
          color: "#ff9800",
        },
      ];

      setAnalytics({
        industryDistribution: industryData,
        graduationYears,
        locations: locationData,
        confidenceTrend,
        jobStatus: jobStatusData,
        topCompanies: companiesRes.data.companies || [],
      });

      // Set recent alumni
      setRecentAlumni(recentRes.data || []);
    } catch (error) {
      console.error("Error loading dashboard:", error);
      // Set fallback data
      setStats({
        total_alumni: 0,
        with_linkedin: 0,
        with_current_job: 0,
        average_confidence: 0,
      });
      setAnalytics({
        industryDistribution: [],
        graduationYears: [],
        locations: [],
        confidenceTrend: [],
        jobStatus: [],
        topCompanies: [],
      });
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
        Analytics Dashboard
      </Typography>

      {/* Stats Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card
            sx={{
              borderRadius: 3,
              backgroundColor: "#667eea",
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
              backgroundColor: "#f093fb",
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
              backgroundColor: "#4facfe",
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
              backgroundColor: "#fa709a",
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

      {/* Charts Section */}
      <Grid container spacing={3}>
        {/* Industry Distribution */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3, borderRadius: 3, height: 400 }}>
            <Typography variant="h6" sx={{ mb: 2, fontWeight: "bold" }}>
              Industry Distribution
            </Typography>
            <ResponsiveContainer width="100%" height="85%">
              <PieChart>
                <Pie
                  data={analytics.industryDistribution}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) =>
                    `${name} ${(percent * 100).toFixed(0)}%`
                  }
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {analytics.industryDistribution?.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        {/* Graduation Year Distribution */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3, borderRadius: 3, height: 400 }}>
            <Typography variant="h6" sx={{ mb: 2, fontWeight: "bold" }}>
              Alumni by Graduation Year
            </Typography>
            <ResponsiveContainer width="100%" height="85%">
              <BarChart data={analytics.graduationYears}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="year" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="count" fill="#8884d8" />
              </BarChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        {/* Location Distribution */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3, borderRadius: 3, height: 400 }}>
            <Typography variant="h6" sx={{ mb: 2, fontWeight: "bold" }}>
              Alumni by Location
            </Typography>
            <ResponsiveContainer width="100%" height="85%">
              <BarChart data={analytics.locations} layout="horizontal">
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" />
                <YAxis dataKey="location" type="category" width={80} />
                <Tooltip />
                <Bar dataKey="count" fill="#82ca9d" />
              </BarChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        {/* Confidence Score Trend */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3, borderRadius: 3, height: 400 }}>
            <Typography variant="h6" sx={{ mb: 2, fontWeight: "bold" }}>
              Confidence Score Trend
            </Typography>
            <ResponsiveContainer width="100%" height="85%">
              <AreaChart data={analytics.confidenceTrend}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis
                  domain={[0, 1]}
                  tickFormatter={(value) => `${(value * 100).toFixed(0)}%`}
                />
                <Tooltip
                  formatter={(value) => `${(value * 100).toFixed(1)}%`}
                />
                <Area
                  type="monotone"
                  dataKey="confidence"
                  stroke="#8884d8"
                  fill="#8884d8"
                  fillOpacity={0.6}
                />
              </AreaChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        {/* Employment Status */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3, borderRadius: 3, height: 400 }}>
            <Typography variant="h6" sx={{ mb: 2, fontWeight: "bold" }}>
              Employment Status
            </Typography>
            <ResponsiveContainer width="100%" height="85%">
              <PieChart>
                <Pie
                  data={analytics.jobStatus}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={100}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {analytics.jobStatus?.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip formatter={(value) => `${value}%`} />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        {/* Key Metrics Summary */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3, borderRadius: 3, height: 400 }}>
            <Typography variant="h6" sx={{ mb: 3, fontWeight: "bold" }}>
              Key Metrics Summary
            </Typography>
            <Box sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
              <Box
                sx={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                }}
              >
                <Typography variant="body1">Data Completeness</Typography>
                <Chip
                  label={`${
                    stats.total_alumni
                      ? Math.round(
                          ((stats.with_linkedin + stats.with_current_job) /
                            (stats.total_alumni * 2)) *
                            100
                        )
                      : 0
                  }%`}
                  color="success"
                  size="small"
                  sx={{ fontWeight: "bold" }}
                />
              </Box>
              <Box
                sx={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                }}
              >
                <Typography variant="body1">LinkedIn Coverage</Typography>
                <Chip
                  label={`${
                    stats.total_alumni
                      ? Math.round(
                          (stats.with_linkedin / stats.total_alumni) * 100
                        )
                      : 0
                  }%`}
                  color="primary"
                  size="small"
                  sx={{ fontWeight: "bold" }}
                />
              </Box>
              <Box
                sx={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                }}
              >
                <Typography variant="body1">Employment Rate</Typography>
                <Chip
                  label={`${
                    stats.total_alumni
                      ? Math.round(
                          (stats.with_current_job / stats.total_alumni) * 100
                        )
                      : 0
                  }%`}
                  color="success"
                  size="small"
                  sx={{ fontWeight: "bold" }}
                />
              </Box>
              <Box
                sx={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                }}
              >
                <Typography variant="body1">Average Confidence</Typography>
                <Chip
                  label={`${((stats.average_confidence || 0) * 100).toFixed(
                    1
                  )}%`}
                  color="secondary"
                  size="small"
                  sx={{ fontWeight: "bold" }}
                />
              </Box>
              <Box
                sx={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                }}
              >
                <Typography variant="body1">Top Industry</Typography>
                <Chip
                  label={
                    analytics.industryDistribution.length > 0
                      ? analytics.industryDistribution[0].name
                      : "N/A"
                  }
                  color="info"
                  size="small"
                  sx={{ fontWeight: "bold" }}
                />
              </Box>
              <Box
                sx={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                }}
              >
                <Typography variant="body1">Top Company</Typography>
                <Chip
                  label={
                    analytics.topCompanies.length > 0
                      ? analytics.topCompanies[0].company
                      : "N/A"
                  }
                  color="warning"
                  size="small"
                  sx={{ fontWeight: "bold" }}
                />
              </Box>
            </Box>
          </Paper>
        </Grid>
      </Grid>

      {/* Recently Added Alumni */}
      <Grid container spacing={3} sx={{ mt: 2 }}>
        <Grid item xs={12}>
          <Paper sx={{ p: 3, borderRadius: 3 }}>
            <Typography variant="h6" sx={{ mb: 2, fontWeight: "bold" }}>
              Recently Added Alumni
            </Typography>
            <Box>
              {recentAlumni.length === 0 ? (
                <Typography>No recent alumni found.</Typography>
              ) : (
                recentAlumni.slice(0, 5).map((alumnus) => (
                  <Box
                    key={alumnus.id}
                    sx={{
                      mb: 2,
                      p: 2,
                      border: "1px solid #e0e0e0",
                      borderRadius: 2,
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "center",
                    }}
                  >
                    <Box>
                      <Typography variant="subtitle1" fontWeight="bold">
                        {alumnus.name}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {alumnus.graduation_year &&
                          `Class of ${alumnus.graduation_year}`}
                        {alumnus.location && ` • ${alumnus.location}`}
                        {alumnus.industry && ` • ${alumnus.industry}`}
                      </Typography>
                      {alumnus.current_job && (
                        <Typography variant="body2" color="primary">
                          {alumnus.current_job.title} at{" "}
                          {alumnus.current_job.company}
                        </Typography>
                      )}
                    </Box>
                    <Box sx={{ textAlign: "right" }}>
                      {alumnus.last_updated && (
                        <Typography variant="body2" color="text.secondary">
                          Added:{" "}
                          {new Date(alumnus.last_updated).toLocaleDateString()}
                        </Typography>
                      )}
                    </Box>
                  </Box>
                ))
              )}
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;
