class DeliveryAgent:
    def __init__(self, agent_id, name, phone_number, vehicle_number, password, status='Available'):
        self.agent_id = agent_id
        self.name = name
        self.phone_number = phone_number
        self.vehicle_number = vehicle_number
        self.password = password
        self.status = status

    @staticmethod
    def get_available_agents(conn):
        """Find available delivery agents"""
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM Delivery_Agents 
            WHERE status = 'Available'
            ORDER BY (
                SELECT COUNT(*) 
                FROM Orders 
                WHERE delivery_agent_id = Delivery_Agents.agent_id 
                AND status = 'active'
            )
        ''')
        return cursor.fetchall()

    @staticmethod
    def assign_order(conn, order_id):
        """Assign order to available delivery agent"""
        cursor = conn.cursor()
        
        # Get available agents
        available_agents = DeliveryAgent.get_available_agents(conn)
        if not available_agents:
            return None
        
        # Select first available agent
        selected_agent = available_agents[0]
        
        # Update order with assigned agent
        cursor.execute('''
            UPDATE Orders 
            SET delivery_agent_id = ?, 
                status = 'assigned' 
            WHERE order_id = ?
        ''', (selected_agent[0], order_id))
        
        # Update agent status
        cursor.execute('''
            UPDATE Delivery_Agents 
            SET status = 'On Delivery' 
            WHERE agent_id = ?
        ''', (selected_agent[0],))
        
        conn.commit()
        return selected_agent[0]

    def complete_delivery(self, conn, order_id):
        """Mark delivery as complete and update agent status"""
        cursor = conn.cursor()
        
        # Update order status
        cursor.execute('''
            UPDATE Orders 
            SET status = 'completed' 
            WHERE order_id = ? 
            AND delivery_agent_id = ?
        ''', (order_id, self.agent_id))
        
        # Update agent status
        cursor.execute('''
            UPDATE Delivery_Agents 
            SET status = 'Available' 
            WHERE agent_id = ?
        ''', (self.agent_id,))
        
        conn.commit()

    def get_current_deliveries(self, conn):
        """Get list of current deliveries for agent"""
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM Orders 
            WHERE delivery_agent_id = ? 
            AND status = 'assigned'
        ''', (self.agent_id,))
        return cursor.fetchall()

    def update_status(self, new_status):
        if new_status in ['Available', 'On Delivery']:
            self.status = new_status
        else:
            raise ValueError("Invalid status. Must be 'Available' or 'On Delivery'.")