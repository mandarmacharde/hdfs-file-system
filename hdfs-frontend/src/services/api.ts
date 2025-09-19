import axios from 'axios';

// API base URL from environment variable or default to localhost:5050
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5050/api/v1';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// --- FILE OPERATIONS ---
export const fileApi = {
  // List all files in the system
  listFiles: async () => {
    try {
      const response = await api.get('/files');
      return response.data;
    } catch (error) {
      console.error('Error listing files:', error);
      throw error;
    }
  },

  // Get information about a specific file
  getFileInfo: async (filename: string) => {
    try {
      const response = await api.get(`/files/${filename}`);
      return response.data;
    } catch (error) {
      console.error(`Error getting info for file ${filename}:`, error);
      throw error;
    }
  },

  // Delete a file
  deleteFile: async (filename: string) => {
    try {
      const response = await api.delete(`/files/${filename}`);
      return response.data;
    } catch (error) {
      console.error(`Error deleting file ${filename}:`, error);
      throw error;
    }
  },

  // Upload a file (Restored to the working version)
  uploadFile: async (file: File) => {
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await api.post('/files/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      
      return response.data;
    } catch (error) {
      console.error(`Error uploading file ${file.name}:`, error);
      throw error;
    }
  },

  // Download a file (Restored to the working version)
  downloadFile: async (filename: string) => {
    try {
      // Step 1: Get the file's "map" from the NameNode
      const fileInfoResponse = await api.get(`/files/${filename}`);
      if (fileInfoResponse.data.status !== 'success') {
        throw new Error('Could not get file information from NameNode.');
      }
      const blocks = fileInfoResponse.data.file.blocks;
      if (!blocks || blocks.length === 0) {
        throw new Error('File has no blocks to download.');
      }

      // Step 2: Fetch each block directly from its DataNode
      const blockFetchPromises = blocks.map(async (block: any) => {
        const location = block.locations[0];
        if (!location) throw new Error(`No location for block ${block.block_id}`);
        const datanodeUrl = `http://${location.host}:${location.port}/api/v1/blocks/${block.block_id}`;
        const blockResponse = await axios.get(datanodeUrl, { responseType: 'blob' });
        return blockResponse.data;
      });
      const blockBlobs = await Promise.all(blockFetchPromises);

      // Step 3: Assemble the blocks and trigger the download
      const fileBlob = new Blob(blockBlobs);
      const url = window.URL.createObjectURL(fileBlob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } finally {
      // This block runs after the download is triggered to log the event
      fileApi.logDownload(filename);
    }
  },

  // Log a download event (Moved back inside the fileApi object)
  logDownload: async (filename: string) => {
    try {
      await api.post(`/files/${filename}/log_download`);
    } catch (error) {
      console.error('Failed to log download event:', error);
    }
  },
};

// --- DATANODE OPERATIONS ---
export const dataNodeApi = {
  listDataNodes: async () => {
    try {
      const response = await api.get('/datanodes');
      return response.data;
    } catch (error) {
      console.error('Error listing DataNodes:', error);
      throw error;
    }
  },
};

// --- STATS OPERATIONS ---
export const statsApi = {
  getStats: async () => {
    try {
      const response = await api.get('/stats');
      return response.data;
    } catch (error) {
      console.error('Error getting stats:', error);
      throw error;
    }
  },
};

export default api;