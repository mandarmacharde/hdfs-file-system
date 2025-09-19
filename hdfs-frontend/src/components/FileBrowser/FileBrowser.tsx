import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  Tooltip,
  CircularProgress,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  List,
  ListItem,
  ListItemText,
} from '@mui/material';
import {
  Delete as DeleteIcon,
  GetApp as DownloadIcon,
  Info as InfoIcon,
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';
import { fileApi } from '../../services/api';

const MotionTableRow = motion(TableRow);

// Interface for a file's metadata
interface FileInfo {
  name: string;
  created: number;
  modified: number;
  blocks: any[];
}

const FileBrowser: React.FC = () => {
  const [files, setFiles] = useState<FileInfo[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null); // <-- 1. ADDED SUCCESS STATE

  // State for the Info Modal
  const [infoModalOpen, setInfoModalOpen] = useState<boolean>(false);
  const [selectedFileInfo, setSelectedFileInfo] = useState<FileInfo | null>(null);

  useEffect(() => {
    fetchFiles();
    const interval = setInterval(fetchFiles, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchFiles = async () => {
    try {
      if (files.length === 0) setLoading(true);
      setError(null);
      
      const response = await fileApi.listFiles();
      if (response.status === 'success') {
        setFiles(response.files);
      } else {
        throw new Error('API returned unsuccessful status');
      }
    } catch (err) {
      setError('Error loading files');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (filename: string) => {
    // 2. UPDATED handleDelete FUNCTION
    setSuccess(null);
    setError(null);
    try {
      const response = await fileApi.deleteFile(filename);
      if (response.status === 'success') {
        setFiles(currentFiles => currentFiles.filter(file => file.name !== filename));
        setSuccess(`File '${filename}' was deleted successfully.`); // Set success message
      } else {
        throw new Error(response.message || 'Delete operation failed');
      }
    } catch (err: any) {
      setError(`Error deleting file: ${err.message || filename}`);
    }
  };

  const handleDownload = async (filename: string) => {
    try {
      await fileApi.downloadFile(filename);
    } catch (err: any) {
      setError(`Error downloading file: ${err.message || filename}`);
    }
  };

  const handleInfo = async (filename: string) => {
    try {
      const response = await fileApi.getFileInfo(filename);
      if (response.status === 'success') {
        setSelectedFileInfo(response.file);
        setInfoModalOpen(true);
      } else {
        throw new Error(response.message || 'Could not get file info');
      }
    } catch (err: any) {
      setError(`Error getting info for file: ${err.message || filename}`);
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
          File Browser
        </Typography>
      </motion.div>

      {/* 3. ADDED SUCCESS ALERT */}
      {success && (
        <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccess(null)}>
          {success}
        </Alert>
      )}
      
      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      <Paper elevation={3} sx={{ overflow: 'hidden' }}>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Filename</TableCell>
                <TableCell>Created</TableCell>
                <TableCell>Modified</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {loading ? (
                <TableRow>
                  <TableCell colSpan={4} align="center" sx={{ py: 4 }}>
                    <CircularProgress />
                  </TableCell>
                </TableRow>
              ) : files.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={4} align="center">
                    No files found in the file system.
                  </TableCell>
                </TableRow>
              ) : (
                <AnimatePresence>
                  {files.map((file) => (
                    <MotionTableRow
                      key={file.name}
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      exit={{ opacity: 0 }}
                      transition={{ duration: 0.3 }}
                    >
                      <TableCell>{file.name}</TableCell>
                      <TableCell>
                        {new Date(file.created * 1000).toLocaleString()}
                      </TableCell>
                      <TableCell>
                        {new Date(file.modified * 1000).toLocaleString()}
                      </TableCell>
                      <TableCell align="right">
                        <Tooltip title="File Info">
                          <IconButton onClick={() => handleInfo(file.name)} size="small" color="primary">
                            <InfoIcon />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Download">
                          <IconButton onClick={() => handleDownload(file.name)} size="small">
                            <DownloadIcon />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Delete">
                          <IconButton onClick={() => handleDelete(file.name)} size="small" color="error">
                            <DeleteIcon />
                          </IconButton>
                        </Tooltip>
                      </TableCell>
                    </MotionTableRow>
                  ))}
                </AnimatePresence>
              )}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>

      {/* File Info Dialog Modal */}
      <Dialog open={infoModalOpen} onClose={() => setInfoModalOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>File Block Information: {selectedFileInfo?.name}</DialogTitle>
        <DialogContent>
          {selectedFileInfo && selectedFileInfo.blocks.length > 0 ? (
            <List>
              {selectedFileInfo.blocks.map((block: any) => (
                <ListItem key={block.block_id} divider>
                  <ListItemText
                    primary={`Block ID: ${block.block_id}`}
                    secondary={
                      <>
                        Stored on DataNode(s):
                        <List dense component="div" disablePadding>
                          {block.locations.map((loc: any) => (
                            <ListItem key={loc.datanode_id} sx={{ pl: 4 }}>
                              <ListItemText primary={`- ID: ${loc.datanode_id.substring(0, 8)}... (${loc.host}:${loc.port})`} />
                            </ListItem>
                          ))}
                        </List>
                      </>
                    }
                  />
                </ListItem>
              ))}
            </List>
          ) : (
            <Typography>No block information available.</Typography>
          )}
        </DialogContent>
      </Dialog>
    </Box>
  );
};

export default FileBrowser;