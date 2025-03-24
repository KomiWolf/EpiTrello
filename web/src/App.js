// Officials React import
import React from 'react';
import { Navigate, BrowserRouter as Router, Routes, Route } from 'react-router-dom'

// Our import
import ProtectedRoute from './utils/ProtectedRoute';
import { AuthProvider } from './components/Pages/Auth/AuthContext';
import { HeaderProvider } from './components/GenericComponents/Header/HeaderContext';
import AuthEntryPoint from './components/Pages/Auth/AuthEntryPoint';
import Menu from './components/Pages/Menu/Menu';
import Profile from './components/Pages/Profile/Profile';
import WorkspaceSettings from './components/Pages/Workspace/WorkspaceSettings';
import Settings from './components/Pages/Settings/Settings';
import Invitations from './components/Pages/Invitations/Invitations';
import Board from './components/Pages/Board/Board';
import NotFound from './components/GenericComponents/NotFound';
import OtherProfile from './components/Pages/Profile/OtherProfile';
import OauthCallback from './components/Pages/Auth/OauthCallback';

function App() {
  return (
    <Router>
      <AuthProvider>
        <Routes>
          <Route path="/" element={<Navigate to="/auth" />} />
          <Route path="/auth" element={<AuthEntryPoint />} />
          <Route path="/callback" element={<OauthCallback />} />
          <Route
            path="/menu"
            element={
              <ProtectedRoute
                element={
                  <HeaderProvider>
                    <Menu />
                  </HeaderProvider>
                }
              />
            }
          />
          <Route
            path="/profile"
            element={
              <ProtectedRoute
                element={
                  <HeaderProvider>
                    <Profile />
                  </HeaderProvider>
                }
              />
            }
          />
          <Route
            path="/workspace-settings"
            element={
              <ProtectedRoute
                element={
                  <HeaderProvider>
                    <WorkspaceSettings />
                  </HeaderProvider>
                }
              />
            }
          />
          <Route
            path="/settings"
            element={
              <ProtectedRoute
                element={
                  <HeaderProvider>
                    <Settings />
                  </HeaderProvider>
                }
              />
            }
          />
          <Route
            path="/invitations"
            element={
              <ProtectedRoute
                element={
                  <HeaderProvider>
                    <Invitations />
                  </HeaderProvider>
                }
              />
            }
          />
          <Route
            path="/board/:boardId"
            element={
              <ProtectedRoute
                element={
                  <HeaderProvider>
                    <Board />
                  </HeaderProvider>
                }
              />
            }
          />
          <Route
            path="/profile/:userId"
            element={
              <ProtectedRoute
                element={
                  <HeaderProvider>
                    <OtherProfile />
                  </HeaderProvider>
                }
              />
            }
          />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </AuthProvider>
    </Router>
  );
}

export default App;
