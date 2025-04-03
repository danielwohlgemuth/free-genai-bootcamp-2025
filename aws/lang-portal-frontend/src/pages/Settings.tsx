import { Button } from "@/components/ui/button";
import { useTheme } from "@/components/theme-provider";
import { useToast } from "@/components/ui/use-toast";
import { api } from "@/lib/api";
import { useAuth } from "react-oidc-context";

export function Settings() {
  const { setTheme, theme } = useTheme();
  const { toast } = useToast();
  const auth = useAuth();

  const handleResetHistory = async () => {
    try {
      const token = auth.user?.access_token || '';
      await api.post(token, "/reset_history");
      toast({
        title: "Success",
        description: "Study history has been reset",
      });
      window.location.href = "/";
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to reset history",
        variant: "destructive",
      });
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
          <h2 className="text-xl font-semibold">Reset Options</h2>
          <div className="flex gap-2">
            <Button
              variant="destructive"
              onClick={handleResetHistory}
            >
              Reset History
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
} 