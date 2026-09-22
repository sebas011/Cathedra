import { Navigate, Route, Routes } from "react-router-dom";
import AppShell from "./components/AppShell";
import DashboardPage from "./pages/DashboardPage";
import FsdpFormPage from "./pages/FsdpFormPage";
import FsdpListPage from "./pages/FsdpListPage";
import FsdpDetailPage from "./pages/FsdpDetailPage";
import LoginPage from "./pages/LoginPage";
import PlaceholderPage from "./pages/PlaceholderPage";
import WorkloadFormPage from "./pages/WorkloadFormPage";
import WorkloadPage from "./pages/WorkloadPage";
import FacultyProfilesPage from "./pages/FacultyProfilesPage";
import BackupExportPage from "./pages/BackupExportPage";
import GrantReviewPage from "./pages/GrantReviewPage";
import ExpensesPage from "./pages/ExpensesPage";
import { getSessionToken } from "./api";

function ProtectedShell() { return getSessionToken() ? <AppShell /> : <Navigate to="/login" replace />; }

export default function App() {
  return <Routes>
    <Route path="/login" element={<LoginPage />} />
    <Route element={<ProtectedShell />}>
      <Route path="/" element={<DashboardPage />} />
      <Route path="/fsdp" element={<FsdpListPage />} />
      <Route path="/fsdp/new" element={<FsdpFormPage />} />
      <Route path="/fsdp/grant-review" element={<GrantReviewPage />} />
      <Route path="/fsdp/:id" element={<FsdpDetailPage />} />
      <Route path="/fsdp/:id/edit" element={<FsdpFormPage />} />
      <Route path="/workload" element={<WorkloadPage />} />
      <Route path="/faculty-profiles" element={<FacultyProfilesPage />} />
      <Route path="/backup-export" element={<BackupExportPage />} />
      <Route path="/workload/new" element={<WorkloadFormPage />} />
      <Route path="/workload/:id/edit" element={<WorkloadFormPage />} />
      <Route path="/expenses" element={<ExpensesPage />} />
    </Route>
    <Route path="*" element={<Navigate to="/" replace />} />
  </Routes>;
}
