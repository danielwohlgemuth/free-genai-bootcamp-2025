import { Button } from "@/components/ui/button";
import { useTheme } from "@/components/theme-provider";
import { useToast } from "@/components/ui/use-toast";
import { api } from "@/lib/api";
import { useAuth } from "react-oidc-context";

export function Settings() {
  const { setTheme, theme } = useTheme();
  const { toast } = useToast();
  const auth = useAuth();

  const handleLoadInitialData = async () => {
    try {
      const token = auth.user?.access_token || '';
      await api.post(token, "/load_initial_data");
      toast({
        title: "Success",
        description: "Initial data has been loaded",
      });
      window.location.href = "/";
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to load initial data",
        variant: "destructive",
      });
      console.error("Failed to load initial data", error);
    }
  };

  const handleResetStudyProgress = async () => {
    try {
      const confirm = window.confirm("Are you sure you want to reset your study progress?")
      if (!confirm) return
      const token = auth.user?.access_token || '';
      await api.post(token, "/reset_study_progress");
      toast({
        title: "Success",
        description: "Study progress has been reset",
      });
      window.location.href = "/";
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to reset study progress",
        variant: "destructive",
      });
      console.error("Failed to reset study progress", error);
    }
  };

  const handleResetData = async () => {
    try {
      const confirm = window.confirm("Are you sure you want to reset your data?")
      if (!confirm) return
      const token = auth.user?.access_token || '';
      await api.post(token, "/reset_data");
      toast({
        title: "Success",
        description: "Data has been reset",
      });
      window.location.href = "/";
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to reset data",
        variant: "destructive",
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