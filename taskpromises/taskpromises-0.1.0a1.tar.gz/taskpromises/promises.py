'''
Created on 05/10/2014

Implementation of Promises for the appengine distributed computing environment,
based on Queues and Tasks, using the "deferred" library.

@author: emlyn
'''

from google.appengine.ext import ndb
from google.appengine.ext import deferred
from google.appengine.api.taskqueue import TaskRetryOptions #, TaskAlreadyExistsError
import pickle
import datetime
import marshal
import sys
import types
import uuid
import logging
import time
import random

def log(f):
    def dolog(*args, **kwargs):
        #app_instance_id = os.environ.get('INSTANCE_ID') 
        #EJO #EJO2 logging.debug("Enter %s" % (f.__name__))
        retval = f(*args, **kwargs)
        #EJO #EJO2 logging.debug("Leave %s" % (f.__name__))
        return retval

    def dologpassthrough(*args, **kwargs):
        return f(*args, **kwargs)
    
    return dologpassthrough

# fully functional version of partial (which can be serialised)
def partialf(f, *args, **kwargs):
    def partialw(* args2, **kwargs2):
        fullargs = args + args2
        fullkwargs = dict(kwargs)
        fullkwargs.update(kwargs2)
        f (*fullargs, **fullkwargs)
    return partialw

def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)

class PromiseTimeoutError(Exception):
    pass

class ProxyFailureError(Exception):
    pass

class PromiseResult(ndb.Model):
    promisekey = ndb.KeyProperty()
    pickledValue = ndb.TextProperty() # pickled result
    
    @property
    def value(self):
        retval = None
        if self.pickledValue:
            try:
                retval = pickle.loads(self.pickledValue)
            except Exception, ex:
                retval = ex
        return retval

    @value.setter
    def value(self, aValue):
        self.pickledValue = pickle.dumps(aValue)
    
STATUSES = enum('PRE', 'UNRESOLVED', 'RESOLVED', 'REJECTED')


class PromiseSpace(object):
    _keyspace = None
    _taskArgs = None
    _taskKwargs = None
    
    @log
    def __init__(self, keyspace="default", *args, **kwargs):
        self._keyspace = keyspace
        self._taskArgs = args
        self._taskKwargs = kwargs
        #EJO #EJO2 logging.debug("self._taskKwargs: %s" % self._taskKwargs)
        
    
    def when(self, aDeferredFunc, *args, **kwargs):
        lretries = InitRetries()

        @ndb.transactional(retries = 20)
        def dowhen():
            logging.debug("DoWhen, retries = %s" % lretries)
            IncRetries(lretries)

            retval = Promise()
            retval._setTaskArgs(*self._taskArgs, **self._taskKwargs)
            kwargs["_keyspace"] = self._keyspace
            retval._doinit(None, aDeferredFunc, False, False, *args, **kwargs)
            return retval

        retval = dowhen()
        
        retval.ProcessSelf()
        
        return retval
    
    
    def allwhen(self, aPredecessors, aDeferredFunc, *args, **kwargs):
        if not aPredecessors:
            raise Exception("At least one predecessor required")

        lkeySpace = self._keyspace
        
        for lpre in aPredecessors:
            if lpre.key.parent().id() != lkeySpace:
                raise Exception("All keyspaces must match promisespace for predecessors in all()")

        kwargs["_keyspace"] = lkeySpace
        
        lretries = InitRetries()

        @ndb.transactional(retries = 20)
        def doallwhen():
            logging.debug("doallwhen, retries = %s" % lretries)
            IncRetries(lretries)

            retval = Promise()
            retval._setTaskArgs(*self._taskArgs, **self._taskKwargs)
            retval._doinit(aPredecessors, aDeferredFunc, True, False, *args, **kwargs)
            
            return retval
        
        retval = doallwhen()

        retval.ProcessSelf()
        
        return retval

    @log
    def allthen(self, aPredecessors, aDeferredFunc, *args, **kwargs):
        return self.allwhen(aPredecessors, WrapThenF(aDeferredFunc), *args, **kwargs)

    @log
    def all(self, aPredecessors, *args, **kwargs):
        return self.allwhen(aPredecessors, None, *args, **kwargs)

class PromiseLink(ndb.Model):
    fromkey = ndb.KeyProperty()
    tokey = ndb.KeyProperty()
    pickledValue = ndb.TextProperty() # pickled result
    
    @property
    def value(self):
        retval = None
        if self.pickledValue:
            try:
                retval = pickle.loads(self.pickledValue)
            except Exception, ex:
                retval = ex
        return retval

    @value.setter
    def value(self, aValue):
        self.pickledValue = pickle.dumps(aValue)
     
     
