#!/usr/bin/env python
#
# test script for the Mock object.
#
# This Python  module and associated files are released under the FreeBSD
# license. Essentially, you can do what you like with it except pretend you wrote
# it yourself.
# 
# 
#     Copyright (c) 2005, Dave Kirby
# 
#     All rights reserved.
# 
#     Redistribution and use in source and binary forms, with or without
#     modification, are permitted provided that the following conditions are met:
# 
#         * Redistributions of source code must retain the above copyright
#           notice, this list of conditions and the following disclaimer.
# 
#         * Redistributions in binary form must reproduce the above copyright
#           notice, this list of conditions and the following disclaimer in the
#           documentation and/or other materials provided with the distribution.
# 
#         * Neither the name of this library nor the names of its
#           contributors may be used to endorse or promote products derived from
#           this software without specific prior written permission.
# 
#     THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
#     ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
#     WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#     DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
#     ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
#     (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
#     LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
#     ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#     (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
#     SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# 
#         mock@thedeveloperscoach.com


import unittest
from mock import *

class MockCallTest(unittest.TestCase):
    """
    Tests for the MockCall class that is used to record calls.
    """
    def test_ConstructorAndAccessors(self):
        mc = MockCall("func", (1,2,"three"), {"a":"a", "b":"b"})
        self.assertEqual(3, mc.getNumParams())
        self.assertEqual(2, mc.getNumKwParams())
        self.assertEqual("func", mc.getName())
        self.assertEqual(1, mc.getParam(0))
        self.assertEqual(2, mc.getParam(1))
        self.assertEqual("three", mc.getParam(2))
        self.assertEqual("a", mc.getParam("a"))
        self.assertEqual("b", mc.getParam("b"))
        self.assertEqual("func(1, 2, 'three', a='a', b='b')", str(mc))

    def test_CallWithNoParams(self):
        mc = MockCall("funcNoArgs", (), {})
        self.assertEqual(0, mc.getNumParams())
        self.assertEqual(0, mc.getNumKwParams())
        self.assertEqual("funcNoArgs", mc.getName())

    def test_DodgyGetParamType_throwsIndexError(self):
        mc = MockCall("func", (1, 2), {})
        self.assertRaises(IndexError, mc.getParam, [])


class TestMockCallable(unittest.TestCase):
    """
    Tests for MockCallable class, independent of real Mock class.
    """
    class MockMock:
        def __init__(self):
            self.mockExpectations = {}
        def _checkInterfaceCall(self, name, params, kwparams):
            pass

    def test_SingleCallWithNoParams_SetsOneCaller(self):
        funcName = "func"
        mockmock = self.MockMock()
        mockmock.mockReturnValues = {funcName:1}
        mockmock.mockCalledMethods = {}
        mockmock.mockAllCalledMethods = []
        mc = MockCallable(funcName, mockmock)
        ret = mc()
        self.assertEqual(1, ret)
        self.assertEqual(1, len(mockmock.mockAllCalledMethods))
        self.failUnless(mockmock.mockCalledMethods.has_key(funcName))
        self.assertEqual("func()", str(mockmock.mockCalledMethods[funcName][0]))


