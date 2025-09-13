#!/usr/bin/env python3
"""
Real-time Stock Request Demo
Shows how cashiers order stock and inventory clerks get notified in real-time.
"""
import asyncio

from app.core.config import UserRole
from app.core.notifications import NotificationType, connection_manager
from app.core.stock_requests import StockRequestPriority, stock_request_service


class MockUser:
    """Mock user for demonstration."""
    
    def __init__(self, id: int, name: str, role: UserRole, branch_id: str = "branch-001"):
        self.id = id
        self.name = name
        self.role = role
        self.branch_id = branch_id
        
        # Handle different branch naming conventions
        if "branch-" in branch_id:
            branch_num = branch_id.split('-')[1] if '-' in branch_id else "001"
            self.branch_name = f"Branch {branch_num}"
        elif branch_id == "warehouse":
            self.branch_name = "Central Warehouse"
        elif branch_id == "headquarters":
            self.branch_name = "Headquarters"
        else:
            self.branch_name = branch_id.title()


async def simulate_stock_request_workflow():
    """Simulate complete stock request workflow with real-time notifications."""
    
    print("🏪 Real-Time Stock Request System Demo")
    print("=" * 50)
    
    # Create mock users
    cashier = MockUser(101, "Sarah (Cashier)", UserRole.CASHIER, "branch-001")
    inventory_clerk = MockUser(201, "Mike (Inventory)", UserRole.INVENTORY_CLERK, "warehouse")
    manager = MockUser(301, "Lisa (Manager)", UserRole.MANAGER, "headquarters")
    
    print("\n👥 Demo Users:")
    print(f"   🛒 {cashier.name} - {cashier.role.value} at {cashier.branch_name}")
    print(f"   📦 {inventory_clerk.name} - {inventory_clerk.role.value} at Warehouse")
    print(f"   👔 {manager.name} - {manager.role.value} at Headquarters")
    
    # Simulate WebSocket connections (in real app, these would be actual WebSocket clients)
    print("\n🔌 Connecting users to real-time notification system...")
    
    # Mock connection manager setup
    connection_manager.user_metadata[cashier.id] = {
        "role": cashier.role.value,
        "branch_id": cashier.branch_id,
        "username": cashier.name
    }
    connection_manager.user_metadata[inventory_clerk.id] = {
        "role": inventory_clerk.role.value,
        "branch_id": inventory_clerk.branch_id,
        "username": inventory_clerk.name
    }
    connection_manager.user_metadata[manager.id] = {
        "role": manager.role.value,
        "branch_id": manager.branch_id,
        "username": manager.name
    }
    
    print("   ✅ All users connected to real-time system")
    
    # Step 1: Cashier creates stock request
    print("\n📋 Step 1: Cashier creates urgent stock request")
    print(f"   👤 {cashier.name} notices low stock and creates request...")
    
    items = [
        {
            "product_id": "P001",
            "product_name": "Premium Coffee Beans 1kg",
            "quantity": 20,
            "current_stock": 3,
            "reason": "Running low - only 3 left"
        },
        {
            "product_id": "P002", 
            "product_name": "Organic Sugar 500g",
            "quantity": 15,
            "current_stock": 1,
            "reason": "Almost out of stock"
        },
        {
            "product_id": "P003",
            "product_name": "Disposable Cups (100 pack)",
            "quantity": 10,
            "current_stock": 0,
            "reason": "Completely out of stock"
        }
    ]
    
    request_id = await stock_request_service.create_request(
        requester_id=cashier.id,
        requester_name=cashier.name,
        branch_id=cashier.branch_id,
        branch_name=cashier.branch_name,
        items=items,
        priority=StockRequestPriority.HIGH,
        notes="Urgent restocking needed for weekend rush"
    )
    
    print(f"   📤 Stock request created: {request_id}")
    print("   🔔 Real-time notification sent to inventory team!")
    
    # Show notifications received by inventory team
    await asyncio.sleep(0.1)  # Small delay to simulate real-time
    
    inventory_notifications = connection_manager.get_user_notifications(inventory_clerk.id, unread_only=True)
    manager_notifications = connection_manager.get_user_notifications(manager.id, unread_only=True)
    
    print("\n📢 Real-time notifications received:")
    if inventory_notifications:
        notif = inventory_notifications[-1]  # Latest notification
        print(f"   📦 {inventory_clerk.name} received: \"{notif['title']}\"")
        print(f"      💬 {notif['message']}")
        print(f"      ⏰ {notif['timestamp']}")
    
    if manager_notifications:
        notif = manager_notifications[-1]
        print(f"   👔 {manager.name} received: \"{notif['title']}\"")
    
    # Step 2: Inventory clerk approves request
    print("\n✅ Step 2: Inventory clerk approves stock request")
    print(f"   👤 {inventory_clerk.name} reviews and approves request...")
    
    approved_items = {
        "P001": 20,  # Full quantity
        "P002": 12,  # Partial quantity 
        "P003": 8    # Partial quantity
    }
    
    await stock_request_service.approve_request(
        request_id=request_id,
        approver_id=inventory_clerk.id,
        approver_name=inventory_clerk.name,
        approved_items=approved_items
    )
    
    print("   ✅ Request approved with adjusted quantities")
    print(f"   🔔 Real-time notification sent to {cashier.name}!")
    
    # Show approval notification
    await asyncio.sleep(0.1)
    cashier_notifications = connection_manager.get_user_notifications(cashier.id, unread_only=True)
    if cashier_notifications:
        notif = cashier_notifications[-1]
        print(f"   📱 {cashier.name} received: \"{notif['title']}\"")
        print(f"      💬 {notif['message']}")
    
    # Step 3: Items are shipped
    print("\n🚚 Step 3: Stock request is shipped")
    print(f"   👤 {inventory_clerk.name} ships approved items...")
    
    await stock_request_service.ship_request(
        request_id=request_id,
        shipper_id=inventory_clerk.id,
        shipper_name=inventory_clerk.name,
        tracking_number="TRK123456789"
    )
    
    print("   📦 Items shipped with tracking: TRK123456789")
    print("   🔔 Real-time notification sent to branch!")
    
    # Show shipping notification
    await asyncio.sleep(0.1)
    cashier_notifications = connection_manager.get_user_notifications(cashier.id, unread_only=True)
    if cashier_notifications:
        notif = cashier_notifications[-1]
        print(f"   📱 {cashier.name} received: \"{notif['title']}\"")
        print(f"      💬 {notif['message']}")
        tracking = notif.get('data', {}).get('tracking_number', 'N/A')
        print(f"      📋 Tracking: {tracking}")
    
    # Step 4: Items are received
    print("\n📥 Step 4: Stock is received at branch")
    print(f"   👤 {cashier.name} receives the shipment...")
    
    received_items = {
        "P001": 20,
        "P002": 12,
        "P003": 8
    }
    
    await stock_request_service.receive_request(
        request_id=request_id,
        receiver_id=cashier.id,
        receiver_name=cashier.name,
        received_items=received_items
    )
    
    print("   ✅ Stock received and updated in inventory")
    print("   🔔 Completion notification sent to inventory team!")
    
    # Show completion notification
    await asyncio.sleep(0.1)
    inventory_notifications = connection_manager.get_user_notifications(inventory_clerk.id, unread_only=True)
    if inventory_notifications:
        notif = inventory_notifications[-1]
        print(f"   📦 {inventory_clerk.name} received: \"{notif['title']}\"")
        print(f"      💬 {notif['message']}")
    
    # Final status
    print("\n🎯 Stock Request Workflow Complete!")
    
    final_request = stock_request_service.get_request(request_id)
    if final_request:
        print("\n📊 Final Status:")
        print(f"   🆔 Request ID: {final_request.id}")
        print(f"   📈 Status: {final_request.status.value.upper()}")
        print(f"   👤 Requester: {final_request.requester_name}")
        print(f"   👤 Approved by: {inventory_clerk.name}")
        print("   ⏱️  Total time: ~5 minutes (demo)")
        print(f"   📦 Items processed: {len(final_request.items)}")
        print("   🔔 Notifications sent: 4 (Create → Approve → Ship → Receive)")
    
    # Show notification summary
    print("\n📈 Notification Summary:")
    total_notifications = len(connection_manager.notifications)
    print(f"   📧 Total notifications sent: {total_notifications}")
    
    for user_id, username in [(cashier.id, cashier.name), (inventory_clerk.id, inventory_clerk.name), (manager.id, manager.name)]:
        user_notifs = connection_manager.get_user_notifications(user_id)
        print(f"   👤 {username}: {len(user_notifs)} notifications received")
    
    print("\n✨ Real-time Inventory Management System Benefits:")
    print("   🚀 Instant notifications - no email delays")
    print("   👥 Role-based delivery - right person gets right info")
    print("   📱 Real-time status updates - everyone stays informed")
    print("   📊 Complete audit trail - full workflow tracking")
    print("   🔄 Automatic workflows - reduce manual coordination")


