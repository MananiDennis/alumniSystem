import React, { useState } from 'react';
import {
    Box, Card, CardContent, TextField, Button, Typography,
    Alert, Container, Paper
} from '@mui/material';
import axios from 'axios';

export default function Login({ onLogin }) {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');

        try {
            const response = await axios.post('http://localhost:8000/auth/login', {
                email,
                password
            });

            localStorage.setItem('token', response.data.access_token);
            onLogin(response.data.user, response.data.access_token);
        } catch (err) {
            setError('Invalid credentials');
        } finally {
            setLoading(false);
        }
    };

    return (
        <Container maxWidth="sm" sx={{ mt: 8 }}>
            <Paper elevation={8} sx={{ borderRadius: 4, overflow: 'hidden' }}>
                <Box sx={{
                    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                    p: 4, color: 'white', textAlign: 'center'
                }}>
                    <Box sx={{ mb: 2, display: 'flex', justifyContent: 'center' }}>
                        <img 
                            src="/img/Edith_Cowan_University_Logo.svg" 
                            alt="Edith Cowan University Logo" 
                            style={{ height: '48px', width: 'auto' }}
                        />
                    </Box>
                    <Typography variant="h4" fontWeight="bold">
                        ECU Alumni System
                    </Typography>
                    <Typography variant="body1" sx={{ opacity: 0.9 }}>
                        Secure Access Portal
                    </Typography>
                </Box>

                <CardContent sx={{ p: 4 }}>
                    <form onSubmit={handleSubmit}>
                        <TextField
                            fullWidth
                            label="Email"
                            type="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            margin="normal"
                            required
                            sx={{
                                '& .MuiOutlinedInput-root': {
                                    borderRadius: 2
                                }
                            }}
                        />
                        <TextField
                            fullWidth
                            label="Password"
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            margin="normal"
                            required
                            sx={{
                                '& .MuiOutlinedInput-root': {
                                    borderRadius: 2
                                }
                            }}
                        />

                        {error && (
                            <Alert severity="error" sx={{ mt: 2, borderRadius: 2 }}>
                                {error}
                            </Alert>
                        )}

                        <Button
                            type="submit"
                            fullWidth
                            variant="contained"
                            disabled={loading}
                            sx={{
                                mt: 3,
                                py: 1.5,
                                borderRadius: 2,
                                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                                fontWeight: 600,
                                fontSize: '1.1rem',
                                '&:hover': {
                                    background: 'linear-gradient(135deg, #5a67d8 0%, #6b46c1 100%)'
                                }
                            }}
                        >
                            {loading ? 'Signing In...' : 'Sign In'}
                        </Button>
                    </form>


                    <Box sx={{ mt: 3, p: 2, bgcolor: '#f8fafc', borderRadius: 2 }}>
                        <Typography variant="body2" sx={{ color: '#64748b', mb: 1 }}>
                            Demo Credentials:
                        </Typography>
                        <Typography variant="body2" sx={{ fontFamily: 'monospace', fontSize: '0.8rem' }}>
                            admin@ecu.edu.au / admin123<br />
                            flavio@ecu.edu.au / flavio123
                        </Typography>
                    </Box>
                </CardContent>
            </Paper>
        </Container>
    );
}