class MockTest(unittest.TestCase):
    def test_NoCalls_EmptyCallLists(self):
        mock = Mock()
        calls = mock.mockGetAllCalls()
        self.assertEqual(calls, [])
        calls = mock.mockGetNamedCalls('blah')
        self.assertEqual(calls, [])
        calls = mock.mockGetAllCalls()
        self.assertEqual(calls, [])

    def test_SingleCall_AccessByMethodName(self):
        mock = Mock()
        mock.testMethod("hello", key="some value")
        calls = mock.mockGetNamedCalls('testMethod')
        self.assertEqual(len(calls), 1, "test Calls Count")
        call = calls[0]
        self.assertEqual(call.getName(), 'testMethod')
        self.assertEqual(call.getParam(0), "hello")
        self.assertEqual(call.getParam('key'), "some value")
        self.assertEqual(str(call), "testMethod('hello', key='some value')", str(call))

    def test_mockCheckCall(self):
        mock = Mock()
        mock.testMethod("hello", key="some value")
        calls = mock.mockGetNamedCalls('testMethod')
        self.assertEqual(len(calls), 1, "test Calls Count")
        call = calls[0]
        self.assertEqual(call.getName(), 'testMethod')
        self.assertEqual(call.getParam(0), "hello")
        self.assertEqual(call.getParam('key'), "some value")
        self.assertEqual(str(call), "testMethod('hello', key='some value')", str(call))
        # test the mockCheckCall method
        mock.mockCheckCall( 0, 'testMethod', "hello", key="some value" )
        self.assertRaises(AssertionError, mock.mockCheckCall, 0, 'testMethod', "hello", key="wrong value" )

    def test_SingleCall_AccessByIndex(self):
        mock = Mock()
        mock.testMethod("hello", key="some value")
        call = mock.mockGetAllCalls()[0]
        self.assertEqual(call.getName(), 'testMethod')
        self.assertEqual(call.getParam(0), "hello")
        self.assertEqual(call.getParam('key'), "some value")

    def test_ReturnValue(self):
        mock1 = Mock({'start':'here we go', 'stop':'finished', 'run':42})
        # create second mock to make sure it doesn't intefere with the first
        mock2 = Mock({'foo':23, 'run':13})
        a = mock1.start()
        b1 = mock1.run()
        b2 = mock1.run()
        b3 = mock1.run()
        c = mock1.stop()
        d = mock1.DoSomethingInteresting()
        self.assertEqual(a, 'here we go')
        self.assertEqual(b1, 42)
        self.assertEqual(b2, 42)
        self.assertEqual(b3, 42)
        self.assertEqual(c, 'finished')
        self.assertEqual(d, None)
        calls = mock1.mockGetAllCalls()
        self.assertEqual(len(calls), 6)
        self.assertEqual(calls[0].getName(), 'start')
        self.assertEqual(calls[1].getName(), 'run')
        self.assertEqual(calls[4].getName(), 'stop')
        self.assertEqual(calls[5].getName(), 'DoSomethingInteresting')
        e = mock2.run()
        self.assertEqual(e, 13)

    def test_IndirectCalls(self):
        mock = Mock()
        f1 = mock.first
        f2 = mock.second
        f3 = mock.third
        f3()
        f2()
        f1()
        f3()
        expected = ['third', 'second', 'first', 'third']
        calls = mock.mockGetAllCalls()
        self.assertEqual(calls[0].getName(), expected[0])
        self.assertEqual(calls[1].getName(), expected[1])
        self.assertEqual(calls[2].getName(), expected[2])
        self.assertEqual(calls[3].getName(), expected[3])
        
    def test_AddReturnValues( self ):
        mock = Mock({'foo':42})
        self.assertEqual(42, mock.foo())
        mock.mockAddReturnValues(foo=21, bar='stuff')
        self.assertEqual('stuff', mock.bar())
        self.assertEqual(21, mock.foo())



class MockSubclassTest(unittest.TestCase):
    class MockSub(Mock):
        """ A class for testing inherited behaviour of Mock """
        def testFortyTwo(self, x):
            assert x == 42
        def getSquare(self, x):
            return x*x
        def concatNamedArgs(self, a="a", b="b"):
            return a + b

    def test_InheritanceCallUndefinedMethod_DoesntBreakStandardBehaviour(self):
        mock = self.MockSub({'wibble': 23})
        x = mock.wibble("foo")
        self.assertEqual(x, 23)
        call = mock.mockGetNamedCalls('wibble')[0]
        self.assertEqual(call.getParam(0), "foo")

    def test_CallHandcraftedMethod_IsRecordedLikeNormal(self):
        mock = self.MockSub()
        # Test a specialised method of the derived class
        mock.testFortyTwo(42)
        call = mock.mockGetNamedCalls('testFortyTwo')[0]
        self.assertEqual(call.getParam(0), 42)
        self.assertEqual(len(mock.mockGetAllCalls()), 1)
        
    def test_AssertionFailureInHandcraftedMethod_IsThrown(self):
        mock = self.MockSub()
        self.assertRaises(AssertionError, mock.testFortyTwo, 0)

    def test_CallHandcraftedMethod_GivesDifferentValuesForDifferentCalls(self):
        mock = self.MockSub()
        squares = []
        for i in range(5):
            squares.append(mock.getSquare(i))
        self.assertEqual(squares, [0, 1, 4, 9, 16])
        calls = mock.mockGetAllCalls()
        self.assertEqual(len(calls), 5)

    def test_CallHandcraftedMethod_RecordsKwParams(self):
        mock = self.MockSub()
        ret = mock.concatNamedArgs(a="hi")
        self.assertEqual(ret, "hib")
        calls = mock.mockGetAllCalls()
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0].getName(), "concatNamedArgs")
        self.assertEqual(calls[0].getParam("a"), "hi")


