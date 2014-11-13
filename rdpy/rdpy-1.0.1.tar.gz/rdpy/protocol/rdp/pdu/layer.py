#
# Copyright (c) 2014 Sylvain Peyrefitte
#
# This file is part of rdpy.
#
# rdpy is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#

"""
Implement the main graphic layer

In this layer are managed all mains bitmap update orders end user inputs
"""

from rdpy.network.layer import LayerAutomata
from rdpy.base.error import InvalidExpectedDataException, CallPureVirtualFuntion
from rdpy.network.type import UInt16Le
import rdpy.base.log as log
import rdpy.protocol.rdp.gcc as gcc
import rdpy.protocol.rdp.tpkt as tpkt
import lic, data, caps

class PDUClientListener(object):
    """
    Interface for PDU client automata listener
    """
    def onReady(self):
        """
        Event call when PDU layer is ready to send events
        """
        raise CallPureVirtualFuntion("%s:%s defined by interface %s"%(self.__class__, "onReady", "PDUClientListener"))
    
    def onUpdate(self, rectangles):
        """
        call when a bitmap data is received from update PDU
        @param rectangles: [pdu.BitmapData] struct
        """
        raise CallPureVirtualFuntion("%s:%s defined by interface %s"%(self.__class__, "onUpdate", "PDUClientListener"))
    
    def recvDstBltOrder(self, order):
        """
        @param order: rectangle order
        """
        pass

class PDUServerListener(object):
    """
    Interface for PDU server automata listener
    """
    def onReady(self):
        """
        Event call when PDU layer is ready to send update
        """
        raise CallPureVirtualFuntion("%s:%s defined by interface %s"%(self.__class__, "onReady", "PDUServerListener"))
    
    def onSlowPathInput(self, slowPathInputEvents):
        """
        Event call when slow path input are available
        @param slowPathInputEvents: [data.SlowPathInputEvent]
        """
        raise CallPureVirtualFuntion("%s:%s defined by interface %s"%(self.__class__, "onSlowPathInput", "PDUServerListener"))
    
class PDULayer(LayerAutomata):
    """
    Global channel for MCS that handle session
    identification user, licensing management, and capabilities exchange
    """
    def __init__(self):
        LayerAutomata.__init__(self, None)
        
        #logon info send from client to server
        self._info = data.RDPInfo(extendedInfoConditional = lambda:(self._transport.getGCCServerSettings().getBlock(gcc.MessageType.SC_CORE).rdpVersion.value == gcc.Version.RDP_VERSION_5_PLUS))
        #server capabilities
        self._serverCapabilities = {
            caps.CapsType.CAPSTYPE_GENERAL : caps.Capability(caps.GeneralCapability()),
            caps.CapsType.CAPSTYPE_BITMAP : caps.Capability(caps.BitmapCapability()),
            caps.CapsType.CAPSTYPE_ORDER : caps.Capability(caps.OrderCapability()),
            caps.CapsType.CAPSTYPE_POINTER : caps.Capability(caps.PointerCapability()),
            caps.CapsType.CAPSTYPE_INPUT : caps.Capability(caps.InputCapability()),
            caps.CapsType.CAPSTYPE_VIRTUALCHANNEL : caps.Capability(caps.VirtualChannelCapability()),
            caps.CapsType.CAPSTYPE_FONT : caps.Capability(caps.FontCapability()),
            caps.CapsType.CAPSTYPE_COLORCACHE : caps.Capability(caps.ColorCacheCapability()),
            caps.CapsType.CAPSTYPE_SHARE : caps.Capability(caps.ShareCapability())
        }
        #client capabilities
        self._clientCapabilities = {
            caps.CapsType.CAPSTYPE_GENERAL : caps.Capability(caps.GeneralCapability()),
            caps.CapsType.CAPSTYPE_BITMAP : caps.Capability(caps.BitmapCapability()),
            caps.CapsType.CAPSTYPE_ORDER : caps.Capability(caps.OrderCapability()),
            caps.CapsType.CAPSTYPE_BITMAPCACHE : caps.Capability(caps.BitmapCacheCapability()),
            caps.CapsType.CAPSTYPE_POINTER : caps.Capability(caps.PointerCapability()),
            caps.CapsType.CAPSTYPE_INPUT : caps.Capability(caps.InputCapability()),
            caps.CapsType.CAPSTYPE_BRUSH : caps.Capability(caps.BrushCapability()),
            caps.CapsType.CAPSTYPE_GLYPHCACHE : caps.Capability(caps.GlyphCapability()),
            caps.CapsType.CAPSTYPE_OFFSCREENCACHE : caps.Capability(caps.OffscreenBitmapCacheCapability()),
            caps.CapsType.CAPSTYPE_VIRTUALCHANNEL : caps.Capability(caps.VirtualChannelCapability()),
            caps.CapsType.CAPSTYPE_SOUND : caps.Capability(caps.SoundCapability())
        }
        #share id between client and server
        self._shareId = 0x103EA
    
    def sendPDU(self, pduMessage):
        """
        Send a PDU data to transport layer
        @param pduMessage: PDU message
        """
        self._transport.send(data.PDU(self._transport.getUserId(), pduMessage))
        
    def sendDataPDU(self, pduData):
        """
        Send an PDUData to transport layer
        @param pduData: PDU data message
        """
        self.sendPDU(data.DataPDU(pduData, self._shareId))

