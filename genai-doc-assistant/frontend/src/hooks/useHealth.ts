import { useEffect, useState } from 'react';
import { api } from '../api/client';

export function useHealth() {
  const [healthy, setHealthy] = useState<boolean | null>(null);
  const [geminiConnected, setGeminiConnected] = useState(false);

  useEffect(() => {
    let cancelled = false;
    let timer: ReturnType<typeof setTimeout>;

    const check = async () => {
      try {
        const res = await api.health();
        if (!cancelled) {
          setHealthy(true);
          setGeminiConnected(res.gemini_connected);
        }
      } catch {
        if (!cancelled) {
          setHealthy(false);
          timer = setTimeout(check, 3000);
        }
      }
    };

    check();

    return () => {
      cancelled = true;
      clearTimeout(timer);
    };
  }, []);

  return { healthy, geminiConnected };
}
