#!/usr/bin/env python
# -*- coding: utf-8 -*-

class Command(object):
    STATUS = ("GET","/status")
    NEW_SESSION = ("POST","/session")
    GET_CAPABILITIES = ("GET","/session/$sessionId")
    GET_ALL_SESSIONS = ("GET","/sessions")
    QUIT = ("DELETE","/session/$sessionId")
    GET_CURRENT_WINDOW_HANDLE = ("GET","/session/$sessionId/window_handle")
    GET_WINDOW_HANDLES = ("GET","/session/$sessionId/window_handles")
    OPEN_URL = ("POST","/session/$sessionId/url")
    GO_FORWARD = ("POST","/session/$sessionId/forward")
    GO_BACK = ("POST","/session/$sessionId/back")
    REFRESH = ("POST","/session/$sessionId/refresh")
    EXECUTE_SCRIPT = ("POST","/session/$sessionId/execute")
    GET_CURRENT_URL = ("GET","/session/$sessionId/url")
    GET_TITLE = ("GET","/session/$sessionId/title")
    GET_PAGE_SOURCE = ("GET","/session/$sessionId/source")
    SCREENSHOT = ("GET","/session/$sessionId/screenshot")
    FIND_ELEMENT = ("POST","/session/$sessionId/element")
    FIND_ELEMENTS = ("POST","/session/$sessionId/elements")
    FIND_CHILD_ELEMENT = ("POST","/session/$sessionId/element/$id/element")
    FIND_CHILD_ELEMENTS = ("POST","/session/$sessionId/element/$id/elements")
    CLICK_ELEMENT = ("POST","/session/$sessionId/element/$id/click")
    CLEAR_ELEMENT = ("POST","/session/$sessionId/element/$id/clear")
    SUBMIT_ELEMENT = ("POST","/session/$sessionId/element/$id/submit")
    GET_ELEMENT_TEXT = ("GET","/session/$sessionId/element/$id/text")
    SEND_KEYS_TO_ELEMENT = ("POST","/session/$sessionId/element/$id/value")
    SEND_KEYS_TO_ACTIVE_ELEMENT = ("POST","/session/$sessionId/keys")
    GET_ELEMENT_TAG_NAME = ("GET","/session/$sessionId/element/$id/name")
    IS_ELEMENT_SELECTED = ("GET","/session/$sessionId/element/$id/selected")
    IS_ELEMENT_ENABLED = ("GET","/session/$sessionId/element/$id/enabled")
    IS_ELEMENT_DISPLAYED = ("GET","/session/$sessionId/element/$id/displayed")
    GET_ELEMENT_LOCATION = ("GET","/session/$sessionId/element/$id/location")
    GET_ELEMENT_LOCATION_ONCE_SCROLLED_INTO_VIEW = ("GET","/session/$sessionId/element/$id/location_in_view")
    GET_ELEMENT_SIZE = ("GET","/session/$sessionId/element/$id/size")
    GET_ELEMENT_ATTRIBUTE = ("GET","/session/$sessionId/element/$id/attribute/$name")
    GET_ALL_COOKIES = ("GET","/session/$sessionId/cookie")
    ADD_COOKIE = ("POST","/session/$sessionId/cookie")
    DELETE_ALL_COOKIES = ("DELETE","/session/$sessionId/cookie")
    DELETE_COOKIE = ("DELETE","/session/$sessionId/cookie/$name")
    SWITCH_TO_FRAME = ("POST","/session/$sessionId/frame")
    SWITCH_TO_WINDOW = ("POST","/session/$sessionId/window")
    GET_ELEMENT_VALUE_OF_CSS_PROPERTY = ("GET","/session/$sessionId/element/$id/css/$propertyName")
    IMPLICIT_WAIT = ("POST","/session/$sessionId/timeouts/implicit_wait")
    EXECUTE_ASYNC_SCRIPT = ("POST","/session/$sessionId/execute_async")
    SET_SCRIPT_TIMEOUT = ("POST","/session/$sessionId/timeouts/async_script")
    SET_TIMEOUTS = ("POST","/session/$sessionId/timeouts")
    DISMISS_ALERT = ("POST","/session/$sessionId/dismiss_alert")
    ACCEPT_ALERT = ("POST","/session/$sessionId/accept_alert")
    SET_ALERT_VALUE = ("POST","/session/$sessionId/alert_text")
    GET_ALERT_TEXT = ("GET","/session/$sessionId/alert_text")
    GET_WINDOW_SIZE = ("GET","/session/$sessionId/window/$windowHandle/size")
    SET_SCREEN_ORIENTATION = ("POST","/session/$sessionId/orientation")
    GET_SCREEN_ORIENTATION = ("GET","/session/$sessionId/orientation")
    GET_NETWORK_CONNECTION = ("GET","/session/$sessionId/network_connection")
    
    
    SINGLE_TAP = ("POST","/session/$sessionId/touch/click")
    TOUCH_DOWN = ("POST","/session/$sessionId/touch/down")
    TOUCH_UP = ("POST","/session/$sessionId/touch/up")
    TOUCH_MOVE = ("POST","/session/$sessionId/touch/move")
    TOUCH_SCROLL = ("POST","/session/$sessionId/touch/scroll")
    DOUBLE_TAP = ("POST","/session/$sessionId/touch/doubleclick")
    LONG_PRESS = ("POST","/session/$sessionId/touch/longclick")
    FLICK = ("POST","/session/$sessionId/touch/flick")

    LOG_ELEMENT = ("GET","/session/$sessionId/element/$id/source")
    GET_CURRENT_CONTEXT = ("GET","/session/$sessionId/context")
    GET_CONTEXTS = ("GET","/session/$sessionId/contexts")
    SWITCH_CONTEXT = ("POST","/session/$sessionId/context")

    #Custom extensions to wire protocol
    GET_SCREEN_STATE = ("GET","/session/$sessionId/selendroid/screen/brightness")
    SET_SCREEN_STATE = ("POST","/session/$sessionId/selendroid/screen/brightness")
    INSPECTOR_TAP = ("POST","/session/$sessionId/tap/2")
    GET_COMMAND_CONFIGURATION = ("GET","/session/$sessionId/selendroid/configure/command/$command")
    SET_COMMAND_CONFIGURATION = ("POST","/session/$sessionId/selendroid/configure/command/$command")
    FORCE_GO_EXPLICITLY = ("POST","/session/$sessionId/selendroid/gc")
    SET_SYSTEM_PROPERTY = ("POST","/session/$sessionId/selendroid/systemProperty")
    
    # Endpoints to send app to background and resume it
    BACKGROUND_APP = ("POST","/session/$sessionId/selendroid/background")
    RESUME_APP = ("POST","/session/$sessionId/selendroid/resume")
    
    #Endpoints to add to and read call logs
    ADD_CALL_LOG = ("POST","/session/$sessionId/selendroid/addCallLog")
    READ_CALL_LOG = ("POST","/session/$sessionId/selendroid/readCallLog")












    
