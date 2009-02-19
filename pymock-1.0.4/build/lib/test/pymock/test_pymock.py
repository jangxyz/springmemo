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

import os
from sets import Set
from unittest import makeSuite, TestCase, TestSuite, TextTestRunner

from pymock import Controller, PlaybackFailure, RecordedCallsWereNotReplayedCorrectly,	\
	IllegalPlaybackRecorded, PyMockTestCase
from pymock.pymock import BaseAction, SetAttributeAction, ActionCache, FixedCountPolicy, \
	FunctionCallAction, GetAttributeAction, MinimumPlaybackPolicy, GeneratorAction, \
	FunctionOverride, ClassOverride

class KlassBeingMocked(object):
    
	pass


	
class TestPyMockUseCases(TestCase):
    
	def testControllerAndMockFactory(self):
	    """Test factory for creating mock objects"""
	    
	    c = Controller()
	    x = c.mock(KlassBeingMocked)
	    self.failIf(x == None)
	    
	
	def testAttributeAssignmentIsIntercepted(self):
	    """Attibute assignment should be intercepted"""
	    
	    c = Controller()
	    x = c.mock(KlassBeingMocked)
	    x.w = 5
	    c.replay()
	    try:
	        x.w
	        self.fail()
	    except PlaybackFailure, e:
	        pass
	
	
	def testUnusedAttributeAssignmentCanBeVerified(self):
	    """Ensure that unused calls cause verification failure"""
	    
	    c = Controller()
	    x = c.mock(KlassBeingMocked)
	    x.w = 5
	    c.replay()
	    self.failUnlessRaises(RecordedCallsWereNotReplayedCorrectly, c.verify)
	
	
	def testAttributeAssignmentCanBePlayedBack(self):
	    """Attibute assignment should be intercepted"""
	    
	    c = Controller()
	    x = c.mock(KlassBeingMocked)
	    x.w = 5
	    x.w = 6
	    c.replay()
	    x.w = 5
	
	
	def testUsedAttributeAssignmentCanBeVerified(self):
	    """Ensure that used calls will not cause verification failure"""        
	    c = Controller()
	    x = c.mock(KlassBeingMocked)
	    x.w = 5
	    x.h = 3
	    c.replay()
	    x.h = 3
	    x.w = 5
	    c.verify()
	
	
	def testSetAttributeRecordsField(self):
	    """Ensure setting an attribute is correctly recorded"""
	
	    c = Controller()
	    x = c.mock(KlassBeingMocked)
	    x.w = 5
	    self.failUnless(len(c.actions) == 1)
	    action = c.actions.get(BaseAction((x,'w')))
	    self.failUnless(action.field == 'w')
	    self.failUnless(action.value == 5)
	
	
	def testPlaybackFailsWithIncorrectValues(self):
	    """Ensure playing back incorrect values results in an error"""
	
	    c = Controller()
	    x = c.mock(KlassBeingMocked)
	    x.w = 5
	    c.replay()
	    try:
	        x.w = 4
	        self.fail()
	    except PlaybackFailure, e:
	        pass
	
	
	def testSpecifyingMultiCounts(self):
		"""Specify multi counts for a single argument"""
	
		c = Controller()
		x = c.mock(KlassBeingMocked)
		x.w = 5
		c.setCount(2)
		c.replay()
		x.w = 5
		x.w = 5
		try:
			x.w = 5
			self.fail()
		except PlaybackFailure, e:
			pass


	def testSetCountZeroOrMoreRaisesErrorOnNextRecord(self):
		"""Setting an unlimited count causes subsequent records to fail"""
		c = Controller()
		x = c.mock(KlassBeingMocked)
		x.w = 5
		c.zeroOrMore()
		try:
			x.w = 6
			self.fail()
		except IllegalPlaybackRecorded, e:
			pass
		c.verify()
		

	def testSetCountOneOrMoreRaisesErrorOnNextRecord(self):
		"""Setting an unlimited count causes subsequent records to fail"""
		c = Controller()
		x = c.mock(KlassBeingMocked)
		x.w = 5
		c.oneOrMore()
		try:
			x.w = 6
			self.fail()
		except IllegalPlaybackRecorded, e:
			pass
		
    
	def testUndefinedPlaybackRaisesException(self):
		"""Playback failure should raise an exception"""	
		c = Controller()
		x = c.mock(KlassBeingMocked)
		c.replay()
		try:
			x.w = 5
			self.fail()
		except PlaybackFailure, e:
			pass


	def testGetattrWithNoReturnValueSpecified(self):
		"""Getattr with no return value specified"""
		c = Controller()
		x = c.mock(KlassBeingMocked)
		x.g
		c.replay()
		self.failIf(x.g == None)
		try:
			x.g
			self.fail()
		except PlaybackFailure, e:
			pass


	def testGetattrWithReturnValueSpecified(self):
		"""Getattr with return value specified"""
		c = Controller()
		x = c.mock(KlassBeingMocked)
		x.g
		c.setReturn(8)
		c.replay()
		self.failUnless(x.g == 8)
		
	
	def testFunctionCallWithNoReturnValueSpecified(self):
		"""Function call with no return value specified"""
		c = Controller()
		x = c.mock(KlassBeingMocked)
		x.g(3, 4)
		c.replay()
		x.g(3, 4)
		c.verify()


	def testFunctionCallWithMismatchedArguments(self):
		"""Function call with mismatched arguments"""
		c = Controller()
		x = c.mock(KlassBeingMocked)
		x.g(3, 4)
		x.h()
		x.i(8, v1=4, v2=3)
		c.replay()
		self.failUnlessRaises(PlaybackFailure, x.g, 5, 3)
		self.failUnlessRaises(PlaybackFailure, x.h, 2)
		self.failUnlessRaises(PlaybackFailure, x.i, 8, v1=4, v2=5)


	def testFunctionCalReturnValues(self):
		"""Ensure function call return values get set"""
		c = Controller()
		x = c.mock(KlassBeingMocked)
		x.g.h(3, 4)
		c.setReturn(5)
		x.g.h(6, 7)
		c.setReturn(8)
		c.replay()
		self.failUnless(x.g.h(3, 4) == 5)
		self.failUnless(x.g.h(6, 7) == 8)


	def testGettingFunctionOnceAndCallingMultipleTimes(self):
		"""Get a function once and call it multiple times"""
		c = Controller()
		x = c.mock(KlassBeingMocked)
		h = x.g.h
		h(3, 4)
		c.setReturn(5)
		h(6, 7, 8)
		c.setReturn(9)
		c.replay()
		h = x.g.h
		self.failUnless(h(3, 4) == 5)
		self.failUnless(h(6, 7, 8) == 9)


	def testExceptionRaisedByFunctions(self):
		"""Ensure that function calls play back exceptions"""
		c = Controller()
		x = c.mock(KlassBeingMocked)
		x.g.h(3, 4)
		c.setException(Exception)
		c.replay()
		self.failUnlessRaises(Exception, x.g.h, 3, 4)


	def testExceptionRaisedByGetattr(self):
		"""Ensure that getattr plays back exceptions"""
		c = Controller()
		x = c.mock(KlassBeingMocked)
		x.g
		c.setException(Exception)
		c.replay()
		try:
			x.g
			self.fail()
		except Exception, e:
			pass
		
		
	def testExceptionRaisedBySetattr(self):
		"""Ensure that setattr returns function calls"""
		c = Controller()
		x = c.mock(KlassBeingMocked)
		x.g = 6
		c.setException(Exception)
		c.replay()
		try:
			x.g = 6
			self.fail()
		except Exception, e:
			pass


	def testAtLeastSetsLimit(self):
		"""Ensure that setattr returns function calls"""
		c = Controller()
		x = c.mock(KlassBeingMocked)
		x.g = 6
		c.atLeast(2)
		c.replay()
		x.g = 6
		self.failUnlessRaises(Exception, c.verify)
		x.g = 6
		c.verify()
		
	
	def test__foo__MethodsWorkWithSyntacticalFormAndMethodCallInterchangably(self):
		"""Ensure that __foo__ methods work with their special syntax forms interchangaly"""
		c = Controller()
		x = c.mock(KlassBeingMocked)
		x.g.__getitem__(5)
		c.setReturn(6)
		x.h.__getitem__(7)
		c.setReturn(8)
		c.replay()
		self.failUnless(x.g[5] == 6)
		self.failUnless(x.h.__getitem__(7) == 8)


	def testGetItem(self):
		"""Ensure that __getitem__ works"""
		c = Controller()
		x = c.mock(KlassBeingMocked)
		x.g[5]
		c.setReturn(6)
		c.replay()
		self.failUnless(x.g[5] == 6)
		c.verify()
		

	def testSetItem(self):
		"""Ensure that __setitem__ works"""
		c = Controller()
		x = c.mock(KlassBeingMocked)
		x.g[6] = 7
		c.replay()
		x.g[6] = 7
		c.verify()
		

	def testLen(self):
		"""Ensure that __len__ works"""
		c = Controller()
		x = c.mock(KlassBeingMocked)
		k = len(x)
		c.setReturn(5)
		c.replay()
		self.failUnless(len(x) == 5)
		c.verify()


	def testIter(self):
		"""Ensure that __iter__ records and replays values"""
		c = Controller()
		x = c.mock()
		x.__iter__()
		c.setReturn(1)
		c.setReturn(2)
		c.replay()
		self.assertTrue([k for k in x] == [1, 2])


	def testIterWithException(self):
		"""Ensure that __iter__ records and replays exceptions"""
		c = Controller()
		x = c.mock()
		x.__iter__()
		c.setReturn(1)
		c.setException(Exception)
		c.replay()
		i = x.__iter__()
		self.failUnless(i.next() == 1)
		self.failUnlessRaises(Exception, i.next)


        
	def testIterDoesNotAllowRecordingAfterAnException(self):
		"""Ensure that __iter__ records and replays exceptions"""
		c = Controller()
		x = c.mock()
		x.__iter__()
		c.setReturn(1)
		c.setException(Exception)
		self.failUnlessRaises(Exception, c.setReturn, 2)
		self.failUnlessRaises(Exception, c.setException, Exception)


	def testEnsureThatContainsWorks(self):
		"""Verify that __contains__ is implemented"""
		c = Controller()
		x = c.mock()
		1 in x
		c.setReturn(True)
		2 in x
		c.setReturn(False)
		c.replay()
		self.failUnless(1 in x)
		self.failIf(2 in x)


	def testExplicitGeneratorUsage(self):
		"""Check operation of explicit generators using discrete settings"""
		c = Controller()
		x = c.mock()
		x.g(8, 9)
		c.generator()
		c.setReturn(10)
		c.setReturn(11)
		c.replay()
		self.failUnless([k for k in x.g(8, 9)] == [10, 11])


	def testExplicitGeneratorExecptionUsage(self):
		"""Check exception raising with explicit generators using discrete settings"""
		c = Controller()
		x = c.mock()
		x.g(8, 9)
		c.generator()
		c.setReturn(10)
		c.setException(Exception("bogus"))
		c.replay()
		g = x.g(8, 9)
		self.failUnless(g.next() == 10)
		self.failUnlessRaises(Exception, g.next)


	def testExplicitGeneratorConvenienceFunctionUsage(self):
		"""Check normal operation with explicit generators using  """
		c = Controller()
		x = c.mock()
		c.generator(x.g(8, 9), [10, 11])
		c.replay()
		self.failUnless([k for k in x.g(8, 9)] == [10, 11])


	def testExplicitGeneratorConvenienceFunctionExceptionUsage(self):
		"""Check explicit generators using compact specification"""
		c = Controller()
		x = c.mock()
		c.generator(x.g(8, 9), [10], Exception("bogus"))
		c.replay()
		g = x.g(8, 9)
		self.failUnless(g.next() == 10)
		self.failUnlessRaises(Exception, g.next)


	def testExpectAndReturn(self):
		"""Check expect and return"""
		c = Controller()
		x = c.mock()
		c.expectAndReturn(x.g(8, 9), 5)
		c.replay()
		self.failUnless(x.g(8, 9) == 5)
		c.verify()


	def testExpectAndRaise(self):
		"""Check expect and raise"""
		c = Controller()
		x = c.mock()
		c.expectAndRaise(x.g(8, 9), Exception())
		c.replay()
		try:
			x.g(8, 9)
			self.fail()
		except Exception, e:
			pass
		c.verify()


