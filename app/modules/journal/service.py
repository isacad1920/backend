"""
Journal Entry service layer for business logic.
"""
import logging
from datetime import date, datetime
from decimal import Decimal
from typing import Any

from app.core.exceptions import DatabaseError, NotFoundError, ValidationError
from app.modules.journal.schema import (
    JournalEntryCreateSchema,
    JournalEntryLineSchema,
    JournalEntryListSchema,
    JournalEntrySchema,
    JournalEntryUpdateSchema,
    TrialBalanceLineSchema,
    TrialBalanceSchema,
)
from generated.prisma import Prisma

logger = logging.getLogger(__name__)

class JournalService:
    """Service for journal entry operations."""
    
    def __init__(self, db: Prisma):
        self.db = db

    async def create_journal_entry(
        self, 
        entry_data: JournalEntryCreateSchema,
        created_by_user_id: int
    ) -> JournalEntrySchema:
        """Create a new journal entry with validation."""
        try:
            # Create the journal entry
            journal_entry = await self.db.journalentry.create(
                data={
                    "referenceType": entry_data.reference_type,
                    "referenceId": entry_data.reference_id,
                    "date": entry_data.date or datetime.now()
                }
            )

            # Create journal entry lines
            lines_data = []
            for line in entry_data.lines:
                lines_data.append({
                    "entryId": journal_entry.id,
                    "accountId": line.account_id,
                    "debit": line.debit,
                    "credit": line.credit,
                    "description": line.description
                })

            await self.db.journalentryline.create_many(
                data=lines_data
            )

            # Fetch the complete entry with lines
            return await self.get_journal_entry(journal_entry.id)

        except Exception as e:
            logger.error(f"Error creating journal entry: {str(e)}")
            raise DatabaseError(f"Unable to create journal entry: {str(e)}")

    async def get_journal_entry(self, entry_id: int) -> JournalEntrySchema:
        """Get a journal entry by ID."""
        try:
            entry = await self.db.journalentry.find_unique(
                where={"id": entry_id},
                include={
                    "lines": {
                        "include": {
                            "account": True
                        }
                    }
                }
            )

            if not entry:
                raise NotFoundError(f"Journal entry with ID {entry_id} not found")

            # Convert to schema
            lines = []
            total_amount = Decimal('0')
            
            for line in entry.lines:
                line_schema = JournalEntryLineSchema(
                    id=line.id,
                    account_id=line.accountId,
                    account_name=line.account.name,
                    account_code=getattr(line.account, "code", None),
                    debit=line.debit,
                    credit=line.credit,
                    description=line.description
                )
                lines.append(line_schema)
                total_amount += max(line.debit, line.credit)

            # Check if balanced
            total_debits = sum(line.debit for line in lines)
            total_credits = sum(line.credit for line in lines)
            is_balanced = total_debits == total_credits

            return JournalEntrySchema(
                id=entry.id,
                reference_type=entry.referenceType,
                reference_id=entry.referenceId,
                date=entry.date,
                created_at=entry.date,  # Using date as created_at for now
                updated_at=entry.updatedAt,
                lines=lines,
                total_amount=total_amount / 2,  # Divide by 2 since we counted both sides
                is_balanced=is_balanced
            )

        except NotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error getting journal entry {entry_id}: {str(e)}")
            raise DatabaseError(f"Unable to retrieve journal entry: {str(e)}")

    async def get_journal_entries(
        self,
        page: int = 1,
        size: int = 20,
        reference_type: str | None = None,
        reference_id: int | None = None,
        start_date: date | None = None,
        end_date: date | None = None
    ) -> JournalEntryListSchema:
        """Get paginated list of journal entries."""
        try:
            skip = (page - 1) * size
            where_conditions = {}

            if reference_type:
                where_conditions["referenceType"] = reference_type
            
            if reference_id:
                where_conditions["referenceId"] = reference_id

            if start_date:
                where_conditions.setdefault("date", {})["gte"] = datetime.combine(start_date, datetime.min.time())
            
            if end_date:
                where_conditions.setdefault("date", {})["lte"] = datetime.combine(end_date, datetime.max.time())

            # Get total count
            total = await self.db.journalentry.count(where=where_conditions)

            # Get entries
            entries = await self.db.journalentry.find_many(
                where=where_conditions,
                include={
                    "lines": {
                        "include": {
                            "account": True
                        }
                    }
                },
                skip=skip,
                take=size,
                order={"date": "desc"}
            )

            # Convert to schemas
            entry_schemas = []
            for entry in entries:
                entry_schema = await self._convert_to_schema(entry)
                entry_schemas.append(entry_schema)

            pages = (total + size - 1) // size

            return JournalEntryListSchema(
                entries=entry_schemas,
                total=total,
                page=page,
                size=size,
                pages=pages
            )

        except Exception as e:
            logger.error(f"Error getting journal entries: {str(e)}")
            raise DatabaseError(f"Unable to retrieve journal entries: {str(e)}")

    async def get_trial_balance(self, as_of_date: date | None = None) -> TrialBalanceSchema:
        """Generate trial balance as of specified date."""
        try:
            if not as_of_date:
                as_of_date = date.today()

            # Get all journal entry lines up to the specified date
            lines = await self.db.journalentryline.find_many(
                where={
                    "entry": {
                        "date": {
                            "lte": datetime.combine(as_of_date, datetime.max.time())
                        }
                    }
                },
                include={
                    "account": True
                }
            )

            # Group by account and sum debits/credits
            account_balances = {}
            for line in lines:
                account_id = line.accountId
                if account_id not in account_balances:
                    account_balances[account_id] = {
                        "account": line.account,
                        "total_debits": Decimal('0'),
                        "total_credits": Decimal('0')
                    }
                
                account_balances[account_id]["total_debits"] += line.debit
                account_balances[account_id]["total_credits"] += line.credit

            # Create trial balance lines
            trial_balance_lines = []
            total_debits = Decimal('0')
            total_credits = Decimal('0')

            for account_id, balance_info in account_balances.items():
                account = balance_info["account"]
                account_total_debits = balance_info["total_debits"]
                account_total_credits = balance_info["total_credits"]
                
                # Calculate net balance
                net_balance = account_total_debits - account_total_credits
                
                if net_balance != 0:
                    if net_balance > 0:
                        debit_balance = net_balance
                        credit_balance = Decimal('0')
                        total_debits += net_balance
                    else:
                        debit_balance = Decimal('0')
                        credit_balance = abs(net_balance)
                        total_credits += abs(net_balance)

                    trial_balance_lines.append(TrialBalanceLineSchema(
                        account_id=account_id,
                        account_name=account.name,
                        account_code=str(account_id),
                        account_type=getattr(account, "type", None),
                        debit_balance=debit_balance,
                        credit_balance=credit_balance
                    ))

            is_balanced = total_debits == total_credits

            return TrialBalanceSchema(
                as_of_date=datetime.combine(as_of_date, datetime.min.time()),
                lines=trial_balance_lines,
                total_debits=total_debits,
                total_credits=total_credits,
                is_balanced=is_balanced
            )

        except Exception as e:
            logger.error(f"Error generating trial balance: {str(e)}")
            raise DatabaseError(f"Unable to generate trial balance: {str(e)}")

    async def update_journal_entry(self, entry_id: int, data: JournalEntryUpdateSchema) -> JournalEntrySchema:
        """Update an existing journal entry and optionally replace its lines."""
        try:
            # Ensure entry exists
            entry = await self.db.journalentry.find_unique(where={"id": entry_id})
            if not entry:
                raise NotFoundError(f"Journal entry with ID {entry_id} not found")

            # Update entry fields
            update_data: dict[str, Any] = {}
            if data.reference_type is not None:
                update_data["referenceType"] = data.reference_type
            if data.reference_id is not None:
                update_data["referenceId"] = data.reference_id
            if data.date is not None:
                update_data["date"] = data.date

            if update_data:
                await self.db.journalentry.update(
                    where={"id": entry_id},
                    data=update_data,
                )

            # Replace lines if provided
            if data.lines is not None:
                # Basic validation: ensure balanced if lines provided
                total_debits = sum(l.debit for l in data.lines)
                total_credits = sum(l.credit for l in data.lines)
                if total_debits != total_credits:
                    raise ValidationError("Entry must be balanced: debits != credits")

                # Delete existing lines then create new ones
                await self.db.journalentryline.delete_many(where={"entryId": entry_id})
                await self.db.journalentryline.create_many(
                    data=[{
                        "entryId": entry_id,
                        "accountId": l.account_id,
                        "debit": l.debit,
                        "credit": l.credit,
                        "description": l.description,
                    } for l in data.lines]
                )

            # Return updated entry
            return await self.get_journal_entry(entry_id)

        except (NotFoundError, ValidationError):
            raise
        except Exception as e:
            logger.error(f"Error updating journal entry {entry_id}: {str(e)}")
            raise DatabaseError(f"Unable to update journal entry: {str(e)}")

    async def delete_journal_entry(self, entry_id: int) -> None:
        """Delete a journal entry and its lines."""
        try:
            entry = await self.db.journalentry.find_unique(where={"id": entry_id})
            if not entry:
                raise NotFoundError(f"Journal entry with ID {entry_id} not found")

            await self.db.journalentryline.delete_many(where={"entryId": entry_id})
            await self.db.journalentry.delete(where={"id": entry_id})
        except NotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error deleting journal entry {entry_id}: {str(e)}")
            raise DatabaseError(f"Unable to delete journal entry: {str(e)}")

    async def _convert_to_schema(self, entry) -> JournalEntrySchema:
        """Convert database entry to schema."""
        lines = []
        total_amount = Decimal('0')
        
        for line in entry.lines:
            line_schema = JournalEntryLineSchema(
                id=line.id,
                account_id=line.accountId,
                account_name=line.account.name,
                account_code=getattr(line.account, "code", None),
                debit=line.debit,
                credit=line.credit,
                description=line.description
            )
            lines.append(line_schema)
            total_amount += max(line.debit, line.credit)

        # Check if balanced
        total_debits = sum(line.debit for line in lines)
        total_credits = sum(line.credit for line in lines)
        is_balanced = total_debits == total_credits

        return JournalEntrySchema(
            id=entry.id,
            reference_type=entry.referenceType,
            reference_id=entry.referenceId,
            date=entry.date,
            created_at=entry.date,
            updated_at=entry.updatedAt,
            lines=lines,
            total_amount=total_amount / 2,
            is_balanced=is_balanced
        )

def create_journal_service(db: Prisma) -> JournalService:
    """Factory function to create journal service."""
    return JournalService(db)