class MockInterfaceMethodNameTest(unittest.TestCase):
    class OrigBaseClass:
        def func1(self, x):
            return x + 1
        def func2(self, x):
            return x + 2
        def funcWithThreeParams(self, a, b, c):
            pass
        def undefined(self):
            raise NotImplementedError

    def test_CallMethodNotInInterface_ThrowsAssertion(self):
        mock = Mock(realClass=self.OrigBaseClass)
        try:
            mock.unknownFunc(2)
        except MockInterfaceError, e:
            # expected
            self.assertEqual(str(e), "Calling mock method 'unknownFunc' that was not found in the original class")
            return
        self.fail("calling unknownFunc should have raised exception")

    def test_CallMethodsInInterface_Ok(self):
        mock = Mock({}, realClass=self.OrigBaseClass)
        mock.func1(2)
        mock.func2(7)
        mock.func1(7)
        mock.undefined()

    def test_CallUnknownMethodOnClassWithIntInterface_ExceptionRaised(self):
        mock = Mock({}, realClass=int)
        self.assertRaises(MockInterfaceError, mock.unkFunc, 5)

    def test_FuncRetValNotInIntClass_ExceptionRaised(self):
        self.assertRaises(MockInterfaceError, Mock, {"funk":2}, realClass=int)

    def test_FuncRetValInIntClass_Ok(self):
        mock = Mock({"__repr__":"2", "__coerce__":(2,4)}, realClass=int)
        repr = `mock`
        self.assertEquals(repr, "2")
        # __coerce__ will turn the 7 into a 4
        z = mock + 7
        self.assertEquals(z, 6)

    def test_CallMethodsInDerivedInterface_Ok(self):
        class OrigDerivedClass(self.OrigBaseClass):
            def funcDerived(self):
                return "Uncalled"
        mock = Mock({"funcDerived":"Hi"}, realClass=OrigDerivedClass)
        mock.func1(2)
        self.assertEquals(mock.funcDerived(), "Hi")

    def test_ReturnValueMethodNotInOrigClass_ExceptionRaised(self):
        try:
            mock = Mock({"somethingWild":123}, realClass=self.OrigBaseClass)
        except MockInterfaceError, e:
            # expected
            self.assertEqual(str(e), "Return value supplied for method 'somethingWild' that was not in the original class")
            return
        self.fail("setting up return value for unknown func should have raised exception")

    def test_CallHandcraftedMethodNotInInterface_ExceptionRaised(self):
        class MyClass:
            def func1(self, x):
                return x + 1
        class MockClass(Mock):
            def func1(self, x):
                return x + 2
            def somethingBizarre(self):
                pass
        mock = MockClass({}, realClass=MyClass)
        self.assertEquals(mock.func1(1), 3)
        self.assertRaises(MockInterfaceError, mock.somethingBizarre)