class TestOverrideContainer(TestCase):
	
	def testOverrideOfOneItem(self):
		"""Verify override stores and replays"""
		c = Controller()
		x = KlassBeingMocked()
		x.f = 38
		c.override(x, 'f', 5)
		self.failUnless(x.f == 5)
		c.restore()
		self.failUnless(x.f == 38)

	def testOverrideModule(self):
		"""Verify that overriding a module works"""
		c = Controller()
		c.override(os, 'getsid', classmethod(c.mock()))
		c.restore()
		

	def testOverrideOfTwoItems(self):
		"""Verify override stores and replays for multiple items"""
		c = Controller()
		x = KlassBeingMocked()
		y = KlassBeingMocked()
		x.f = 38
		y.g = 39
		c.override(x, 'f', 5)
		c.override(y, 'g', 6)
		self.failUnless(x.f == 5)
		self.failUnless(y.g == 6)
		c.restore()
		self.failUnless(x.f == 38)
		self.failUnless(y.g == 39)


	def testOverrideWithImplicitMock(self):
		"""Verify override stores and replays"""
		c = Controller()
		x = KlassBeingMocked()
		x.f = 38
		c.override(x, 'f')
		x.f(35)
		c.replay()
		self.failUnlessRaises(Exception, c.verify)
		x.f(35)
		c.verify()
		c.restore()
		self.failUnless(x.f == 38)

		
	def testOverrideFieldWithSetAndGetAndDel(self):
		"""Verify overriding fields and performing operations on them"""
		c = Controller()
		x = KlassBeingMocked()
		x.f = 38
		c.overrideProperty(x, 'f')
		m = x.f
		c.setReturn(5)
		x.f = 74
		del x.f
		c.replay()
		self.failUnlessRaises(Exception, c.verify)
		self.failUnless(x.f == 5)
		x.f = 74
		del x.f
		c.verify()
		c.restore()
		self.failUnless(x.f == 38)
 
 
	def testOverridenPropertiesCheckOrdering(self):
		"""Verify overriding fields detects ordering issues"""
		c = Controller()
		x = KlassBeingMocked()
		x.f = 38
		c.overrideProperty(x, 'f')
		m = x.f
		c.setReturn(5)
		x.f = 74
		c.replay()
		self.failUnlessRaises(Exception, c.verify)
		try:
			x.f = 74
			self.fail()
		except PlaybackFailure, e:
			pass
		c.restore()
		self.failUnless(x.f == 38)	


	def testSettingClassMethod(self):
		c = Controller()
		class MethodTarget(object):
			def m(self):
				pass
		mt = MethodTarget()
		c.override(mt, 'm', lambda(x): x)

	