class Promise(ndb.Model):
#     results = ndb.StructuredProperty(PromiseResult, repeated = True) # results of ancestors
#    successorkeys = ndb.KeyProperty(repeated = True) # keys of successor promises
    
    timeoutsec = ndb.IntegerProperty(default = 660) # assuming timeout is 10 mins, and we're not using task retries'
    cleanupsec = ndb.IntegerProperty(default = 1320)

    stored = ndb.DateTimeProperty(auto_now_add=True)
    updated = ndb.DateTimeProperty(auto_now=True)
    expiry = ndb.DateTimeProperty() # gets set in init based on timeoutsec
    cleanup = ndb.DateTimeProperty() # gets set in init based on cleanupsec
    
    serialisedfuncandargs = ndb.TextProperty()
 
    pickledresult = ndb.TextProperty() # own result

    status = ndb.IntegerProperty(default = STATUSES.PRE)

    needresults = ndb.BooleanProperty()
    needresult = ndb.BooleanProperty()

    serialisedtaskargs = ndb.TextProperty()
        
    # must call this inside a transaction @ndb.transactional(retries = 20)
    def _doinit(self, aPredecessors, aDeferredFunc, aNeedResults, aNeedResult, *args, **kwargs):
        def GetKwarg(aKeyName, aDefault):
            if aKeyName in kwargs:
                retval = kwargs[aKeyName]
                del kwargs[aKeyName]
            else:
                retval = aDefault
            return retval

        lkeySpace = GetKwarg("_keyspace", "default")            
        ltimeoutSec = GetKwarg("_timeoutsec", 660)
        lcleanupSec = GetKwarg("_cleanupsec", 1320)

        # self should never have been saved before
        self._initKey(lkeySpace)
        
        logging.debug("in _doinit (%s, %s): in_transaction: %s" % (self.key.id(), lkeySpace, ndb.in_transaction()))

        self.timeoutsec = ltimeoutSec
        self.cleanupsec = lcleanupSec
        
        self.needresults = aNeedResults
        self.needresult = aNeedResult
        

        if aDeferredFunc:
            self.serialisedfuncandargs = SerialiseFunctionAndArgs(aDeferredFunc, *args, **kwargs)
        else:
            self.serialisedfuncandargs = None
            #raise Exception("Deferred Function required")
        
        lpromisesForPut = [self]

        if aPredecessors:
            # must load predecessors, get result values out where they exist
            lpredecessorKeysSet = set([item.key for item in aPredecessors if item and item.key])
            lreloadedPredecessors = ndb.get_multi(lpredecessorKeysSet) #, use_cache=False, use_memcache=False, use_datastore = True)
#            lreloadedPredecessors = ndb.get_multi([item.key for item in aPredecessors])


            lpromiseLinks = [
                PromiseLink(
                    key = ndb.Key('KeySpace', lkeySpace, PromiseLink, str(uuid.uuid4())),
                    fromkey = item.key,
                    tokey = self.key,
                    pickledValue=pickle.dumps(item.result) if item.result else None
                ) 
                for item in lreloadedPredecessors
            ]
            
            lpromisesForPut.extend(lpromiseLinks)
            
# removed results            
#             self.results = [
#                 PromiseResult(
#                     promisekey=item.key, 
#                     pickledValue=pickle.dumps(item.result) if item.result else None
#                 ) 
#                 for item in lreloadedPredecessors
#             ]

# removed successorkeys
#             for item in lreloadedPredecessors:
#                 lsuccessorKeys = set(item.successorkeys if item.successorkeys else [])
#                 lsuccessorKeys.add(self.key)
#                 item.successorkeys = list(lsuccessorKeys)
#                 logging.debug("Set successors for %s: %s" % (item.key.id(), [skey.id() for skey in item.successorkeys]))
#                 lpromisesForPut.append(item)

#         else:
#             self.results = []

        ndb.put_multi(lpromisesForPut) #, use_cache=False, use_memcache=False, use_datastore = True)

    @log
    def _setTaskArgs(self, *args, **kwargs):
        #EJO #EJO2 logging.debug("%s, %s" % (args, kwargs))
        self.serialisedtaskargs = SerialiseArgs(*args, **kwargs)
        
    @log
    def _getTaskArgs(self):
        retval = ([], {})
        if self.serialisedtaskargs:
            retval = DeserialiseArgs(self.serialisedtaskargs)
        if "_name" in retval:
            del retval["_name"]
        if "_retry_options" in retval:
            del retval["_retry_options"]
        if "_countdown" in retval:
            del retval["_countdown"]
        #EJO #EJO2 logging.debug("%s" % str(retval))
        return retval

    @log
    def StartTimeouts(self, aNeedExpiryCheck = True):
        # run this inside a transaction
        if not self.expiry:
            self.expiry = datetime.datetime.utcnow() + datetime.timedelta(0, self.timeoutsec)
        if not self.cleanup:
            self.cleanup = datetime.datetime.utcnow() + datetime.timedelta(0, self.cleanupsec)
        ltaskArgs, ltaskKwargs = self._getTaskArgs()
        lretryoptions=TaskRetryOptions(task_retry_limit = 2)
        if aNeedExpiryCheck:
            deferred.defer(ProcessPromise, self.key, _countdown = self.timeoutsec+2, _transactional = True, _retry_options = lretryoptions, *ltaskArgs, **ltaskKwargs)
        deferred.defer(ProcessPromise, self.key, _countdown = self.cleanupsec+2, _transactional = True, _retry_options = lretryoptions, *ltaskArgs, **ltaskKwargs)

