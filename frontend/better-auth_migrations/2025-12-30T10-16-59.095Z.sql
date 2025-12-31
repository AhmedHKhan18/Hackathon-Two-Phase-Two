alter table "account" add column "accessTokenExpiresAt" timestamptz;

alter table "account" add column "refreshTokenExpiresAt" timestamptz;

alter table "account" add column "scope" text;

create table "jwks" ("id" text not null primary key, "publicKey" text not null, "privateKey" text not null, "createdAt" timestamptz not null, "expiresAt" timestamptz);