class TestFunctionOverride(TestCase):
	
	def testRestore(self):
		class RestorationTarget(object):
			m = 1
		rt = RestorationTarget()
		fo = FunctionOverride(rt, 'm', 2)
		fo.restore()
		self.failUnless(rt.m == 2)


class TestClassOverride(TestCase):
	
	def testRestore(self):
		class RestorationTarget(object):
			pass
		rt = RestorationTarget()
		class RestoredTarget(object):
			pass
		co = ClassOverride(rt, RestoredTarget)
		co.restore()
		self.failUnless(rt.__class__ == RestoredTarget)
		
		
		
class TestOverrideProperty(TestCase):
	
	def testPropertyOverridePlayback(self):
		c = Controller()
		op = PropertyOverride(c)
		

		
class TestControllerInternals(TestCase):
    
	def testPlayModeAndSwitches(self):
	    """Verify that the replay switch works"""
	    c = Controller()
	    self.failUnless(c.isRecording)
	    self.failIf(c.isPlayingBack)
	    c.replay()
	    self.failIf(c.isRecording)
	    self.failUnless(c.isPlayingBack)

	
	def testPlayback(self):
		"""Ensure that the playback operates correctly"""
		c = Controller()
		action = BaseAction('x')
		c.actions.append(action)
		c.playback(action)
		self.failIf(c.actions.contains(action))
		self.failUnless(action.playbackPolicy.hasBeenPlayedBack)
		self.failUnless(action.playbackPolicy.isReadyForRemoval)


	def testPlaybackWithMultipleCounts(self):
		"""Perform playback with multiple values"""
		c = Controller()
		action = BaseAction('x')
		c.record(action)
		c.setCount(2)
		self.failIf(action.playbackPolicy.hasBeenPlayedBack)
		self.failIf(action.playbackPolicy.isReadyForRemoval)
		c.playback(action)
		self.failIf(action.playbackPolicy.hasBeenPlayedBack)
		self.failIf(action.playbackPolicy.isReadyForRemoval)
		c.playback(action)
		self.failUnless(action.playbackPolicy.hasBeenPlayedBack)
		self.failUnless(action.playbackPolicy.isReadyForRemoval)

		
	
	def testUndefinedPlaybackRaisesException(self):
		"""Ensure that undefined playback raises exception"""
		x = BaseAction('x')
		try:
			pass
		except PlayackException, e:
			pass


	def testSetCount(self):
		"""Verify that settting the count works"""
		c = Controller()
		a = BaseAction('x')
		c.record(a)
		self.failUnless(a.playbackPolicy.remaining == 1)
		c.setCount(2)
		self.failUnless(a.playbackPolicy.remaining == 2)


	def testPlaybackIsUnlimited(self):
		"""Verify that unlimited playback settings are correctly reported"""
		c = Controller()
		a = BaseAction('x')
		c.record(a)


	def testRecord(self):
		"""Verify recording of a new action"""
		c = Controller()
		action = BaseAction('x')
		c.record(action)
		self.failUnless(c.actions.contains(action))
		self.failUnless(c.actionUnderConstruction == action)


	def testGetAttributeReturnsItsControllerWhenAsked(self):
		"""The controller must be returned when asked for"""
		c = Controller()
		x = c.mock()
		self.failIf(type(x._MockObject__controller) == type(x.w))


	def testRecordOrPlayback(self):
		"""Ensure that recordOrPlaback chooses the correct actions based on playback settings"""
		class ControllerRecordOrPlaybackFixture(Controller):
			def record(self, action):
				return 1
			def playback(self, action):
				return 2
		c = ControllerRecordOrPlaybackFixture()
		self.failUnless(c.recordOrPlayback('x') == 1)
		c.replay()
		self.failUnless(c.recordOrPlayback('x') == 2)

	
	def testProxyClassForObject(self):
		c = Controller()
		class ClassToClone(object):
			def m(self):
				pass
		x = ClassToClone()
		ClonedClass = c.proxyClassForObject(x)
		ClonedClass.f = ClonedClass.m
		y = ClonedClass()
		x.m()
		try:
			x.f()
			self.fail()
		except AttributeError, e:
			pass
		y.m()
		y.f()


	def testObjectWithProxiedClass(self):
		c = Controller()
		class ClassToClone(object):
			def m(self):
				pass
		x = ClassToClone()
		y = ClassToClone()
		c.attachObjectToProxyClass(y)
		y.__class__.f = lambda x: None 
		try:
			x.f()
			self.fail()
		except AttributeError, e:
			pass
		y.m()
		y.f()


		