#     @classmethod
#     def when(cls, aDeferredFunc, *args, **kwargs):
#         retval = Promise()
#         retval._doinit(None, aDeferredFunc, False, False, *args, **kwargs)
#         
#         retval.ProcessSelf()
#         
#         return retval

    def _then(self, aDeferredFunc, aIsMulti, *args, **kwargs):

        lretries = InitRetries()
               
        @ndb.transactional(retries = 20)
        def dothen():
            logging.debug("_then, retries = %s" % lretries)
            IncRetries(lretries)

            retval = Promise()
            ltaskArgs, ltaskKwargs = self._getTaskArgs()
            retval._setTaskArgs(*ltaskArgs, **ltaskKwargs)
            kwargs["_keyspace"] = self.key.parent().id()
    #        x = str(uuid.uuid4())
            #EJO2 logging.debug("Before _doinit (%s)" % x)
            retval._doinit([self], aDeferredFunc, aIsMulti, not aIsMulti, *args, **kwargs)
            #EJO2 logging.debug("After _doinit (%s)" % x)
            
            return retval

        retval = dothen()
                
        retval.ProcessSelf()

        return retval

    def thenwhen(self, aDeferredFunc, *args, **kwargs):
        return self._then(aDeferredFunc, False, *args, **kwargs)
        
    def then(self, aDeferredFunc, *args, **kwargs):
        return self._then(WrapThenF(aDeferredFunc), False, *args, **kwargs)

    def mthenwhen(self, aDeferredFunc, *args, **kwargs):
        return self._then(aDeferredFunc, True, *args, **kwargs)
        
    def mthen(self, aDeferredFunc, *args, **kwargs):
        return self._then(WrapThenF(aDeferredFunc), True, *args, **kwargs)

    @property
    def result(self):
        retval = None
        if self.pickledresult:
            try:
                retval = pickle.loads(self.pickledresult)
            except Exception, ex:
                retval = ex
        return retval

    @result.setter
    def result(self, aValue):
        self.pickledresult = pickle.dumps(aValue)

    def _hasAllResults(self):
        lpromiseLinks = PromiseLink.query(PromiseLink.tokey == self.key, ancestor = self.key.parent())
        retval = len([True for lpromiseLink in lpromiseLinks if not lpromiseLink.pickledValue]) == 0
        return retval

#     @log
#     def _hasAllResults(self):
#         lresultsSummary = [(item.promisekey.id(), True if item.pickledValue else False) for item in self.results]
#         retval = not self.results or (len([True for item in self.results if item.pickledValue]) == len(self.results))
#         logging.debug("(%s) %s all results: %s" % (self.key.id() if self.key else None, "HAS" if retval else "doesn't have", lresultsSummary))
#         #EJO2 logging.debug("_hasAllResults: %s" % retval)
#         return retval

    @log
    def _getSuccessorLinks(self):
        lpromiseLinks = PromiseLink.query(PromiseLink.fromkey == self.key, ancestor = self.key.parent())
        return lpromiseLinks

    @log
    def _getSuccessors(self):
        return self._getSuccessorsByKey(self.key)
    
    @classmethod    
    def _getSuccessorsByKey(cls, aKey):
        lpromiseLinks = PromiseLink.query(PromiseLink.fromkey == aKey, ancestor = aKey.parent())
        retval = ndb.get_multi([lpromiseLink.tokey for lpromiseLink in lpromiseLinks])
        return retval
    
#     @log
#     def _getSuccessors(self):
#         return self._getSuccessorsByKey(self.key)
#     
#     @classmethod    
#     def _getSuccessorsByKey(cls, aKey):
#         lpromises = Promise.query(Promise.results.promisekey == aKey, ancestor = aKey.parent())
#         retval = list(lpromises)
#         #if retval:
#             #EJO2 logging.debug("Successors: %s" % retval)
#         return retval

