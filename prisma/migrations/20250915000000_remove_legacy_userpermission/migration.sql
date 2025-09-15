-- Migration: remove legacy UserPermission table (replaced by normalized RBAC tables)
-- Date: 2025-09-15
-- Safety: Archival optional (commented out). Uncomment if you want to preserve historical rows.

BEGIN;

-- Optional archival (uncomment if needed)
-- CREATE TABLE IF NOT EXISTS user_permission_legacy_archive AS
--   SELECT * FROM "UserPermission" WHERE 1=0;  -- structure only
-- INSERT INTO user_permission_legacy_archive SELECT * FROM "UserPermission";

-- Drop legacy table if exists
DROP TABLE IF EXISTS "UserPermission" CASCADE;

COMMIT;