class Client(PDULayer, tpkt.IFastPathListener):
    """
    Client automata of PDU layer
    """
    def __init__(self, listener):
        """
        @param listener: PDUClientListener
        """
        PDULayer.__init__(self)
        self._listener = listener
        #enable or not fast path
        self._fastPathSender = None
        
    def connect(self):
        """
        Connect message in client automata
        Send INfo packet (credentials)
        Wait License info
        """
        self.sendInfoPkt()
        #next state is license info PDU
        self.setNextState(self.recvLicenceInfo)
        #check if client support fast path message
        self._clientFastPathSupported = False
        
    def close(self):
        """
        Send PDU close packet and call close method on transport method
        """
        self._transport.close()
        #self.sendDataPDU(data.ShutdownRequestPDU())
        
    def setFastPathSender(self, fastPathSender):
        """
        @param fastPathSender: tpkt.FastPathSender
        @note: implement tpkt.IFastPathListener
        """
        self._fastPathSender = fastPathSender
        
    def recvLicenceInfo(self, s):
        """
        Read license info packet and check if is a valid client info
        Wait Demand Active PDU
        @param s: Stream
        """
        #packet preambule
        securityFlag = UInt16Le()
        securityFlagHi = UInt16Le()
        s.readType((securityFlag, securityFlagHi))
        
        if not (securityFlag.value & data.SecurityFlag.SEC_LICENSE_PKT):
            raise InvalidExpectedDataException("Waiting license packet")
        
        validClientPdu = lic.LicPacket()
        s.readType(validClientPdu)
        
        if validClientPdu.bMsgtype.value == lic.MessageType.ERROR_ALERT and validClientPdu.licensingMessage.dwErrorCode.value == lic.ErrorCode.STATUS_VALID_CLIENT and validClientPdu.licensingMessage.dwStateTransition.value == lic.StateTransition.ST_NO_TRANSITION:
            self.setNextState(self.recvDemandActivePDU)
        #not tested because i can't buy RDP license server
        elif validClientPdu.bMsgtype.value == lic.MessageType.LICENSE_REQUEST:
            newLicenseReq = lic.createNewLicenseRequest(validClientPdu.licensingMessage)
            self._transport.send((UInt16Le(data.SecurityFlag.SEC_LICENSE_PKT), UInt16Le(), newLicenseReq))
        else:
            raise InvalidExpectedDataException("Not a valid license packet")
        
    def recvDemandActivePDU(self, s):
        """
        Receive demand active PDU which contains 
        Server capabilities. In this version of RDPY only
        Restricted group of capabilities are used.
        Send Confirm Active PDU
        Send Finalize PDU
        Wait Server Synchronize PDU
        @param s: Stream
        """
        pdu = data.PDU()
        s.readType(pdu)
        
        if pdu.shareControlHeader.pduType.value != data.PDUType.PDUTYPE_DEMANDACTIVEPDU:
            #not a blocking error because in deactive reactive sequence 
            #input can be send too but ignored
            log.debug("Ignore message type %s during connection sequence"%hex(pdu.shareControlHeader.pduType.value))
            return
        
        self._shareId = pdu.pduMessage.shareId.value
        
        for cap in pdu.pduMessage.capabilitySets._array:
            self._serverCapabilities[cap.capabilitySetType] = cap
        
        self.sendConfirmActivePDU()
        #send synchronize
        self.sendClientFinalizeSynchronizePDU()
        self.setNextState(self.recvServerSynchronizePDU)
        
    def recvServerSynchronizePDU(self, s):
        """
        Receive from server 
        Wait Control Cooperate PDU
        @param s: Stream from transport layer
        """
        pdu = data.PDU()
        s.readType(pdu)
        if pdu.shareControlHeader.pduType.value != data.PDUType.PDUTYPE_DATAPDU or pdu.pduMessage.shareDataHeader.pduType2.value != data.PDUType2.PDUTYPE2_SYNCHRONIZE:
            #not a blocking error because in deactive reactive sequence 
            #input can be send too but ignored
            log.debug("Ignore message type %s during connection sequence"%hex(pdu.shareControlHeader.pduType.value))
            return
        
        self.setNextState(self.recvServerControlCooperatePDU)
        
    def recvServerControlCooperatePDU(self, s):
        """
        Receive control cooperate PDU from server
        Wait Control Granted PDU
        @param s: Stream from transport layer
        """
        pdu = data.PDU()
        s.readType(pdu)
        if pdu.shareControlHeader.pduType.value != data.PDUType.PDUTYPE_DATAPDU or pdu.pduMessage.shareDataHeader.pduType2.value != data.PDUType2.PDUTYPE2_CONTROL or pdu.pduMessage.pduData.action.value != data.Action.CTRLACTION_COOPERATE:
            #not a blocking error because in deactive reactive sequence 
            #input can be send too but ignored
            log.debug("Ignore message type %s during connection sequence"%hex(pdu.shareControlHeader.pduType.value))
            return
        
        self.setNextState(self.recvServerControlGrantedPDU)
        
    def recvServerControlGrantedPDU(self, s):
        """
        Receive last control PDU the granted control PDU
        Wait Font map PDU
        @param s: Stream from transport layer
        """
        pdu = data.PDU()
        s.readType(pdu)
        if pdu.shareControlHeader.pduType.value != data.PDUType.PDUTYPE_DATAPDU or pdu.pduMessage.shareDataHeader.pduType2.value != data.PDUType2.PDUTYPE2_CONTROL or pdu.pduMessage.pduData.action.value != data.Action.CTRLACTION_GRANTED_CONTROL:
            #not a blocking error because in deactive reactive sequence 
            #input can be send too but ignored
            log.debug("Ignore message type %s during connection sequence"%hex(pdu.shareControlHeader.pduType.value))
            return
        
        self.setNextState(self.recvServerFontMapPDU)
        
    def recvServerFontMapPDU(self, s):
        """
        Last useless connection packet from server to client
        Wait any PDU
        @param s: Stream from transport layer
        """
        pdu = data.PDU()
        s.readType(pdu)
        if pdu.shareControlHeader.pduType.value != data.PDUType.PDUTYPE_DATAPDU or pdu.pduMessage.shareDataHeader.pduType2.value != data.PDUType2.PDUTYPE2_FONTMAP:
            #not a blocking error because in deactive reactive sequence 
            #input can be send too but ignored
            log.debug("Ignore message type %s during connection sequence"%hex(pdu.shareControlHeader.pduType.value))
            return
        
        self.setNextState(self.recvPDU)
        #here i'm connected
        self._listener.onReady()
        
    def recvPDU(self, s):
        """
        Main receive function after connection sequence
        @param s: Stream from transport layer
        """
        pdu = data.PDU()
        s.readType(pdu)
        if pdu.shareControlHeader.pduType.value == data.PDUType.PDUTYPE_DATAPDU:
            self.readDataPDU(pdu.pduMessage)
        elif pdu.shareControlHeader.pduType.value == data.PDUType.PDUTYPE_DEACTIVATEALLPDU:
            #use in deactivation-reactivation sequence
            #next state is either a capabilities re exchange or disconnection
            #http://msdn.microsoft.com/en-us/library/cc240454.aspx
            self.setNextState(self.recvDemandActivePDU)
        
    def recvFastPath(self, fastPathS):
        """
        Implement IFastPathListener interface
        Fast path is needed by RDP 8.0
        @param fastPathS: Stream that contain fast path data
        """
        fastPathPDU = data.FastPathUpdatePDU()
        fastPathS.readType(fastPathPDU)
        if fastPathPDU.updateHeader.value == data.FastPathUpdateType.FASTPATH_UPDATETYPE_BITMAP:
            self._listener.onUpdate(fastPathPDU.updateData.rectangles._array)
            
    def readDataPDU(self, dataPDU):
        """
        read a data PDU object
        @param dataPDU: DataPDU object
        """
        if dataPDU.shareDataHeader.pduType2.value == data.PDUType2.PDUTYPE2_SET_ERROR_INFO_PDU:
            errorMessage = "Unknown code %s"%hex(dataPDU.pduData.errorInfo.value)
            if data.ErrorInfo._MESSAGES_.has_key(dataPDU.pduData.errorInfo):
                errorMessage = data.ErrorInfo._MESSAGES_[dataPDU.pduData.errorInfo]
                
            log.error("INFO PDU : %s"%errorMessage)
        elif dataPDU.shareDataHeader.pduType2.value == data.PDUType2.PDUTYPE2_SHUTDOWN_DENIED:
            #may be an event to ask to user
            self._transport.close()
        elif dataPDU.shareDataHeader.pduType2.value == data.PDUType2.PDUTYPE2_UPDATE:
            self.readUpdateDataPDU(dataPDU.pduData)
    
    def readUpdateDataPDU(self, updateDataPDU):
        """
        Read an update data PDU data
        dispatch update data
        @param: UpdateDataPDU object
        """
        if updateDataPDU.updateType.value == data.UpdateType.UPDATETYPE_BITMAP:
            self._listener.onUpdate(updateDataPDU.updateData.rectangles._array)
        
    def sendInfoPkt(self):
        """
        Send a logon info packet
        client automata data
        """
        self._transport.send((UInt16Le(data.SecurityFlag.SEC_INFO_PKT), UInt16Le(), self._info))
        
    def sendConfirmActivePDU(self):
        """
        Send all client capabilities
        """
        #init general capability
        generalCapability = self._clientCapabilities[caps.CapsType.CAPSTYPE_GENERAL].capability
        generalCapability.osMajorType.value = caps.MajorType.OSMAJORTYPE_WINDOWS
        generalCapability.osMinorType.value = caps.MinorType.OSMINORTYPE_WINDOWS_NT
        generalCapability.extraFlags.value = caps.GeneralExtraFlag.LONG_CREDENTIALS_SUPPORTED | caps.GeneralExtraFlag.NO_BITMAP_COMPRESSION_HDR
        if not self._fastPathSender is None:
            generalCapability.extraFlags.value |= caps.GeneralExtraFlag.FASTPATH_OUTPUT_SUPPORTED
        
        #init bitmap capability
        bitmapCapability = self._clientCapabilities[caps.CapsType.CAPSTYPE_BITMAP].capability
        bitmapCapability.preferredBitsPerPixel = self._transport.getGCCClientSettings().getBlock(gcc.MessageType.CS_CORE).highColorDepth
        bitmapCapability.desktopWidth = self._transport.getGCCClientSettings().getBlock(gcc.MessageType.CS_CORE).desktopWidth
        bitmapCapability.desktopHeight = self._transport.getGCCClientSettings().getBlock(gcc.MessageType.CS_CORE).desktopHeight
         
        #init order capability
        orderCapability = self._clientCapabilities[caps.CapsType.CAPSTYPE_ORDER].capability
        orderCapability.orderFlags.value |= caps.OrderFlag.ZEROBOUNDSDELTASSUPPORT
        
        #init input capability
        inputCapability = self._clientCapabilities[caps.CapsType.CAPSTYPE_INPUT].capability
        inputCapability.inputFlags.value = caps.InputFlags.INPUT_FLAG_SCANCODES | caps.InputFlags.INPUT_FLAG_MOUSEX | caps.InputFlags.INPUT_FLAG_UNICODE
        inputCapability.keyboardLayout = self._transport.getGCCClientSettings().getBlock(gcc.MessageType.CS_CORE).kbdLayout
        inputCapability.keyboardType = self._transport.getGCCClientSettings().getBlock(gcc.MessageType.CS_CORE).keyboardType
        inputCapability.keyboardSubType = self._transport.getGCCClientSettings().getBlock(gcc.MessageType.CS_CORE).keyboardSubType
        inputCapability.keyboardrFunctionKey = self._transport.getGCCClientSettings().getBlock(gcc.MessageType.CS_CORE).keyboardFnKeys
        inputCapability.imeFileName = self._transport.getGCCClientSettings().getBlock(gcc.MessageType.CS_CORE).imeFileName
        
        #make active PDU packet
        confirmActivePDU = data.ConfirmActivePDU()
        confirmActivePDU.shareId.value = self._shareId
        confirmActivePDU.capabilitySets._array = self._clientCapabilities.values()
        self.sendPDU(confirmActivePDU)
        
    def sendClientFinalizeSynchronizePDU(self):
        """
        send a synchronize PDU from client to server
        """
        synchronizePDU = data.SynchronizeDataPDU(self._transport.getChannelId())
        self.sendDataPDU(synchronizePDU)
        
        #ask for cooperation
        controlCooperatePDU = data.ControlDataPDU(data.Action.CTRLACTION_COOPERATE)
        self.sendDataPDU(controlCooperatePDU)
        
        #request control
        controlRequestPDU = data.ControlDataPDU(data.Action.CTRLACTION_REQUEST_CONTROL)
        self.sendDataPDU(controlRequestPDU)
        
        #TODO persistent key list http://msdn.microsoft.com/en-us/library/cc240494.aspx
        
        #deprecated font list pdu
        fontListPDU = data.FontListDataPDU()
        self.sendDataPDU(fontListPDU)
        
    def sendInputEvents(self, pointerEvents):
        """
        send client input events
        @param pointerEvents: list of pointer events
        """
        pdu = data.ClientInputEventPDU()
        pdu.slowPathInputEvents._array = [data.SlowPathInputEvent(x) for x in pointerEvents]
        self.sendDataPDU(pdu)
        