class TestBaseAction(TestCase):
    
	def testBaseActionRecording(self):
	    """Verify that construction produces the right fields"""
	    x = BaseAction('x')
	    self.failUnless(x.key== 'x')
	
	    
	def testEqualityBasedOnFields(self):
		"""Verify field equality"""
		x = BaseAction('x')
		y = BaseAction('y')
		self.failIf(x == y)
		self.failIf(y == x)
		self.failUnless(x == x)
	
		
	def testEqualityBasedOnType(self):
		"""Verify field equality"""
		class DescendentBaseAction(BaseAction):
			pass
		x = BaseAction('x')
		y = DescendentBaseAction('x')
		self.failIf(x == y)
		self.failIf(y == x)
		self.failUnless(y == y)
	
	
	def testPlaybackMechanism(self):
		"""Ensure taht playback is tracked"""
		x = BaseAction('x')
		self.failIf(x.playbackPolicy.hasBeenPlayedBack)
		self.failIf(x.playbackPolicy.isReadyForRemoval)
		x.playback()
		self.failUnless(x.playbackPolicy.hasBeenPlayedBack)
		self.failUnless(x.playbackPolicy.isReadyForRemoval)


	def testRaisesException(self):
		"""Ensure that record recorded exceptions are played back"""
		x = BaseAction('x')
		x.throws = Exception()
		self.failUnlessRaises(Exception, x.playback)


	def testReturn(self):
		"""Ensure that the default action returns itself when recording"""
		x = BaseAction('x')
		self.failUnless(x.record() == x)
				


