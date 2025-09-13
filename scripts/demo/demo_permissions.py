#!/usr/bin/env python3
"""
Permission Override System Demo
Shows how admin can grant custom permissions to override role restrictions.
"""
import asyncio

from app.core.config import UserRole
from app.core.security import PermissionManager
from app.modules.permissions.schema import PermissionGrantRequest, PermissionRevokeRequest
from app.modules.permissions.service import permission_service


async def demo_permission_override():
    """Demonstrate the permission override system."""
    print("🔐 SOFinance Permission Override System Demo")
    print("=" * 50)
    
    # Scenario: Emergency situation where a CASHIER needs to manage inventory
    cashier_user_id = 456
    cashier_role = UserRole.CASHIER
    admin_id = 1
    
    print("\n📋 Scenario: Emergency - Cashier needs temporary inventory access")
    print(f"User ID: {cashier_user_id} | Role: {cashier_role.value}")
    
    # Step 1: Show default permissions
    print("\n1️⃣ Default CASHIER permissions:")
    default_perms = PermissionManager.get_user_permissions(cashier_role)
    for perm in sorted(default_perms):
        print(f"   ✅ {perm}")
    
    # Check if cashier can manage inventory (should be False)
    can_manage_inventory = PermissionManager.has_permission(cashier_role, "inventory:write")
    print(f"\n🔍 Can CASHIER manage inventory? {can_manage_inventory}")
    
    # Step 2: Admin grants emergency permissions
    print("\n2️⃣ Admin granting emergency permissions...")
    emergency_permissions = ["inventory:read", "inventory:write", "products:write"]
    
    grant_request = PermissionGrantRequest(
        user_id=cashier_user_id,
        permissions=emergency_permissions,
        reason="Emergency inventory coverage - staff shortage"
    )
    
    result = await permission_service.grant_permissions(grant_request, admin_id)
    print(f"   Status: {result['message']}")
    
    # Step 3: Show enhanced permissions
    print("\n3️⃣ Enhanced permissions after admin override:")
    custom_perms = PermissionManager.get_custom_permissions(cashier_user_id)
    total_perms = PermissionManager.get_user_permissions(cashier_role, custom_perms)
    
    print(f"   📝 Custom permissions: {custom_perms}")
    print(f"   📊 Total permissions ({len(total_perms)}):")
    for perm in sorted(total_perms):
        prefix = "🆕" if perm in custom_perms else "   "
        print(f"   {prefix} {perm}")
    
    # Step 4: Test new capabilities
    print("\n4️⃣ Testing new capabilities:")
    checks = [
        ("inventory:write", "Manage inventory"),
        ("products:write", "Update products"), 
        ("sales:write", "Process sales"),
        ("users:delete", "Delete users")  # Should still be False
    ]
    
    for permission, description in checks:
        can_do = PermissionManager.has_permission(
            cashier_role, permission, cashier_user_id, custom_perms
        )
        status = "✅ ALLOWED" if can_do else "❌ DENIED"
        print(f"   {status} {description} ({permission})")
    
    # Step 5: Show all available permissions that can be granted
    print("\n5️⃣ All available permissions that admin can grant:")
    all_available = PermissionManager.get_all_available_permissions()
    
    # Group by resource
    grouped = {}
    for perm in all_available:
        if ":" in perm:
            resource, action = perm.split(":", 1)
            if resource not in grouped:
                grouped[resource] = []
            grouped[resource].append(action)
    
    for resource in sorted(grouped.keys()):
        actions = ", ".join(sorted(grouped[resource]))
        print(f"   📂 {resource}: {actions}")
    
    # Step 6: Emergency over - revoke permissions
    print("\n6️⃣ Emergency over - revoking temporary permissions...")
    revoke_request = PermissionRevokeRequest(
        user_id=cashier_user_id,
        permissions=emergency_permissions,
        reason="Emergency over - returning to normal operations"
    )
    
    result = await permission_service.revoke_permissions(revoke_request, admin_id)
    print(f"   Status: {result['message']}")
    
    # Step 7: Confirm back to normal
    final_perms = PermissionManager.get_user_permissions(cashier_role)
    final_custom = PermissionManager.get_custom_permissions(cashier_user_id)
    print(f"\n7️⃣ Back to normal - Current permissions ({len(final_perms)}):")
    print(f"   Custom permissions: {final_custom}")
    for perm in sorted(final_perms):
        print(f"   ✅ {perm}")
    
    print("\n🎯 Permission Override System Demo Complete!")
    print("\n💡 Key Benefits:")
    print("   • Flexible role-based access control")
    print("   • Emergency permission overrides")
    print("   • Complete audit trail")
    print("   • Granular permission management")
    print("   • Bulk operations support")


if __name__ == "__main__":
    print("Running Permission Override System Demo...")
    asyncio.run(demo_permission_override())