#     @log
#     def _getSuccessors(self):
# #        return ndb.get_multi(self.successorkeys, use_cache=False, use_memcache=False, use_datastore = True) if self.successorkeys else []
#         return ndb.get_multi(self.successorkeys) if self.successorkeys else []
# 
#     @classmethod    
#     def _getSuccessorsByKey(cls, aKey):
#         retval = []
# #        lpromise = aKey.get(use_cache=False, use_memcache=False, use_datastore = True) if aKey else None
#         lpromise = aKey.get() if aKey else None
#         if lpromise:
#             retval = lpromise._getSuccessors()
#         return retval


    
#     @log
#     def _getPredecessors(self):
# #        lpromises = [item.promisekey.get(use_cache=False, use_memcache=False, use_datastore = True) for item in (self.results if self.results else [])]
#         lpromises = [item.promisekey.get() for item in (self.results if self.results else [])]
#         retval = [litem for litem in lpromises if litem]
#         #EJO #EJO2 logging.debug("Predecessors: %s" % retval)
#         return retval
                
    def _getResultValues(self):
        lpromiseLinks = PromiseLink.query(PromiseLink.tokey == self.key, ancestor = self.key.parent())
        retval = ([lpromiseLink.value for lpromiseLink in lpromiseLinks])
        return retval

    def _delete(self):
        logging.debug("_delete")
        lfromLinks = PromiseLink.query(PromiseLink.tokey == self.key, ancestor = self.key.parent())
        ltoLinks = PromiseLink.query(PromiseLink.fromkey == self.key, ancestor = self.key.parent())
        
        ldeleteKeys = [self.key]
        ldeleteKeys.extend([lpromiseLink.key for lpromiseLink in lfromLinks])
        ldeleteKeys.extend([lpromiseLink.key for lpromiseLink in ltoLinks])
        
        ndb.delete_multi(ldeleteKeys)

#     @log
#     def _getResultValues(self):
#         return [lresult.value for lresult in (self.results if self.results else [])]

#     @log
#     def InitSelf(self):
#         # first get all results from 
#         InitPromise(self.key)
                        
    @log
    def ProcessSelf(self):
        ProcessPromise(self.key)
            
    # internal version of resolve, assumes caller will do transactions
    def _resolveInt(self, aResult):
        logging.debug("_resolveInt for %s, in_transaction: %s" % (self.key.id(), ndb.in_transaction()))
        
        self.result = aResult
        
        if isinstance(aResult, Exception):
            self.status = STATUSES.REJECTED
        else:
            self.status = STATUSES.RESOLVED
            
        lputList = [self]

        # need to go to each successor link, and set a resolved value.
        lsuccessorLinks = self._getSuccessorLinks()
        
        for lsuccessorLink in lsuccessorLinks:
            lsuccessorLink.value = aResult
            lputList.append(lsuccessorLink)
        
        # need to go to each successor, and set a resolved value
#         lsuccessors = self._getSuccessors()
#         logging.debug("resolve, successors for %s: %s" % (self.key.id(), [lsuccessor.key.id() for lsuccessor in lsuccessors]))
#         for lpromise in lsuccessors:
#             if lpromise._setResultValue(self.key, aResult):
#                 lputList.append(lpromise)
#             else:
#                 raise Exception("Internal: Not found in own successors")

        #EJO2 logging.debug("lputList: %s" % [litem.key.id() for litem in lputList])
        ndb.put_multi(lputList) #, use_cache=False, use_memcache=False, use_datastore = True)            

#     @log
#     def ResolveSelf(self, aResult):
#         #EJO2 logging.debug("self: %s" % self)
#         #EJO2 logging.debug("result: %s" % aResult)
#         ResolvePromise(self.key, aResult)
        
#     @log
#     def _setResultValue(self, lpredecessorKey, aResultValue):
#         lneedPut = False
#         if self.results:
#             for lresult in self.results:
#                 if lresult.promisekey == lpredecessorKey:
#                     lresult.value = aResultValue
#                     lneedPut = True
#                     break
#         return lneedPut
        
    @log
    def _initKey(self, aKeySpace):
        if not self.key:
            self.key = ndb.Key('KeySpace', aKeySpace, Promise, str(uuid.uuid4()))
            #EJO #EJO2 logging.debug(self.key)
            
    @log
    def _getTaskName(self):
        ltaskName = "Promise-%s-%s" % (self.key.parent().id(), self.key.id())
        #EJO #EJO2 logging.debug(ltaskName)
        return ltaskName
    
    @log
    def _callDeferred(self):
        if self.status == STATUSES.PRE:
            if self.serialisedfuncandargs:
                ltaskArgs, ltaskKwargs = self._getTaskArgs()
                if "_name" in ltaskKwargs:
                    del ltaskKwargs["_name"]
                if "_retry_options" in ltaskKwargs:
                    del ltaskKwargs["_retry_options"]
                
                deferred.defer(
                    WrapDeferred, 
                    self.serialisedfuncandargs, 
                    self._getResultValues(),
                    self.key,
                    self.needresults,
                    self.needresult,
                    # _name=self._getTaskName(), 
                    _transactional = True,
                    _retry_options=TaskRetryOptions(task_retry_limit = 20), 
                    *ltaskArgs,
                    **ltaskKwargs
                )
    
    

