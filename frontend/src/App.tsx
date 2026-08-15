import { Navigate, Route, Routes } from "react-router-dom";
import { useAuth } from "@/context/AuthContext";
import { Landing } from "@/features/landing/Landing";
import { AuthPage } from "@/features/auth/AuthPage";
import { AppShell } from "@/components/layout/AppShell";
import { Home } from "@/features/home/Home";
import { ProfilePage } from "@/features/profile/ProfilePage";
import { AssessmentHistory } from "@/features/assessment/AssessmentHistory";
import { AssessmentRunner } from "@/features/assessment/AssessmentRunner";
import { StartAssessment } from "@/features/assessment/StartAssessment";
import { ResultPage } from "@/features/results/ResultPage";
import { ReportPage } from "@/features/report/ReportPage";

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth();
  if (loading) return null;
  if (!user) return <Navigate to="/signin" replace />;
  return <>{children}</>;
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Landing />} />
      <Route path="/signin" element={<AuthPage mode="signin" />} />
      <Route path="/signup" element={<AuthPage mode="signup" />} />

      <Route
        path="/app"
        element={
          <ProtectedRoute>
            <AppShell />
          </ProtectedRoute>
        }
      >
        <Route index element={<Home />} />
        <Route path="profile" element={<ProfilePage />} />
        <Route path="assessments" element={<AssessmentHistory />} />
        <Route path="assessments/new" element={<StartAssessment />} />
        <Route path="assessments/:id" element={<AssessmentRunner />} />
        <Route path="assessments/:id/result" element={<ResultPage />} />
        <Route path="assessments/:id/report" element={<ReportPage />} />
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
