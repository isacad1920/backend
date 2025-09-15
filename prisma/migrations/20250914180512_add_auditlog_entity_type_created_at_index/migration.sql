-- CreateIndex
CREATE INDEX "auditlog_entityType_createdAt_idx" ON "public"."AuditLog"("entityType", "created_at");