class MockInterfaceMethodParamTest(unittest.TestCase):
    def test_CallMethodInInterfaceOneParam(self):
        class OrigBaseClass:
            def func1(self, x):
                return x + 1
        mock = Mock({}, realClass=OrigBaseClass)
        self.assertEquals(mock.func1(1), None)
        self.assertEquals(mock.func1(x=1), None)
        self.assertRaises(MockInterfaceError, mock.func1)
        self.assertRaises(MockInterfaceError, mock.func1, 1, 2)
        self.assertRaises(MockInterfaceError, mock.func1, unk=3)

    def test_CallMethodInInterfaceWithRightNamedParam_ExceptionRaised(self):
        class OrigBaseClass:
            def funcWithThreeParams(self, a, b, c):
                return 4
        mock = Mock({}, realClass=OrigBaseClass)
        self.assertEquals(mock.funcWithThreeParams(a=1, c=3, b=0), None)
        self.assertRaises(MockInterfaceError, mock.funcWithThreeParams, a=1, c=3, wrong=0)
        self.assertRaises(MockInterfaceError, mock.funcWithThreeParams, a=1, b=2, c=3, wrong=0)



class MockInterfaceMethodKwParamTest(unittest.TestCase):
    class TestKwClass:
        def funcWithKwParams(self, x, **kwparams):
            pass
    def test_CallKwParamMethodInInterfaceWithUnknownKwParams_Ok(self):
        mock = Mock({}, realClass=self.TestKwClass)
        mock.funcWithKwParams(3, a=1, b=2, c=3)

    def test_CallKwParamMethodInInterfaceWithInsufficientArgs_ExceptionRaised(self):
        mock = Mock({}, realClass=self.TestKwClass)
        self.assertRaises(MockInterfaceError, mock.funcWithKwParams, a=1, b=2, c=3)

    def test_CallKwParamMethodInInterfaceWithTooManyParams_ExceptionRaised(self):
        mock = Mock({}, realClass=self.TestKwClass)
        self.assertRaises(MockInterfaceError, mock.funcWithKwParams, 1, 2)

    def cannot_test_CallDuplicatedKwParam_ExceptionRaised(self):
        pass
        # Can't test this since the interpreter raises an uncatchable SyntaxError for us.
        # mock = Mock({}, realClass=self.TestKwClass)
        # mock.funcWithKwParams(1, a=2, a=3)


class MockInterfaceMethodDefaultParamTest(unittest.TestCase):
    def test_CallKwDefaultParamMethodInInterface(self):
        class TestDefaultClass:
            def funcWithKwDefaults(self, x=3, **kwparams):
                pass
        mock = Mock({}, realClass=TestDefaultClass)
        mock.funcWithKwDefaults(x=1)
        mock.funcWithKwDefaults(1)
        mock.funcWithKwDefaults()
        # Too many params
        self.assertRaises(MockInterfaceError, mock.funcWithKwDefaults, 1, 2)
        # Set x param twice
        self.assertRaises(MockInterfaceError, mock.funcWithKwDefaults, 1, x=2)

    def test_KwDefaultAndVarargs(self):
        class NastyClass:
            def func(self, x, y, *rest, **kw):
                pass
        mock = Mock({}, realClass=NastyClass)
        mock.func(1, 2)
        mock.func(1, y=2)
        mock.func(1, 2, 3, 4)
        mock.func(1, 2, 3, extra1="4", extra2="5")
        self.assertRaises(MockInterfaceError, mock.funcWithKwDefaults, "z")
        self.assertRaises(MockInterfaceError, mock.funcWithKwDefaults, unk=1, unk2=2)

    def test_KwDefaultAndVarargsHandcraftMockOk(self):
        class NastyClass:
            def func(self, x, y=2, *rest, **kw):
                return 0
        class NastyMock(Mock):
            def func(SELF, X, Y=1, *REST, **KW):
                return Y
        mock = NastyMock({}, realClass=NastyClass)
        self.assertEquals(mock.func(1), 1)
        self.assertEquals(mock.func(1, 2), 2)
        self.assertEquals(mock.func(1, 2), 2)
        self.assertEquals(mock.func(1, 2, 3, 4), 2)
        self.assertEquals(mock.func(1, 2, 3, extra1="4", extra2="5"), 2)
        self.assertEquals(mock.func(1, z=7), 1)

    def test_DefaultInMockSubclassNotInOrig(self):
        class OrigClass:
            def func(self, x):
                pass
        class MockClass(Mock):
            def func(self, x=3):
                pass
        mock = Mock({}, realClass=OrigClass)
        mock.func(1)
        self.assertRaises(MockInterfaceError, mock.func)

    def test_DefaultInOrigNotInMockSubclass(self):
        class OrigClass:
            def func(self, x=1):
                pass
        class MockClass(Mock):
            def func(self, x):
                pass
        mock = MockClass({}, realClass=OrigClass)
        mock.func(1)
        self.assertRaises(TypeError, mock.func)


