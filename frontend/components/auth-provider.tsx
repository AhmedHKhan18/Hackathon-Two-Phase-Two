"use client";

import { ReactNode } from "react";

interface AuthProviderProps {
  children: ReactNode;
}

/**
 * AuthProvider wraps the application to provide authentication context.
 * Better Auth uses React context internally via useSession hook.
 */
export function AuthProvider({ children }: AuthProviderProps) {
  return <>{children}</>;
}
