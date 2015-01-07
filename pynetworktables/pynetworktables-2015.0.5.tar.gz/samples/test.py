# To see messages from networktables, you must setup logging
import logging
logging.basicConfig(level=logging.DEBUG)


from networktables import NetworkTable

NetworkTable.setTeam(900)
NetworkTable.setClientMode()
NetworkTable.initialize()

dashboard = NetworkTable.getTable('SmartDashboard')

print("HI")
