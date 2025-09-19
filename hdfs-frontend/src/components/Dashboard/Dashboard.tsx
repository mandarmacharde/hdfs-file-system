import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Typography,
  CircularProgress,
  Alert,
  Card,
  CardContent,
} from '@mui/material';
import {
  Storage as StorageIcon,
  InsertDriveFile as FileIcon,
  CloudUpload as UploadIcon,
  CloudDownload as DownloadIcon,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { statsApi } from '../../services/api';

const Dashboard: React.FC = () => {
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [stats, setStats] = useState({
    totalFiles: 0,
    activeDataNodes: 0,
    totalUploads: 0,
    totalDownloads: 0,
  });

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Fetch stats from the backend
      const statsResponse = await statsApi.getStats();
      
      if (statsResponse.status === 'success') {
        setStats({
          totalFiles: statsResponse.stats.total_files,
          activeDataNodes: statsResponse.stats.active_datanodes,
          totalUploads: statsResponse.stats.total_uploads,
          totalDownloads: statsResponse.stats.total_downloads,
        });
      } else {
        throw new Error('Stats API returned unsuccessful status');
      }
    } catch (err) {
      setError('Error loading dashboard data');
      console.error('Error in dashboard:', err);
    } finally {
      setLoading(false);
    }
  };

  const statCards = [
    {
      title: 'Total Files',
      value: stats.totalFiles,
      icon: <FileIcon sx={{ fontSize: 40 }} color="primary" />,
      color: '#3f51b5',
    },
    {
      title: 'Active DataNodes',
      value: stats.activeDataNodes,
      icon: <StorageIcon sx={{ fontSize: 40 }} color="secondary" />,
      color: '#f50057',
    },
    {
      title: 'Total Uploads',
      value: stats.totalUploads,
      icon: <UploadIcon sx={{ fontSize: 40 }} style={{ color: '#4caf50' }} />,
      color: '#4caf50',
    },
    {
      title: 'Total Downloads',
      value: stats.totalDownloads,
      icon: <DownloadIcon sx={{ fontSize: 40 }} style={{ color: '#ff9800' }} />,
      color: '#ff9800',
    },
  ];

  return (
    <Box>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <Typography variant="h4" gutterBottom>
          Dashboard
        </Typography>
      </motion.div>

      {error && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.3 }}
        >
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        </motion.div>
      )}

      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
          <CircularProgress />
        </Box>
      ) : (
        <Grid container spacing={3}>
          {statCards.map((card, index) => (
            <Grid item xs={12} sm={6} md={3} key={card.title}>
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
              >
                <Card 
                  elevation={3}
                  component={motion.div}
                  whileHover={{ scale: 1.05 }}
                  transition={{ duration: 0.2 }}
                  sx={{
                    height: '100%',
                    display: 'flex',
                    flexDirection: 'column',
                    position: 'relative',
                    overflow: 'hidden',
                    '&::after': {
                      content: '""',
                      position: 'absolute',
                      top: 0,
                      left: 0,
                      width: '100%',
                      height: '5px',
                      backgroundColor: card.color,
                    },
                  }}
                >
                  <CardContent sx={{ flexGrow: 1, textAlign: 'center' }}>
                    <Box sx={{ mb: 2 }}>
                      {card.icon}
                    </Box>
                    <Typography variant="h3" component="div">
                      {card.value}
                    </Typography>
                    <Typography variant="subtitle1" color="text.secondary">
                      {card.title}
                    </Typography>
                  </CardContent>
                </Card>
              </motion.div>
            </Grid>
          ))}
        </Grid>
      )}
    </Box>
  );
};

export default Dashboard;