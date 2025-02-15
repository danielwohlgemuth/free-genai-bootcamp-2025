import { Button } from "@/components/ui/button";
import { useTheme } from "@/components/theme-provider";
import { useToast } from "@/components/ui/use-toast";
import { api } from "@/lib/api";

export default function Settings() {
  const { setTheme, theme } = useTheme();
  const { toast } = useToast();

  const handleResetHistory = async () => {
    try {
      await api.post("/reset_history");
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

  const handleFullReset = async () => {
    try {
      await api.post("/full_reset");
      setTheme("system");
      toast({
        title: "Success",
        description: "System has been fully reset",
      });
      window.location.href = "/";
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to perform full reset",
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
            <Button
              variant="destructive"
              onClick={handleFullReset}
            >
              Full Reset
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
} 