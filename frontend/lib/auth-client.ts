import { createAuthClient } from "better-auth/react";
import { jwtClient } from "better-auth/client/plugins";

export const authClient = createAuthClient({
  baseURL: typeof window !== "undefined" ? window.location.origin : "http://localhost:3000",
  basePath: "/api/auth",
  plugins: [jwtClient()],
  fetchOptions: {
    credentials: "include",
  },
});

export const { useSession, signIn, signUp, signOut, getSession } = authClient;