class TestReplayMechanism(TestCase):
	
	def testReplayMechanism(self):
		"""Test mechanics of replay system"""
		c = Controller()
		c = Mock



class TestSetAttributeAction(TestCase):
	
	def testSetAttributeAction(self):
	    """Verify construction of set attribute actions"""
	    action = SetAttributeAction('x', 'y', ('key',), 'z')
	    self.failUnless(action.field == 'y')
	    self.failUnless(action.value == 'z')
	
	    
	def testEquality(self):
		"""Verify equality"""
		action1 = SetAttributeAction(1, 2, ('k1',), 3)
		action2 = SetAttributeAction(1, 2, ('k2',), 4)
		action3 = SetAttributeAction(1, 3, ('k3',), 3)
		self.failUnless(action1 == action1)
		self.failIf(action1 == action2)
		self.failIf(action1 == action3)
		self.failIf(action1 == None)
	
	
	def testStr(self):
		"""Check string representation of an attribute"""
		action = SetAttributeAction('mock', 'y', ('key', ), 5)
		self.failUnless(str(action) == "y = 5")

		
	def testRecord(self):
		"""Ensure that setattibute returns itself"""
		action = SetAttributeAction('mock', 'y', ('key', ), 5)
		self.failUnless(action == action.record())
		



class TestGetAttributeAction(TestCase):
	
	def testGetAttributeAction(self):
		"""Verify construction of get attribute actions"""
		action = GetAttributeAction('y', ('key',), 'z')
		self.failUnless(action.key == ('key', 'y'))
		self.failUnless(action.field == 'y')
		self.failUnless(action.value == 'z')

		
	def testRecordReturnsMockObject(self):
		"""Get attribute returns the default mock it is constructed with"""
		action = GetAttributeAction('y', ('key',) , 'z')
		self.failUnless(action.record() == 'z')
	

	def testRecord(self):
		"""Ensure that getattribute returns the value"""
		action = GetAttributeAction('y', ('key',) , 'z')
		self.failUnless(action.record() == 'z')



