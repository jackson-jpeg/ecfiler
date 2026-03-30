"use client";

import { useEffect } from "react";
import { useAuth, useUser } from "@clerk/nextjs";
import { setSessionToken, setUserId } from "@/lib/api";

/**
 * Initializes the API client with the authenticated user's ID and session token.
 * Renders nothing — just a side-effect component.
 */
export function UserInit() {
  const { user } = useUser();
  const { getToken } = useAuth();

  useEffect(() => {
    if (user?.id) {
      setUserId(user.id);
      // Fetch and set the Clerk session token for backend JWT verification
      getToken().then((token) => {
        if (token) setSessionToken(token);
      });
    }
  }, [user?.id, getToken]);

  // Refresh token periodically (Clerk tokens expire after ~60s)
  useEffect(() => {
    if (!user?.id) return;
    const interval = setInterval(async () => {
      const token = await getToken();
      if (token) setSessionToken(token);
    }, 50000); // Refresh every 50s
    return () => clearInterval(interval);
  }, [user?.id, getToken]);

  return null;
}