async def demonstrate_low_stock_alert():
    """Demonstrate automatic low stock alerts."""
    
    print("\n🔔 Bonus: Automatic Low Stock Alert Demo")
    print("-" * 40)
    
    import uuid

    from app.core.notifications import Notification, NotificationPriority
    
    # Simulate low stock detection
    low_stock_notification = Notification(
        id=str(uuid.uuid4()),
        type=NotificationType.LOW_STOCK_ALERT,
        title="⚠️ Low Stock Alert",
        message="Multiple products below minimum stock levels",
        data={
            "products": [
                {"name": "Coffee Beans", "current": 2, "minimum": 10},
                {"name": "Sugar", "current": 1, "minimum": 5},
                {"name": "Cups", "current": 0, "minimum": 20}
            ],
            "branch": "Branch 001",
            "severity": "high"
        },
        priority=NotificationPriority.HIGH,
        recipient_roles=["CASHIER", "MANAGER", "INVENTORY_CLERK"],
        branch_id="branch-001"
    )
    
    await connection_manager.send_notification(low_stock_notification)
    
    print("   📤 Automatic low stock alert sent to all relevant staff")
    print("   🎯 Recipients: Cashiers, Managers, Inventory Clerks")
    print("   ⚡ Triggered automatically by inventory monitoring")


if __name__ == "__main__":
    print("Starting Real-time Stock Request System Demo...")
    asyncio.run(simulate_stock_request_workflow())
    print("\n" + "="*50)
    asyncio.run(demonstrate_low_stock_alert())
    print("\n🏁 Demo Complete!")