class TestFunctionCallAction(TestCase):
	
	def testCreateFunctionCallAction(self):
		"""Create a new function call"""
		fca = FunctionCallAction(('key',), 'c', 'd', 'ret')
		self.failUnless(fca.key == ('key',))
		self.failUnless(fca.pargs == 'c')
		self.failUnless(fca.vargs == 'd')
		self.failUnless(fca.value == 'ret')


	def testRecord(self):
		"""Ensure that record returns the value"""
		fca = FunctionCallAction(('key',), 'c', 'd', 'ret')
		self.failUnless(fca.record() == 'ret')



class TestGeneratorAction(TestCase):
	
	def testCreateFunctionCallAction(self):
		"""Create a new function call"""
		fca = GeneratorAction(('key',), 'c', 'd')
		self.failUnless(fca.key == ('key',))
		self.failUnless(fca.pargs == 'c')
		self.failUnless(fca.vargs == 'd')


	def testFromFunctionCall(self):
		"""Ensure that record returns the value"""
		fca = FunctionCallAction(('key',), 'c', 'd', 'ret')
		gca = GeneratorAction.fromAction(fca)
		gcr = GeneratorAction(('key',), 'c', 'd')
		self.failUnless(gca == gcr)
		self.failUnless(gca == fca)
		self.failUnless(fca.playbackPolicy == gca.playbackPolicy)


		
