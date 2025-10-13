import React, { useState, useEffect, useCallback } from "react";
import {
  Box,
  Card,
  CardContent,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  TextField,
  Button,
  Grid,
  LinearProgress,
  Avatar,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Divider,
  List,
  ListItem,
  ListItemText,
  IconButton,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  CircularProgress,
} from "@mui/material";
import {
  Search,
  Person,
  LinkedIn,
  Work,
  Close,
  Business,
  LocationOn,
  School,
  CalendarToday,
  Add,
  Delete,
  DeleteForever,
} from "@mui/icons-material";
import axios from "axios";
import { api } from "../utils/api";

export default function Alumni({ token }) {
  const [alumni, setAlumni] = useState([]);
  const [filteredAlumni, setFilteredAlumni] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [detailedViewOpen, setDetailedViewOpen] = useState(false);
  const [detailedAlumni, setDetailedAlumni] = useState(null);
  const [detailedLoading, setDetailedLoading] = useState(false);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [editingAlumni, setEditingAlumni] = useState(null);
  const [editLoading, setEditLoading] = useState(false);
  const [editError, setEditError] = useState("");
  const [editSuccess, setEditSuccess] = useState("");
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [deletingAlumni, setDeletingAlumni] = useState(null);
  const [deleteLoading, setDeleteLoading] = useState(false);

  // Edit form state
  const [editForm, setEditForm] = useState({
    full_name: "",
    graduation_year: "",
    location: "",
    industry: "",
    linkedin_url: "",
    current_job_title: "",
    current_job_company: "",
    current_job_start_date: "",
    current_job_industry: "",
    current_job_location: "",
    work_history: [],
    education: [],
  });

  const fetchAlumni = useCallback(async () => {
    try {
      const response = await axios.get(api.endpoints.alumni, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setAlumni(response.data.alumni);
      setFilteredAlumni(response.data.alumni);
    } catch (error) {
      // Error handled silently
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => {
    fetchAlumni();
  }, [fetchAlumni]);

  useEffect(() => {
    // Filter alumni based on search term
    if (searchTerm) {
      const filtered = alumni.filter(
        (a) =>
          a.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
          (a.industry &&
            a.industry.toLowerCase().includes(searchTerm.toLowerCase())) ||
          (a.location &&
            a.location.toLowerCase().includes(searchTerm.toLowerCase())) ||
          (a.current_job &&
            (a.current_job.title
              .toLowerCase()
              .includes(searchTerm.toLowerCase()) ||
              a.current_job.company
                .toLowerCase()
                .includes(searchTerm.toLowerCase())))
      );
      setFilteredAlumni(filtered);
    } else {
      setFilteredAlumni(alumni);
    }
  }, [searchTerm, alumni]);

  const fetchDetailedAlumni = async (alumniId) => {
    setDetailedLoading(true);
    try {
      const response = await axios.get(`${api.endpoints.alumni}/${alumniId}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setDetailedAlumni(response.data);
      setDetailedViewOpen(true);
    } catch (error) {
      // Error handled silently
    } finally {
      setDetailedLoading(false);
    }
  };

  const handleViewDetails = (alumni) => {
    fetchDetailedAlumni(alumni.id);
  };

  const handleCloseDetailedView = () => {
    setDetailedViewOpen(false);
    setDetailedAlumni(null);
  };

  const handleEditAlumni = async (alumni) => {
    setEditingAlumni(alumni);

    try {
      // Fetch detailed alumni data to get work history and education
      const response = await axios.get(`${api.endpoints.alumni}/${alumni.id}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      const detailedData = response.data;

      // Pre-populate form with existing data
      setEditForm({
        full_name: detailedData.name || "",
        graduation_year: detailedData.graduation_year || "",
        location: detailedData.location || "",
        industry: detailedData.industry || "",
        linkedin_url: detailedData.linkedin_url || "",
        current_job_title: detailedData.current_job?.title || "",
        current_job_company: detailedData.current_job?.company || "",
        current_job_start_date: detailedData.current_job?.start_date || "",
        current_job_industry: "",
        current_job_location: "",
        work_history: detailedData.work_history
          ? detailedData.work_history.map((job) => ({
              title: job.title || "",
              company: job.company || "",
              start_date: job.start_date || "",
              end_date: job.end_date || "",
              industry: job.industry || "",
              location: job.location || "",
            }))
          : [],
        education: detailedData.education
          ? detailedData.education.map((edu) => ({
              degree: edu.degree || "",
              institution: edu.institution || "",
              start_date: edu.start_date || "",
              end_date: edu.end_date || "",
              field_of_study: edu.field_of_study || "",
            }))
          : [],
      });

      setEditDialogOpen(true);
    } catch (error) {
      setEditError("Failed to load alumni data for editing");
    }
  };

  // Edit form handlers
  const addEditWorkHistoryEntry = () => {
    setEditForm({
      ...editForm,
      work_history: [
        ...editForm.work_history,
        {
          title: "",
          company: "",
          start_date: "",
          end_date: "",
          industry: "",
          location: "",
        },
      ],
    });
  };

  const updateEditWorkHistoryEntry = (index, field, value) => {
    const updatedWorkHistory = [...editForm.work_history];
    updatedWorkHistory[index][field] = value;
    setEditForm({ ...editForm, work_history: updatedWorkHistory });
  };

  const removeEditWorkHistoryEntry = (index) => {
    setEditForm({
      ...editForm,
      work_history: editForm.work_history.filter((_, i) => i !== index),
    });
  };

  const addEditEducationEntry = () => {
    setEditForm({
      ...editForm,
      education: [
        ...editForm.education,
        {
          degree: "",
          institution: "",
          start_date: "",
          end_date: "",
          field_of_study: "",
        },
      ],
    });
  };

  const updateEditEducationEntry = (index, field, value) => {
    const updatedEducation = [...editForm.education];
    updatedEducation[index][field] = value;
    setEditForm({ ...editForm, education: updatedEducation });
  };

  const removeEditEducationEntry = (index) => {
    setEditForm({
      ...editForm,
      education: editForm.education.filter((_, i) => i !== index),
    });
  };

  const handleEditSubmit = async () => {
    if (!editForm.full_name.trim()) {
      setEditError("Full name is required");
      return;
    }

    setEditLoading(true);
    setEditError("");
    setEditSuccess("");

    try {
      // Format work history and education for backend
      const formattedWorkHistory = editForm.work_history
        .map(
          (job) =>
            `${job.title} - ${job.company} - ${job.start_date || ""} - ${
              job.end_date || ""
            }`
        )
        .join("\n");

      const formattedEducation = editForm.education
        .map(
          (edu) =>
            `${edu.degree} - ${edu.institution} - ${edu.start_date || ""} - ${
              edu.end_date || ""
            }`
        )
        .join("\n");

      const submitData = {
        ...editForm,
        work_history: formattedWorkHistory,
        education: formattedEducation,
      };

      await axios.put(
        `${api.endpoints.alumni}/${editingAlumni.id}`,
        submitData,
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      setEditSuccess("Alumni profile updated successfully!");

      // Refresh the alumni list and detailed view
      await fetchAlumni();
      await fetchDetailedAlumni(editingAlumni.id);

      // Close edit dialog after a short delay
      setTimeout(() => {
        setEditDialogOpen(false);
        setEditingAlumni(null);
        setEditSuccess("");
      }, 2000);
    } catch (err) {
      setEditError(
        err.response?.data?.detail || "Failed to update alumni profile"
      );
    } finally {
      setEditLoading(false);
    }
  };

  const handleCloseEditDialog = () => {
    setEditDialogOpen(false);
    setEditingAlumni(null);
    setEditForm({
      full_name: "",
      graduation_year: "",
      location: "",
      industry: "",
      linkedin_url: "",
      current_job_title: "",
      current_job_company: "",
      current_job_start_date: "",
      current_job_industry: "",
      current_job_location: "",
      work_history: [],
      education: [],
    });
    setEditError("");
    setEditSuccess("");
  };

  const handleDeleteAlumni = (alumni) => {
    setDeletingAlumni(alumni);
    setDeleteDialogOpen(true);
  };

  const handleConfirmDelete = async () => {
    if (!deletingAlumni) return;

    setDeleteLoading(true);
    try {
      await axios.delete(`${api.endpoints.alumni}/${deletingAlumni.id}`, {
        headers: { Authorization: `Bearer ${token}` },
      });

      // Refresh the alumni list
      await fetchAlumni();

      // Close dialogs
      setDeleteDialogOpen(false);
      setDeletingAlumni(null);
      setDetailedViewOpen(false);
      setDetailedAlumni(null);
    } catch (err) {
      // Error handled silently
    } finally {
      setDeleteLoading(false);
    }
  };

  const handleCloseDeleteDialog = () => {
    setDeleteDialogOpen(false);
    setDeletingAlumni(null);
  };

  const getConfidenceColor = (score) => {
    if (score > 0.8) return "success";
    if (score > 0.6) return "warning";
    return "error";
  };

  if (loading) {
    return (
      <Box sx={{ display: "flex", justifyContent: "center", mt: 4 }}>
        <LinearProgress sx={{ width: "50%" }} />
      </Box>
    );
  }

  return (
    <Box>
      <Typography
        variant="h4"
        sx={{ mb: 4, fontWeight: 700, color: "#1e293b" }}
      >
        Alumni Directory
      </Typography>

      <Card
        sx={{
          mb: 4,
          borderRadius: 3,
          boxShadow: "0 4px 20px rgba(0,0,0,0.08)",
        }}
      >
        <CardContent sx={{ p: 3 }}>
          <Grid container spacing={3} alignItems="center">
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                placeholder="Search alumni by name, industry, location, or company..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                InputProps={{
                  startAdornment: <Search sx={{ mr: 1, color: "#64748b" }} />,
                }}
                sx={{
                  "& .MuiOutlinedInput-root": {
                    borderRadius: 2,
                  },
                }}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <Typography variant="body1" sx={{ color: "#64748b" }}>
                Showing {filteredAlumni.length} of {alumni.length} alumni
              </Typography>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      <Card sx={{ borderRadius: 3, boxShadow: "0 4px 20px rgba(0,0,0,0.08)" }}>
        <CardContent sx={{ p: 0 }}>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow sx={{ backgroundColor: "#f8fafc" }}>
                  <TableCell sx={{ fontWeight: 600, py: 2 }}>Alumni</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>Industry</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>
                    Current Position
                  </TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>Location</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>Confidence</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {filteredAlumni.map((alumni, index) => (
                  <TableRow
                    key={index}
                    sx={{ "&:hover": { backgroundColor: "#f8fafc" } }}
                  >
                    <TableCell>
                      <Box
                        sx={{ display: "flex", alignItems: "center", gap: 2 }}
                      >
                        <Avatar
                          sx={{ bgcolor: "#667eea", width: 40, height: 40 }}
                        >
                          {alumni.name.charAt(0)}
                        </Avatar>
                        <Box>
                          <Typography
                            variant="subtitle2"
                            sx={{ fontWeight: 600 }}
                          >
                            {alumni.name}
                          </Typography>
                          {alumni.graduation_year && (
                            <Typography
                              variant="caption"
                              sx={{ color: "#64748b" }}
                            >
                              Class of {alumni.graduation_year}
                            </Typography>
                          )}
                        </Box>
                      </Box>
                    </TableCell>
                    <TableCell>
                      {alumni.industry ? (
                        <Chip
                          label={alumni.industry}
                          size="small"
                          sx={{
                            borderRadius: 2,
                            bgcolor: "#e0e7ff",
                            color: "#3730a3",
                          }}
                        />
                      ) : (
                        <Typography variant="body2" sx={{ color: "#94a3b8" }}>
                          N/A
                        </Typography>
                      )}
                    </TableCell>
                    <TableCell>
                      {alumni.current_job ? (
                        <Box>
                          <Typography variant="body2" sx={{ fontWeight: 500 }}>
                            {alumni.current_job.title}
                          </Typography>
                          <Typography
                            variant="caption"
                            sx={{ color: "#64748b" }}
                          >
                            {alumni.current_job.company}
                          </Typography>
                        </Box>
                      ) : (
                        <Typography variant="body2" sx={{ color: "#94a3b8" }}>
                          N/A
                        </Typography>
                      )}
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">
                        {alumni.location || "N/A"}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={`${(alumni.confidence_score * 100).toFixed(0)}%`}
                        size="small"
                        color={getConfidenceColor(alumni.confidence_score)}
                        sx={{ borderRadius: 2 }}
                      />
                    </TableCell>
                    <TableCell>
                      <Box sx={{ display: "flex", gap: 1 }}>
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
                        {/* <Button
                          size="small"
                          variant="outlined"
                          onClick={() => handleDeleteAlumni(alumni)}
                          sx={{
                            borderRadius: 2,
                            textTransform: "none",
                            borderColor: "#dc2626",
                            color: "#dc2626",
                            "&:hover": {
                              borderColor: "#b91c1c",
                              backgroundColor: "rgba(220, 38, 38, 0.1)",
                            },
                          }}
                        >
                          Delete
                        </Button> */}
                        {alumni.linkedin_url && (
                          <Button
                            size="small"
                            startIcon={<LinkedIn />}
                            href={alumni.linkedin_url}
                            target="_blank"
                            sx={{
                              color: "#0077b5",
                              "&:hover": {
                                backgroundColor: "rgba(0, 119, 181, 0.1)",
                              },
                            }}
                          >
                            LinkedIn
                          </Button>
                        )}
                      </Box>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>

          {filteredAlumni.length === 0 && (
            <Box sx={{ textAlign: "center", py: 8 }}>
              <Person sx={{ fontSize: 64, color: "#cbd5e1", mb: 2 }} />
              <Typography variant="h6" sx={{ color: "#64748b", mb: 1 }}>
                No alumni found
              </Typography>
              <Typography variant="body2" sx={{ color: "#94a3b8" }}>
                {searchTerm
                  ? "Try adjusting your search terms"
                  : "Start by collecting alumni data"}
              </Typography>
            </Box>
          )}
        </CardContent>
      </Card>

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
            onClick={() => handleDeleteAlumni(detailedAlumni)}
            variant="outlined"
            startIcon={<DeleteForever />}
            sx={{
              borderRadius: 2,
              textTransform: "none",
              borderColor: "#dc2626",
              color: "#dc2626",
              "&:hover": {
                borderColor: "#b91c1c",
                backgroundColor: "rgba(220, 38, 38, 0.1)",
              },
            }}
          >
            Delete Profile
          </Button>
          <Box sx={{ flex: 1 }} />
          <Button
            onClick={handleCloseDetailedView}
            variant="outlined"
            sx={{ borderRadius: 2, textTransform: "none" }}
          >
            Close
          </Button>
          <Button
            onClick={() => handleEditAlumni(detailedAlumni)}
            variant="contained"
            sx={{
              borderRadius: 2,
              textTransform: "none",
              background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
              ml: 1,
            }}
          >
            Edit Profile
          </Button>
        </DialogActions>
      </Dialog>

      {/* Edit Alumni Dialog */}
      <Dialog
        open={editDialogOpen}
        onClose={handleCloseEditDialog}
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
            Edit Alumni Profile
          </Typography>
          <IconButton onClick={handleCloseEditDialog} size="small">
            <Close />
          </IconButton>
        </DialogTitle>
        <DialogContent dividers sx={{ p: 3 }}>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Full Name *"
                value={editForm.full_name}
                onChange={(e) =>
                  setEditForm({
                    ...editForm,
                    full_name: e.target.value,
                  })
                }
                sx={{ mb: 2 }}
              />
              <FormControl fullWidth sx={{ mb: 2 }}>
                <InputLabel>Graduation Year</InputLabel>
                <Select
                  value={editForm.graduation_year}
                  onChange={(e) =>
                    setEditForm({
                      ...editForm,
                      graduation_year: e.target.value,
                    })
                  }
                >
                  {Array.from({ length: 81 }, (_, i) => 1950 + i).map(
                    (year) => (
                      <MenuItem key={year} value={year}>
                        {year}
                      </MenuItem>
                    )
                  )}
                </Select>
              </FormControl>
              <TextField
                fullWidth
                label="Location"
                value={editForm.location}
                onChange={(e) =>
                  setEditForm({
                    ...editForm,
                    location: e.target.value,
                  })
                }
                sx={{ mb: 2 }}
              />
              <FormControl fullWidth sx={{ mb: 2 }}>
                <InputLabel>Industry</InputLabel>
                <Select
                  value={editForm.industry}
                  onChange={(e) =>
                    setEditForm({
                      ...editForm,
                      industry: e.target.value,
                    })
                  }
                >
                  <MenuItem value="Technology">Technology</MenuItem>
                  <MenuItem value="Finance">Finance</MenuItem>
                  <MenuItem value="Healthcare">Healthcare</MenuItem>
                  <MenuItem value="Education">Education</MenuItem>
                  <MenuItem value="Consulting">Consulting</MenuItem>
                  <MenuItem value="Mining">Mining</MenuItem>
                  <MenuItem value="Government">Government</MenuItem>
                  <MenuItem value="Non-Profit">Non-Profit</MenuItem>
                  <MenuItem value="Retail">Retail</MenuItem>
                  <MenuItem value="Manufacturing">Manufacturing</MenuItem>
                  <MenuItem value="Other">Other</MenuItem>
                </Select>
              </FormControl>
              <TextField
                fullWidth
                label="LinkedIn URL"
                value={editForm.linkedin_url}
                onChange={(e) =>
                  setEditForm({
                    ...editForm,
                    linkedin_url: e.target.value,
                  })
                }
                sx={{ mb: 2 }}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <Typography variant="subtitle2" sx={{ mb: 2, fontWeight: 600 }}>
                Current Job
              </Typography>
              <TextField
                fullWidth
                label="Job Title"
                value={editForm.current_job_title}
                onChange={(e) =>
                  setEditForm({
                    ...editForm,
                    current_job_title: e.target.value,
                  })
                }
                sx={{ mb: 2 }}
              />
              <TextField
                fullWidth
                label="Company"
                value={editForm.current_job_company}
                onChange={(e) =>
                  setEditForm({
                    ...editForm,
                    current_job_company: e.target.value,
                  })
                }
                sx={{ mb: 2 }}
              />
              <TextField
                fullWidth
                label="Start Date"
                type="date"
                value={editForm.current_job_start_date}
                onChange={(e) =>
                  setEditForm({
                    ...editForm,
                    current_job_start_date: e.target.value,
                  })
                }
                InputLabelProps={{ shrink: true }}
                sx={{ mb: 2 }}
              />
              <TextField
                fullWidth
                label="Job Industry"
                value={editForm.current_job_industry}
                onChange={(e) =>
                  setEditForm({
                    ...editForm,
                    current_job_industry: e.target.value,
                  })
                }
                sx={{ mb: 2 }}
              />
              <TextField
                fullWidth
                label="Job Location"
                value={editForm.current_job_location}
                onChange={(e) =>
                  setEditForm({
                    ...editForm,
                    current_job_location: e.target.value,
                  })
                }
                sx={{ mb: 2 }}
              />
            </Grid>

            {/* Work History Section */}
            <Grid item xs={12}>
              <Box
                sx={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  mb: 2,
                }}
              >
                <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                  Work History
                </Typography>
                <Button
                  variant="outlined"
                  size="small"
                  startIcon={<Add />}
                  onClick={addEditWorkHistoryEntry}
                  sx={{ borderRadius: 2 }}
                >
                  Add Job
                </Button>
              </Box>

              {editForm.work_history.map((job, index) => (
                <Card
                  key={index}
                  sx={{
                    mb: 2,
                    border: "1px solid #e2e8f0",
                    borderRadius: 2,
                  }}
                >
                  <CardContent sx={{ p: 3 }}>
                    <Box
                      sx={{
                        display: "flex",
                        justifyContent: "space-between",
                        alignItems: "center",
                        mb: 2,
                      }}
                    >
                      <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                        Job #{index + 1}
                      </Typography>
                      <IconButton
                        onClick={() => removeEditWorkHistoryEntry(index)}
                        color="error"
                        size="small"
                      >
                        <Delete />
                      </IconButton>
                    </Box>

                    <Grid container spacing={2}>
                      <Grid item xs={12} md={6}>
                        <TextField
                          fullWidth
                          label="Job Title"
                          value={job.title}
                          onChange={(e) =>
                            updateEditWorkHistoryEntry(
                              index,
                              "title",
                              e.target.value
                            )
                          }
                          size="small"
                        />
                      </Grid>
                      <Grid item xs={12} md={6}>
                        <TextField
                          fullWidth
                          label="Company"
                          value={job.company}
                          onChange={(e) =>
                            updateEditWorkHistoryEntry(
                              index,
                              "company",
                              e.target.value
                            )
                          }
                          size="small"
                        />
                      </Grid>
                      <Grid item xs={12} md={3}>
                        <TextField
                          fullWidth
                          label="Start Date"
                          type="date"
                          value={job.start_date}
                          onChange={(e) =>
                            updateEditWorkHistoryEntry(
                              index,
                              "start_date",
                              e.target.value
                            )
                          }
                          InputLabelProps={{ shrink: true }}
                          size="small"
                        />
                      </Grid>
                      <Grid item xs={12} md={3}>
                        <TextField
                          fullWidth
                          label="End Date"
                          type="date"
                          value={job.end_date}
                          onChange={(e) =>
                            updateEditWorkHistoryEntry(
                              index,
                              "end_date",
                              e.target.value
                            )
                          }
                          InputLabelProps={{ shrink: true }}
                          size="small"
                        />
                      </Grid>
                      <Grid item xs={12} md={3}>
                        <TextField
                          fullWidth
                          label="Industry"
                          value={job.industry}
                          onChange={(e) =>
                            updateEditWorkHistoryEntry(
                              index,
                              "industry",
                              e.target.value
                            )
                          }
                          size="small"
                        />
                      </Grid>
                      <Grid item xs={12} md={3}>
                        <TextField
                          fullWidth
                          label="Location"
                          value={job.location}
                          onChange={(e) =>
                            updateEditWorkHistoryEntry(
                              index,
                              "location",
                              e.target.value
                            )
                          }
                          size="small"
                        />
                      </Grid>
                    </Grid>
                  </CardContent>
                </Card>
              ))}

              {editForm.work_history.length === 0 && (
                <Typography
                  variant="body2"
                  sx={{
                    color: "#64748b",
                    textAlign: "center",
                    py: 4,
                    border: "1px dashed #e2e8f0",
                    borderRadius: 2,
                  }}
                >
                  No work history added yet. Click "Add Job" to add work
                  experience.
                </Typography>
              )}
            </Grid>

            {/* Education Section */}
            <Grid item xs={12}>
              <Box
                sx={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  mb: 2,
                }}
              >
                <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                  Education
                </Typography>
                <Button
                  variant="outlined"
                  size="small"
                  startIcon={<Add />}
                  onClick={addEditEducationEntry}
                  sx={{ borderRadius: 2 }}
                >
                  Add Education
                </Button>
              </Box>

              {editForm.education.map((edu, index) => (
                <Card
                  key={index}
                  sx={{
                    mb: 2,
                    border: "1px solid #e2e8f0",
                    borderRadius: 2,
                  }}
                >
                  <CardContent sx={{ p: 3 }}>
                    <Box
                      sx={{
                        display: "flex",
                        justifyContent: "space-between",
                        alignItems: "center",
                        mb: 2,
                      }}
                    >
                      <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                        Education #{index + 1}
                      </Typography>
                      <IconButton
                        onClick={() => removeEditEducationEntry(index)}
                        color="error"
                        size="small"
                      >
                        <Delete />
                      </IconButton>
                    </Box>

                    <Grid container spacing={2}>
                      <Grid item xs={12} md={6}>
                        <TextField
                          fullWidth
                          label="Degree/Program"
                          value={edu.degree}
                          onChange={(e) =>
                            updateEditEducationEntry(
                              index,
                              "degree",
                              e.target.value
                            )
                          }
                          size="small"
                          placeholder="e.g., Bachelor of Science"
                        />
                      </Grid>
                      <Grid item xs={12} md={6}>
                        <TextField
                          fullWidth
                          label="Institution"
                          value={edu.institution}
                          onChange={(e) =>
                            updateEditEducationEntry(
                              index,
                              "institution",
                              e.target.value
                            )
                          }
                          size="small"
                          placeholder="e.g., Edith Cowan University"
                        />
                      </Grid>
                      <Grid item xs={12} md={3}>
                        <TextField
                          fullWidth
                          label="Start Date"
                          type="date"
                          value={edu.start_date}
                          onChange={(e) =>
                            updateEditEducationEntry(
                              index,
                              "start_date",
                              e.target.value
                            )
                          }
                          InputLabelProps={{ shrink: true }}
                          size="small"
                        />
                      </Grid>
                      <Grid item xs={12} md={3}>
                        <TextField
                          fullWidth
                          label="End Date"
                          type="date"
                          value={edu.end_date}
                          onChange={(e) =>
                            updateEditEducationEntry(
                              index,
                              "end_date",
                              e.target.value
                            )
                          }
                          InputLabelProps={{ shrink: true }}
                          size="small"
                        />
                      </Grid>
                      <Grid item xs={12} md={6}>
                        <TextField
                          fullWidth
                          label="Field of Study"
                          value={edu.field_of_study}
                          onChange={(e) =>
                            updateEditEducationEntry(
                              index,
                              "field_of_study",
                              e.target.value
                            )
                          }
                          size="small"
                          placeholder="e.g., Computer Science"
                        />
                      </Grid>
                    </Grid>
                  </CardContent>
                </Card>
              ))}

              {editForm.education.length === 0 && (
                <Typography
                  variant="body2"
                  sx={{
                    color: "#64748b",
                    textAlign: "center",
                    py: 4,
                    border: "1px dashed #e2e8f0",
                    borderRadius: 2,
                  }}
                >
                  No education added yet. Click "Add Education" to add
                  educational background.
                </Typography>
              )}
            </Grid>
          </Grid>

          {editError && (
            <Alert severity="error" sx={{ mt: 3, borderRadius: 2 }}>
              {editError}
            </Alert>
          )}

          {editSuccess && (
            <Alert severity="success" sx={{ mt: 3, borderRadius: 2 }}>
              {editSuccess}
            </Alert>
          )}
        </DialogContent>
        <DialogActions sx={{ p: 3, pt: 2 }}>
          <Button
            onClick={handleCloseEditDialog}
            variant="outlined"
            sx={{ borderRadius: 2, textTransform: "none" }}
          >
            Cancel
          </Button>
          <Button
            onClick={handleEditSubmit}
            variant="contained"
            disabled={editLoading}
            sx={{
              borderRadius: 2,
              textTransform: "none",
              background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
              fontWeight: 600,
            }}
          >
            {editLoading ? (
              <>
                <CircularProgress size={20} sx={{ mr: 1 }} />
                Updating...
              </>
            ) : (
              "Update Profile"
            )}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog
        open={deleteDialogOpen}
        onClose={handleCloseDeleteDialog}
        maxWidth="sm"
        fullWidth
        sx={{
          "& .MuiDialog-paper": {
            borderRadius: 3,
          },
        }}
      >
        <DialogTitle
          sx={{
            display: "flex",
            alignItems: "center",
            gap: 2,
            pb: 1,
          }}
        >
          <DeleteForever sx={{ color: "#dc2626" }} />
          <Typography variant="h6" sx={{ fontWeight: 600 }}>
            Delete Alumni Profile
          </Typography>
        </DialogTitle>
        <DialogContent sx={{ p: 3 }}>
          <Typography variant="body1" sx={{ mb: 2 }}>
            Are you sure you want to delete the profile for{" "}
            <strong>{deletingAlumni?.name}</strong>?
          </Typography>
          <Typography variant="body2" sx={{ color: "#64748b" }}>
            This action cannot be undone. All work history, education records,
            and associated data will be permanently removed.
          </Typography>
        </DialogContent>
        <DialogActions sx={{ p: 3, pt: 2 }}>
          <Button
            onClick={handleCloseDeleteDialog}
            variant="outlined"
            sx={{ borderRadius: 2, textTransform: "none" }}
            disabled={deleteLoading}
          >
            Cancel
          </Button>
          <Button
            onClick={handleConfirmDelete}
            variant="contained"
            disabled={deleteLoading}
            sx={{
              borderRadius: 2,
              textTransform: "none",
              backgroundColor: "#dc2626",
              "&:hover": {
                backgroundColor: "#b91c1c",
              },
            }}
          >
            {deleteLoading ? (
              <>
                <CircularProgress size={20} sx={{ mr: 1 }} />
                Deleting...
              </>
            ) : (
              "Delete Profile"
            )}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
