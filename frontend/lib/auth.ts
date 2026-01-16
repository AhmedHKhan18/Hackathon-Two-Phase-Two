import { betterAuth } from "better-auth";
import { jwt } from "better-auth/plugins";
import { Pool } from "pg";

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: {
    rejectUnauthorized: false,
  },
});

export const auth = betterAuth({
  database: pool,
  basePath: "/api/auth",
  trustedOrigins: ["http://localhost:3000", "http://localhost:3001"],
  emailAndPassword: {
    enabled: true,
    minPasswordLength: 8,
  },
  session: {
    expiresIn: 60 * 60 * 24 * 7, // 7 days
    updateAge: 60 * 60 * 24, // 1 day
    cookieCache: {
      enabled: true,
      maxAge: 60 * 5, // 5 minutes
    },
  },
  advanced: {
    useSecureCookies: false, // Set to true in production with HTTPS
  },
  plugins: [
    jwt({
      jwt: {
        expirationTime: "7d",
        definePayload: async ({ user, session }) => {
          return {
            sub: user.id,
            email: user.email,
            name: user.name,
            sessionId: session.id,
          };
        },
      },
    }),
  ],
  secret: process.env.BETTER_AUTH_SECRET,
});

export type Session = typeof auth.$Infer.Session;
