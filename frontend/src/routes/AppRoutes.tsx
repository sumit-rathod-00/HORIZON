import { Navigate, Route, Routes } from "react-router-dom";

import { AppShell } from "../components/layout/AppShell";
import { ProtectedRoute } from "./ProtectedRoute";

import { Dashboard } from "../pages/Dashboard";
import { Assets } from "../pages/Assets";
import { Profile } from "../pages/Profile";
import { Projects } from "../pages/Projects";
import { Scans } from "../pages/Scans";
import { Settings } from "../pages/Settings";
import { Users } from "../pages/Users";
import { Vulnerabilities } from "../pages/Vulnerabilities";

import { Login } from "../pages/auth/Login";
import { Register } from "../pages/auth/Register";

export function AppRoutes() {
  return (
    <Routes>
      {/* Public routes */}
      <Route path="/" element={<Navigate to="/dashboard" replace />} />

      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />

      {/* Protected routes */}
      <Route element={<ProtectedRoute />}>
        <Route
          path="/dashboard"
          element={
            <AppShell>
              <Dashboard />
            </AppShell>
          }
        />

        <Route
          path="/projects"
          element={
            <AppShell>
              <Projects />
            </AppShell>
          }
        />

        <Route
          path="/scans"
          element={
            <AppShell>
              <Scans />
            </AppShell>
          }
        />

        <Route
          path="/vulnerabilities"
          element={
            <AppShell>
              <Vulnerabilities />
            </AppShell>
          }
        />

        <Route
          path="/assets"
          element={
            <AppShell>
              <Assets />
            </AppShell>
          }
        />

        <Route
          path="/users"
          element={
            <AppShell>
              <Users />
            </AppShell>
          }
        />

        <Route
          path="/profile"
          element={
            <AppShell>
              <Profile />
            </AppShell>
          }
        />

        <Route
          path="/settings"
          element={
            <AppShell>
              <Settings />
            </AppShell>
          }
        />
      </Route>

      {/* Unknown route */}
      <Route
        path="*"
        element={<Navigate to="/dashboard" replace />}
      />
    </Routes>
  );
}