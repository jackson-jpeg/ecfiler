"use client";

import { useEffect } from "react";
import { useUser } from "@clerk/nextjs";
import { setUserId } from "@/lib/api";

/**
 * Initializes the API client with the authenticated user's ID.
 * Renders nothing — just a side-effect component.
 */
export function UserInit() {
  const { user } = useUser();

  useEffect(() => {
    if (user?.id) {
      setUserId(user.id);
    }
  }, [user?.id]);

  return null;
}
