-- CreateEnum
CREATE TYPE "public"."PermissionType" AS ENUM ('ALLOW', 'DENY');

-- CreateTable
CREATE TABLE "public"."permissions_rbac" (
    "id" SERIAL NOT NULL,
    "resource" TEXT NOT NULL,
    "action" TEXT NOT NULL,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "permissions_rbac_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "public"."role_permissions_rbac" (
    "id" SERIAL NOT NULL,
    "role" "public"."Role" NOT NULL,
    "permissionId" INTEGER NOT NULL,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "role_permissions_rbac_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "public"."user_permissions_rbac" (
    "id" SERIAL NOT NULL,
    "userId" INTEGER NOT NULL,
    "permissionId" INTEGER NOT NULL,
    "type" "public"."PermissionType" NOT NULL,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "user_permissions_rbac_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "permissions_rbac_resource_action_key" ON "public"."permissions_rbac"("resource", "action");

-- CreateIndex
CREATE UNIQUE INDEX "role_permissions_rbac_role_permissionId_key" ON "public"."role_permissions_rbac"("role", "permissionId");

-- CreateIndex
CREATE UNIQUE INDEX "user_permissions_rbac_userId_permissionId_key" ON "public"."user_permissions_rbac"("userId", "permissionId");

-- AddForeignKey
ALTER TABLE "public"."role_permissions_rbac" ADD CONSTRAINT "role_permissions_rbac_permissionId_fkey" FOREIGN KEY ("permissionId") REFERENCES "public"."permissions_rbac"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "public"."user_permissions_rbac" ADD CONSTRAINT "user_permissions_rbac_userId_fkey" FOREIGN KEY ("userId") REFERENCES "public"."users"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "public"."user_permissions_rbac" ADD CONSTRAINT "user_permissions_rbac_permissionId_fkey" FOREIGN KEY ("permissionId") REFERENCES "public"."permissions_rbac"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
