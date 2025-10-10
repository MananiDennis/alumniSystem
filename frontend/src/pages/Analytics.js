import React, { useState } from "react";
import {
  Box,
  Card,
  CardContent,
  TextField,
  Button,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  CircularProgress,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Avatar,
  Grid,
  Divider,
  List,
  ListItem,
  ListItemText,
  IconButton,
  LinearProgress,
} from "@mui/material";
import {
  Search,
  Psychology,
  Close,
  Person,
  LinkedIn,
  Work,
  Business,
  LocationOn,
  School,
  CalendarToday,
} from "@mui/icons-material";
import axios from "axios";

export default function Analytics({ token }) {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [selectedAlumni, setSelectedAlumni] = useState(null);
  const [detailedViewOpen, setDetailedViewOpen] = useState(false);
  const [detailedAlumni, setDetailedAlumni] = useState(null);
  const [detailedLoading, setDetailedLoading] = useState(false);

  const handleQuery = async () => {
    if (!query.trim()) return;

    setLoading(true);
    setError("");

    try {
      const response = await axios.post(
        "http://localhost:8000/query",
        { query },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setResults(response.data);
    } catch (err) {
      setError("Failed to process query");
    } finally {
      setLoading(false);
    }
  };

  const fetchDetailedAlumni = async (alumniId) => {
    setDetailedLoading(true);
    try {
      const response = await axios.get(
        `http://localhost:8000/alumni/${alumniId}`,
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );
      setDetailedAlumni(response.data);
      setDetailedViewOpen(true);
    } catch (error) {
      console.error("Error fetching detailed alumni:", error);
    } finally {
      setDetailedLoading(false);
    }
  };

  const handleViewDetails = (alumni) => {
    setSelectedAlumni(alumni);
    fetchDetailedAlumni(alumni.id);
  };

  const handleCloseDetailedView = () => {
    setDetailedViewOpen(false);
    setDetailedAlumni(null);
    setSelectedAlumni(null);
  };

  const getConfidenceColor = (score) => {
    if (score > 0.8) return "success";
    if (score > 0.6) return "warning";
    return "error";
  };

  const exampleQueries = [
    "Show me alumni working in the mining sector",
    "Find graduates from 2018 to 2020",
    "Who is working at Microsoft?",
    "Alumni in Perth working in technology",
    "Show me all finance professionals",
  ];

  return (
    <Box>
      <Typography
        variant="h4"
        sx={{ mb: 4, fontWeight: 700, color: "#1e293b" }}
      >
        AI-Powered Analytics
      </Typography>

      <Card
        sx={{
          mb: 4,
          borderRadius: 3,
          boxShadow: "0 4px 20px rgba(0,0,0,0.08)",
        }}
      >
        <CardContent sx={{ p: 4 }}>
          <Box sx={{ display: "flex", alignItems: "center", mb: 3 }}>
            <Psychology sx={{ mr: 2, color: "#667eea" }} />
            <Typography variant="h6" sx={{ fontWeight: 600 }}>
              Natural Language Query
            </Typography>
          </Box>

          <Box sx={{ display: "flex", gap: 2, mb: 3 }}>
            <TextField
              fullWidth
              placeholder="Ask anything about your alumni... e.g., 'Show me alumni working in mining'"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyPress={(e) => e.key === "Enter" && handleQuery()}
              sx={{
                "& .MuiOutlinedInput-root": {
                  borderRadius: 2,
                },
              }}
            />
            <Button
              variant="contained"
              onClick={handleQuery}
              disabled={loading || !query.trim()}
              startIcon={loading ? <CircularProgress size={20} /> : <Search />}
              sx={{
                px: 4,
                borderRadius: 2,
                background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
              }}
            >
              {loading ? "Searching..." : "Search"}
            </Button>
          </Box>

          <Typography variant="body2" sx={{ color: "#64748b", mb: 2 }}>
            Try these example queries:
          </Typography>
          <Box sx={{ display: "flex", flexWrap: "wrap", gap: 1 }}>
            {exampleQueries.map((example, index) => (
              <Chip
                key={index}
                label={example}
                variant="outlined"
                onClick={() => setQuery(example)}
                sx={{
                  borderRadius: 2,
                  "&:hover": {
                    backgroundColor: "rgba(102, 126, 234, 0.1)",
                    borderColor: "#667eea",
                  },
                }}
              />
            ))}
          </Box>
        </CardContent>
      </Card>

      {error && (
        <Alert severity="error" sx={{ mb: 3, borderRadius: 2 }}>
          {error}
        </Alert>
      )}

      {results && (
        <Card
          sx={{ borderRadius: 3, boxShadow: "0 4px 20px rgba(0,0,0,0.08)" }}
        >
          <CardContent sx={{ p: 4 }}>
            <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
              Query Results
            </Typography>

            <Box sx={{ mb: 3, p: 2, bgcolor: "#f8fafc", borderRadius: 2 }}>
              <Typography
                variant="body2"
                sx={{ fontWeight: 600, color: "#374151", mb: 1 }}
              >
                Your Query: "{results.query}"
              </Typography>
              <Typography variant="body2" sx={{ color: "#6b7280" }}>
                Interpreted as:{" "}
                {JSON.stringify(results.structured_query, null, 2)}
              </Typography>
              <Typography variant="body2" sx={{ color: "#6b7280", mt: 1 }}>
                Found {results.count} result{results.count !== 1 ? "s" : ""}
              </Typography>
            </Box>

            {results.results && results.results.length > 0 ? (
              <TableContainer component={Paper} sx={{ borderRadius: 2 }}>
                <Table>
                  <TableHead>
                    <TableRow sx={{ backgroundColor: "#f8fafc" }}>
                      <TableCell sx={{ fontWeight: 600 }}>Name</TableCell>
                      <TableCell sx={{ fontWeight: 600 }}>Location</TableCell>
                      <TableCell sx={{ fontWeight: 600 }}>Industry</TableCell>
                      <TableCell sx={{ fontWeight: 600 }}>
                        Current Job
                      </TableCell>
                      <TableCell sx={{ fontWeight: 600 }}>Confidence</TableCell>
                      <TableCell sx={{ fontWeight: 600 }}>Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {results.results.map((alumni, index) => (
                      <TableRow key={index}>
                        <TableCell>{alumni.name}</TableCell>
                        <TableCell>{alumni.location || "N/A"}</TableCell>
                        <TableCell>
                          {alumni.industry && (
                            <Chip
                              label={alumni.industry}
                              size="small"
                              sx={{ borderRadius: 2 }}
                            />
                          )}
                        </TableCell>
                        <TableCell>
                          {alumni.current_job
                            ? `${alumni.current_job.title} at ${alumni.current_job.company}`
                            : "N/A"}
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={`${(alumni.confidence_score * 100).toFixed(
                              0
                            )}%`}
                            size="small"
                            color={
                              alumni.confidence_score > 0.8
                                ? "success"
                                : alumni.confidence_score > 0.6
                                ? "warning"
                                : "error"
                            }
                            sx={{ borderRadius: 2 }}
                          />
                        </TableCell>
                        <TableCell>
                          <Button
                            size="small"
                            variant="outlined"
                            onClick={() => handleViewDetails(alumni)}
                            sx={{
                              borderRadius: 2,
                              textTransform: "none",
                              borderColor: "#667eea",
                              color: "#667eea",
                              "&:hover": {
                                borderColor: "#5a67d8",
                                backgroundColor: "rgba(102, 126, 234, 0.1)",
                              },
                            }}
                          >
                            View Details
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            ) : (
              <Typography
                variant="body1"
                sx={{ color: "#64748b", textAlign: "center", py: 4 }}
              >
                No results found for your query.
              </Typography>
            )}
          </CardContent>
        </Card>
      )}

      {/* Detailed Alumni View Dialog */}
      <Dialog
        open={detailedViewOpen}
        onClose={handleCloseDetailedView}
        maxWidth="md"
        fullWidth
        sx={{
          "& .MuiDialog-paper": {
            borderRadius: 3,
            maxHeight: "90vh",
          },
        }}
      >
        <DialogTitle
          sx={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            pb: 1,
          }}
        >
          <Typography variant="h5" sx={{ fontWeight: 600 }}>
            Alumni Profile
          </Typography>
          <IconButton onClick={handleCloseDetailedView} size="small">
            <Close />
          </IconButton>
        </DialogTitle>
        <DialogContent dividers sx={{ p: 3 }}>
          {detailedLoading ? (
            <Box sx={{ display: "flex", justifyContent: "center", py: 4 }}>
              <LinearProgress sx={{ width: "50%" }} />
            </Box>
          ) : detailedAlumni ? (
            <Box>
              {/* Basic Information */}
              <Box
                sx={{ display: "flex", alignItems: "center", gap: 3, mb: 3 }}
              >
                <Avatar
                  sx={{
                    bgcolor: "#667eea",
                    width: 80,
                    height: 80,
                    fontSize: 32,
                  }}
                >
                  {detailedAlumni.name?.charAt(0)}
                </Avatar>
                <Box>
                  <Typography variant="h5" sx={{ fontWeight: 600, mb: 1 }}>
                    {detailedAlumni.name}
                  </Typography>
                  {detailedAlumni.graduation_year && (
                    <Typography
                      variant="subtitle1"
                      sx={{ color: "#64748b", mb: 1 }}
                    >
                      Class of {detailedAlumni.graduation_year}
                    </Typography>
                  )}
                  <Chip
                    label={`${(detailedAlumni.confidence_score * 100).toFixed(
                      0
                    )}% Confidence`}
                    size="small"
                    color={getConfidenceColor(detailedAlumni.confidence_score)}
                    sx={{ borderRadius: 2 }}
                  />
                </Box>
              </Box>

              <Divider sx={{ my: 3 }} />

              {/* Contact Information */}
              <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>
                Contact Information
              </Typography>
              <Grid container spacing={2} sx={{ mb: 3 }}>
                {detailedAlumni.location && (
                  <Grid item xs={12} sm={6}>
                    <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                      <LocationOn sx={{ color: "#64748b" }} />
                      <Typography variant="body2">
                        <strong>Location:</strong> {detailedAlumni.location}
                      </Typography>
                    </Box>
                  </Grid>
                )}
                {detailedAlumni.linkedin_url && (
                  <Grid item xs={12} sm={6}>
                    <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                      <LinkedIn sx={{ color: "#0077b5" }} />
                      <Button
                        size="small"
                        href={detailedAlumni.linkedin_url}
                        target="_blank"
                        sx={{
                          textTransform: "none",
                          p: 0,
                          minWidth: "auto",
                          color: "#0077b5",
                        }}
                      >
                        View LinkedIn Profile
                      </Button>
                    </Box>
                  </Grid>
                )}
              </Grid>

              {/* Current Position */}
              {detailedAlumni.current_job && (
                <>
                  <Divider sx={{ my: 3 }} />
                  <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>
                    Current Position
                  </Typography>
                  <Card
                    sx={{ p: 2, mb: 3, borderRadius: 2, bgcolor: "#f8fafc" }}
                  >
                    <Box
                      sx={{
                        display: "flex",
                        alignItems: "center",
                        gap: 2,
                        mb: 1,
                      }}
                    >
                      <Work sx={{ color: "#667eea" }} />
                      <Typography variant="h6" sx={{ fontWeight: 600 }}>
                        {detailedAlumni.current_job.title}
                      </Typography>
                    </Box>
                    <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
                      <Business sx={{ color: "#64748b" }} />
                      <Typography variant="body1">
                        {detailedAlumni.current_job.company}
                      </Typography>
                    </Box>
                    {detailedAlumni.current_job.start_date && (
                      <Box
                        sx={{
                          display: "flex",
                          alignItems: "center",
                          gap: 1,
                          mt: 1,
                        }}
                      >
                        <CalendarToday
                          sx={{ color: "#64748b", fontSize: 16 }}
                        />
                        <Typography variant="body2" sx={{ color: "#64748b" }}>
                          Since {detailedAlumni.current_job.start_date}
                        </Typography>
                      </Box>
                    )}
                  </Card>
                </>
              )}

              {/* Work History */}
              {detailedAlumni.work_history &&
                detailedAlumni.work_history.length > 0 && (
                  <>
                    <Divider sx={{ my: 3 }} />
                    <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>
                      Work History
                    </Typography>
                    <List>
                      {detailedAlumni.work_history.map((job, index) => (
                        <ListItem key={index} sx={{ px: 0, py: 1 }}>
                          <ListItemText
                            primary={
                              <Box
                                sx={{
                                  display: "flex",
                                  alignItems: "center",
                                  gap: 1,
                                }}
                              >
                                <Work sx={{ color: "#667eea", fontSize: 20 }} />
                                <Typography
                                  variant="subtitle1"
                                  sx={{ fontWeight: 600 }}
                                >
                                  {job.title} at {job.company}
                                </Typography>
                              </Box>
                            }
                            secondary={
                              job.start_date && job.end_date ? (
                                <Typography
                                  variant="body2"
                                  sx={{ color: "#64748b" }}
                                >
                                  {job.start_date} - {job.end_date}
                                </Typography>
                              ) : job.start_date ? (
                                <Typography
                                  variant="body2"
                                  sx={{ color: "#64748b" }}
                                >
                                  Since {job.start_date}
                                </Typography>
                              ) : null
                            }
                          />
                        </ListItem>
                      ))}
                    </List>
                  </>
                )}

              {/* Education */}
              {detailedAlumni.education &&
                detailedAlumni.education.length > 0 && (
                  <>
                    <Divider sx={{ my: 3 }} />
                    <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>
                      Education
                    </Typography>
                    <List>
                      {detailedAlumni.education.map((edu, index) => (
                        <ListItem key={index} sx={{ px: 0, py: 1 }}>
                          <ListItemText
                            primary={
                              <Box
                                sx={{
                                  display: "flex",
                                  alignItems: "center",
                                  gap: 1,
                                }}
                              >
                                <School
                                  sx={{ color: "#667eea", fontSize: 20 }}
                                />
                                <Typography
                                  variant="subtitle1"
                                  sx={{ fontWeight: 600 }}
                                >
                                  {edu.degree} in {edu.field_of_study}
                                </Typography>
                              </Box>
                            }
                            secondary={
                              <Box>
                                <Typography
                                  variant="body2"
                                  sx={{ color: "#64748b" }}
                                >
                                  {edu.institution}
                                </Typography>
                                {edu.graduation_year && (
                                  <Typography
                                    variant="body2"
                                    sx={{ color: "#64748b" }}
                                  >
                                    Graduated {edu.graduation_year}
                                  </Typography>
                                )}
                              </Box>
                            }
                          />
                        </ListItem>
                      ))}
                    </List>
                  </>
                )}

              {/* Industry */}
              {detailedAlumni.industry && (
                <>
                  <Divider sx={{ my: 3 }} />
                  <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>
                    Industry
                  </Typography>
                  <Chip
                    label={detailedAlumni.industry}
                    size="medium"
                    sx={{
                      borderRadius: 2,
                      bgcolor: "#e0e7ff",
                      color: "#3730a3",
                      fontWeight: 500,
                    }}
                  />
                </>
              )}
            </Box>
          ) : (
            <Typography variant="body1" sx={{ textAlign: "center", py: 4 }}>
              Failed to load alumni details.
            </Typography>
          )}
        </DialogContent>
        <DialogActions sx={{ p: 3, pt: 2 }}>
          <Button
            onClick={handleCloseDetailedView}
            variant="outlined"
            sx={{ borderRadius: 2, textTransform: "none" }}
          >
            Close
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
