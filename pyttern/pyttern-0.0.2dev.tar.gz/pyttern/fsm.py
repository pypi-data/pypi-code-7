# -*- coding: UTF-8 -*-

__author__ = 'yangtianhang'
import types


def behavior(state, event):
    def _behavior(method):
        method.__fsm_state__ = state
        method.__fsm_event__ = event
        return method

    return _behavior


def stateful(init_state, ext_states=None):
    if init_state is None:
        raise FsmException('init state cannot be None.')
    if ext_states is None:
        ext_states = []

    def _stateful(cls):
        def _init_valid_states(cls, init_state, ext_states):
            cls.__valid_states__ = set()
            cls.__valid_states__.add(init_state)
            if hasattr(ext_states, '__iter__'):
                for ext_state in ext_states:
                    cls.__valid_states__.add(ext_state)
            else:
                cls.__valid_states__.add(ext_states)

        def _set_behaviors(cls, behavior):
            states = _get_iterable_attr_(behavior, '__fsm_state__')
            events = _get_iterable_attr_(behavior, '__fsm_event__')

            if states and events:
                _set_explicit_behaviors(cls, states, events, behavior)
            elif states and not events:
                _set_states_default_behaviors(cls, states, behavior)
            elif not states and events:
                _set_events_default_behaviors(cls, events, behavior)
            else:
                _set_default_behaviors(cls, behavior)

        def _set_explicit_behaviors(cls, states, events, explicit_behavior):
            for state in states:
                cls.__valid_states__.add(state)
                if state not in cls.__explicit_behaviors__:
                    cls.__explicit_behaviors__[state] = dict()
                _add_event(cls.__explicit_behaviors__[state], events, explicit_behavior)

        def _set_states_default_behaviors(cls, states, states_default_behavior):
            for state in states:
                cls.__valid_states__.add(state)
                if state in cls.__states_default_behaviors__:
                    raise FsmException('duplicate state(' + str(state) + ') default behavior)')
                else:
                    cls.__states_default_behaviors__[state] = states_default_behavior

        def _set_events_default_behaviors(cls, events, events_default_behavior):
            for event in events:
                if event in cls.__events_default_behaviors__:
                    raise FsmException('duplicate event(' + str(event) + ') default behavior)')
                else:
                    cls.__events_default_behaviors__[event] = events_default_behavior

        def _set_default_behaviors(cls, default_behavior):
            if cls.__default_behavior__ is None:
                cls.__default_behavior__ = default_behavior
            else:
                raise FsmException('duplicate default behavior')

        def _add_event(state, events, behavior):
            for event in events:
                if event in state:
                    raise FsmException('duplicate event(' + event + ') of state(' + state + ')')
                state[event] = behavior

        def _get_iterable_attr_(behavior, item):
            attr = getattr(behavior, item)
            if attr is None:
                return None
            if not hasattr(attr, '__iter__'):
                attr = [attr]
            return attr

        def _switch(self, state):
            _check_state(state)
            self.__state__ = state

        def _state(self):
            return self.__state__

        def _event(self):
            return self.__event__

        def _check_state(state):
            if state not in cls.__valid_states__:
                if state:
                    raise FsmException('invalid state: ' + str(state))
                else:
                    raise FsmException('invalid state: None')

        def _get_behavior(self, cls, event):
            state_behaviors = cls.__explicit_behaviors__.get(self.__state__, None)
            if state_behaviors:
                behavior = state_behaviors.get(event, None)
                if behavior:
                    return behavior

            behavior = cls.__states_default_behaviors__.get(self.__state__, None)
            if behavior:
                return behavior

            behavior = cls.__events_default_behaviors__.get(event, None)
            if behavior:
                return behavior

            return cls.__default_behavior__

        def _handle(self, event, *args, **kwargs):
            self.__event__ = event
            behavior = _get_behavior(self, cls, event)
            if not behavior:
                raise FsmException("there's no behavior to handle event(" + str(event) + ") of state(" + str(self.__state__) + ")")
            return behavior(self, *args, **kwargs)

        cls.__explicit_behaviors__ = dict()
        cls.__states_default_behaviors__ = dict()
        cls.__events_default_behaviors__ = dict()
        cls.__default_behavior__ = None

        _init_valid_states(cls, init_state, ext_states)
        behaviors = [behavior for behavior in cls.__dict__.values() if isinstance(behavior, types.FunctionType) and '__fsm_state__' in dir(behavior)]
        for behavior in behaviors:
            _set_behaviors(cls, behavior)

        _check_state(init_state)

        cls.__state__ = init_state
        cls.switch = _switch
        cls.state = _state
        cls.handle = _handle
        cls.event = _event

        return cls

    return _stateful


class FsmException(Exception):
    def __init__(self, message):
        super(FsmException, self).__init__(message)