# @log
# def InitPromise(aKey):
#     @ndb.transactional(retries = 20)
#     def TransactionalInit():
#         retval = False
#         lpromise = aKey.get()
#         lpredecessors = lpromise._getPredecessors()
#         for lpredecessor in lpredecessors:
#             if lpredecessor.status == STATUSES.RESOLVED or lpredecessor.status == STATUSES.REJECTED:
#                 retval = lpromise._setResultValue(lpredecessor.key, lpredecessor.result) and retval
#         
#         if retval:
#             lpromise.put()
#         
#     TransactionalInit()

def ProcessPromise(aKey, aCheckSuccessors = False):
    lretries = InitRetries()
    
    @ndb.transactional(retries = 20)
    def TransactionalProcess():
        logging.debug("TransactionalProcess, retries = %s" % lretries)
        IncRetries(lretries)
        
        #EJO #EJO2 logging.debug("Enter TransactionProcess, key = %s" % aKey)
        retval = False
        lpromise = aKey.get() #use_cache=False, use_memcache=False, use_datastore = True)
        if lpromise:
            #EJO #EJO2 logging.debug("Got promise, status = %s" % lpromise.status)
            if lpromise.status == STATUSES.PRE:
                if lpromise._hasAllResults():
                    retval = True
                    if lpromise.serialisedfuncandargs:
                        # got a function to call, so do that.
                        lneedStatus = True
                        try:
                            #EJO #EJO2 logging.debug("About to start timeouts for %s" % aKey)
#                            lpromise.StartTimeouts() # now doing this in WrapDeferred
                            #EJO #EJO2 logging.debug("About to call deferred for %s" % aKey)
                            lpromise._callDeferred()
    #                     except TaskAlreadyExistsError, _:
    #                         logging.exception("Error, skipping")
    #                         pass # that's fine, just keep going
                        except Exception, ex:
                            logging.exception("Error, failing")
                            lpromise._resolveInt(ex)
                            lneedStatus = False
                        if lneedStatus:
                            #EJO #EJO2 logging.debug("Setting to UNRESOLVED for %s" % aKey)
                            lpromise.status = STATUSES.UNRESOLVED
                            lpromise.put() #use_cache=False, use_memcache=False, use_datastore = True)
                    else:
                        # no function, pass through.
                        lpromise.StartTimeouts(False) # don't check expiry, this one's never going to timeout, never runs a function
                        lresults = lpromise._getResultValues()
                        # #EJO2 logging.debug("Passthrough pre flatten: lresults=%s" % lresults)
                        lresults = list(maybeflatten(lresults))
                        # #EJO2 logging.debug("Passthrough post flatten: lresults=%s" % lresults)

                        lretval = lresults
                        for lresult in lresults:
                            if isinstance(lresult, Exception):
                                lretval = lresult
                                break

                        # #EJO2 logging.debug("Passthrough: lretval=%s" % lretval)
                        lpromise._resolveInt(lretval)
            elif lpromise.status == STATUSES.UNRESOLVED:
                if lpromise.expiry and lpromise.expiry < datetime.datetime.utcnow():
                    logging.error("Timing out %s" % aKey)
                    lpromise._resolveInt(PromiseTimeoutError("Timed out"))
                    retval = True
            elif lpromise.status == STATUSES.RESOLVED or lpromise.status == STATUSES.REJECTED:
                #EJO #EJO2 logging.debug("checking for cleanup. cleanup = %s, now = %s" % (lpromise.cleanup, datetime.datetime.utcnow()))
                lresult = lpromise.result
                ltimedOut = isinstance(lresult, PromiseTimeoutError)
                if not ltimedOut and lpromise.cleanup and lpromise.cleanup < datetime.datetime.utcnow():
                    #EJO #EJO2 logging.debug("deleting...")
                    # should probably load successors and predecessors and remove self
                    lpromise._delete()
                    #lpromise.key.delete()
        # else no such promise, do nothing
        
        #EJO #EJO2 logging.debug("Leave TransactionProcess, key = %s" % aKey)
        return retval

    #EJO #EJO2 logging.debug("Entered ProcessPromise; key = %s" % aKey)        
    lworked = TransactionalProcess()
    ldidSomething = lworked
    while lworked:
        lworked = TransactionalProcess()
        
    if aCheckSuccessors or ldidSomething:
        lsuccessors = Promise._getSuccessorsByKey(aKey)
        logging.debug("Successors for %s in ProcessPromise: %s" % (aKey.id(), [lsuccessor.key.id() for lsuccessor in lsuccessors]))
        for lsuccessor in lsuccessors:
            lsuccessor.ProcessSelf()
    
    #EJO #EJO2 logging.debug("Left ProcessPromise")        
    return ldidSomething

    
