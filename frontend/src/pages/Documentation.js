import React, { useState } from "react";
import {
  Box,
  Typography,
  Paper,
  Stepper,
  Step,
  StepLabel,
  StepContent,
  Card,
  CardContent,
  Grid,
  Divider,
  Chip,
  Alert,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Button,
} from "@mui/material";
import {
  MenuBook,
  PlayArrow,
  Check,
  Info,
  Warning,
  ExpandMore,
  Upload,
  Search,
  People,
  Assessment,
  Help,
  Settings,
} from "@mui/icons-material";

const Documentation = () => {
  const [activeStep, setActiveStep] = useState(0);

  const gettingStartedSteps = [
    {
      label: "Login to the System",
      description: "Use your ECU credentials to access the Alumni Tracking System.",
      image: "login-screen.png",
      details: [
        "Navigate to the login page",
        "Enter your email address",
        "Enter your password",
        "Click 'Sign In' to access the dashboard",
      ],
    },
    {
      label: "Dashboard Overview",
      description: "Familiarize yourself with the main dashboard and key metrics.",
      image: "dashboard-overview.png",
      details: [
        "View total alumni count",
        "Check LinkedIn coverage percentage",
        "Review employment statistics",
        "Examine confidence scores",
        "Explore industry and location distributions",
      ],
    },
    {
      label: "Navigate the System",
      description: "Learn how to move between different sections.",
      image: "navigation-menu.png",
      details: [
        "Use the sidebar menu to switch between pages",
        "Access Dashboard for analytics overview",
        "Browse Alumni directory for detailed profiles",
        "Use Data Collection for adding new alumni",
        "Explore AI Analytics for insights",
      ],
    },
  ];

  const dataCollectionSteps = [
    {
      label: "Manual Data Entry",
      description: "Add alumni information manually through the form interface.",
      image: "manual-entry-form.png",
      steps: [
        "Navigate to 'Data Collection' page",
        "Click 'Add Alumni Manually' button",
        "Fill in required fields (Full Name, Graduation Year)",
        "Add optional information (Location, Industry, LinkedIn URL)",
        "Add work history and education details",
        "Click 'Save' to store the profile",
      ],
    },
    {
      label: "Batch Upload via CSV",
      description: "Import multiple alumni records at once using CSV files.",
      image: "csv-upload-interface.png",
      steps: [
        "Prepare CSV file with required columns: Full Name, Graduation Year",
        "Optional columns: Location, Industry, LinkedIn URL, Current Job, Company",
        "Navigate to 'Data Collection' page",
        "Click 'Upload CSV' button",
        "Select your CSV file",
        "Review the upload preview",
        "Confirm import to add records to database",
      ],
    },
    {
      label: "Web Research Collection",
      description: "Use AI-powered web research to automatically gather alumni data.",
      image: "web-research-interface.png",
      steps: [
        "Navigate to 'Data Collection' page",
        "Select 'Web Research' method",
        "Enter alumni names (one per line)",
        "Click 'Start Collection'",
        "Monitor progress in real-time",
        "Review collected data with confidence scores",
        "Verify and approve AI-collected information",
      ],
    },
  ];

  const alumniManagementFeatures = [
    {
      title: "Search and Filter",
      icon: <Search />,
      description: "Quickly find alumni using multiple search criteria",
      image: "search-filter.png",
      features: [
        "Search by name, industry, or company",
        "Filter by graduation year range",
        "Filter by location",
        "Sort by confidence score",
      ],
    },
    {
      title: "View Detailed Profiles",
      icon: <People />,
      description: "Access comprehensive alumni information",
      image: "alumni-profile-detail.png",
      features: [
        "View complete work history",
        "Access education background",
        "Check LinkedIn profile links",
        "Review confidence scores",
        "See data collection sources",
      ],
    },
    {
      title: "Edit Alumni Records",
      icon: <Settings />,
      description: "Update and maintain accurate alumni information",
      image: "edit-alumni-form.png",
      features: [
        "Edit basic information",
        "Update current position",
        "Modify work history entries",
        "Update education records",
        "Change LinkedIn URL",
      ],
    },
    {
      title: "Export Data",
      icon: <Upload />,
      description: "Export alumni data for external use",
      image: "export-options.png",
      features: [
        "Export to Excel (.xlsx)",
        "Export to CSV format",
        "Filter data before export",
        "Include/exclude specific fields",
      ],
    },
  ];

  const analyticsFeatures = [
    {
      title: "Industry Distribution",
      description: "Visualize alumni across different industries",
      image: "industry-chart.png",
      insights: [
        "Identify top industries",
        "Track career trends",
        "Compare sector representation",
      ],
    },
    {
      title: "Location Analysis",
      description: "Geographic distribution of alumni",
      image: "location-chart.png",
      insights: [
        "View alumni by city/region",
        "Identify geographic clusters",
        "Track migration patterns",
      ],
    },
    {
      title: "Graduation Year Trends",
      description: "Alumni distribution by graduation year",
      image: "graduation-year-chart.png",
      insights: [
        "View cohort sizes",
        "Track data coverage by year",
        "Identify gaps in records",
      ],
    },
    {
      title: "Top Companies",
      description: "Organizations employing ECU alumni",
      image: "top-companies.png",
      insights: [
        "See major employers",
        "Track company representation",
        "Identify partnership opportunities",
      ],
    },
    {
      title: "Confidence Scores",
      description: "Data quality and reliability metrics",
      image: "confidence-scores.png",
      insights: [
        "Assess data accuracy",
        "Identify records needing review",
        "Track verification status",
      ],
    },
  ];

  const troubleshootingTopics = [
    {
      issue: "Unable to login",
      solutions: [
        "Verify your email address is correct",
        "Check your password (case-sensitive)",
        "Ensure you have proper account permissions",
        "Contact IT support if credentials are lost",
      ],
    },
    {
      issue: "Data collection is slow",
      solutions: [
        "Web research can take 2-5 minutes per alumni",
        "Use batch collection for multiple names",
        "Check your internet connection",
        "Consider collecting in smaller batches",
      ],
    },
    {
      issue: "Low confidence scores",
      solutions: [
        "Review and verify AI-collected data manually",
        "Add LinkedIn URLs for better accuracy",
        "Update profiles with more recent information",
        "Use manual entry for difficult cases",
      ],
    },
    {
      issue: "CSV upload fails",
      solutions: [
        "Ensure CSV has required columns: Full Name, Graduation Year",
        "Check for special characters in data",
        "Verify file encoding is UTF-8",
        "Ensure dates are in correct format (YYYY-MM-DD)",
      ],
    },
    {
      issue: "Dashboard loads slowly",
      solutions: [
        "Backend is optimized with SQL queries",
        "Clear browser cache if needed",
        "Check network connection",
        "Contact administrator if persistent",
      ],
    },
  ];

  return (
    <Box>
      <Box sx={{ mb: 4 }}>
        <Typography
          variant="h3"
          sx={{ mb: 2, fontWeight: "bold", color: "#333", display: "flex", alignItems: "center", gap: 2 }}
        >
          <MenuBook sx={{ fontSize: 40, color: "#667eea" }} />
          System Documentation
        </Typography>
        <Typography variant="h6" sx={{ color: "#666", mb: 3 }}>
          Complete guide to using the ECU Alumni Tracking System
        </Typography>
        <Alert severity="info" sx={{ borderRadius: 2 }}>
          <Typography variant="body2">
            <strong>Welcome!</strong> This documentation provides step-by-step guidance for using all features of the alumni tracking system.
            Screenshots and diagrams are included to help you navigate the interface.
          </Typography>
        </Alert>
      </Box>

      {/* Getting Started Section */}
      <Paper sx={{ p: 4, mb: 4, borderRadius: 3, boxShadow: 3 }}>
        <Typography variant="h4" sx={{ mb: 3, fontWeight: "bold", display: "flex", alignItems: "center", gap: 2 }}>
          <PlayArrow sx={{ color: "#667eea" }} />
          Getting Started
        </Typography>
        <Divider sx={{ mb: 3 }} />
        
        <Stepper activeStep={activeStep} orientation="vertical">
          {gettingStartedSteps.map((step, index) => (
            <Step key={step.label}>
              <StepLabel
                onClick={() => setActiveStep(index)}
                sx={{ cursor: "pointer" }}
              >
                <Typography variant="h6">{step.label}</Typography>
              </StepLabel>
              <StepContent>
                <Typography variant="body1" sx={{ mb: 2, color: "#666" }}>
                  {step.description}
                </Typography>
                
                {/* Image */}
                <Box sx={{ mb: 2, textAlign: "center" }}>
                  <img 
                    src={`/docs-images/${step.image}`} 
                    alt={step.label}
                    style={{ 
                      width: '100%', 
                      maxWidth: '600px', 
                      borderRadius: '8px',
                      border: '1px solid #e0e0e0',
                      boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
                    }}
                  />
                </Box>

                <List dense>
                  {step.details.map((detail, idx) => (
                    <ListItem key={idx}>
                      <ListItemIcon>
                        <Check sx={{ color: "#4caf50" }} />
                      </ListItemIcon>
                      <ListItemText primary={detail} />
                    </ListItem>
                  ))}
                </List>

                <Box sx={{ mb: 2, mt: 2 }}>
                  <Button
                    variant="contained"
                    onClick={() => setActiveStep(index + 1)}
                    sx={{ mt: 1, mr: 1 }}
                    disabled={index === gettingStartedSteps.length - 1}
                  >
                    Continue
                  </Button>
                  <Button
                    disabled={index === 0}
                    onClick={() => setActiveStep(index - 1)}
                    sx={{ mt: 1, mr: 1 }}
                  >
                    Back
                  </Button>
                </Box>
              </StepContent>
            </Step>
          ))}
        </Stepper>
      </Paper>

      {/* Data Collection Section */}
      <Paper sx={{ p: 4, mb: 4, borderRadius: 3, boxShadow: 3 }}>
        <Typography variant="h4" sx={{ mb: 3, fontWeight: "bold", display: "flex", alignItems: "center", gap: 2 }}>
          <Upload sx={{ color: "#667eea" }} />
          Data Collection Methods
        </Typography>
        <Divider sx={{ mb: 3 }} />

        {dataCollectionSteps.map((method, index) => (
          <Accordion key={index} sx={{ mb: 2, borderRadius: 2 }}>
            <AccordionSummary expandIcon={<ExpandMore />}>
              <Typography variant="h6" sx={{ fontWeight: 600 }}>
                {index + 1}. {method.label}
              </Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Typography variant="body1" sx={{ mb: 2, color: "#666" }}>
                {method.description}
              </Typography>

              {/* Image */}
              <Box sx={{ mb: 3, textAlign: "center" }}>
                <img 
                  src={`/docs-images/${method.image}`} 
                  alt={method.label}
                  style={{ 
                    width: '100%', 
                    maxWidth: '600px', 
                    borderRadius: '8px',
                    border: '1px solid #e0e0e0',
                    boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
                  }}
                />
              </Box>

              <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 2 }}>
                Steps to Follow:
              </Typography>
              <List>
                {method.steps.map((step, idx) => (
                  <ListItem key={idx}>
                    <ListItemIcon>
                      <Chip label={idx + 1} size="small" sx={{ bgcolor: "#667eea", color: "white" }} />
                    </ListItemIcon>
                    <ListItemText primary={step} />
                  </ListItem>
                ))}
              </List>
            </AccordionDetails>
          </Accordion>
        ))}
      </Paper>

      {/* Alumni Management Section */}
      <Paper sx={{ p: 4, mb: 4, borderRadius: 3, boxShadow: 3 }}>
        <Typography variant="h4" sx={{ mb: 3, fontWeight: "bold", display: "flex", alignItems: "center", gap: 2 }}>
          <People sx={{ color: "#667eea" }} />
          Alumni Management
        </Typography>
        <Divider sx={{ mb: 3 }} />

        <Grid container spacing={3}>
          {alumniManagementFeatures
            .filter(feature => feature.title !== "Export Data")
            .map((feature, index) => (
            <Grid item xs={12} md={6} key={index}>
              <Card sx={{ height: "100%", borderRadius: 2, border: "1px solid #e0e0e0" }}>
                <CardContent>
                  <Box sx={{ display: "flex", alignItems: "center", gap: 2, mb: 2 }}>
                    <Box sx={{ p: 1, bgcolor: "#e0e7ff", borderRadius: 2 }}>
                      {React.cloneElement(feature.icon, { sx: { color: "#667eea" } })}
                    </Box>
                    <Typography variant="h6" sx={{ fontWeight: 600 }}>
                      {feature.title}
                    </Typography>
                  </Box>
                  
                  <Typography variant="body2" sx={{ mb: 2, color: "#666" }}>
                    {feature.description}
                  </Typography>

                  {/* Image */}
                  <Box sx={{ mb: 2, textAlign: "center" }}>
                    <img 
                      src={`/docs-images/${feature.image}`} 
                      alt={feature.title}
                      style={{ 
                        width: '100%', 
                        maxWidth: '400px', 
                        borderRadius: '8px',
                        border: '1px solid #e0e0e0',
                        boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
                      }}
                    />
                  </Box>

                  <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 600 }}>
                    Key Features:
                  </Typography>
                  <List dense>
                    {feature.features.map((item, idx) => (
                      <ListItem key={idx}>
                        <ListItemIcon sx={{ minWidth: 30 }}>
                          <Check sx={{ fontSize: 16, color: "#4caf50" }} />
                        </ListItemIcon>
                        <ListItemText primary={item} primaryTypographyProps={{ variant: "body2" }} />
                      </ListItem>
                    ))}
                  </List>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Paper>

      {/* Analytics Section */}
      <Paper sx={{ p: 4, mb: 4, borderRadius: 3, boxShadow: 3 }}>
        <Typography variant="h4" sx={{ mb: 3, fontWeight: "bold", display: "flex", alignItems: "center", gap: 2 }}>
          <Assessment sx={{ color: "#667eea" }} />
          Analytics & Insights
        </Typography>
        <Divider sx={{ mb: 3 }} />

        <Typography variant="body1" sx={{ mb: 3, color: "#666" }}>
          The analytics dashboard provides comprehensive visualizations and insights about your alumni network.
          Use these charts to understand trends, identify opportunities, and make data-driven decisions.
        </Typography>

        <Grid container spacing={3}>
          {analyticsFeatures
            .filter(feature => 
              feature.title !== "Graduation Year Trends" && 
              feature.title !== "Location Analysis" && 
              feature.title !== "Top Companies"
            )
            .map((feature, index) => (
            <Grid item xs={12} md={6} lg={4} key={index}>
              <Card sx={{ height: "100%", borderRadius: 2 }}>
                <CardContent>
                  <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
                    {feature.title}
                  </Typography>
                  
                  {/* Image */}
                  <Box sx={{ mb: 2, textAlign: "center" }}>
                    <img 
                      src={`/docs-images/${feature.image}`} 
                      alt={feature.title}
                      style={{ 
                        width: '100%', 
                        maxWidth: '300px', 
                        borderRadius: '8px',
                        border: '1px solid #e0e0e0',
                        boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
                      }}
                    />
                  </Box>

                  <Typography variant="body2" sx={{ mb: 2, color: "#666" }}>
                    {feature.description}
                  </Typography>

                  <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 600 }}>
                    What You Can Learn:
                  </Typography>
                  <List dense>
                    {feature.insights.map((insight, idx) => (
                      <ListItem key={idx}>
                        <ListItemIcon sx={{ minWidth: 25 }}>
                          <Info sx={{ fontSize: 14, color: "#667eea" }} />
                        </ListItemIcon>
                        <ListItemText primary={insight} primaryTypographyProps={{ variant: "body2" }} />
                      </ListItem>
                    ))}
                  </List>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Paper>

      {/* Troubleshooting Section */}
      <Paper sx={{ p: 4, mb: 4, borderRadius: 3, boxShadow: 3 }}>
        <Typography variant="h4" sx={{ mb: 3, fontWeight: "bold", display: "flex", alignItems: "center", gap: 2 }}>
          <Help sx={{ color: "#667eea" }} />
          Troubleshooting & FAQ
        </Typography>
        <Divider sx={{ mb: 3 }} />

        {troubleshootingTopics.map((topic, index) => (
          <Accordion key={index} sx={{ mb: 2, borderRadius: 2 }}>
            <AccordionSummary expandIcon={<ExpandMore />}>
              <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
                <Warning sx={{ color: "#ff9800" }} />
                <Typography variant="h6" sx={{ fontWeight: 600 }}>
                  {topic.issue}
                </Typography>
              </Box>
            </AccordionSummary>
            <AccordionDetails>
              <Typography variant="subtitle2" sx={{ mb: 2, fontWeight: 600 }}>
                Solutions:
              </Typography>
              <List>
                {topic.solutions.map((solution, idx) => (
                  <ListItem key={idx}>
                    <ListItemIcon>
                      <Check sx={{ color: "#4caf50" }} />
                    </ListItemIcon>
                    <ListItemText primary={solution} />
                  </ListItem>
                ))}
              </List>
            </AccordionDetails>
          </Accordion>
        ))}
      </Paper>

      {/* Best Practices Section */}
      <Paper sx={{ p: 4, mb: 4, borderRadius: 3, boxShadow: 3, bgcolor: "#f8fafc" }}>
        <Typography variant="h4" sx={{ mb: 3, fontWeight: "bold" }}>
          Best Practices
        </Typography>
        <Divider sx={{ mb: 3 }} />

        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Card sx={{ height: "100%", borderRadius: 2, border: "2px solid #4caf50" }}>
              <CardContent>
                <Typography variant="h6" sx={{ mb: 2, fontWeight: 600, color: "#4caf50" }}>
                  ✓ Do's
                </Typography>
                <List>
                  <ListItem>
                    <ListItemText primary="Verify AI-collected data before final approval" />
                  </ListItem>
                  <ListItem>
                    <ListItemText primary="Keep LinkedIn URLs updated for better accuracy" />
                  </ListItem>
                  <ListItem>
                    <ListItemText primary="Use batch collection for multiple alumni" />
                  </ListItem>
                  <ListItem>
                    <ListItemText primary="Regularly export data as backups" />
                  </ListItem>
                  <ListItem>
                    <ListItemText primary="Review low confidence scores and update manually" />
                  </ListItem>
                </List>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6}>
            <Card sx={{ height: "100%", borderRadius: 2, border: "2px solid #f44336" }}>
              <CardContent>
                <Typography variant="h6" sx={{ mb: 2, fontWeight: 600, color: "#f44336" }}>
                  ✗ Don'ts
                </Typography>
                <List>
                  <ListItem>
                    <ListItemText primary="Don't trust 100% AI data without verification" />
                  </ListItem>
                  <ListItem>
                    <ListItemText primary="Don't upload CSV files with incorrect formatting" />
                  </ListItem>
                  <ListItem>
                    <ListItemText primary="Don't delete profiles without proper review" />
                  </ListItem>
                  <ListItem>
                    <ListItemText primary="Don't run multiple collection tasks simultaneously" />
                  </ListItem>
                  <ListItem>
                    <ListItemText primary="Don't ignore data quality warnings" />
                  </ListItem>
                </List>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Paper>

      {/* Contact Support */}
      <Alert severity="success" sx={{ borderRadius: 2 }}>
        <Typography variant="body1" sx={{ fontWeight: 600, mb: 1 }}>
          Need Additional Help?
        </Typography>
        <Typography variant="body2">
          If you encounter issues not covered in this documentation, please contact the IT support team
          or system administrator for assistance. For technical issues, provide details about what you were
          trying to do and any error messages you received.
        </Typography>
      </Alert>
    </Box>
  );
};

export default Documentation;
