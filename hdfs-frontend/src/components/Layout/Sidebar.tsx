import React from 'react';
import { List, ListItem, ListItemIcon, ListItemText, Divider } from '@mui/material';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  Dashboard as DashboardIcon,
  Folder as FolderIcon,
  Storage as StorageIcon,
  Upload as UploadIcon,
  Settings as SettingsIcon,
} from '@mui/icons-material';

const listItemVariants = {
  hidden: { opacity: 0, x: -20 },
  visible: (i: number) => ({
    opacity: 1,
    x: 0,
    transition: {
      delay: i * 0.1,
    },
  }),
};

const Sidebar: React.FC = () => {
  const menuItems = [
    { text: 'Dashboard', icon: <DashboardIcon />, path: '/' },
    { text: 'File Browser', icon: <FolderIcon />, path: '/files' },
    { text: 'DataNodes', icon: <StorageIcon />, path: '/datanodes' },
    { text: 'Upload', icon: <UploadIcon />, path: '/upload' },
    { text: 'Settings', icon: <SettingsIcon />, path: '/settings' },
  ];

  return (
    <>
      <List>
        {menuItems.map((item, index) => (
          <motion.div
            key={item.text}
            custom={index}
            initial="hidden"
            animate="visible"
            variants={listItemVariants}
          >
            <ListItem 
              button 
              component={Link} 
              to={item.path}
              sx={{
                '&:hover': {
                  backgroundColor: 'rgba(63, 81, 181, 0.08)',
                },
                borderRadius: 1,
                m: 0.5,
              }}
            >
              <ListItemIcon>{item.icon}</ListItemIcon>
              <ListItemText primary={item.text} />
            </ListItem>
          </motion.div>
        ))}
      </List>
      <Divider />
    </>
  );
};

export default Sidebar;