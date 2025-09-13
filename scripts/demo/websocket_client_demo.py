"""
WebSocket Client Example for Real-time Notifications
This shows how frontend clients can connect to receive real-time notifications.
"""
import asyncio
import json
import websockets
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NotificationClient:
    """WebSocket client for receiving real-time notifications."""
    
    def __init__(self, user_id: int, role: str, branch_id: str, username: str):
        self.user_id = user_id
        self.role = role
        self.branch_id = branch_id
        self.username = username
        self.websocket = None
        self.running = False
    
    async def connect(self, server_url: str = "ws://localhost:8000"):
        """Connect to the WebSocket server."""
        uri = f"{server_url}/api/v1/ws/notifications?user_id={self.user_id}&role={self.role}&branch_id={self.branch_id}&username={self.username}"
        
        try:
            logger.info(f"Connecting {self.username} ({self.role}) to {uri}")
            self.websocket = await websockets.connect(uri)
            logger.info(f"✅ {self.username} connected successfully!")
            return True
        except Exception as e:
            logger.error(f"❌ Connection failed for {self.username}: {e}")
            return False
    
    async def listen_for_notifications(self):
        """Listen for incoming notifications."""
        if not self.websocket:
            logger.error("Not connected to server")
            return
        
        self.running = True
        logger.info(f"🔊 {self.username} listening for notifications...")
        
        try:
            while self.running:
                try:
                    # Receive message from server
                    message = await asyncio.wait_for(
                        self.websocket.recv(), timeout=30.0
                    )
                    
                    # Handle ping/pong
                    if message == "pong":
                        continue
                    
                    # Parse and handle notification
                    try:
                        notification = json.loads(message)
                        await self.handle_notification(notification)
                    except json.JSONDecodeError:
                        logger.warning(f"Invalid JSON received: {message}")
                
                except asyncio.TimeoutError:
                    # Send ping to keep connection alive
                    await self.websocket.send("ping")
                
                except websockets.exceptions.ConnectionClosed:
                    logger.warning(f"Connection closed for {self.username}")
                    break
        
        except Exception as e:
            logger.error(f"Error in notification listener for {self.username}: {e}")
        
        finally:
            self.running = False
            if self.websocket:
                await self.websocket.close()
    
    async def handle_notification(self, notification: dict):
        """Handle received notification."""
        notif_type = notification.get("type")
        title = notification.get("title", "Notification")
        message = notification.get("message", "")
        timestamp = notification.get("timestamp", "")
        priority = notification.get("priority", "medium")
        
        # Format notification based on type
        icon = self.get_notification_icon(notif_type)
        priority_marker = self.get_priority_marker(priority)
        
        print(f"\n{priority_marker} {icon} {title}")
        print(f"   👤 {self.username} ({self.role})")
        print(f"   💬 {message}")
        print(f"   ⏰ {timestamp}")
        
        # Handle specific notification types
        if notif_type == "stock_request":
            await self.handle_stock_request_notification(notification)
        elif notif_type == "stock_approved":
            await self.handle_stock_approved_notification(notification)
        elif notif_type == "stock_shipped":
            await self.handle_stock_shipped_notification(notification)
        elif notif_type == "low_stock_alert":
            await self.handle_low_stock_alert(notification)
        
        # Mark notification as read
        await self.mark_as_read(notification.get("id"))
    
    async def handle_stock_request_notification(self, notification: dict):
        """Handle stock request notification."""
        data = notification.get("data", {})
        requester = data.get("requester", "Unknown")
        branch = data.get("branch", "Unknown")
        item_count = data.get("item_count", 0)
        
        print(f"   📋 From: {requester} at {branch}")
        print(f"   📦 Items: {item_count}")
        
        # If this is an inventory clerk, show action options
        if self.role == "INVENTORY_CLERK":
            print(f"   🔧 Actions: Review → Approve/Reject → Ship")
    
    async def handle_stock_approved_notification(self, notification: dict):
        """Handle stock approved notification."""
        data = notification.get("data", {})
        approver = data.get("approver", "Unknown")
        approved_items = data.get("approved_items", 0)
        
        print(f"   ✅ Approved by: {approver}")
        print(f"   📦 Items: {approved_items}")
        print(f"   📅 ETA: 1-2 business days")
    
    async def handle_stock_shipped_notification(self, notification: dict):
        """Handle stock shipped notification."""
        data = notification.get("data", {})
        tracking = data.get("tracking_number", "N/A")
        shipper = data.get("shipper", "Unknown")
        
        print(f"   🚚 Shipped by: {shipper}")
        print(f"   📋 Tracking: {tracking}")
        print(f"   📱 Track at: https://tracking.example.com/{tracking}")
    
    async def handle_low_stock_alert(self, notification: dict):
        """Handle low stock alert."""
        data = notification.get("data", {})
        products = data.get("products", [])
        
        print(f"   ⚠️  Low stock items:")
        for product in products[:3]:  # Show first 3
            name = product.get("name", "Unknown")
            current = product.get("current", 0)
            minimum = product.get("minimum", 0)
            print(f"      • {name}: {current}/{minimum}")
        
        if len(products) > 3:
            print(f"      • ... and {len(products) - 3} more items")
    
    def get_notification_icon(self, notif_type: str) -> str:
        """Get icon for notification type."""
        icons = {
            "stock_request": "📋",
            "stock_approved": "✅",
            "stock_rejected": "❌",
            "stock_shipped": "🚚",
            "stock_received": "📥",
            "low_stock_alert": "⚠️",
            "connection_established": "🔗"
        }
        return icons.get(notif_type, "🔔")
    
    def get_priority_marker(self, priority: str) -> str:
        """Get priority marker."""
        markers = {
            "urgent": "🚨",
            "high": "🔴",
            "medium": "🟡",
            "low": "🟢"
        }
        return markers.get(priority, "🔔")
    
    async def mark_as_read(self, notification_id: str):
        """Send message to mark notification as read."""
        if self.websocket and notification_id:
            message = {
                "type": "mark_read",
                "notification_id": notification_id
            }
            try:
                await self.websocket.send(json.dumps(message))
            except Exception as e:
                logger.error(f"Error marking notification as read: {e}")
    
    async def disconnect(self):
        """Disconnect from server."""
        self.running = False
        if self.websocket:
            await self.websocket.close()
            logger.info(f"🔌 {self.username} disconnected")


