import React, { useState, useRef } from 'react';
import {
  Box,
  Button,
  Typography,
  Paper,
  LinearProgress,
  Alert,
  IconButton,
} from '@mui/material';
import { CloudUpload as UploadIcon, Close as CloseIcon } from '@mui/icons-material';
import { motion } from 'framer-motion';
import { fileApi } from '../../services/api';

const FileUpload: React.FC = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState<boolean>(false);
  const [progress, setProgress] = useState<number>(0);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files.length > 0) {
      setSelectedFile(event.target.files[0]);
      setError(null);
      setSuccess(null);
    }
  };

  const handleDrop = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    event.stopPropagation();
    
    if (event.dataTransfer.files && event.dataTransfer.files.length > 0) {
      setSelectedFile(event.dataTransfer.files[0]);
      setError(null);
      setSuccess(null);
    }
  };

  const handleDragOver = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    event.stopPropagation();
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setError('Please select a file to upload');
      return;
    }

    try {
      setUploading(true);
      setProgress(0);
      setError(null);
      setSuccess(null);

      // Simulate progress
      const progressInterval = setInterval(() => {
        setProgress((prevProgress) => {
          const newProgress = prevProgress + 10;
          return newProgress >= 100 ? 100 : newProgress;
        });
      }, 500);

      // Upload the file to the backend
      const response = await fileApi.uploadFile(selectedFile);
      
      clearInterval(progressInterval);
      setProgress(100);
      
      if (response.status === 'success') {
        setSuccess(`File '${selectedFile.name}' uploaded successfully`);
        setSelectedFile(null);
        if (fileInputRef.current) {
          fileInputRef.current.value = '';
        }
      } else {
        throw new Error(response.message || 'Unknown error');
      }
    } catch (err: any) {
      setError(`Error uploading file: ${err.message || 'Unknown error'}`);
      console.error('Error uploading file:', err);
    } finally {
      setUploading(false);
    }
  };

  const clearSelectedFile = () => {
    setSelectedFile(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <Box>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <Typography variant="h4" gutterBottom>
          Upload File
        </Typography>
      </motion.div>

      {error && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.3 }}
        >
          <Alert 
            severity="error" 
            sx={{ mb: 2 }}
            action={
              <IconButton
                aria-label="close"
                color="inherit"
                size="small"
                onClick={() => setError(null)}
              >
                <CloseIcon fontSize="inherit" />
              </IconButton>
            }
          >
            {error}
          </Alert>
        </motion.div>
      )}

      {success && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.3 }}
        >
          <Alert 
            severity="success" 
            sx={{ mb: 2 }}
            action={
              <IconButton
                aria-label="close"
                color="inherit"
                size="small"
                onClick={() => setSuccess(null)}
              >
                <CloseIcon fontSize="inherit" />
              </IconButton>
            }
          >
            {success}
          </Alert>
        </motion.div>
      )}

      <Paper
        elevation={3}
        sx={{
          p: 3,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          border: '2px dashed #3f51b5',
          borderRadius: 2,
          backgroundColor: 'background.paper',
          minHeight: 200,
          mb: 3,
        }}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        component={motion.div}
        whileHover={{ scale: 1.01 }}
        transition={{ duration: 0.2 }}
      >
        <input
          type="file"
          style={{ display: 'none' }}
          onChange={handleFileChange}
          ref={fileInputRef}
        />
        
        {!selectedFile ? (
          <>
            <UploadIcon sx={{ fontSize: 60, color: 'primary.main', mb: 2 }} />
            <Typography variant="h6" gutterBottom>
              Drag & Drop File Here
            </Typography>
            <Typography variant="body2" color="textSecondary" gutterBottom>
              or
            </Typography>
            <Button
              variant="contained"
              color="primary"
              onClick={() => fileInputRef.current?.click()}
              startIcon={<UploadIcon />}
            >
              Browse Files
            </Button>
          </>
        ) : (
          <Box sx={{ width: '100%', textAlign: 'center' }}>
            <Typography variant="h6" gutterBottom>
              Selected File:
            </Typography>
            <Typography variant="body1" gutterBottom>
              {selectedFile.name} ({(selectedFile.size / 1024 / 1024).toFixed(2)} MB)
            </Typography>
            
            {uploading && (
              <Box sx={{ width: '100%', mt: 2 }}>
                <LinearProgress variant="determinate" value={progress} />
                <Typography variant="body2" color="textSecondary" align="center" sx={{ mt: 1 }}>
                  {progress}%
                </Typography>
              </Box>
            )}
            
            <Box sx={{ mt: 2, display: 'flex', justifyContent: 'center', gap: 2 }}>
              {!uploading && (
                <>
                  <Button
                    variant="outlined"
                    color="secondary"
                    onClick={clearSelectedFile}
                  >
                    Cancel
                  </Button>
                  <Button
                    variant="contained"
                    color="primary"
                    onClick={handleUpload}
                    startIcon={<UploadIcon />}
                  >
                    Upload
                  </Button>
                </>
              )}
            </Box>
          </Box>
        )}
      </Paper>
    </Box>
  );
};

export default FileUpload;