@log
def ResolvePromise(aKey, aResult):
     
    lretries = InitRetries()
    
    @ndb.transactional(retries = 20)
    def DoResolve():
        logging.debug("DoResolve, retries = %s" % lretries)
        IncRetries(lretries)

        retval = False
        #EJO2 logging.debug("Enter DoResolve, key = %s, result = %s" % (aKey, aResult))
        
        lpromise = aKey.get() # use_cache=False, use_memcache=False, use_datastore = True)
        if lpromise:
            lpromise._resolveInt(aResult)
            retval = True
        else:
            raise Exception("Self can't be reloaded")
        #EJO2 logging.debug("Leave DoResolve")
        return retval
        
    retval = DoResolve()
    if retval:
        #EJO #EJO2 logging.debug("globals: %s" % globals().keys())
        #EJO3 logging.info("Resolved %s successfully. About to process self and successors" % aKey)
        ProcessPromise(aKey, True)
            
def WrapThenF(aThenF):
    def thenFWrapper(result, resolve, *args, **kwargs):
        try:
            aThenF(result, *args, **kwargs)
            resolve(None)
        except ProxyFailureError, pfex:
            logging.exception("proxy failed, need retry")
            raise pfex
        except Exception, ex:
            logging.exception("error calling aThenF with %s (%s, %s)" % (result, args, kwargs))
            resolve(ex)
    return thenFWrapper
        
def WrapDeferred(aSerialisedFunctionAndArgs, aResultValues, aPromiseKey, aNeedResults, aNeedResult):
    class WrapResultValue(object):
        def __init__(self, aValue):
            self._value = aValue
            
        @property
        def value(self):
            if self._value and isinstance(self._value, Exception):
                raise self._value
            else:
                return self._value
        
    #EJO #EJO2 logging.debug("Enter WrapDeferred: %s" % aResultValues)
    #lfunction = DeserialiseFunction(aSerialisedFunction)
    
    lfunction, (largs, lkwargs) = DeserialiseFunctionAndArgs(aSerialisedFunctionAndArgs)
    if lfunction:
        lretries = InitRetries()
        
        # start the timeout now
        @ndb.transactional(retries = 20)
        def StartTimeouts():
            logging.debug("StartTimeouts, retries = %s" % lretries)
            IncRetries(lretries)

            lpromise = aPromiseKey.get() # use_cache=False, use_memcache=False, use_datastore = True)
            if lpromise:
                lpromise.StartTimeouts()
                lpromise.put() # use_cache=False, use_memcache=False, use_datastore = True)
            else:
                raise Exception("Can't reload promise in WrapDeferred")
                
        StartTimeouts()
        
        lfixedArgs = []
        if aNeedResults or aNeedResult:
            lresults = [WrapResultValue(lresultValue) for lresultValue in aResultValues]
            if aNeedResults:
                lfixedArgs.append(lresults)
            if aNeedResult:
                lresult = lresults[0] if lresults else None 
                lfixedArgs.append(lresult)
        lresolve = partialf(ResolvePromise, aPromiseKey)
        lfixedArgs.append(lresolve)

        try:
            #EJO #EJO2 logging.debug("about to call function")
            lfixedArgs.extend(largs)
#             lstart = time.clock()
            lfunction(*lfixedArgs, **lkwargs)
#             lend = time.clock()
            
            # pad run time to at least 2 seconds.
#             lduration = lend - lstart
#             if lduration < 0:
#                 lduration = 0
#             if lduration < 1:
#                 time.sleep(1 - lduration)
            #EJO #EJO2 logging.debug("finished call function")
        except ProxyFailureError, ex:
            logging.exception("need retry for proxy")
            raise ex
            
        except Exception, ex:
            logging.exception("error calling function")
            ResolvePromise(aPromiseKey, ex)
    else:
        #EJO #EJO2 logging.debug("Internal: Can't deserialise function in WrapDeferred")
        ResolvePromise(aPromiseKey, Exception("Internal: Can't deserialise function and args in WrapDeferred"))
    #EJO #EJO2 logging.debug("Leave WrapDeferred")


