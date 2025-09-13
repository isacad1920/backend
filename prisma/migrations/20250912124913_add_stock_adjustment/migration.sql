-- CreateEnum
CREATE TYPE "AdjustmentType" AS ENUM ('INCREASE', 'DECREASE', 'RECOUNT', 'DAMAGED', 'EXPIRED', 'THEFT', 'RETURNED');

-- CreateEnum
CREATE TYPE "AdjustmentReason" AS ENUM ('physical_count', 'damage', 'expiry', 'theft', 'supplier_return', 'customer_return', 'correction', 'other');

-- CreateTable
CREATE TABLE "stock_adjustments" (
    "id" SERIAL NOT NULL,
    "product_id" INTEGER NOT NULL,
    "adjustment_type" "AdjustmentType" NOT NULL,
    "reason" "AdjustmentReason" NOT NULL,
    "quantity_before" INTEGER NOT NULL,
    "quantity_after" INTEGER NOT NULL,
    "adjustment_qty" INTEGER NOT NULL,
    "notes" TEXT,
    "reference_number" TEXT,
    "created_by" INTEGER,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "stock_adjustments_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE INDEX "stock_adjustments_product_id_idx" ON "stock_adjustments"("product_id");

-- CreateIndex
CREATE INDEX "stock_adjustments_created_by_idx" ON "stock_adjustments"("created_by");

-- AddForeignKey
ALTER TABLE "stock_adjustments" ADD CONSTRAINT "stock_adjustments_product_id_fkey" FOREIGN KEY ("product_id") REFERENCES "products"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "stock_adjustments" ADD CONSTRAINT "stock_adjustments_created_by_fkey" FOREIGN KEY ("created_by") REFERENCES "users"("id") ON DELETE SET NULL ON UPDATE CASCADE;