class MultipleInheritanceTests(unittest.TestCase):
    def test_MultiInheritance_CallsLeafAndRecordsCall(self):
        class OrigClass:
            def func(self, x):
                return self.templateMethod(x)
            def templateMethod(self, x):
                raise NotImplementedError
        class MultiMock(OrigClass, Mock):
            def templateMethod(self, x):
                return x + 1
        mock = MultiMock({}, realClass=OrigClass)
        ret = mock.func(1)

        self.assertEquals(ret, 2)
        calls = mock.mockGetAllCalls()
        self.assertEqual(len(calls), 2)
        self.assertEqual(calls[0].getName(), 'func')
        self.assertEqual(calls[1].getName(), 'templateMethod')
        self.assertEqual(calls[1].getNumParams(), 1)
        self.assertEqual(calls[1].getParam(0), 1)

    def test_MultiInheritanceNoBaseTemplate_CallsLeafAndRecordsCall(self):
        class OrigClass:
            def func(self, x):
                return self.templateMethod(x)
        class MultiMock(OrigClass, Mock):
            def templateMethod(self, x):
                return x + 1
        mock = MultiMock({}, realClass=MultiMock)
        ret = mock.func(1)

        self.assertEquals(ret, 2)
        calls = mock.mockGetAllCalls()
        self.assertEqual(len(calls), 2)
        self.assertEqual(calls[0].getName(), 'func')
        self.assertEqual(calls[1].getName(), 'templateMethod')

    def test_DeepHierarchy_CallsAppropriateDefinitions(self):
        class A:
            def funcA(self):
                return "a"
            def funcB(self):
                return "a"
        class B(A):
            def funcB(self):
                return "b"
        class C(A):
            def funcA(self):
                return "c"
            def funcC(self):
                return "c"
        class MultiMock(B, C, Mock):
            def templateMethod(self, x):
                return x + 1
        mock = MultiMock({}, realClass=MultiMock)
        self.assertEquals(mock.funcA(), "a")
        self.assertEquals(mock.funcB(), "b")
        self.assertEquals(mock.funcC(), "c")
        calls = mock.mockGetAllCalls()
        self.assertEqual(len(calls), 3)

    def test_TemplateMethodCallNoInterfaceClass(self):
        class TemplateMethodBase:
            def func(self, x):
                '''Calls template method "overflow" if x is too big.'''
                if x > 10000000:
                    self.overflow(x)
                return x*x
            def overflow(self, x):
                raise NotImplementedError
        class TemplateMethodMock(TemplateMethodBase, Mock):
            def overflow(self, x):
                assert x > 10000000
        mock = TemplateMethodMock()
        mock.func(20000000)
        calls = mock.mockGetAllCalls()
        self.assertEqual(len(calls), 2)

class ReturnValuesTest(unittest.TestCase):
    def test_ReturnValues(self):
        mock = Mock({'foo':ReturnValues(1,2,3)} )
        result = [ mock.foo() for x in xrange(3) ]
        self.assertEqual([1,2,3], result)
        self.assertRaises( AssertionError, mock.foo ) 
        
    def test_ReturnIterator(self):
        def squareGen(limit):
            for i in xrange(1, limit+1):
                yield i*i
        mock = Mock({'foo':ReturnIterator(squareGen(3))} )
        result = [ mock.foo() for x in xrange(3) ]
        self.assertEqual([1,4,9], result)
        self.assertRaises( AssertionError, mock.foo ) 


    
