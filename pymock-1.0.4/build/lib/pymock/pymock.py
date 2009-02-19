#!/usr/local/bin/python
#

"""
Copyright 2006 Jeff Younker 

Redistribution and use in source and binary forms, with or without modification, are
permitted provided that the following conditions are met:

   1. Redistributions of source code must retain the above copyright notice, this list of
       conditions and the following disclaimer.
   2. Redistributions in binary form must reproduce the above copyright notice, this
       list of conditions and the following disclaimer in the document ation and/or
      other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY JEFF YOUNKER ``AS IS'' AND ANY
EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITE
TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL
THE FREEBSD PROJECT OR CONTRIBUTORS BE LIABLE FOR ANY
DIR ECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF
USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH
DAMAGE.
"""



import sys
import traceback
from unittest import TestCase

class RecordedCallsWereNotReplayedCorrectly(Exception):
    pass


class PlaybackFailure(Exception):
    pass


class IllegalPlaybackRecorded(Exception):
	pass


class PyMockTestCase(TestCase):
	
	def setUp(self):
		self.controller = Controller()
		
	def tearDown(self):
		self.controller.restore()

	def __getattr__(self, name):
		return getattr(self.controller, name)
	
		
class Controller(object):
	
	RECORD = 1
	PLAYBACK = 2
	
	isPlayingBack = property(lambda self: self.mode == self.PLAYBACK)
	isRecording = property(lambda self: self.mode == self.RECORD)
	
	def __init__(self):
		self.mode = self.RECORD
		self.actions = ActionCache()
		self.actionUnderConstruction = None
		self.preservedValues = []
	    
	    
	def mock(self, klass=object):
	    return MockObject(self, klass)


	def override(self, obj, field, value=None):
		if value == None:
			value = self.mock()
		self.preservedValues.append(FunctionOverride(obj, field, getattr(obj, field)))
		setattr(obj, field, value)


	def overrideProperty(self, obj, field):
		prop = property(lambda x: self.getField(x, field),
					 lambda x, value: self.setField(x, field, value),
					 lambda x: self.getField(x, field))
		self.preservedValues.append(ClassOverride(obj, obj.__class__))
		self.attachObjectToProxyClass(obj)
		setattr(obj.__class__, field, prop)


	def proxyClassForObject(self, obj):
		 return type('Proxied' + obj.__class__.__name__, (), dict(obj.__class__.__dict__))

	
	def attachObjectToProxyClass(self, obj):
		proxyClass = self.proxyClassForObject(obj)
		obj.__class__ = proxyClass

		
	def getField(self, obj, field):
		accessPath = (repr(obj), 'propertyOp(%s)' % field)
		returnObject = MockObject(self, obj, (repr(self), accessPath + (':',)))
		getAttribute = GetAttributeAction(field, accessPath, returnObject)
		return self.recordOrPlayback(getAttribute)

	
	def setField(self, obj, field, value):
		accessPath = (repr(obj), 'propertyOp(%s)' % field)
		setAttribute = SetAttributeAction(None, field, accessPath, value)
		return self.recordOrPlayback(setAttribute)

		
	def restore(self):
		self.preservedValues.reverse()
		for override in self.preservedValues:
			override.restore()	
	
	
	def replay(self):
	    self.mode = self.PLAYBACK
	
	
	def verify(self):
		for x in self.actions:
			if not x.hasBeenPlayedBack:
				raise RecordedCallsWereNotReplayedCorrectly()


	def recordOrPlayback(self, action):
		if self.isPlayingBack:
			return self.playback(action)
		else:
			return self.record(action)
	
	
	def playback(self, action):
		recordedAction = self.actions.get(action)
		if recordedAction == None:
			raise PlaybackFailure("No further actions defined")
		elif not action == recordedAction:
			raise PlaybackFailure("Inappropriate action")
		else:
			exprValue = recordedAction.playback()
			if recordedAction.isReadyForRemoval:
				self.actions.pop(recordedAction)
			return exprValue

			
	def record(self, action):
		if self.actions.contains(action) and self.actions.get(action).playbackPolicy.hasUnlimitedPlaybacks:
			raise IllegalPlaybackRecorded("You cannot record additional playbacks when you have defined an unlimited playback")
		else:
			self.actions.append(action)
			self.actionUnderConstruction = action
			return action.record()


	def generator(self, functionCall=None, yieldValues=[], terminalException=None):
		"""Turn the last function call into a generator"""
		functionCall = self.actionUnderConstruction
		generatorCall = GeneratorAction.fromAction(functionCall)
		self.actions.pop(functionCall)
		self.record(generatorCall)
		for x in yieldValues:
			self.setReturn(x)
		if terminalException != None:
			self.setException(terminalException)
		
	
	def setReturn(self, value):
		self.actionUnderConstruction.value = value


	def expectAndReturn(self, expr, value):
		self.setReturn(value)
		
		
	def setException(self, exc):
		self.actionUnderConstruction.throws = exc


	def expectAndRaise(self, expr, exc):
		self.setException(exc)
		

	def setCount(self, exactly=1):
		self.actionUnderConstruction.playbackPolicy = FixedCountPolicy(exactly)


	def atLeast(self, limit=1):
		self.actionUnderConstruction.playbackPolicy = MinimumPlaybackPolicy(limit)

	
	def zeroOrMore(self):
		self.atLeast(0)


	def oneOrMore(self):
		self.atLeast(1)


