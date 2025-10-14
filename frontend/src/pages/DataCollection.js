import React, { useState } from "react";
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  Chip,
  Alert,
  Switch,
  FormControlLabel,
  Grid,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  CircularProgress,
  Tabs,
  Tab,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
} from "@mui/material";
import {
  Add,
  Delete,
  CloudDownload,
  Psychology,
  CheckCircle,
  Error,
  Pending,
  Upload,
  Description,
} from "@mui/icons-material";
import axios from "axios";
import { api } from "../utils/api";

const TaskStatusChip = ({ status }) => {
  const getStatusProps = (status) => {
    switch (status) {
      case "completed":
        return { color: "success", icon: <CheckCircle />, label: "Completed" };
      case "failed":
        return { color: "error", icon: <Error />, label: "Failed" };
      case "running":
        return { color: "warning", icon: <Pending />, label: "Running" };
      default:
        return { color: "default", icon: <Pending />, label: "Unknown" };
    }
  };

  const props = getStatusProps(status);
  return (
    <Chip
      icon={props.icon}
      label={props.label}
      color={props.color}
      size="small"
      sx={{ borderRadius: 2 }}
    />
  );
};

export default function DataCollection({ token }) {
  const [tabValue, setTabValue] = useState(0);
  const [names, setNames] = useState([""]);
  const [useWebResearch, setUseWebResearch] = useState(true);
  const [loading, setLoading] = useState(false);
  const [tasks, setTasks] = useState([]);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [bulkImportOpen, setBulkImportOpen] = useState(false);
  const [bulkText, setBulkText] = useState("");
  const [fileUploadOpen, setFileUploadOpen] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploadLoading, setUploadLoading] = useState(false);

  // Manual form state
  const [manualForm, setManualForm] = useState({
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

  // Add work history entry
  const addWorkHistoryEntry = () => {
    setManualForm({
      ...manualForm,
      work_history: [
        ...manualForm.work_history,
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

  // Update work history entry
  const updateWorkHistoryEntry = (index, field, value) => {
    const updatedWorkHistory = [...manualForm.work_history];
    updatedWorkHistory[index][field] = value;
    setManualForm({ ...manualForm, work_history: updatedWorkHistory });
  };

  // Remove work history entry
  const removeWorkHistoryEntry = (index) => {
    setManualForm({
      ...manualForm,
      work_history: manualForm.work_history.filter((_, i) => i !== index),
    });
  };

  // Add education entry
  const addEducationEntry = () => {
    setManualForm({
      ...manualForm,
      education: [
        ...manualForm.education,
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

  // Update education entry
  const updateEducationEntry = (index, field, value) => {
    const updatedEducation = [...manualForm.education];
    updatedEducation[index][field] = value;
    setManualForm({ ...manualForm, education: updatedEducation });
  };

  // Remove education entry
  const removeEducationEntry = (index) => {
    setManualForm({
      ...manualForm,
      education: manualForm.education.filter((_, i) => i !== index),
    });
  };

  const addNameField = () => {
    setNames([...names, ""]);
  };

  const removeNameField = (index) => {
    setNames(names.filter((_, i) => i !== index));
  };

  const updateName = (index, value) => {
    const newNames = [...names];
    newNames[index] = value;
    setNames(newNames);
  };

  const handleBulkImport = () => {
    const importedNames = bulkText
      .split("\n")
      .map((name) => name.trim())
      .filter((name) => name.length > 0);

    setNames([...names.filter((n) => n.trim()), ...importedNames]);
    setBulkImportOpen(false);
    setBulkText("");
  };

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file) {
      if (
        file.name.endsWith(".xlsx") ||
        file.name.endsWith(".xls") ||
        file.name.endsWith(".csv")
      ) {
        setSelectedFile(file);
        setError("");
      } else {
        setError(
          "Please select an Excel file (.xlsx, .xls) or CSV file (.csv)"
        );
        setSelectedFile(null);
      }
    }
  };

  const handleExcelUpload = async () => {
    if (!selectedFile) {
      setError("Please select a file first");
      return;
    }

    setUploadLoading(true);
    setError("");
    setSuccess("");

    try {
      const formData = new FormData();
      formData.append("file", selectedFile);
      // Don't send auto_collect parameter, it defaults to false

      const response = await axios.post(api.endpoints.uploadNames, formData, {
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "multipart/form-data",
        },
      });

      const extractedNames = response.data.names;
      // Replace existing names with imported ones
      setNames(extractedNames);
      setSuccess(
        `Successfully imported ${extractedNames.length} names from ${selectedFile.name}`
      );

      // Close dialog and reset
      setFileUploadOpen(false);
      setSelectedFile(null);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to upload file");
    } finally {
      setUploadLoading(false);
    }
  };

  const startCollection = async () => {
    const validNames = names.filter((name) => name.trim());
    if (validNames.length === 0) {
      setError("Please add at least one name");
      return;
    }

    setLoading(true);
    setError("");
    setSuccess("");

    try {
      const response = await axios.post(
        api.endpoints.collect,
        {
          names: validNames,
          use_web_research: useWebResearch,
        },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      setSuccess(`Collection started! Task ID: ${response.data.task_id}`);

      // Add task to tracking list
      const newTask = {
        id: response.data.task_id,
        names: validNames,
        status: "running",
        timestamp: new Date().toLocaleString(),
        method: "Web Research",
      };
      setTasks([newTask, ...tasks]);

      // Clear form
      setNames([""]);

      // Start polling for status
      pollTaskStatus(response.data.task_id);
    } catch (err) {
      setError("Failed to start collection");
    } finally {
      setLoading(false);
    }
  };

  const pollTaskStatus = async (taskId) => {
    try {
      const response = await axios.get(
        `${api.endpoints.collect}/status/${taskId}`,
        { headers: { Authorization: `Bearer ${token}` } }
      );

      // Update task status in the list
      setTasks((prevTasks) =>
        prevTasks.map((task) =>
          task.id === taskId
            ? {
                ...task,
                status: response.data.status,
                results: response.data.results_count || task.results,
              }
            : task
        )
      );

      // Continue polling if still running
      if (response.data.status === "running") {
        setTimeout(() => pollTaskStatus(taskId), 2000); // Poll every 2 seconds
      }
    } catch (err) {
      console.error("Failed to poll task status:", err);
      // Update task as failed if we can't get status
      setTasks((prevTasks) =>
        prevTasks.map((task) =>
          task.id === taskId ? { ...task, status: "failed" } : task
        )
      );
    }
  };

  const handleManualSubmit = async () => {
    if (!manualForm.full_name.trim()) {
      setError("Full name is required");
      return;
    }

    setLoading(true);
    setError("");
    setSuccess("");

    try {
      // Format work history and education for backend
      const formattedWorkHistory = manualForm.work_history
        .map(
          (job) =>
            `${job.title} - ${job.company} - ${job.start_date || ""} - ${
              job.end_date || ""
            }`
        )
        .join("\n");

      const formattedEducation = manualForm.education
        .map(
          (edu) =>
            `${edu.degree} - ${edu.institution} - ${edu.start_date || ""} - ${
              edu.end_date || ""
            }`
        )
        .join("\n");

      const submitData = {
        ...manualForm,
        graduation_year:
          manualForm.graduation_year === ""
            ? null
            : parseInt(manualForm.graduation_year),
        work_history: formattedWorkHistory,
        education: formattedEducation,
      };

      await axios.post(api.endpoints.manualCollect, submitData, {
        headers: { Authorization: `Bearer ${token}` },
      });

      setSuccess("Manual alumni data saved successfully!");

      // Reset form
      setManualForm({
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
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to save manual data");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box>
      <Typography
        variant="h4"
        sx={{ mb: 4, fontWeight: 700, color: "#1e293b" }}
      >
        Data Collection
      </Typography>
      <Tabs
        value={tabValue}
        onChange={(e, newValue) => setTabValue(newValue)}
        sx={{ mb: 3 }}
      >
        <Tab label="Automated Collection" />
        <Tab label="Manual Entry" />
      </Tabs>
      {tabValue === 0 && (
        <Grid container spacing={3}>
          <Grid item xs={12} md={8}>
            <Card
              sx={{
                borderRadius: 3,
                boxShadow: "0 4px 20px rgba(0,0,0,0.08)",
                mb: 3,
              }}
            >
              <CardContent sx={{ p: 4 }}>
                <Box sx={{ display: "flex", alignItems: "center", mb: 3 }}>
                  <CloudDownload sx={{ mr: 2, color: "#667eea" }} />
                  <Typography variant="h6" sx={{ fontWeight: 600 }}>
                    Collect Alumni Data
                  </Typography>
                </Box>

                <Typography variant="body2" sx={{ color: "#64748b", mb: 3 }}>
                  Enter alumni names to collect their professional information
                  from web research and public sources.
                </Typography>

                <Box sx={{ mb: 3 }}>
                  <Box
                    sx={{
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "center",
                      mb: 2,
                    }}
                  >
                    <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                      Alumni Names
                    </Typography>
                    <Box sx={{ display: "flex", gap: 1 }}>
                      <Button
                        variant="outlined"
                        size="small"
                        startIcon={<Upload />}
                        onClick={() => setFileUploadOpen(true)}
                        sx={{ borderRadius: 2 }}
                      >
                        File Upload
                      </Button>
                      <Button
                        variant="outlined"
                        size="small"
                        onClick={() => setBulkImportOpen(true)}
                        sx={{ borderRadius: 2 }}
                      >
                        Text Import
                      </Button>
                    </Box>
                  </Box>

                  {names.map((name, index) => (
                    <Box key={index} sx={{ display: "flex", gap: 1, mb: 2 }}>
                      <TextField
                        fullWidth
                        placeholder="Enter full name (e.g., John Smith)"
                        value={name}
                        onChange={(e) => updateName(index, e.target.value)}
                        sx={{
                          "& .MuiOutlinedInput-root": {
                            borderRadius: 2,
                          },
                        }}
                      />
                      {names.length > 1 && (
                        <IconButton
                          onClick={() => removeNameField(index)}
                          color="error"
                        >
                          <Delete />
                        </IconButton>
                      )}
                    </Box>
                  ))}

                  <Button
                    variant="outlined"
                    startIcon={<Add />}
                    onClick={addNameField}
                    sx={{ borderRadius: 2 }}
                  >
                    Add Another Name
                  </Button>
                </Box>

                <Box sx={{ mb: 3 }}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={useWebResearch}
                        onChange={(e) => setUseWebResearch(e.target.checked)}
                      />
                    }
                    label={
                      <Box sx={{ display: "flex", alignItems: "center" }}>
                        <Psychology sx={{ mr: 1, color: "#667eea" }} />
                        <Typography variant="body2">
                          Use AI-powered web research (default - comprehensive
                          but slower)
                        </Typography>
                      </Box>
                    }
                  />
                  <Typography
                    variant="caption"
                    sx={{ color: "#64748b", display: "block", mt: 1 }}
                  >
                    Web research uses AI to analyze public web results for
                    comprehensive data collection
                  </Typography>
                </Box>

                {error && (
                  <Alert severity="error" sx={{ mb: 3, borderRadius: 2 }}>
                    {error}
                  </Alert>
                )}

                {success && (
                  <Alert severity="success" sx={{ mb: 3, borderRadius: 2 }}>
                    {success}
                  </Alert>
                )}

                <Button
                  variant="contained"
                  onClick={startCollection}
                  disabled={loading}
                  fullWidth
                  sx={{
                    py: 1.5,
                    borderRadius: 2,
                    background:
                      "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                    fontWeight: 600,
                  }}
                >
                  {loading ? "Starting Collection..." : "Start Collection"}
                </Button>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={4}>
            <Card
              sx={{ borderRadius: 3, boxShadow: "0 4px 20px rgba(0,0,0,0.08)" }}
            >
              <CardContent sx={{ p: 3 }}>
                <Typography variant="h6" sx={{ mb: 3, fontWeight: 600 }}>
                  Collection Tasks
                </Typography>

                {tasks.length === 0 ? (
                  <Typography
                    variant="body2"
                    sx={{ color: "#64748b", textAlign: "center", py: 4 }}
                  >
                    No collection tasks yet
                  </Typography>
                ) : (
                  <List>
                    {tasks.map((task, index) => (
                      <ListItem key={index} sx={{ px: 0, py: 2 }}>
                        <ListItemText
                          primary={
                            <Typography
                              variant="body2"
                              sx={{ fontWeight: 600 }}
                            >
                              {task.names.length} alumni
                            </Typography>
                          }
                          secondary={
                            <Box>
                              <Typography
                                variant="caption"
                                sx={{ color: "#64748b" }}
                              >
                                {task.timestamp}
                              </Typography>
                              {task.method === "Web Research" && (
                                <Chip
                                  label="Web Research"
                                  size="small"
                                  sx={{ ml: 1, height: 20 }}
                                />
                              )}
                              {task.results && (
                                <Typography
                                  variant="caption"
                                  sx={{ display: "block", mt: 0.5 }}
                                >
                                  {task.results} profiles collected
                                </Typography>
                              )}
                            </Box>
                          }
                        />
                        <ListItemSecondaryAction>
                          <TaskStatusChip status={task.status} />
                        </ListItemSecondaryAction>
                      </ListItem>
                    ))}
                  </List>
                )}
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}
      {tabValue === 1 && (
        <Grid container spacing={3}>
          <Grid item xs={12} md={8}>
            <Card
              sx={{
                borderRadius: 3,
                boxShadow: "0 4px 20px rgba(0,0,0,0.08)",
                mb: 3,
              }}
            >
              <CardContent sx={{ p: 4 }}>
                <Box sx={{ display: "flex", alignItems: "center", mb: 3 }}>
                  <Description sx={{ mr: 2, color: "#667eea" }} />
                  <Typography variant="h6" sx={{ fontWeight: 600 }}>
                    Manual Alumni Entry
                  </Typography>
                </Box>

                <Typography variant="body2" sx={{ color: "#64748b", mb: 3 }}>
                  Enter alumni details manually. All fields are optional except
                  full name.
                </Typography>

                <Alert severity="info" sx={{ mb: 3, borderRadius: 2 }}>
                  <Typography variant="body2">
                    <strong>Tip:</strong> Fields marked with * are required.
                    Graduation year and other dates can be left blank if
                    unknown.
                  </Typography>
                </Alert>

                <Grid container spacing={3}>
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      label="Full Name *"
                      placeholder="e.g., John Smith"
                      value={manualForm.full_name}
                      onChange={(e) =>
                        setManualForm({
                          ...manualForm,
                          full_name: e.target.value,
                        })
                      }
                      sx={{ mb: 2 }}
                    />
                    <FormControl fullWidth sx={{ mb: 2 }}>
                      <InputLabel>Graduation Year</InputLabel>
                      <Select
                        value={manualForm.graduation_year}
                        onChange={(e) =>
                          setManualForm({
                            ...manualForm,
                            graduation_year: e.target.value,
                          })
                        }
                      >
                        <MenuItem value="">
                          <em>Not specified</em>
                        </MenuItem>
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
                      placeholder="e.g., Perth, Australia"
                      value={manualForm.location}
                      onChange={(e) =>
                        setManualForm({
                          ...manualForm,
                          location: e.target.value,
                        })
                      }
                      sx={{ mb: 2 }}
                    />
                    <FormControl fullWidth sx={{ mb: 2 }}>
                      <InputLabel>Industry</InputLabel>
                      <Select
                        value={manualForm.industry}
                        onChange={(e) =>
                          setManualForm({
                            ...manualForm,
                            industry: e.target.value,
                          })
                        }
                      >
                        <MenuItem value="">
                          <em>Not specified</em>
                        </MenuItem>
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
                      placeholder="e.g., https://linkedin.com/in/johnsmith"
                      value={manualForm.linkedin_url}
                      onChange={(e) =>
                        setManualForm({
                          ...manualForm,
                          linkedin_url: e.target.value,
                        })
                      }
                      sx={{ mb: 2 }}
                    />
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <Typography
                      variant="subtitle2"
                      sx={{ mb: 2, fontWeight: 600 }}
                    >
                      Current Job
                    </Typography>
                    <TextField
                      fullWidth
                      label="Job Title"
                      placeholder="e.g., Software Engineer"
                      value={manualForm.current_job_title}
                      onChange={(e) =>
                        setManualForm({
                          ...manualForm,
                          current_job_title: e.target.value,
                        })
                      }
                      sx={{ mb: 2 }}
                    />
                    <TextField
                      fullWidth
                      label="Company"
                      placeholder="e.g., Tech Corp Pty Ltd"
                      value={manualForm.current_job_company}
                      onChange={(e) =>
                        setManualForm({
                          ...manualForm,
                          current_job_company: e.target.value,
                        })
                      }
                      sx={{ mb: 2 }}
                    />
                    <TextField
                      fullWidth
                      label="Start Date"
                      type="date"
                      value={manualForm.current_job_start_date}
                      onChange={(e) =>
                        setManualForm({
                          ...manualForm,
                          current_job_start_date: e.target.value,
                        })
                      }
                      InputLabelProps={{ shrink: true }}
                      sx={{ mb: 2 }}
                    />
                    <TextField
                      fullWidth
                      label="Job Industry"
                      placeholder="e.g., Technology"
                      value={manualForm.current_job_industry}
                      onChange={(e) =>
                        setManualForm({
                          ...manualForm,
                          current_job_industry: e.target.value,
                        })
                      }
                      sx={{ mb: 2 }}
                    />
                    <TextField
                      fullWidth
                      label="Job Location"
                      placeholder="e.g., Perth, WA"
                      value={manualForm.current_job_location}
                      onChange={(e) =>
                        setManualForm({
                          ...manualForm,
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
                        onClick={addWorkHistoryEntry}
                        sx={{ borderRadius: 2 }}
                      >
                        Add Job
                      </Button>
                    </Box>

                    {manualForm.work_history.map((job, index) => (
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
                            <Typography
                              variant="subtitle2"
                              sx={{ fontWeight: 600 }}
                            >
                              Job #{index + 1}
                            </Typography>
                            <IconButton
                              onClick={() => removeWorkHistoryEntry(index)}
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
                                placeholder="e.g., Senior Developer"
                                value={job.title}
                                onChange={(e) =>
                                  updateWorkHistoryEntry(
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
                                placeholder="e.g., ABC Corporation"
                                value={job.company}
                                onChange={(e) =>
                                  updateWorkHistoryEntry(
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
                                  updateWorkHistoryEntry(
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
                                  updateWorkHistoryEntry(
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
                                placeholder="e.g., Technology"
                                value={job.industry}
                                onChange={(e) =>
                                  updateWorkHistoryEntry(
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
                                placeholder="e.g., Sydney, NSW"
                                value={job.location}
                                onChange={(e) =>
                                  updateWorkHistoryEntry(
                                    index,
                                    "location",
                                    e.target.value
                                  )
                                }
                                InputLabelProps={{ shrink: true }}
                                size="small"
                              />
                            </Grid>
                          </Grid>
                        </CardContent>
                      </Card>
                    ))}

                    {manualForm.work_history.length === 0 && (
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
                        onClick={addEducationEntry}
                        sx={{ borderRadius: 2 }}
                      >
                        Add Education
                      </Button>
                    </Box>

                    {manualForm.education.map((edu, index) => (
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
                            <Typography
                              variant="subtitle2"
                              sx={{ fontWeight: 600 }}
                            >
                              Education #{index + 1}
                            </Typography>
                            <IconButton
                              onClick={() => removeEducationEntry(index)}
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
                                  updateEducationEntry(
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
                                  updateEducationEntry(
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
                                  updateEducationEntry(
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
                                  updateEducationEntry(
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
                                  updateEducationEntry(
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

                    {manualForm.education.length === 0 && (
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

                {error && (
                  <Alert severity="error" sx={{ mb: 3, borderRadius: 2 }}>
                    {error}
                  </Alert>
                )}

                {success && (
                  <Alert severity="success" sx={{ mb: 3, borderRadius: 2 }}>
                    {success}
                  </Alert>
                )}

                <Button
                  variant="contained"
                  onClick={handleManualSubmit}
                  disabled={loading}
                  fullWidth
                  sx={{
                    py: 1.5,
                    borderRadius: 2,
                    background:
                      "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                    fontWeight: 600,
                  }}
                >
                  {loading ? "Saving..." : "Save Alumni Data"}
                </Button>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}{" "}
      {/* Bulk Import Dialog */}
      <Dialog
        open={bulkImportOpen}
        onClose={() => setBulkImportOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Text Import Names</DialogTitle>
        <DialogContent>
          <Typography variant="body2" sx={{ color: "#64748b", mb: 2 }}>
            Enter one name per line:
          </Typography>
          <TextField
            fullWidth
            multiline
            rows={8}
            placeholder="John Smith&#10;Jane Doe&#10;Michael Johnson&#10;..."
            value={bulkText}
            onChange={(e) => setBulkText(e.target.value)}
            sx={{
              "& .MuiOutlinedInput-root": {
                borderRadius: 2,
              },
            }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setBulkImportOpen(false)}>Cancel</Button>
          <Button
            onClick={handleBulkImport}
            variant="contained"
            disabled={!bulkText.trim()}
          >
            Import Names
          </Button>
        </DialogActions>
      </Dialog>
      {/* File Upload Dialog */}
      <Dialog
        open={fileUploadOpen}
        onClose={() => setFileUploadOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>
          <Box sx={{ display: "flex", alignItems: "center" }}>
            <Description sx={{ mr: 1, color: "#667eea" }} />
            File Upload (Excel/CSV)
          </Box>
        </DialogTitle>
        <DialogContent>
          <Typography variant="body2" sx={{ color: "#64748b", mb: 3 }}>
            Upload an Excel file (.xlsx, .xls) or CSV file (.csv) with alumni
            names. The file should contain columns named "GIVEN NAME" and "FIRST
            NAME".
          </Typography>

          <Box
            sx={{
              border: "2px dashed #e2e8f0",
              borderRadius: 2,
              p: 3,
              textAlign: "center",
              backgroundColor: selectedFile ? "#f0f9ff" : "#f8fafc",
              borderColor: selectedFile ? "#0ea5e9" : "#e2e8f0",
            }}
          >
            <input
              type="file"
              accept=".xlsx,.xls,.csv"
              onChange={handleFileSelect}
              style={{ display: "none" }}
              id="file-upload"
            />
            <label htmlFor="file-upload">
              <Button
                component="span"
                variant="outlined"
                startIcon={<Upload />}
                sx={{ mb: 2 }}
              >
                Choose File (Excel/CSV)
              </Button>
            </label>

            {selectedFile ? (
              <Box>
                <Typography
                  variant="body2"
                  sx={{ fontWeight: 600, color: "#0ea5e9" }}
                >
                  {selectedFile.name}
                </Typography>
                <Typography variant="caption" sx={{ color: "#64748b" }}>
                  {(selectedFile.size / 1024).toFixed(1)} KB
                </Typography>
              </Box>
            ) : (
              <Typography variant="body2" sx={{ color: "#64748b" }}>
                Select an Excel or CSV file with GIVEN NAME and FIRST NAME
                columns
              </Typography>
            )}
          </Box>

          <Box sx={{ mt: 3, p: 2, bgcolor: "#fef3c7", borderRadius: 2 }}>
            <Box
              sx={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
              }}
            >
              <Box>
                <Typography
                  variant="caption"
                  sx={{ color: "#92400e", fontWeight: 600 }}
                >
                  Required File Format:
                </Typography>
                <Typography
                  variant="caption"
                  sx={{ display: "block", color: "#92400e", mt: 0.5 }}
                >
                  Column A: GIVEN NAME | Column B: FIRST NAME
                </Typography>
              </Box>
              <Button
                size="small"
                variant="outlined"
                onClick={() => {
                  // Create and download template
                  const csvContent =
                    "GIVEN NAME,FIRST NAME\nJohn,Smith\nJane,Doe\nMichael,Johnson";
                  const blob = new Blob([csvContent], { type: "text/csv" });
                  const url = window.URL.createObjectURL(blob);
                  const a = document.createElement("a");
                  a.href = url;
                  a.download = "alumni_template.csv";
                  a.click();
                  window.URL.revokeObjectURL(url);
                }}
                sx={{
                  borderColor: "#92400e",
                  color: "#92400e",
                  "&:hover": {
                    borderColor: "#78350f",
                    backgroundColor: "rgba(146, 64, 14, 0.1)",
                  },
                }}
              >
                Download Template
              </Button>
            </Box>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button
            onClick={() => {
              setFileUploadOpen(false);
              setSelectedFile(null);
            }}
          >
            Cancel
          </Button>
          <Button
            onClick={handleExcelUpload}
            variant="contained"
            disabled={!selectedFile || uploadLoading}
            startIcon={
              uploadLoading ? <CircularProgress size={20} /> : <Upload />
            }
          >
            {uploadLoading ? "Uploading..." : "Upload & Import"}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