async def simulate_multiple_clients():
    """Simulate multiple clients connecting to receive notifications."""
    
    print("🌐 WebSocket Real-time Notification Client Demo")
    print("=" * 55)
    
    # Create different types of users
    clients = [
        NotificationClient(101, "CASHIER", "branch-001", "Sarah (Cashier)"),
        NotificationClient(201, "INVENTORY_CLERK", "warehouse", "Mike (Inventory)"),
        NotificationClient(301, "MANAGER", "headquarters", "Lisa (Manager)")
    ]
    
    print(f"\n👥 Connecting {len(clients)} clients...")
    
    # Try to connect all clients
    connected_clients = []
    for client in clients:
        if await client.connect():
            connected_clients.append(client)
        else:
            print(f"❌ Failed to connect {client.username}")
    
    if not connected_clients:
        print("❌ No clients connected. Make sure server is running at http://localhost:8000")
        return
    
    print(f"✅ {len(connected_clients)} clients connected successfully!")
    print(f"\n📱 Clients are now listening for real-time notifications...")
    print(f"📝 To test: Use the API endpoints to create stock requests")
    print(f"🌐 Server API: http://localhost:8000/docs")
    print(f"\n⏹️  Press Ctrl+C to stop all clients")
    
    # Start listening tasks
    tasks = []
    for client in connected_clients:
        task = asyncio.create_task(client.listen_for_notifications())
        tasks.append(task)
    
    try:
        # Keep clients running
        await asyncio.gather(*tasks)
    except KeyboardInterrupt:
        print(f"\n🛑 Shutting down all clients...")
        
        # Disconnect all clients
        for client in connected_clients:
            await client.disconnect()
        
        # Cancel all tasks
        for task in tasks:
            if not task.done():
                task.cancel()
        
        print(f"✅ All clients disconnected")


if __name__ == "__main__":
    print("Starting WebSocket Notification Clients...")
    print("Make sure the server is running: python run.py")
    print("-" * 50)
    
    try:
        asyncio.run(simulate_multiple_clients())
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure the FastAPI server is running on http://localhost:8000")
