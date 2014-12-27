"""
RAVN Smart Drone Platform
Copyright (C) 2014 RaptorBird Robotics Inc.
<http://www.raptorbird.com/>

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; Version 2

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
"""

# Import System Libraries
import sys, os
from time import sleep
# Import DroneApi & MAVLINK
from droneapi.lib import VehicleMode, Location
from pymavlink import mavutil
# Import ws4py - WebSocket Library for python
from wsgiref.simple_server import make_server
from ws4py.server.wsgirefserver import WSGIServer, WebSocketWSGIRequestHandler
from ws4py.server.wsgiutils import WebSocketWSGIApplication
from ws4py.websocket import WebSocket
from ws4py.messaging import TextMessage

class RavnServer(object):
    """
    The Object that interacts with the Flight Controller
    """
    def __init__(self, callback):
        """
        Initialize the connection to RAVN
        """
        try:
            self.ravn = local_connect().get_vehicles()[0]
        except Exception, e:
            sys.exit()
        self.create_pidfile()
        self.ravn.set_mavlink_callback(self.ravn_callback)
        self.ravn_current_waypoint = ""
        self.on_ground = True
        self.is_taking_off = False
        self.is_landing = False
        self.send = callback
        self.arm_fail = 0

    def ravn_callback(self, message):
        """
        Function gets called every time a mavlink message is recieved
        """
        if message.get_type() == "HEARTBEAT":
            if self.location_comparison(self.ravn.location,\
             self.ravn_current_waypoint):
                self.send("@")
                self.ravn_current_waypoint = Location(360, 360, 150,\
                    is_relative=True)

    @staticmethod
    def location_comparison(loc1, loc2):
        """
        Location comparison with lat/longtitude error of 1m
        and altitude error of 10 cm

        @return
        True -- if locations are within the error
        False -- if locations are outside the error range
        """
        if abs(loc1.alt - loc2.alt) <= .01:
            if abs(loc1.lat - loc2.lat) <= .0001:
                if abs(loc1.lon - loc2.lon) <= .0001:
                    return True

    @staticmethod
    def create_pidfile():
        """
        Create PIDFile for RAVN, to let startup script know the Server
        is setup
        """
        f = open('~/.RAVNServer/pidfile','w')
        f.write(os.getpid())
        f.close()

    def set_mode(self, mode):
        """
        Sets the mode of the APM

        @params
        mode -- APM Flight modes, LOITER, STABILIZE, GUIDED, AUTO
        """
        self.ravn.mode = VehicleMode(mode)
        self.ravn.flush()

    def user_override(self):
        """
        Returns the status on the user override channel,
        most likely a switch

        @return
        True -- if channel 8 is HIGH
        False -- if channel 8 is LOW
        """
        if self.ravn.channel_readback["7"] >= 1500:
            print "User Override: False"
            return False
        print "User Override: True"
        return True

    def goto(self, lat=None, lng=None, alt=None):
        """
        Goto Location

        @params
        lat -- The target latitude in degrees
        lng -- The target longtitude in degrees
        alt -- The target Altitude in meters
        """
        if self.user_override():
            return
        if not -90 <= lat <= 90:
            lat = self.ravn.location.lat
        if not -180 <= lng <= -180:
            lng = self.ravn.location.lon
        if alt >= 150:
            alt = self.ravn.location.alt
        self.ravn_current_waypoint = Location(lat, lng, alt, is_relative=True)
        self.set_mode("GUIDED")
        self.ravn.commands.goto(self.ravn_current_waypoint)
        self.ravn.flush()

    def holdposition(self):
        """
        Hold the current position by send the drone to its current position
        """
        self.ravn_current_waypoint = Location(self.ravn.location.lat,\
            self.ravn.location.lon, self.ravn.location.alt, is_relative=True)
        self.set_mode("GUIDED")
        self.ravn.commands.goto(self.ravn_current_waypoint)
        self.ravn.flush()
    def arm(self):
        """
        Tries to arm the Drone, if it fails more than 3 times then, it quits
        """
        self.set_mode("LOITER")
        if self.ravn.armed:
            return True
        self.ravn.armed = True
        self.ravn.flush()
        while not self.ravn.armed:
            if self.arm_fail < 3:
                self.arm_fail += 1
                self.ravn.armed = True
                self.ravn.flush()
                sleep(5)
            else:
                print "Excessive number of Arming Failures, check your drone!"
                return False
        return True

    def takeoff(self, alt=150):
        """
        Takeoff to a desired altitude

        @params
        alt -- altitude target in meters
        """
        if self.user_override():
            return
        if alt >= 150:
            alt = 2
        if not self.arm():
            return
        self.ravn.channel_override = {3: 1500}
        self.ravn.flush()
        sleep(.5)
        for i in range(1500, 1600, 20):
            self.ravn.channel_override = {3: i}
            self.ravn.flush()
            sleep(.2)
        for i in range(1600, 1500, -20):
            self.ravn.channel_override = {3: i}
            self.ravn.flush()
            sleep(.2)
        self.ravn.channel_override = {3: 1500}
        self.ravn.flush()
        sleep(.2)
        self.is_taking_off = True
        self.arm_fail = 0
        self.goto(alt=alt)
        self.ravn.channel_override = {3: 0}

    def land(self):
        """
        Land at current location
        """
        if self.user_override():
            return
        self.is_landing = True
        msg = self.ravn.message_factory.command_long_encode(0, 0,\
            mavutil.mavlink.MAV_CMD_NAV_LAND, 0,\
            0, 0, 0, 0, self.ravn.location.lat,\
            self.ravn.location.lon, 0)
        self.ravn.send_mavlink(msg)

    def send_data(self):
        """
        Return a stringified list of data
        """
        self.send(','.join(["%",
            str(self.ravn.mode.name),
            str(self.ravn.location.lat),
            str(self.ravn.location.lon),
            str(self.ravn.location.alt),
            str(self.ravn.attitude.roll),
            str(self.ravn.attitude.pitch),
            str(self.ravn.attitude.yaw),
            str(self.ravn.velocity[0]),
            str(self.ravn.velocity[1]),
            str(self.ravn.velocity[2]),
            str(self.ravn.armed),
            str(self.ravn.groundspeed),
            str(self.ravn.airspeed)
        ]))

    def listener(self, message):
        """
        The function that handles messages sent to the server,
        and decide the right action to call

        @params
        message -- the incoming message
        """
        if self.user_override():
            return
        elif self.is_landing:
            return
        try:
            message = message.split(',')
            cmd = message[0]
            armed = self.ravn.armed
            if cmd == "T" and not armed: # TAKEOFF
                self.takeoff(alt=float(message[1]))
            elif cmd == "L" and armed: # LAND
                self.land()
            elif cmd == "G" and armed: # GOTO
                self.goto(lat=float(message[1]), lng=float(message[2]),\
                    alt=float(message[3]))
            elif cmd == "H" and armed: # HOVER
                self.holdposition()
            self.send_data()
        except Exception as _:
            exc_type, _, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)


class RavnHandler(WebSocket):
    """
    Ravn WebSocket Server that parses commands and controls the drone
    """
    def __init__(self, sock, protocols=None, extensions=None,\
            environ=None, heartbeat_freq=.2):
        """
        Initializes the WebSocket Server with all default values
        """
        WebSocket.__init__(self, sock, protocols, extensions,\
            environ, heartbeat_freq)
        self.ravn = RavnServer(self.send_str)

    def send_str(self, string):
        self.send(TextMessage(string))

    def received_message(self, m):
        """
        Recieved message
        """
        self.ravn.listener(str(m))

    def ponged(self, pong):
        """
        Heartbeat message, send 2 times a sec
        """
        self.ravn.send_data()

    def opened(self):
        self.ravn.send_data()

    def closed(self, code, reason="Exit without Code"):
        """
        Closes the server connection
        """
        self.close()

class Server(object):
    def __init__(port=9000):
        RAVN_SERVER = make_server('', port, server_class=WSGIServer,\
            handler_class=WebSocketWSGIRequestHandler,\
            app=WebSocketWSGIApplication(handler_cls=RavnHandler))
        RAVN_SERVER.initialize_websockets_manager()
        RAVN_SERVER.serve_forever()
