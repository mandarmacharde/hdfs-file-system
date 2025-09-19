import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  Card,
  CardContent,
  CircularProgress,
  Alert,
  Chip,
} from '@mui/material';
import { Storage as StorageIcon } from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';
import { dataNodeApi } from '../../services/api';

interface DataNode {
  datanode_id: string;
  host: string;
  port: number;
  status: string;
  last_heartbeat: string;
}

const DataNodeList: React.FC = () => {
  const [dataNodes, setDataNodes] = useState<DataNode[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchDataNodes();
    
    // Poll for updates every 10 seconds
    const interval = setInterval(fetchDataNodes, 10000);
    
    return () => clearInterval(interval);
  }, []);

  const fetchDataNodes = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await dataNodeApi.listDataNodes();
      if (response.status === 'success') {
        setDataNodes(response.datanodes);
      } else {
        throw new Error('API returned unsuccessful status');
      }
    } catch (err) {
      setError('Error loading DataNodes');
      console.error('Error in DataNodeList:', err);
    } finally {
      setLoading(false);
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
          DataNode Status
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
      ) : dataNodes.length === 0 ? (
        <Paper elevation={3} sx={{ p: 3, textAlign: 'center' }}>
          <Typography variant="h6">No DataNodes found</Typography>
        </Paper>
      ) : (
        <Grid container spacing={3}>
          <AnimatePresence>
            {dataNodes.map((node, index) => (
              <Grid item xs={12} sm={6} md={4} key={node.datanode_id}>
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, scale: 0.95 }}
                  transition={{ duration: 0.3, delay: index * 0.1 }}
                >
                  <Card 
                    elevation={3}
                    component={motion.div}
                    whileHover={{ scale: 1.03 }}
                    transition={{ duration: 0.2 }}
                  >
                    <CardContent>
                      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                        <StorageIcon color="primary" sx={{ fontSize: 40, mr: 2 }} />
                        <Typography variant="h6" component="div">
                          DataNode {node.datanode_id.substring(0, 8)}...
                        </Typography>
                      </Box>
                      
                      <Box sx={{ mb: 1 }}>
                        <Typography variant="body2" color="text.secondary" component="span">
                          Status: 
                        </Typography>
                        <Chip 
                          label={node.status} 
                          color={node.status === 'active' ? 'success' : 'error'}
                          size="small"
                          sx={{ ml: 1 }}
                        />
                      </Box>
                      
                      <Typography variant="body2" color="text.secondary">
                        Host: {node.host}
                      </Typography>
                      
                      <Typography variant="body2" color="text.secondary">
                        Port: {node.port}
                      </Typography>
                      
                      <Typography variant="body2" color="text.secondary">
                        Last Heartbeat: {new Date(node.last_heartbeat).toLocaleString()}
                      </Typography>
                    </CardContent>
                  </Card>
                </motion.div>
              </Grid>
            ))}
          </AnimatePresence>
        </Grid>
      )}
    </Box>
  );
};

export default DataNodeList;