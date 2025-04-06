import { Button } from "@/components/ui/button";
import { useTheme } from "@/components/theme-provider";
import { useToast } from "@/components/toast-provider";
import { useNavigate } from 'react-router-dom';
import { api } from '@/services/api'
import { SystemResponse } from '@/types/api'
import { useAuth } from "react-oidc-context";

export function Settings() {
  const { setTheme, theme } = useTheme();
  const { toast } = useToast();
  const navigate = useNavigate();
  const auth = useAuth();

  const handleLoadInitialData = async () => {
    try {
      const token = auth.user?.access_token || '';
      const response = await api.post<SystemResponse>(token, "/load_initial_data");
      if (!response.data?.success) {
        toast({
          variant: "error",
          description: response.data?.message,
        });
        return;
      }
      toast({
        variant: "success",
        description: response.data?.message,
      });
      navigate("/");
    } catch (error) {
      toast({
        variant: "error",
        description: "Failed to load initial data",
      });
      console.error("Failed to load initial data", error);
    }
  };

  const handleResetStudyProgress = async () => {
    try {
      const confirm = window.confirm("Are you sure you want to reset your study progress?")
      if (!confirm) return
      const token = auth.user?.access_token || '';
      const response = await api.post<SystemResponse>(token, "/reset_study_progress");
      if (!response.data?.success) {
        toast({
          variant: "error",
          description: response.data?.message,
        });
        return;
      }
      toast({
        variant: "success",
        description: response.data?.message,
      });
      navigate("/");
    } catch (error) {
      toast({
        variant: "error",
        description: "Failed to reset study progress",
      });
      console.error("Failed to reset study progress", error);
    }
  };

  const handleResetData = async () => {
    try {
      const confirm = window.confirm("Are you sure you want to reset your data?")
      if (!confirm) return
      const token = auth.user?.access_token || '';
      const response = await api.post<SystemResponse>(token, "/reset_data");
      if (!response.data?.success) {
        toast({
          variant: "error",
          description: response.data?.message,
        });
        return;
      }
      toast({
        variant: "success",
        description: response.data?.message,
      });
      navigate("/");
    } catch (error) {
      toast({
        variant: "error",
        description: "Failed to reset data",
      });
      console.error("Failed to reset data", error);
    }
  };

  return (
    <div className="container py-8 space-y-8">
      <h1 className="text-3xl font-bold">Settings</h1>

      <div className="space-y-6">
        <div className="space-y-2">
          <h2 className="text-xl font-semibold">Theme</h2>
          <div className="flex gap-2">
            <Button
              variant={theme === "light" ? "default" : "outline"}
              onClick={() => setTheme("light")}
            >
              Light
            </Button>
            <Button
              variant={theme === "dark" ? "default" : "outline"}
              onClick={() => setTheme("dark")}
            >
              Dark
            </Button>
            <Button
              variant={theme === "system" ? "default" : "outline"}
              onClick={() => setTheme("system")}
            >
              System
            </Button>
          </div>
        </div>

        <div className="space-y-2">
          <h2 className="text-xl font-semibold">Data</h2>
          <div className="flex gap-2">
            <Button
              variant={theme === "dark" ? "default" : "outline"}
              onClick={handleLoadInitialData}
            >
              Load Initial Data
            </Button>
            <Button
              variant="destructive"
              onClick={handleResetStudyProgress}
            >
              Reset Study Progress
            </Button>
            <Button
              variant="destructive"
              onClick={handleResetData}
            >
              Reset Data
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
} 