def MapDS(aSuccessF, aProgressF, aPromiseSpaceF, aQuery, aPageSize = 50, aMapF = None, aKeyOnly = False):
    @log
    def GetBatch(resolve, aSubTotal, aCursor):
        try:
            lqry = aQuery
            if aCursor:
                litems, lnextCursor, lmore = lqry.fetch_page(aPageSize, start_cursor = aCursor, keys_only = aKeyOnly)
            else:
                litems, lnextCursor, lmore = lqry.fetch_page(aPageSize, keys_only = aKeyOnly)

            lcount = 0
            if aMapF:
                for litem in litems:
                    try:
                        if aMapF(litem):
                            lcount += 1
                    except:
                        logging.exception("Failed in Map for %s" % litem)
            else:
                lcount = len(litems)
                
            resolve((True, lmore, lnextCursor, aSubTotal + lcount))
        except Exception, _:
            logging.exception("Exception")
            resolve((False, True, aCursor, aSubTotal))
        
    @log
    def GotBatch(result):
        lsuccess, lmore, lcursor, lsubtotal = result.value
        if lsuccess and not lmore:
            aSuccessF(lsubtotal)
        else:
            aProgressF(lsubtotal)
            lpromise = aPromiseSpaceF().when(GetBatch, lsubtotal, lcursor)
            lpromise.then(GotBatch)
            
    lpromise = aPromiseSpaceF().when(GetBatch, 0, None)
    lpromise.then(GotBatch)
    
def ProcessAllPromises(aSuccessF = None, aProgressF=None, aPromiseSpaceF=None):
    lsuccessF = aSuccessF if aSuccessF else lambda x: None
    lprogressF = aProgressF if aProgressF else lambda x: None
    lpromiseSpaceF = aPromiseSpaceF if aPromiseSpaceF else lambda: PromiseSpace()
    
    def ProcessPromiseF(aPromise):
        deferred.defer(ProcessPromise, aPromise.key)
        return True
        
    MapDS(lsuccessF, lprogressF, lpromiseSpaceF, Promise.query(), aPageSize=100, aMapF = ProcessPromiseF)

# ****************************************************
#
# Serialisation routines
#
# ****************************************************






gfunctions = {}

@log
def DeserialiseFunction(aSerialisedFunction):
    lserialisedFunc, lserialisedClosureValues, lmoduleName = pickle.loads(aSerialisedFunction)
    
    #EJO2 logging.debug("lmoduleName: %s" % lmoduleName)
    
    logging.debug("moduleName: %s" % lmoduleName)
    logging.debug("len of sys.modules: %s" % len(sys.modules))
    lmodule = sys.modules.get(lmoduleName)

    if lmodule:
        lglobals = lmodule.__dict__
        lglobals["gfunctions"] = gfunctions
    else:
        __import__(lmoduleName)
        lmodule = sys.modules.get(lmoduleName)
    
        if lmodule:
            lglobals = lmodule.__dict__
            lglobals["gfunctions"] = gfunctions
        else:
            raise Exception("No module for lmoduleName (%s) in sys.modules" % lmoduleName)
    
    def make_proxy(f_hash):
        def f_proxy(*args, **kwargs):
            global gfunctions
            f = gfunctions.get(f_hash)
            if not f:
                raise ProxyFailureError("couldn't get function for hash %s from gfunctions" % f_hash)
            f(*args, **kwargs)
            
        return f_proxy
        
    def make_cell(value):
        return (lambda x: lambda: x)(value).func_closure[0]
    
    def DeserialiseClosureValues(aSerialisedClosureValues):
        global gfunctions
        
        lclosure = None
        if aSerialisedClosureValues:
            lclosureValues = []
            for item in aSerialisedClosureValues:
                ltype = len(item)
                if ltype == 1:
                    #lclosureValues.append(pickle.loads(item[0]))
                    ldeserialiseItem = DeserialiseItem(item[0])
                    lclosureValues.append(ldeserialiseItem)
                    #EJO2 logging.debug("Standard Item: %s" % (ldeserialiseItem))
                elif ltype == 2:
                    lfunction = make_proxy(item[0])
                    #EJO2 logging.debug("Made proxy for function with hash %s" % item[0])
                    lclosureValues.append(lfunction)
                elif ltype == 4:
                    lfuncglobals = sys.modules[item[3]].__dict__
                    lfuncglobals["gfunctions"] = gfunctions
                    lfunction = types.FunctionType(marshal.loads(item[1]), lfuncglobals, closure=DeserialiseClosureValues(item[2]))
                    gfunctions[item[0]] = lfunction
                    #EJO2 logging.debug("Added function with hash %s to gfunctions" % item[0])
                    lclosureValues.append(lfunction)
            lclosure = tuple([make_cell(lvalue) for lvalue in lclosureValues])
        return lclosure
            
    lfunctionCode = marshal.loads(lserialisedFunc)
    lclosure = DeserialiseClosureValues(lserialisedClosureValues)
    lfunction = types.FunctionType(lfunctionCode, lglobals, closure=lclosure)
    return lfunction
        
