-- AlterTable
ALTER TABLE "public"."sales" ADD COLUMN     "deleted_at" TIMESTAMP(3),
ADD COLUMN     "deleted_by_id" INTEGER;

-- AddForeignKey
ALTER TABLE "public"."sales" ADD CONSTRAINT "sales_deleted_by_id_fkey" FOREIGN KEY ("deleted_by_id") REFERENCES "public"."users"("id") ON DELETE SET NULL ON UPDATE CASCADE;