class FunctionOverride(object):
	
	def __init__(self, obj, fieldName, originalValue):
		self.obj = obj
		self.fieldName = fieldName
		self.originalValue = originalValue
	
	def restore(self):
		#self.obj.__dict__[self.fieldName] = self.originalValue
		setattr(self.obj, self.fieldName, self.originalValue)


class ClassOverride(object):
	
	def __init__(self, obj, originalClass):
		self.obj = obj
		self.originalClass = originalClass
	
	def restore(self):
		self.obj.__class__ = self.originalClass
		
	


    
class MockObject(object):
    
	def __init__(self, controller, klass, accessPath=None):
		self.__controller = controller
		if accessPath == None:
			self.__accessPath = (self, )
		else:
			self.__accessPath = accessPath
	
	
	def __setattr__(self, name, value):
		if name == '_MockObject__controller' or name == '_MockObject__accessPath':
			self.__dict__[name] = value
			return
		else:
			self.__controller.recordOrPlayback(SetAttributeAction(self, name, self.__accessPath, value))
	        

	def __getattr__(self, name):
		if name == '_MockObject__controller' or name == '_MockObject__accessPath':
			return self.__dict__[name]
		returnObject = MockObject(self.__controller, object, self.__accessPath + (name,))
		getAttribute = GetAttributeAction(name, self.__accessPath, returnObject)
		return self.__controller.recordOrPlayback(getAttribute)


	def __call__(self, *pargs, **vargs):
		accessPath = self.__accessPath + ('()',)
		returnObject = MockObject(self.__controller, object, accessPath)
		functionCall = FunctionCallAction(accessPath, pargs, vargs, returnObject)
		return self.__controller.recordOrPlayback(functionCall)

	
	def __mockfunc__(self, accessElt, pargs):
		accessPath = self.__accessPath + (accessElt,)
		returnObject = MockObject(self.__controller, object, accessPath)
		functionCall = FunctionCallAction(accessPath, pargs, {}, returnObject)
		return self.__controller.recordOrPlayback(functionCall)


	# len(x) requires an integer result under all circumstances... damn python
	def __len__(self):
		accessPath = self.__accessPath + ('len()',)
		functionCall = FunctionCallAction(accessPath, (self, ), {}, 0)
		return self.__controller.recordOrPlayback(functionCall)


	def __iter__(self):
		accessPath = self.__accessPath + ('__iter__()', )
		generatorCall = GeneratorAction(accessPath, (), ())
		return self.__controller.recordOrPlayback(generatorCall)


	__getitem__ = lambda self, index:  self.__mockfunc__('[x]', (self, index))

	__setitem__ = lambda self, index, value:  self.__mockfunc__('[x]=y', (self, index, value))

	__contains__ = lambda self, value:  self.__mockfunc__('x in y', (self, value))


class MockProperty(object):
	"""Used to override single properties in a non-mock object"""
	
	def __init__(self, controller, mockObject):
		self.controller = controller
		self.mockObject = mockObject
		



class BaseAction(object):
    
	def __init__(self, key):
	    """Field description"""
	    self.key = key
	    self.playbackPolicy = FixedCountPolicy(1)
	    self._throws = None

	throws = property(lambda self: self._throws, lambda self, v: self.__dict__.__setitem__('_throws', v))
	    
	    
	def __eq__(self, x):
		"""Equality based on fields and type"""
		if None == x:
			return False
		else:
			return self.key == x.key and \
					self.__class__ == x.__class__
	
	
	def __str__(self):
		return str((self.key, self.__class__))
	
	
	def playback(self):
		self.playbackPolicy.playback()
		if self.throws:
			raise self.throws


	def record(self):
		return self

	
	isReadyForRemoval = property(lambda self: self.playbackPolicy.isReadyForRemoval)
	hasBeenPlayedBack = property(lambda self: self.playbackPolicy.hasBeenPlayedBack)

	    	

