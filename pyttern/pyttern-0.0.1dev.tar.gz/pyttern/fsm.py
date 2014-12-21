# -*- coding: UTF-8 -*-

__author__ = 'yangtianhang'
import types


def behavior(state, event):
    def _behavior(method):
        method.__fsm_state__ = state
        method.__fsm_event__ = event
        return method

    return _behavior


def stateful(init_state):
    def _stateful(cls):
        def _set_behaviors(behaviors, behavior):
            states = _get_iterable_attr_(behavior, '__fsm_state__')
            events = _get_iterable_attr_(behavior, '__fsm_event__')

            for state in states:
                if state not in behaviors:
                    behaviors[state] = dict()
                _add_event(behaviors[state], events, behavior)

        def _add_event(state, events, behavior):
            for event in events:
                if event in state:
                    raise FsmException('duplicate event(' + event + ') of state(' + state + ')')
                state[event] = behavior

        def _get_iterable_attr_(behavior, item):
            attr = getattr(behavior, item)
            if not hasattr(attr, '__iter__'):
                attr = [attr]
            return attr

        def _get_acceptable_events(behaviors):
            acceptable_events = set()
            keys = [behavior_map for behavior_map in behaviors.values()]
            for key in keys:
                acceptable_events.update(key)
            return acceptable_events

        def _switch(self, state):
            _check_state(state)
            self.__state__ = state

        def _state(self):
            return self.__state__

        def _check_state(state):
            if state not in cls.__behaviors__:
                raise FsmException('invalid state: ' + state)

        def _check_event(event):
            if event not in cls.__acceptable_events__:
                raise FsmException('invalid event: ' + event)

        def _handle(self, event, *args, **kwargs):
            _check_event(event)
            behavior = cls.__behaviors__[self.__state__].get(event)
            if not behavior:
                raise FsmException("there's no behavior to handle event(" + event + ") of state(" + self.__state__ + ")")

            return behavior(self, *args, **kwargs)

        cls.__behaviors__ = dict()
        behaviors = [behavior for behavior in cls.__dict__.values() if isinstance(behavior, types.FunctionType) and '__fsm_state__' in dir(behavior)]
        for behavior in behaviors:
            _set_behaviors(cls.__behaviors__, behavior)

        cls.__acceptable_events__ = _get_acceptable_events(cls.__behaviors__)
        cls.__state__ = init_state
        _check_state(cls.__state__)
        cls.switch = _switch
        cls.state = _state
        cls.handle = _handle

        return cls

    return _stateful


class FsmException(Exception):
    def __init__(self, message):
        super(FsmException, self).__init__(message)
