"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { signOut } from "@/lib/auth-client";

interface SignOutButtonProps {
  className?: string;
}

export function SignOutButton({ className }: SignOutButtonProps = {}) {
  const router = useRouter();
  const [loading, setLoading] = useState(false);

  const handleSignOut = async () => {
    setLoading(true);
    try {
      await signOut();
      router.push("/signin");
    } catch (error) {
      console.error("Sign out failed:", error);
      setLoading(false);
    }
  };

  const baseClasses = "px-3 py-1.5 text-sm font-medium focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed min-touch-target";
  const defaultClasses = "text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50";

  return (
    <button
      onClick={handleSignOut}
      disabled={loading}
      className={className || `${baseClasses} ${defaultClasses}`}
    >
      <svg className="w-4 h-4 inline-block mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
      </svg>
      {loading ? "Signing out..." : "Sign out"}
    </button>
  );
}