class SetAttributeAction(BaseAction):
    
	def __init__(self, mockObject, field, key, value):
	    """Set an attribute"""
	    super(SetAttributeAction, self).__init__(key + (field, ))
	    self.field = field
	    self.value = value
	
	
	def __eq__(self, x):
		"""Equality based on both slot identity and value"""
		return super(SetAttributeAction, self).__eq__(x) and self.value == x.value


	def __str__(self):
		return "%s = %s" % (str(self.field), str(self.value))


	def record(self):
		return self
	


class GetAttributeAction(BaseAction):
	
	def __init__(self, field, key, defaultValueMockObject):
		"""Get an attribute with no method specified"""
		super(GetAttributeAction, self).__init__(key + (field,))
		self.field = field
		self.value = defaultValueMockObject
		
	
	def playback(self):
		super(GetAttributeAction, self).playback()
		return self.value


	def record(self):
		return self.value



class CallAction(BaseAction):

	def __init__(self, key, pargs, vargs):
		super(CallAction, self).__init__(key)
		self.pargs = pargs
		self.vargs = vargs

	
	def __eq__(self, x):
		return isinstance(x, CallAction) and \
				self.key == x.key and \
				self.pargs == x.pargs and \
				self.vargs == x.vargs

	

class FunctionCallAction(CallAction):
	
	def __init__(self, key, pargs, vargs, mockObject):
		super(FunctionCallAction, self).__init__(key, pargs, vargs)
		self.value = mockObject


	def playback(self):
		super(FunctionCallAction, self).playback()
		return self.value


	def record(self):
		return self.value
	


class GeneratorAction(CallAction):
	
	def __init__(self, key, pargs, vargs):
		super(GeneratorAction, self).__init__(key, pargs, vargs)
		self.values = []


	@classmethod
	def fromAction(cls, action):
		generatorAction = GeneratorAction(action.key, action.pargs, action.vargs)
		generatorAction.playbackPolicy = action.playbackPolicy
		return generatorAction
	

	def record(self):
		return None
	
					
	def playback(self):
		super(GeneratorAction, self).playback()
		return self.playbackGenerator()

	
	def playbackGenerator(self):
		for (value, exc) in self.values:
			if exc == None:
				yield value
			else:
				raise exc


	def assertRecordingIsNotComplete(self):
		if  len(self.values):
			(value, exc) = self.values[-1]
			if exc != None:
				raise IllegalPlaybackRecorded


	def setValue(self, x):
		self.assertRecordingIsNotComplete()
		self.values.append((x, None))


	def setException(self, exc):
		self.assertRecordingIsNotComplete()
		self.values.append((None, exc))


	value = property(lambda self: None, lambda self, x: self.setValue(x))

	throws = property(lambda self: None, lambda self, x: self.setException(x))




class FixedCountPolicy(object):
	
	def __init__(self, count=1):
		self.remaining = count
		
	hasBeenPlayedBack = property(lambda x: x.remaining == 0)
	isReadyForRemoval = property(lambda x: x.remaining == 0)
	hasUnlimitedPlaybacks = False;


	def playback(self):
		if self.remaining == 0:
			raise RecordedCallsWereNotReplayedCorrectly()
		else:
			self.remaining = self.remaining - 1

	

class MinimumPlaybackPolicy(object):
	
	def __init__(self, count=1):
		self.remaining = count
		
	hasBeenPlayedBack = property(lambda x: x.remaining == 0)
	isReadyForRemoval = False
	hasUnlimitedPlaybacks = True;


	def playback(self):
		self.remaining = max(0, self.remaining - 1)


class ActionCache(object):

    def __init__(self):
        self.actions = {}
    
    
    def __len__(self):
    	return len(self.actions)
    
    
    def contains(self, action):
        return self.actions.has_key(action.key)

        
    def append(self, action):
        if not self.contains(action):
            self.actions[action.key] = []
        self.actions[action.key].append(action)
    
    
    def get(self, action, default=None):
        if not self.contains(action):
            return None
        else:
            return self.actions[action.key][0]
    
    
    def pop(self, action):
        if not self.contains(action):
            return None
        else:
            queue = self.actions[action.key]
            if len(queue) == 1:
                del self.actions[action.key]
            else:
                self.actions[action.key] = queue[1:]
            return queue[0]

           
    def __iter__(self):
    	for queue in self.actions.values():
    		for x in queue:
    			yield x

     
     

    