class ExpectationsTest(unittest.TestCase):
    def test_Expectations(self):
        mock = Mock({'foo':42})
        mock.mockSetExpectation('foo', lambda mockObj, callObj, idx: idx==0)
        result = mock.foo()
        self.assertEqual(42, result)
        self.assertRaises( AssertionError, mock.foo ) 

    def test_ExpectParams(self):
        mock = Mock({'runMe':23})
        mock.mockSetExpectation('runMe', expectParams(1, 2, 3, foo='bar'))
        val = mock.runMe(1, 2, 3, foo='bar')
        self.assertEqual(23, val)
        self.assertRaises(AssertionError, mock.runMe, 1, 2, foo='bar')
        self.assertRaises(AssertionError, mock.runMe, 1, 2, 3, foo='xxx')

    def test_ExpectAfter(self):
        mock = Mock()
        mock.mockSetExpectation('runSecond', expectAfter('runFirst'))
        mock.mockSetExpectation('runThird', expectAfter('runFirst', 'runSecond'))
        #calling runSecond before runFirst should now raise an exception
        self.assertRaises(AssertionError, mock.runSecond)
        self.assertRaises(AssertionError, mock.runThird)
        mock.runFirst()
        mock.runSecond()
        mock.runThird()
        
    def test_MultipleExpectations(self):
        '''test that setting two expectations on the same function works
        '''
        mock = Mock()
        mock.mockSetExpectation('runSecond', expectAfter('runFirst'))
        mock.mockSetExpectation('runSecond', expectParams('foo'))
        self.assertRaises(AssertionError, mock.runSecond, 'foo')
        mock.runFirst()
        mock.runSecond('foo')   #should not raise an exception
        self.assertRaises(AssertionError, mock.runSecond, 'bar')
        
    def test_ExpectException(self):
        mock = Mock()
        mock.mockSetExpectation('allocate', expectException(MemoryError, 'no memory'))
        self.assertRaises(MemoryError, mock.allocate, 'stuff')

    def test_ExpectationWithRange(self):
        mock = Mock()
        #set the expectation so that the third and fourth calls to allocate raise an exception
        mock.mockSetExpectation('allocate', expectException(MemoryError, 'no memory'), after=2, until=5)
        mock.allocate()
        mock.ignoreThisFunction()
        mock.allocate()
        self.assertRaises(MemoryError, mock.allocate)
        mock.ignoreThisFunction()
        self.assertRaises(MemoryError, mock.allocate)
        mock.allocate()

    def test_expectParamEQ(self):
        mock = Mock()
        # expect a function to be called with the first parameter == 3 
        mock.mockSetExpectation('callWithThree', expectParam(0, EQ(3)))
        # this should work OK
        mock.callWithThree(3)
        # doesnt matter what other parameters are:
        mock.callWithThree(3, 'this parameter is ignored')
        self.assertRaises(AssertionError, mock.callWithThree, 2)

    def test_expectKeywordParamEQ(self):
        mock = Mock()
        # expect a function to be called with the keyword parameter 'three' == 3 
        mock.mockSetExpectation('callWithThree', expectParam('three', EQ(3)))
        # this should work OK
        mock.callWithThree(2,4, 6, three=3, thisParameter='ignored')
        # this should raise an exception
        self.assertRaises(AssertionError, mock.callWithThree, 2, 4, 6, three=2)


    def test_expectWithComplexConditional(self):
        #example test showing the use of compex condtionals
        mock = Mock()
        # expect a method to be called with the following parameters:
        #  1st parameter is a number in the range 0-10
        #  2nd parameter is a string containing a single word
        #  3rd parameter is a callable function
        mock.mockSetExpectation('exampleMethod', expectParam(0, AND(GE(0), LE(10))) )
        mock.mockSetExpectation('exampleMethod', expectParam(1, MATCHES(r'\w+$') ) )
        mock.mockSetExpectation('exampleMethod', expectParam(2, CALLABLE ) )
        # this should work OK
        def dummyfn(): pass
        mock.exampleMethod(5, 'OneWord', dummyfn)
        # these should raise an exception
        self.assertRaises(AssertionError, mock.exampleMethod, 20, 'OneWord', dummyfn)
        self.assertRaises(AssertionError, mock.exampleMethod, 5, 'Two Words', dummyfn)
        self.assertRaises(AssertionError, mock.exampleMethod, 5, 'OneWord', 'This is not callable')