class TestActionCache(TestCase):
    
    class ArbitraryAction(object):

    	def __init__(self, mockObject, field):
    		self.key = (mockObject, field)
    		(self.mockObject, self.field) = self.key

    		
    def testHasEntry(self):
        """Ensure we can tell if an entry exists"""
        cache = ActionCache()
        self.failIf(cache.contains(BaseAction('x')))


    def testPutEntry(self):
        """Put an entry in and check for its existance"""
        cache = ActionCache()
        action = BaseAction('x')
        cache.append(action)
        self.failUnless(cache.contains(action))
        
        
    def testGetEntry(self):
        """Put an entry on top and retrieve its value"""
        cache = ActionCache()
        z1 = self.ArbitraryAction(1, 2)
        z2 = self.ArbitraryAction(1, 2)
        self.failUnless(cache.get(z1) == None)
        cache.append(z1)
        self.failUnless(cache.get(z1) == z1)
        cache.append(z2)
        self.failUnless(cache.get(z1) == z1)
        self.failIf(cache.get(z2) == z2)

        
    def testPopEntry(self):
        """Pop an entry off the queue"""
        cache = ActionCache()
        z = self.ArbitraryAction('x', 'y')
        w= self.ArbitraryAction('x', 'y')
        cache.append(z)
        cache.append(w)
        self.failUnless(cache.pop(w) == z)
        self.failUnless(cache.get(w) == w)
        self.failUnless(cache.pop(z) == w)
        self.failUnless(cache.pop(z) == None)
        self.failIf(cache.contains(w))
        
        
    def testIter(self):
   		"""Replay all actions"""
   		cache = ActionCache()
   		z1 = BaseAction(1)
   		z2 = BaseAction(1)
   		w1 = BaseAction(2)
   		all = Set([z1, z2, w1])
   		self.failIf(list(cache))
   		[cache.append(x) for x in all]
   		self.failUnless(Set(cache) == all)


class TestFixedCountPlaybackPolicy(TestCase):
	
	def testDefaultSettingOfOnePlayack(self):
		"""Ensure that we play back only one time"""
		policy = FixedCountPolicy()
		self.failIf(policy.hasBeenPlayedBack)
		self.failIf(policy.isReadyForRemoval)
		policy.playback()
		self.failUnless(policy.hasBeenPlayedBack)
		self.failUnless(policy.isReadyForRemoval)
		
		
	def testTooManyPlaybacksRaisesAnException(self):
		"""Too many playback raises an exception"""
		policy = FixedCountPolicy()
		policy.playback()
		self.failUnlessRaises(RecordedCallsWereNotReplayedCorrectly, policy.playback)
	
	
	def testSettingCountsCorrectlyPlaysBack(self):
		"""Setting the playback count works"""
		policy = FixedCountPolicy(2)
		for x in [1, 2]:
			self.failIf(policy.hasBeenPlayedBack)
			self.failIf(policy.isReadyForRemoval)
			policy.playback()
		self.failUnless(policy.hasBeenPlayedBack)
		self.failUnless(policy.isReadyForRemoval)


	def testEnsurePlaybacksAreLimited(self):
		"""Ensure that the unlimited playbacks option is set to False"""
		policy = FixedCountPolicy()
		self.failIf(policy.hasUnlimitedPlaybacks)
        
    

