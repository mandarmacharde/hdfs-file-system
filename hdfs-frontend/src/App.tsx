import { useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, CssBaseline } from '@mui/material';
import darkTheme from './theme/darkTheme';
import Layout from './components/Layout/Layout';

// Pages
import DashboardPage from './pages/DashboardPage';
import FilesPage from './pages/FilesPage';
import DataNodesPage from './pages/DataNodesPage';
import UploadPage from './pages/UploadPage';
import SettingsPage from './pages/SettingsPage';

function App() {
  return (
    <ThemeProvider theme={darkTheme}>
      <CssBaseline />
      <Router>
        <Layout>
          <Routes>
            <Route path="/" element={<DashboardPage />} />
            <Route path="/files" element={<FilesPage />} />
            <Route path="/datanodes" element={<DataNodesPage />} />
            <Route path="/upload" element={<UploadPage />} />
            <Route path="/settings" element={<SettingsPage />} />
          </Routes>
        </Layout>
      </Router>
    </ThemeProvider>
  );
}

export default App;
