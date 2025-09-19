import React, { useState } from 'react';
import {
  Box,
  Typography,
  Paper,
  TextField,
  Button,
  Switch,
  FormControlLabel,
  Divider,
  Alert,
} from '@mui/material';
import { motion } from 'framer-motion';

const SettingsPage: React.FC = () => {
  const [settings, setSettings] = useState({
    nameNodeHost: 'localhost',
    nameNodePort: '5050',
    blockSize: '67108864', // 64MB in bytes
    replicationFactor: '2',
    darkMode: true,
    autoRefresh: true,
    refreshInterval: '10',
  });

  const [saved, setSaved] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, type, checked } = e.target;
    setSettings({
      ...settings,
      [name]: type === 'checkbox' ? checked : value,
    });
    setSaved(false);
  };

  const handleSave = () => {
    // In a real app, we would save these settings to localStorage or a backend
    localStorage.setItem('hdfsSettings', JSON.stringify(settings));
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  return (
    <Box>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <Typography variant="h4" gutterBottom>
          Settings
        </Typography>
      </motion.div>

      {saved && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.3 }}
        >
          <Alert severity="success" sx={{ mb: 2 }}>
            Settings saved successfully
          </Alert>
        </motion.div>
      )}

      <Paper 
        elevation={3} 
        sx={{ p: 3 }}
        component={motion.div}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.2 }}
      >
        <Typography variant="h6" gutterBottom>
          Connection Settings
        </Typography>
        
        <Box sx={{ mb: 3 }}>
          <TextField
            label="NameNode Host"
            name="nameNodeHost"
            value={settings.nameNodeHost}
            onChange={handleChange}
            fullWidth
            margin="normal"
            variant="outlined"
          />
          
          <TextField
            label="NameNode Port"
            name="nameNodePort"
            value={settings.nameNodePort}
            onChange={handleChange}
            fullWidth
            margin="normal"
            variant="outlined"
            type="number"
          />
        </Box>
        
        <Divider sx={{ my: 3 }} />
        
        <Typography variant="h6" gutterBottom>
          HDFS Configuration
        </Typography>
        
        <Box sx={{ mb: 3 }}>
          <TextField
            label="Block Size (bytes)"
            name="blockSize"
            value={settings.blockSize}
            onChange={handleChange}
            fullWidth
            margin="normal"
            variant="outlined"
            type="number"
            helperText="Default: 64MB (67108864 bytes)"
          />
          
          <TextField
            label="Replication Factor"
            name="replicationFactor"
            value={settings.replicationFactor}
            onChange={handleChange}
            fullWidth
            margin="normal"
            variant="outlined"
            type="number"
            inputProps={{ min: 1, max: 10 }}
            helperText="Number of replicas for each block"
          />
        </Box>
        
        <Divider sx={{ my: 3 }} />
        
        <Typography variant="h6" gutterBottom>
          UI Settings
        </Typography>
        
        <Box sx={{ mb: 3 }}>
          <FormControlLabel
            control={
              <Switch
                checked={settings.darkMode}
                onChange={handleChange}
                name="darkMode"
                color="primary"
              />
            }
            label="Dark Mode"
          />
          
          <Box sx={{ mt: 2 }}>
            <FormControlLabel
              control={
                <Switch
                  checked={settings.autoRefresh}
                  onChange={handleChange}
                  name="autoRefresh"
                  color="primary"
                />
              }
              label="Auto Refresh"
            />
            
            {settings.autoRefresh && (
              <TextField
                label="Refresh Interval (seconds)"
                name="refreshInterval"
                value={settings.refreshInterval}
                onChange={handleChange}
                margin="normal"
                variant="outlined"
                type="number"
                inputProps={{ min: 5, max: 60 }}
                sx={{ ml: 2, width: 200 }}
              />
            )}
          </Box>
        </Box>
        
        <Box sx={{ mt: 4, textAlign: 'right' }}>
          <Button
            variant="contained"
            color="primary"
            onClick={handleSave}
            size="large"
          >
            Save Settings
          </Button>
        </Box>
      </Paper>
    </Box>
  );
};

export default SettingsPage;