class TestMinimumPlaybackPolicy(TestCase):
	
	def testOnePlaybacksIsTheDefault(self):
		"""Ensure that we must play back at least once"""
		policy = MinimumPlaybackPolicy()
		self.failIf(policy.hasBeenPlayedBack)
		self.failIf(policy.isReadyForRemoval)
		policy.playback()
		self.failUnless(policy.hasBeenPlayedBack)
		self.failIf(policy.isReadyForRemoval)


	def testVerifyArbitraryLimits(self):
		"""Ensure that we can require arbitrary minimum playback limits"""
		policy = MinimumPlaybackPolicy(3)
		for x in range(0, 3):
			self.failIf(policy.hasBeenPlayedBack)
			self.failIf(policy.isReadyForRemoval)
			policy.playback()
		self.failUnless(policy.hasBeenPlayedBack)
		self.failIf(policy.isReadyForRemoval)
		

	def testEnsurePlaybacksAreUnlimited(self):
		"""Ensure that the unlimited playbacks is set"""
		policy = MinimumPlaybackPolicy()
		self.failUnless(policy.hasUnlimitedPlaybacks)


	def testZeroPlaybacksIsSufficientlyPlayedBack(self):
		"""Ensure that we don't need to actually need playback when count=0"""
		policy = MinimumPlaybackPolicy(0)
		self.failUnless(policy.hasBeenPlayedBack)


		
class TestMockObject(TestCase):
	
	def testIdentifierSequenceCreation(self):
		"""Verify that identifiers are correctly created"""
		c = Controller()
		m = c.mock(KlassBeingMocked)
		expectedKeys = Set()
		m.g = 2
		expectedKeys.add((m, 'g'))
		self.failUnless(expectedKeys == self.actions(c))
		m.g.h
		expectedKeys.add((m, 'g', 'h'))
		self.failUnless(expectedKeys == self.actions(c))
		m.g()
		expectedKeys.add((m, 'g', '()'))
		self.failUnless(expectedKeys == self.actions(c))
		m.g().i()
		expectedKeys.add((m, 'g', '()', 'i'))
		expectedKeys.add((m, 'g', '()', 'i', '()'))
		self.failUnless(expectedKeys == self.actions(c))


	def actions(self, c):
		return Set(c.actions.actions.keys())


class TestPyMockTestCase(PyMockTestCase):
	
	def testMock(self):
		x = self.mock()
		self.expectAndReturn(x.read(), 5)
		self.replay()
		self.failUnless(x.read() == 5)
		self.verify()
		
	def testOverrideModule(self):
		"""Verify that overriding a module works"""
		c = Controller()
		c.override(os, 'getsid', classmethod(c.mock()))
		c.restore()
		

	
	

def suiteFor(*cases):
	suite = TestSuite()
	for x in cases:
		suite.addTest(makeSuite(x))
	return suite
    
suite = suiteFor(TestPyMockUseCases, TestControllerInternals, TestBaseAction,
                  TestSetAttributeAction, TestActionCache, TestFixedCountPlaybackPolicy,
                  TestFunctionCallAction, TestMockObject, TestGetAttributeAction,
                  TestMinimumPlaybackPolicy, TestGeneratorAction, TestOverrideContainer,
                  TestFunctionOverride, TestClassOverride, TestPyMockTestCase)

             
if __name__ == '__main__':
    TextTestRunner(verbosity=2).run(suite)