class Server(PDULayer, tpkt.IFastPathListener):
    """
    Server Automata of PDU layer
    """
    def __init__(self, listener):
        """
        @param listener: PDUServerListener
        """
        PDULayer.__init__(self)
        self._listener = listener
        #fast path layer
        self._fastPathSender = None
        
    def connect(self):
        """
        Connect message for server automata
        Wait Info Packet
        """
        self.setNextState(self.recvInfoPkt)
        
    def setFastPathSender(self, fastPathSender):
        """
        @param fastPathSender: tpkt.FastPathSender
        @note: implement tpkt.IFastPathListener
        """
        self._fastPathSender = fastPathSender
        
    def recvInfoPkt(self, s):
        """
        Receive info packet from client
        Client credentials
        Send License valid error message
        Send Demand Active PDU
        Wait Confirm Active PDU
        @param s: Stream
        """
        securityFlag = UInt16Le()
        securityFlagHi = UInt16Le()
        s.readType((securityFlag, securityFlagHi))
        
        if not (securityFlag.value & data.SecurityFlag.SEC_INFO_PKT):
            raise InvalidExpectedDataException("Waiting info packet")
        
        s.readType(self._info)
        #next state send error license
        self.sendLicensingErrorMessage()
        self.sendDemandActivePDU()
        self.setNextState(self.recvConfirmActivePDU)
        
    def recvConfirmActivePDU(self, s):
        """
        Receive confirm active PDU from client
        Capabilities exchange
        Wait Client Synchronize PDU
        @param s: Stream
        """
        pdu = data.PDU()
        s.readType(pdu)
        
        if pdu.shareControlHeader.pduType.value != data.PDUType.PDUTYPE_CONFIRMACTIVEPDU:
            #not a blocking error because in deactive reactive sequence 
            #input can be send too but ignored
            log.debug("Ignore message type %s during connection sequence"%hex(pdu.shareControlHeader.pduType.value))
            return
        
        for cap in pdu.pduMessage.capabilitySets._array:
            self._clientCapabilities[cap.capabilitySetType] = cap
            
        #find use full flag
        self._clientFastPathSupported = self._clientCapabilities[caps.CapsType.CAPSTYPE_GENERAL].capability.extraFlags.value & caps.GeneralExtraFlag.FASTPATH_OUTPUT_SUPPORTED
            
        self.setNextState(self.recvClientSynchronizePDU)
        
    def recvClientSynchronizePDU(self, s):
        """
        Receive from client 
        Wait Control Cooperate PDU
        @param s: Stream from transport layer
        """
        pdu = data.PDU()
        s.readType(pdu)
        if pdu.shareControlHeader.pduType.value != data.PDUType.PDUTYPE_DATAPDU or pdu.pduMessage.shareDataHeader.pduType2.value != data.PDUType2.PDUTYPE2_SYNCHRONIZE:
            #not a blocking error because in deactive reactive sequence 
            #input can be send too but ignored
            log.debug("Ignore message type %s during connection sequence"%hex(pdu.shareControlHeader.pduType.value))
            return
        self.setNextState(self.recvClientControlCooperatePDU)
        
    def recvClientControlCooperatePDU(self, s):
        """
        Receive control cooperate PDU from client
        Wait Control Request PDU
        @param s: Stream from transport layer
        """
        pdu = data.PDU()
        s.readType(pdu)
        if pdu.shareControlHeader.pduType.value != data.PDUType.PDUTYPE_DATAPDU or pdu.pduMessage.shareDataHeader.pduType2.value != data.PDUType2.PDUTYPE2_CONTROL or pdu.pduMessage.pduData.action.value != data.Action.CTRLACTION_COOPERATE:
            #not a blocking error because in deactive reactive sequence 
            #input can be send too but ignored
            log.debug("Ignore message type %s during connection sequence"%hex(pdu.shareControlHeader.pduType.value))
            return
        self.setNextState(self.recvClientControlRequestPDU)
        
    def recvClientControlRequestPDU(self, s):
        """
        Receive last control PDU the request control PDU from client
        Wait Font List PDU
        @param s: Stream from transport layer
        """
        pdu = data.PDU()
        s.readType(pdu)
        if pdu.shareControlHeader.pduType.value != data.PDUType.PDUTYPE_DATAPDU or pdu.pduMessage.shareDataHeader.pduType2.value != data.PDUType2.PDUTYPE2_CONTROL or pdu.pduMessage.pduData.action.value != data.Action.CTRLACTION_REQUEST_CONTROL:
            #not a blocking error because in deactive reactive sequence 
            #input can be send too but ignored
            log.debug("Ignore message type %s during connection sequence"%hex(pdu.shareControlHeader.pduType.value))
            return
        self.setNextState(self.recvClientFontListPDU)
        
    def recvClientFontListPDU(self, s):
        """
        Last synchronize packet from client to server
        Send Server Finalize PDUs
        Wait any PDU
        @param s: Stream from transport layer
        """
        pdu = data.PDU()
        s.readType(pdu)
        if pdu.shareControlHeader.pduType.value != data.PDUType.PDUTYPE_DATAPDU or pdu.pduMessage.shareDataHeader.pduType2.value != data.PDUType2.PDUTYPE2_FONTLIST:
            #not a blocking error because in deactive reactive sequence 
            #input can be send but ignored
            log.debug("Ignore message type %s during connection sequence"%hex(pdu.shareControlHeader.pduType.value))
            return
        
        #finalize server
        self.sendServerFinalizeSynchronizePDU()
        self.setNextState(self.recvPDU)
        #now i'm ready
        self._listener.onReady()
        
    def recvPDU(self, s):
        """
        Main receive function after connection sequence
        @param s: Stream from transport layer
        """
        pdu = data.PDU()
        s.readType(pdu)
        if pdu.shareControlHeader.pduType.value == data.PDUType.PDUTYPE_DATAPDU:
            self.readDataPDU(pdu.pduMessage)
            
    def readDataPDU(self, dataPDU):
        """
        read a data PDU object
        @param dataPDU: DataPDU object
        """
        if dataPDU.shareDataHeader.pduType2.value == data.PDUType2.PDUTYPE2_SET_ERROR_INFO_PDU:
            errorMessage = "Unknown code %s"%hex(dataPDU.pduData.errorInfo.value)
            if data.ErrorInfo._MESSAGES_.has_key(dataPDU.pduData.errorInfo):
                errorMessage = data.ErrorInfo._MESSAGES_[dataPDU.pduData.errorInfo]
                
            log.error("INFO PDU : %s"%errorMessage)
        elif dataPDU.shareDataHeader.pduType2.value == data.PDUType2.PDUTYPE2_INPUT:
            self._listener.onSlowPathInput(dataPDU.pduData.slowPathInputEvents._array)
        elif dataPDU.shareDataHeader.pduType2.value == data.PDUType2.PDUTYPE2_SHUTDOWN_REQUEST:
            log.debug("Receive Shutdown Request")
            self._transport.close()
            
    def recvFastPath(self, fastPathS):
        """
        Implement IFastPathListener interface
        Fast path is needed by RDP 8.0
        @param fastPathS: Stream that contain fast path data
        """
        pass
        
    def sendLicensingErrorMessage(self):
        """
        Send a licensing error data
        """
        self._transport.send((UInt16Le(data.SecurityFlag.SEC_LICENSE_PKT), UInt16Le(), lic.createValidClientLicensingErrorMessage()))
        
    def sendDemandActivePDU(self):
        """
        Send server capabilities
        server automata PDU
        """
        #init general capability
        generalCapability = self._serverCapabilities[caps.CapsType.CAPSTYPE_GENERAL].capability
        generalCapability.osMajorType.value = caps.MajorType.OSMAJORTYPE_WINDOWS
        generalCapability.osMinorType.value = caps.MinorType.OSMINORTYPE_WINDOWS_NT
        generalCapability.extraFlags.value = caps.GeneralExtraFlag.LONG_CREDENTIALS_SUPPORTED | caps.GeneralExtraFlag.NO_BITMAP_COMPRESSION_HDR
        
        inputCapability = self._serverCapabilities[caps.CapsType.CAPSTYPE_INPUT].capability
        inputCapability.inputFlags.value = caps.InputFlags.INPUT_FLAG_SCANCODES | caps.InputFlags.INPUT_FLAG_MOUSEX
        
        demandActivePDU = data.DemandActivePDU()
        demandActivePDU.shareId.value = self._shareId
        demandActivePDU.capabilitySets._array = self._serverCapabilities.values()
        self.sendPDU(demandActivePDU)
        
    def sendServerFinalizeSynchronizePDU(self):
        """
        Send last synchronize packet from server to client
        """
        synchronizePDU = data.SynchronizeDataPDU(self._transport.getChannelId())
        self.sendDataPDU(synchronizePDU)
        
        #ask for cooperation
        controlCooperatePDU = data.ControlDataPDU(data.Action.CTRLACTION_COOPERATE)
        self.sendDataPDU(controlCooperatePDU)
        
        #request control
        controlRequestPDU = data.ControlDataPDU(data.Action.CTRLACTION_GRANTED_CONTROL)
        self.sendDataPDU(controlRequestPDU)
        
        #TODO persistent key list http://msdn.microsoft.com/en-us/library/cc240494.aspx
        
        #deprecated font list pdu
        fontMapPDU = data.FontMapDataPDU()
        self.sendDataPDU(fontMapPDU)
        
    def sendPDU(self, pduMessage):
        """
        Send a PDU data to transport layer
        @param pduMessage: PDU message
        """
        PDULayer.sendPDU(self, pduMessage)
        #restart capabilities exchange in case of deactive reactive sequence
        if isinstance(pduMessage, data.DeactiveAllPDU):
            self.sendDemandActivePDU()
            self.setNextState(self.recvConfirmActivePDU)
        
    def sendBitmapUpdatePDU(self, bitmapDatas):
        """
        Send bitmap update data
        @param bitmapDatas: List of data.BitmapData
        """
        #check bitmap header for client that want it (very old client)
        if self._clientCapabilities[caps.CapsType.CAPSTYPE_GENERAL].capability.extraFlags.value & caps.GeneralExtraFlag.NO_BITMAP_COMPRESSION_HDR:
            for bitmapData in bitmapDatas:
                if bitmapData.flags.value & data.BitmapFlag.BITMAP_COMPRESSION:
                    bitmapData.flags.value |= data.BitmapFlag.NO_BITMAP_COMPRESSION_HDR
        
        if self._clientFastPathSupported and not self._fastPathSender is None:
            #fast path case
            fastPathUpdateDataPDU = data.FastPathBitmapUpdateDataPDU()
            fastPathUpdateDataPDU.rectangles._array = bitmapDatas
            self._fastPathSender.sendFastPath(data.FastPathUpdatePDU(fastPathUpdateDataPDU))
        else:
            #slow path case
            updateDataPDU = data.BitmapUpdateDataPDU()
            updateDataPDU.rectangles._array = bitmapDatas
            self.sendDataPDU(data.UpdateDataPDU(updateDataPDU))