@log
def SerialiseFunction(aFunction):
    if not aFunction or not hasattr(aFunction, "func_code"):
        raise Exception ("First argument required, must be a function")
    
    lfunctionHashes = set()
    
    #EJO #EJO2 logging.debug("Function Name: %s" % aFunction.__name__)
    
    def SerialiseClosureValues(aClosure, aParentIndices = []):
        #EJO #EJO2 logging.debug("Closure: %s" % repr(aClosure))
        lserialiseClosureValues = []
        if aClosure:
            lclosureValues = [lcell.cell_contents for lcell in aClosure]
            
            lserialiseClosureValues = []
            for index, litem in enumerate(lclosureValues):
                lfullIndex = list(aParentIndices)
                lfullIndex.append(index)
                
                if isinstance(litem, types.FunctionType):
                    #EJO #EJO2 logging.debug("(%s) Begin Marshalling Function %s" % (lfullIndex, litem.__name__))
                    lhash = hash(litem)
                    if lhash in lfunctionHashes:
                        lserialiseClosureValues.append([lhash, None])
                    else:
                        lfunctionHashes.add(lhash)
                        lserialiseClosureValues.append([lhash, marshal.dumps(litem.func_code), SerialiseClosureValues(litem.func_closure, lfullIndex), litem.__module__])
                    #EJO #EJO2 logging.debug("(%s) End Marshalling Function %s" % (lfullIndex, litem.__name__))
                else:
                    #EJO #EJO2 logging.debug("(%s) Begin Marshalling Item %s" % (lfullIndex, litem))
#                     lserialiseClosureValues.append([pickle.dumps(litem)])
                    lserialiseClosureValues.append([SerialiseItem(litem)])
                    #EJO #EJO2 logging.debug("(%s) End Marshalling Item %s" % (lfullIndex, litem))
        return lserialiseClosureValues
    
    lmarshalledFunc = marshal.dumps(aFunction.func_code)
    lserialiseClosureValues = SerialiseClosureValues(aFunction.func_closure)
    lmoduleName = aFunction.__module__
    
    lcombined = (lmarshalledFunc, lserialiseClosureValues, lmoduleName)
    
    retval = pickle.dumps(lcombined)
    
    return retval


@log
def SerialiseArgs(*args, **kwargs):
    return pickle.dumps({
        "args": [SerialiseItem(litem) for litem in args],
        "kwargs": {lkey: SerialiseItem(lvalue) for lkey, lvalue in kwargs.iteritems()}
    })

@log
def DeserialiseArgs(aSerialisedArgs):
    lserDict = pickle.loads(aSerialisedArgs)
    largs = [DeserialiseItem(litem) for litem in lserDict["args"]]
    lkwargs = {lkey: DeserialiseItem(lvalue) for lkey, lvalue in lserDict["kwargs"].iteritems()}
    return (largs, lkwargs)

@log
def SerialiseItem(aItem):
    if isinstance(aItem, types.FunctionType):
        return ("f", SerialiseFunction(aItem))
    else:
        return ("i", pickle.dumps(aItem))
                
@log
def DeserialiseItem(aSerialisedItem):
    retval = None
    if isinstance(aSerialisedItem, tuple) and len(aSerialisedItem) == 2:
        if aSerialisedItem[0] == "f":
            retval = DeserialiseFunction(aSerialisedItem[1])
        elif aSerialisedItem[0] == "i":
            retval = pickle.loads(aSerialisedItem[1])
    return retval

@log
def SerialiseFunctionAndArgs(aFunction, *args, **kwargs):
    lserialisedFunction = SerialiseFunction(aFunction)
    lserialisedArgs = SerialiseArgs(*args, **kwargs)
    return pickle.dumps((lserialisedFunction, lserialisedArgs))

@log
def DeserialiseFunctionAndArgs(aSerialisedFunctionAndArgs):
    lserialisedFunction, lserialisedArgs = pickle.loads(aSerialisedFunctionAndArgs)
    return DeserialiseFunction(lserialisedFunction), DeserialiseArgs(lserialisedArgs)

def maybeflatten(aInput):
    for item in aInput:
        if isinstance(item, list):
            for item2 in item:
                yield item2
        else:
            yield item


def InitRetries():
    return [0]

def IncRetries(retries):
    if retries[0] > 0:
        time.sleep(4 * ((random.randrange(retries[0])+1)) * 0.125)
    retries[0] += 1