class TestConditionals(unittest.TestCase):
    def test_EQ(self):
        self.failUnless( EQ(0)(0) )
        self.failIf( EQ(1)(0) )
        self.failUnless( EQ('xxx')('xxx') )
        self.failIf( EQ('xxx')('xxxy') )

    def test_NE(self):
        self.failIf( NE(0)(0) )
        self.failUnless( NE(1)(0) )
        self.failIf( NE('xxx')('xxx') )
        self.failUnless( NE('xxx')('xxxy') )

    def test_GT(self):
        self.failIf( GT(5)(4) )
        self.failUnless( GT(5)(6) )
        self.failIf( GT(5)(5) )

    def test_LT(self):
        self.failUnless( LT(5)(4) )
        self.failIf( LT(5)(6) )
        self.failIf( LT(5)(5) )

    def test_AND(self):
        self.failUnless( AND( EQ(1), LT(2), GT(0) )(1) )
        self.failIf( AND( GT(0), LT(5), EQ(3) )(4) )

    def test_OR(self):
        self.failUnless( OR(EQ(1), EQ(2), EQ(3))(2) )
        self.failIf( OR(EQ(1), EQ(2), EQ(3))(4) )

    def test_NOT(self):
        self.failUnless( NOT(EQ(1))(2) )
        self.failIf( NOT(EQ(1))(1) )

    def test_MATCHES(self):
        import re
        self.failUnless( MATCHES(r'\d+')('123') )
        self.failIf( MATCHES(r'\d+')('no digits') )
        self.failUnless( MATCHES(r'[a-z_]+$', re.I)('UPPER_CASE') )

    def test_SEQ(self):
        cond = SEQ( EQ(1), EQ(2), EQ(3), EQ(4) )
        self.failUnless( cond(1) )
        self.failIf( cond(0) )
        self.failUnless( cond(3) )
        self.failUnless( cond(4) )
        self.assertRaises(AssertionError, cond, 5)

    def test_IS(self):
        class A: pass
        a = A()
        self.failUnless( IS(a)(a) )
        b = A()
        self.failIf( IS(a)(b) )

    def test_ISINSTANCE(self):
        class A: pass
        class B(A): pass
        class C: pass
        b = B()
        self.failUnless( ISINSTANCE(A)(b) )
        self.failIf( ISINSTANCE(C)(b) )

    def test_ISSUBCLASS(self):
        class A: pass
        class B(A): pass
        class C: pass
        self.failUnless( ISSUBCLASS(A)(B) )
        self.failIf( ISSUBCLASS(A)(C) )
        self.failIf( ISSUBCLASS(B)(A) )

    def test_CONTAINS(self):
        self.failUnless( CONTAINS('a')('abc') )
        self.failIf( CONTAINS('x')('abc') )
        self.failUnless( CONTAINS('a')(dict(a=1, b=2, c=3)) )
        self.failIf( CONTAINS('x')(dict(a=1, b=2, c=3)) )

    def test_IN(self):
        self.failUnless( IN('abc')('a') )
        self.failIf( IN('abc')('x') )

    def test_HASATTR(self):
        class A:
            classVal = 1
            def __init__(self):
                self.val = 1
            def method(self):
                pass
        a = A()
        self.failUnless( HASATTR('val')(a) )
        self.failUnless( HASATTR('method')(a) )
        self.failUnless( HASATTR('classVal')(a) )

    def test_HASATTR(self):
        def function(): pass
        non_function = 'non-callable'
        self.failUnless( CALLABLE(function) )
        self.failIf( CALLABLE(non_function) )

    def test_HASMETHOD(self):
        class A:
            classVal = 1
            def __init__(self):
                self.val = 1
            def method(self):
                pass
        a = A()
        self.failUnless( HASMETHOD('method')(a) )
        self.failIf( HASMETHOD('val')(a) )
        self.failIf( HASMETHOD('classVal')(a) )


        
if __name__ == "__main__":
    unittest.main()
