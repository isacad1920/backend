-- CreateEnum
CREATE TYPE "public"."CategoryStatus" AS ENUM ('ACTIVE', 'INACTIVE');

-- AlterTable
ALTER TABLE "public"."categories" ADD COLUMN     "status" "public"."CategoryStatus" NOT NULL DEFAULT 'ACTIVE';
