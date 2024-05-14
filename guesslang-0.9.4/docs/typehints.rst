Adding type hints
=================

.. toctree::
   :maxdepth: 2

.. contents::
  :local:

What are type hints?
--------------------

Type hints are optional value types that can be use in a Python source code.

Python being a dynamic language, it is difficult to statically determine
the type of each variable defined in a source code.
**To enjoy the benefits of static typing without losing
the flexibility of dynamic typing**,
an optional static typing system, called ``type hints`` was proposed by the
`PEP 483 <https://www.python.org/dev/peps/pep-0483/>`_
and the `PEP 484 <https://www.python.org/dev/peps/pep-0484/>`_.

.. note::

  * All the examples shown here are only compatible with
    **Python 3.6+**.
  * All the example (except the ones with ellipis ``...``)
    **will run** fine with no changes required.

Here are simple statements with type hints:

.. code-block:: python
  :linenos:

  # a variable with type hints
  pi: float = 3.1415

  # a method with type hints
  def to_hex(value: int) -> str:
      return hex(value)

Benefits of type hints
^^^^^^^^^^^^^^^^^^^^^^

The overall benefits of type hints are:

* Being able to run type checkers, and **statically validate Python code**.
* Write code that can be easily understood and **maintained**.
* Improve the **documentation** of the code.
* Use advanced IDEs tools that are based on type hints.
  Like
  `PyCharm type hints support <https://www.jetbrains.com/help/pycharm/type-hinting-in-product.html>`_

Type hints are by nature **optional**.
Adding or removing type hints should not change the behavior
of a Python program.

In fact type hints are **not meant** to make your code run faster
or to make it consume less RAM.
They will be mostly ignored during the run-time.

The theory behind type hints
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Before using type hints it is useful, *but not mandatory*,
to know the core ideas that shape this typing system.

Gradual Typing
~~~~~~~~~~~~~~

Python type hints are based on
`gradual typing <https://wphomes.soic.indiana.edu/jsiek/what-is-gradual-typing/>`_.
Gradual typing is a typing system where some part of a source code
can be statistically typed while other parts of the same code
are dynamically typed.

Lets take this portion of code:

.. code-block:: python
  :linenos:

  x = 3       # "x" variable is dynamically typed as "int"
  y: int = x  # while "y" variable is statically typed as "int"

While ``x`` type can be dynamically inferred (deduced) from its value,
``y`` type is statically written in the code.
For programmers, the advantage is that they can gradually
define static types until they are satisfied.

Programmers then can stop adding new static types when:

* All type ambiguities have been removed from the program.
* Or all application public interfaces are statically typed.
* Or maybe when static types have been added everywhere?
* etc... (there is no written rule)

Type versus Class
~~~~~~~~~~~~~~~~~

An other interesting thing is that **types** used in type hints
are not always equivalent to **classes**.
In fact types are static representation of a value while
classes are dynamic representation of the same value.

You can see the difference in the following example:

.. code-block:: python
  :linenos:

  def even(value: int) -> Optional[str]:
      if value % 2 == 0:
          return "{} is even".format(value)
      # returns None if "value" is an odd number

Like the Schrödinger's cat, the ``even`` function return type is
**both** ``str`` and ``NoneType``.
This composed type is written ``Optional[str]``.

On the other hand, during the run-time the class of the returned value
is not ``Optional[str]`` but **either** ``str`` or ``NoneType``.

How to use type hints?
----------------------

We will give an overview of the different types
that can be used for type hints.

Simple types
^^^^^^^^^^^^

Classes as types
~~~~~~~~~~~~~~~~

All Python classes can be used as types for type hints:
``int``, ``float``, ``bool``, ``str``, ``bytes``, etc...

.. note::

  * The ``ERROR`` comments are the messages given by the static type checker.
    They are explained by the ``-->`` comment that follows.

.. code-block:: python
  :linenos:

  x: int = 3
  y: float = 4

  x = y
  # ERROR: Incompatible types in assignment
  #     (expression has type "float", variable has type "int")
  #
  # --> should not set a "float" value in an "int" variable

Container types
~~~~~~~~~~~~~~~

However, some Python classes are not well suited for type hints.

For example, Python container classes ``list``, ``dict``, ``set``, etc...
are too permissive to be used for type hints,
because it is not possible to define the contained values types:

.. code-block:: python
  :linenos:

  x: list = [1, 2, 3]
  y: list = ['a', 'b', 'c']

  y[0] = x[0]
  # OK: because both are lists of "something", but TOO PERMISSIVE

For tighter type checking, it is required to define the content type.
This is done using the predefined types available in
`typing standard library <https://docs.python.org/3/library/typing.html>`_.

The previous code will then become:

.. code-block:: python
  :linenos:

  from typing import List


  x: List[int] = [1, 2, 3]
  y: List[str] = ['a', 'b', 'c']

  y[0] = x[0]
  # ERROR: No overload variant of "__setitem__" of "list"
  #     matches argument types "int", "int"
  #
  # --> the content types are not the same "int" != "str"

`Typing library <https://docs.python.org/3/library/typing.html>`_
defined types for a large range of containers including:
``List``, ``Set``, ``Dict`` and others.

It also gives access to abstract classes described in the
`collections.abc standard library <https://docs.python.org/3/library/collections.abc.html#collections-abstract-base-classes>`_
like ``Iterator``, ``Iterable``, ``Mapping``, ``Coroutine``, etc...

Any type
~~~~~~~~

There is a special type named ``Any`` that can replace any type.
It can be used for types that are too complex,
or when we don't really care about the type of a given variable.

.. code-block:: python
  :linenos:

  from typing import Any


  x: Any = [1, 'two', [[[3]]]]
  y: Any = None
  z: int = 0

  y = x
  # OK: "Any" is anything

  z = x
  # OK: "Any" can become everything.
  #     BUT actually "x" content doesn't match "z" static type "int"

As shown in the last line ``z = x``, ``Any`` should be used with care
to avoid hiding mismatched types errors during the run-time.

None type
~~~~~~~~~

An other special type is ``None``
that is used for variables that contains ``None`` value.
``None`` is used in type hints as an alia of ``type(None)`` AKA ``NoneType``:

.. code-block:: python
  :linenos:

  def print_empty_div() -> None:
      print("<div></div>")
      # returns None

Aliases and new types
~~~~~~~~~~~~~~~~~~~~~

Programmers can create an **alias** for a type (put the type into a variables)
or even create **new types**:

.. code-block:: python
  :linenos:

  from typing import NewType, List


  # Create a type alias
  Measures = List[int]

  a: Measures = [25, 38]
  b: Measures = [19, 19]

  # Create a new type
  Temperatures = NewType('Temperatures', List[int])
  x: Temperatures = Temperatures([15, 17])
  y: Temperatures = Temperatures([44, 36])

Instances of the new class must be created through the class constructor.

All of these types can be mixed together to produce composed types
that represent more precisely a given value.

Composed types
^^^^^^^^^^^^^^

There are multiple ways to compose types:

Union type
~~~~~~~~~~

``Union[TypeX, TypeY, TypeZ...]``:
represents a value that can have any of the types that compose the ``Union``:
``TypeX``, ``TypeY`` or ``TypeZ``, etc...

.. code-block:: python
  :linenos:

  from typing import Union


  representation = input('choose "text" or "number" > ')
  output: Union[int, str] = 'twelve' if representation == 'text' else 12

  print(output)  # prints «twelve» or «12»

Optional type
~~~~~~~~~~~~~

``Optional[TypeX]``: same as ``Union[TypeX, None]``
represents a value that can either be ``TypeX`` or ``None``.

.. code-block:: python
  :linenos:

  from typing import Optional


  a = {'top': 10}
  b: Optional[int] = a.get('bottom')

Tuple type
~~~~~~~~~~

``Tuple[TypeX, TypeY, TypeZ,...]``: represents a ``tuple``.
``TypeX``, ``TypeY``, etc... being the tuple item types.

.. code-block:: python
  :linenos:

  from typing import Tuple


  user: Tuple[str, int] = ("John", 36)

Callable type
~~~~~~~~~~~~~

``Callable[[TypaParam1, TypeParam2, ...], TypeReturn]``:
represents a ``callable``.

The callable can be a function, a class method, a ``class``, a ``lambda``,
a metaclass etc... any object that can be called with parenthesis.

``TypaParam1``, ``TypeParam2``, etc... are the parameters types
while ``TypeReturn`` is the callable return type.

.. code-block:: python
  :linenos:

  from typing import Callable


  def divide_by_two(value: int) -> float:
      return value / 2

  def run(method: Callable[[int], float], value: int) -> float:
      return method(value)

  result: float = run(divide_by_two, 3)

NoReturn type
~~~~~~~~~~~~~

``NoReturn``: an indication that a function will never return any value.

.. code-block:: python
  :linenos:

  from typing import NoReturn


  def fail(message: str) -> NoReturn:
      raise RuntimeError(message)

  x = fail("an error")
  # ERROR: Need type annotation for "x"
  #
  # --> in fact, "x" variable cannot receive a value from a function
  #     that returns nothing

Object oriented programming support
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Python type hints support most of the modern object oriented programming
and abstraction features, including type variance and generic types.

The most interesting features are detailed bellow.

ClassVar: class attribute type
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``ClassVar`` is a composed types that is used to specify that a variable
is a **class attribute** (also known as class variable).
Therefore, this class attribute should not be used as an instance attribute.

*Example:*

.. code-block:: python
  :linenos:

  from typing import ClassVar


  class Robot:
      kill_switch: ClassVar[bool] = False


  Robot.kill_switch = True
  # OK: "kill_switch" is declared as a class variable,
  #     it can be modified through the class itself

  bot = Robot()

  bot.kill_switch = True
  # ERROR: Cannot assign to class variable "kill_switch" via instance

TypeVar: type variables
~~~~~~~~~~~~~~~~~~~~~~~

In programming an abstraction refers to the *use of generic concepts
instead of actual classes and types*.

The base generic concept that can be used is **type variable**.
Type variables are placeholders that can be replaced by actual types
during the runtime:

``T = TypeVar('T')``


In the following example, the type variable ``T`` is replaced first
by ``int`` type then by ``str`` type:

.. code-block:: python
  :linenos:

  from typing import TypeVar


  T = TypeVar('T')


  def middle(items: List[T]) -> T:
      pos = int(len(items) / 2)
      return items[pos]


  digit: int = middle([1, 2, 3])
  # OK: "T" type variable is replaced by "int"

  letter: str = middle(['a', 'b', 'c'])
  # OK: "T" type variable is replaced by "str"

Type variables can be restricted to certain types:

``T = TypeVar('T', TypeX, TypeY, ...)``

In this case only the listed types ``TypeX``, ``TypeY``, etc...,
can replace the type variable ``T``.

*Example:*

.. code-block:: python
  :linenos:

  from typing import TypeVar


  Number = TypeVar('Number', int, float)


  def safe_div(dividend: Number, divisor: Number) -> float:
      return float('nan') if divisor == 0 else dividend / divisor


  x: float = safe_div(2, 3)
  # OK: "Number" type variable is replaced by "int"

  y: float = safe_div(9.1, 0.0)
  # OK: "Number" type variable is replaced by "float"

  z: float = safe_div('many', 'some')
  # ERROR: Value of type variable "Number" of "safe_div" cannot be "str"

``TypeVar`` with restricted types looks a lot like ``Union``
but there is a catch.
A ``TypeVar`` is replaced by only one actual type at a time
when ``Union`` can be replaced by different types at a time.

This difference between ``TypeVar`` with restricted types and ``Union``
can be seen in this example:

.. code-block:: python
  :linenos:

  from typing import Union, TypeVar


  T = TypeVar('T', bytes, str)
  U = Union[bytes, str]


  # The function arguments "first" and "second" must have the same type
  def size_1(first: T, second: T) -> int:
      return len(first) + len(second)


  # The function arguments "first" and "second" can have different types
  def size_2(first: U, second: U) -> int:
      return len(first) + len(second)


  a: int = size_1('long', 'story')
  # OK: the function arguments have the same type "str"

  b: int = size_1('long', b'story')
  # ERROR: Value of type variable "T" of "size_1" cannot be "object"
  #
  # --> in fact the function arguments are "str" and "bytes"
  #     but type "T" can be replaced by ONE type not two.
  #
  #     "object" type that is a common base class of "str" and "bytes" is tried
  #      but "object" is not compatible with "T = TypeVar('T', bytes, str)"

  c: int = size_2('long', b'story')
  # OK: unlike "size_1", here the function arguments can have DIFFERENT types
  #     "str" and "bytes".
  #     These types matches "U = Union[bytes, str]".

TypeVar: type bounds
~~~~~~~~~~~~~~~~~~~~

Type variables can be bound to a given type:

``T = TypeVar('T', bound=TypeX)``

Here the types that can replace the type variable ``T``
are:

* The bound type ``TypeX``
* All types that derive from ``TypeX`` (i.e ``TypeX`` child classes)

*Example:*

.. code-block:: python
  :linenos:

  from typing import TypeVar


  class SeriousError(Exception):
      def __init__(self, message: str) -> None:
          super().__init__('SERIOUS', message)


  # "T" can be "Exception" or any of its child classes
  T = TypeVar('T', bound=Exception)


  def print_error(exception: T) -> None:
      text = ': '.join(exception.args)
      print(text)


  try:
      raise SeriousError("alert!")
  except SeriousError as error:
      print_error(error)  # prints «SERIOUS: alert»
      # OK: because "SeriousError" is a child class of "Exception"

Type: set a type to actual types
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The following type hints can be added to a variable definition
when this variable **contains a class**:

``Type[TypeX]``

*Example:*

.. code-block:: python
  :linenos:

  from typing import Type


  bool_class: Type[bool] = bool
  # OK: "bool" class object has the type "Type[bool]"

This feature is pertucularly usefull when associated with type variables.

In the following example, a function ``new`` is defined.
``new`` takes a class as an argument then returns an instance of this class:

.. code-block:: python
  :linenos:

  from typing import TypeVar, Type


  T = TypeVar('T', bool, int)


  def new(item_class: Type[T]) -> T:
      return item_class()


  boolean_false: bool = new(bool)
  # OK: the function parameter type is "type(bool)" and it returns a "bool"

  zero: int = new(int)
  # OK: the function parameter type is "type(int)" and it returns an "int"

  empty_string: str = new(str)
  # ERROR: Value of type variable "T" of "new" cannot be "str"
  #
  # --> because of the type restriction, the only accepted types are
  #     "bool" and "int"

@overload: function overloading
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A **generic method** can be defined using ``@overload`` decorator.

This decorator doesn't select which version of the function to call.
It just defines the different type combinations that are available
for the function.

The actual implementation of the function is defined without
``@overload`` decorator.

*Example:*

.. code-block:: python
  :linenos:

  from typing import overload


  @overload
  def dotted(*values: int) -> str:
      # leave blank
      ...


  @overload
  def dotted(*values: str) -> str:
      # leave blank
      ...


  # @overload" not used here
  def dotted(*values):
      """Convert parameters to a string separed by dots '.' """
      text_values = [str(value) for value in values]
      return '.'.join(text_values)


  print(dotted(1, 234, 567))  # «1.234.567»
  # OK: matches method variant "def dotted(*values: int) -> str"

  print(dotted('you', 'shall', 'not', 'pass'))  # «you.shall.not.pass»
  # OK: matches method variant "def dotted(*values: str) -> str"

  print(dotted(b'hello'))
  # ERROR: No overload variant of "dotted" matches argument type "bytes"
  #     Possible overload variants:
  #        def dotted(*values: int) -> str
  #        def dotted(*values: str) -> str

Generic: generic types
~~~~~~~~~~~~~~~~~~~~~~

Generic types are **custom composed types** that are defined in a program.
Generic types are defined by creating types that inherit
from the following type:

``Generic[T, U,...]``, where ``T``, ``U``, etc... are type variables.

A **variants** of a generic class is defined by replacing the type variable
with an actual type.

For example:

* ``List[T]`` is a generic type, ``T`` being a type variables
* ``List[int]`` is a variant of ``List[T]``
  where the type variable ``T`` is replaced by ``int``
* ``List[str]`` is also a variant of ``List[T]``
  and here the type variable ``T`` is replaced by ``str``

A new generic types is defined in the next example.
It is an implementation of a task runner using a generic type:

.. code-block:: python
  :linenos:

  import time
  from typing import Generic, TypeVar, List, NoReturn, Callable


  Param = TypeVar('Param')
  Result = TypeVar('Result')


  class Task(Generic[Param, Result]):
      """A generic task runner.

      A function is passed to the task during its creation.
      That function is executed when the "task.run(...)" method is called.

      - Param: type variable that represents the function parameter
      - Result: type variable that represents the function return value
      """

      def __init__(self, function: Callable[[Param], Result]) -> None:
          self.function = function

      def run(self, param: Param) -> Result:
          return self.function(param)


  def text_hash(text: str) -> int:
      """Compute a (broken) hash"""
      return sum(ord(x) for x in text)


  def triple(items: List[int]) -> List[int]:
      """Multiply each element of a list by three"""
      return [item * 3 for item in items]


  def loop_forever() -> NoReturn:
      """Loop forever"""
      while True:
          time.sleep(1)


  hash_task: Task[str, int] = Task(text_hash)
  result: int = hash_task.run("gold diggers diggin' until they find oil")
  # OK: creates a variant of "Task" where
  #     - "Param" type variable is "str"
  #     - "Result" type variable is "int"

  triple_task: Task[List[int], List[int]] = Task(triple)
  values: List[int] = triple_task.run([1, 2, 3])
  # OK: creates a variant of "Task" where
  #     - "Param" type variables is "List[int]"
  #     - "Result" type variables is also "List[int]"

  loop_task: Task[[], NoReturn] = Task(loop_forever)
  # ERROR: Argument 1 to "Task" has incompatible type Callable[[], NoReturn]";
  #     expected "Callable[[Any], Any]"
  #
  # --> There is no type that matches "Param" type variable
  #     because "loop_forever" function doesn't take any argument.

Sometimes the code is too ambiguous to know which variant of a generic type
will be instantiated.
In this case the programmers can **explicitly** choose which variant of
the generic type they want to instantiate.

*Example:*

.. code-block:: python
  :linenos:

  from typing import Generic, TypeVar, Optional


  T = TypeVar('T')


  class Store(Generic[T]):
      """Generic item store"""

      def __init__(self) -> None:
          self.item: Optional[T] = None

      def set(self, item: T) -> None:
          self.item = item

      def get(self) -> Optional[T]:
          return self.item


  store_x = Store[str]()
  # OK: the variant of "Store[T]" where "T" is replaced by "str" type
  #     is explicitly created

  store_x.set('javascript')
  x: Optional[str] = store_x.get()

  store_y: Store[int] = Store()
  # OK: the type checker guesses the variant that is instantiated "Store[int]"
  #     from the variable "store_y" type

  store_y.set(3)
  y: Optional[int] = store_y.get()

  store_z = Store()
  # ERROR: Need type annotation for "store_z"
  #
  # --> there is no type information that the type checker can use to determine
  #     which variant is instantiated

In addition to that, a generic type variant can be partially defined
using a type alias.

*Example:*

.. code-block:: python
  :linenos:

  from typing import Dict, TypeVar


  T = TypeVar('T')

  StrDict = Dict[str, T]
  # The generic type "Dict[K, V]" is partially defined:
  #     the type variable "K" is replaced by the concrete type "str"
  #     while "V" remains a type variable (renamed "T")

  a: StrDict[int] = {'a': 1}
  # OK: "StrDict[int]" is in fact "Dict[str, int]".
  #     And "Dict[str, int]" matches the given value

  b: StrDict[bool] = {'b': 1.2}
  # ERROR: Dict entry 0 has incompatible type "str": "int";
  #     expected "str": "bool"
  #
  # --> the defined type "StrDict[bool]" is in fact "Dict[str, bool]"
  #     unfortunately the given value is a "Dict[str, float]"

More advanced usages of generic types are described in the
`typing module documentation <https://docs.python.org/3/library/typing.html#user-defined-generic-types>`_.

Variance: invariant, covariant and contravariant
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

`Subtyping <https://en.wikipedia.org/wiki/Subtyping>`_
is a relation between two types ``Parent`` and ``Child``
(``Parent`` is the subtype of ``Child``)
that allow the type ``Parent`` to be safely used in the code where
the type ``Child`` is expected.

A subtyping relation is implicitly created when a ``Child`` class inherit
from a ``Parent`` class.
It can also be explicitly created using
`Python abstract base classes <https://docs.python.org/3.5/glossary.html#term-abstract-base-class>`_.

Let's consider a composed type ``Container[T]``, ``T`` being a type variable.
What is the relation between ``Container[Parent]`` and ``Container[Child]``?

In fact the relation between these composed types depends on the **variance**
of the type variable ``T``.

If the type variable ``T`` is:

* **Invariant**: there is no subtyping relation between
  ``Container[Parent]`` and ``Container[Child]``.
* **Covariant**:
  ``Container[Parent]`` is a subtype of ``Container[Child]``.
  The same relation as ``Parent`` and ``Child``.
* **Contravariant**:
  ``Container[Child]`` is a subtype of ``Container[Parent]``.
  The inverse of ``Parent`` and ``Child`` relation.

In the following example ``Container[Parent]`` and ``Container[Child]``
have no special relation, because the type variable ``T`` is **invariant**
by default.

.. code-block:: python
  :linenos:

  from typing import Generic, TypeVar


  class Parent: pass
  class Child(Parent): pass

  T = TypeVar('T')
  class Container(Generic[T]): pass


  x: Container[Parent] = Container[Child]()
  # ERROR: Incompatible types in assignment (
  #     expression has type "Container[Child]",
  #     variable has type "Container[Parent]")
  #
  # --> "T" is invariant (no relation):
  #     "Container[Parent]" variable cannot receive "Container[Child]" value

To replicate the subtyping relation and
make ``Container[Parent]`` the subtype of ``Container[Child]``,
the type variable ``T`` must be **covariant**:

.. code-block:: python
  :linenos:

  from typing import Generic, TypeVar


  class Parent: pass
  class Child(Parent): pass

  T = TypeVar('T', covariant=True)
  class Container(Generic[T]): pass


  x: Container[Parent] = Container[Child]()
  # OK: "T" is covariant:
  #     "Container[Parent]" variable can now receive a "Container[Child]" value

To reverse the subtyping relation and
make ``Container[Child]`` the subtype of ``Container[Parent]``,
the type variable ``T`` must be **contravariant**:

.. code-block:: python
  :linenos:

  from typing import Generic, TypeVar


  class Parent: pass
  class Child(Parent): pass

  T = TypeVar('T', contravariant=True)
  class Container(Generic[T]): pass


  x: Container[Child] = Container[Parent]()
  # OK: "T" is contravariant:
  #     "Container[Child]" variable can receive a "Container[Parent]" value

Variance: a use case
~~~~~~~~~~~~~~~~~~~~

In this detailed example we are implementing a plug-in system
using the variance of type variables.

The plugin system is designed as follows:

* The plug-ins:

  * Each plug-in is represented by a class.
  * All plug-ins share a same base class ``BasePlugIn``
  * A special class ``SecurePlugIn`` has as parent classes,
    a list of plug-in that are considered secure

* Tools that manage plug-in:

  * ``PlugInSandbox`` runs a plug-in in a sandbox.
  * ``PlugInInfo`` retrieves the name of a given plug-in.
  * ``PlugInInfo[BasePlugIn]`` is the common type for all plug-in name readers.
  * ``PlugInManager`` checks if a plug-in is available for use.
  * ``PlugInManager[SecurePlugIn]`` is the common type for all managed
    secure plug-ins.

*The implementation:*

.. code-block:: python
  :linenos:

  """
  PlugIn classes hierarchy:

  BasePlugIn ──┬──> LowerPlugIn ──┬──> SecurePlugIn
               ├──> TitlePlugIn ──┘
               │
               └──> EvalPlugIn (not secure)
  """

  from ast import literal_eval
  from contextlib import contextmanager
  import time
  from typing import Generic, TypeVar, Optional, Generator


  class BasePlugIn:
      """Base plug-in class"""
      def execute(self, data: str) -> str:
          raise NotImplementedError()


  class LowerPlugIn(BasePlugIn):
      """Plug-in that converts a text to lower case"""
      def execute(self, data: str) -> str:
          return data.lower()


  class TitlePlugIn(BasePlugIn):
      """Plug-in that puts the first letter of a text in upper case"""
      def execute(self, data: str) -> str:
          return data.title()


  class EvalPlugIn(BasePlugIn):
      """Plug-in that evaluates a Python expression"""
      def execute(self, data: str) -> str:
          # evaluation of data provided by the user
          # without error handling is NOT SAFE
          return str(literal_eval(data))


  class SecurePlugIn(LowerPlugIn, TitlePlugIn):
      """List all secure plug-ins as base classes"""
      pass


  # Create the plugin that will be used in all examples above
  title_plugin = TitlePlugIn()


  #------------------------------------------------------------------------------
  # Invariant type variables
  #------------------------------------------------------------------------------


  T = TypeVar('T')


  class PlugInSandbox(Generic[T]):
      """Runs a plug-in in a sandbox"""

      def __init__(self, plugin: T) -> None:
          self.plugin: T = plugin

      # A context manager that mimic a sandbox
      # this code is not relevant to understand the types relations
      @contextmanager
      def sandboxed(self) -> Generator[T, None, None]:
          print("[Sandbox ON]")
          yield self.plugin
          print("[Sandbox OFF]")


  sandbox: PlugInSandbox[TitlePlugIn] = PlugInSandbox[TitlePlugIn](title_plugin)
  # OK: value and variable have the same type: "PlugInSandbox[TitlePlugIn]"

  with sandbox.sandboxed() as safe_plugin:
      sandboxed_execution_result = safe_plugin.execute('here we go')
      print(sandboxed_execution_result)
      # prints:
      #     [Sandbox ON]
      #     Here We Go
      #     [Sandbox OFF]

  base_sandbox: PlugInSandbox[BasePlugIn] = PlugInSandbox[TitlePlugIn](
      title_plugin)
  # ERROR: Incompatible types in assignment (
  #     expression has type "PlugInSandbox[TitlePlugIn]",
  #     variable has type "PlugInSandbox[BasePlugIn]")
  #
  # --> "Container[Parent]" to "Container[Child]" type conversions are only valid
  #     for *contravariant* type variables. But here "T" type variable is invariant

  secure_sandbox: PlugInSandbox[SecurePlugIn] = PlugInSandbox[TitlePlugIn](
      title_plugin)
  # ERROR: Incompatible types in assignment (
  #     expression has type "PlugInSandbox[TitlePlugIn]",
  #     variable has type "PlugInSandbox[SecurePlugIn]")
  #
  # --> "Container[Child]" to "Container[Parent]" type conversions are only valid
  #     for *covariant* type variables. But here "T" type variable is invariant


  #------------------------------------------------------------------------------
  # Covariant type variables
  #------------------------------------------------------------------------------


  U = TypeVar('U', covariant=True)


  class PlugInInfo(Generic[U]):
      """Get a plug-in name"""

      def __init__(self, plugin: U) -> None:
          self.plugin: U = plugin

      def name(self) -> str:
          return self.plugin.__class__.__name__


  info: PlugInInfo[TitlePlugIn] = PlugInInfo[TitlePlugIn](title_plugin)
  # OK: value and variable have the same type: "PlugInInfo[TitlePlugIn]"

  plugin_name = info.name()
  print(plugin_name)  # prints «TitlePlugIn»

  base_info: PlugInInfo[BasePlugIn] = PlugInInfo[TitlePlugIn](title_plugin)
  # OK: "U" is covariant, therefore:
  #     "Container[Child]" to "Container[Parent]" type conversions are valid

  base_plugin_name = base_info.name()
  print(base_plugin_name)  # «TitlePlugIn»
  # Note that the type conversion doesn't affect the plug-in runtime class
  #     that remains "TitlePlugIn"

  secure_info: PlugInInfo[SecurePlugIn] = PlugInInfo[TitlePlugIn](title_plugin)
  # ERROR: Incompatible types in assignment (
  #     expression has type "PlugInInfo[TitlePlugIn]",
  #     variable has type "PlugInInfo[SecurePlugIn]")
  #
  # --> "Container[Parent]" to "Container[Child]" type conversions are only valid
  #     for *contravariant* type variables. But here "U" type variable is covariant


  #------------------------------------------------------------------------------
  # Contrariant type variables
  #------------------------------------------------------------------------------


  V = TypeVar('V', contravariant=True)


  class PlugInManager(Generic[V]):
      """Checks if a plugin is available"""

      def __init__(self, plugin: Optional[V] = None) -> None:
          self.plugin: Optional[V] = plugin

      def is_available(self) -> bool:
          return self.plugin is not None


  manager: PlugInManager[TitlePlugIn] = PlugInManager[TitlePlugIn](title_plugin)
  # OK: value and variable have the same type: "PlugInManager[TitlePlugIn]"

  if manager.is_available():
      message = manager.plugin.execute("hip hip hooray")
      print(message)  # prints «Hip Hip Hooray»

  base_manager: PlugInManager[BasePlugIn] = PlugInManager[TitlePlugIn]()
  # ERROR: Incompatible types in assignment (
  #     expression has type "PlugInManager[TitlePlugIn]",
  #     variable has type "PlugInManager[BasePlugIn]")
  #
  # --> "Container[Child]" to "Container[Parent]" type conversions are only valid
  #     for *covariant* type variables. But here "V" type variable is contravariant

  secure_manager: PlugInManager[SecurePlugIn] = PlugInManager[TitlePlugIn]()
  # OK: "V" is contravariant, therefore:
  #     "Container[Parent]" to "Container[Child]" type conversions are valid

  if not secure_manager.is_available():
      print("exiting...")  # prints «exiting...»

Other features
^^^^^^^^^^^^^^

There are practical features that can help programmers write type hints
with more ease.

Explicit type casting: cast function
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Sometimes the variables content type doesn't exactly match the expected type.
If this mismatch doesn't harm the program, it is possible to explicitly
change the static type of the variable using the method:

``cast(TypeX, value)``

*Example:*

.. code-block:: python
  :linenos:

  from typing import cast, List


  x: List[int] = [0, 1]

  y: List[float] = x
  # ERROR: Incompatible types in assignment (
  #     expression has type "List[int]",
  #     variable has type "List[float]")
  #
  # --> the conversion from "List[float]" to "List[int]" is not implicit
  #     even if "int" type can be implicitly casted to "float"

  z: List[float] = cast(List[float], x)
  # OK: we explicitly cast "List[int]" into "List[float]"
  #     BUT the content of "z" variable is still a list of "int" values

The static type casting provided by ``cast(...)`` function
doesn't actually change the value content.

.. warning::

  Programmers sould not rely on ``cast(...)`` to convert the run-time
  value of a variable.

  They should properly convert the value themselves.

*Example:*

.. code-block:: python
  :linenos:

  from typing import cast, List


  message: str = "SUCCESS"
  status_code: int = cast(int, message)
  # OK: "status_code" static type have been converted from "str" to "int"
  #     BUT "status_code" run-time class is still "str".
  #     Python objects run-time classes are not affected by static type casting.

  print(status_code)  # prints «SUCCESS»

Data holders: NamedTuple, @dataclass
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

There are at least two ways to create data holder classes that takes advantage
of type hints:

* ``NamedTuple``
  base class defined in
  `typing standard module <https://docs.python.org/3/library/typing.html#typing.NamedTuple>`_
  and compatible with **Python 3.6+**
* ``@dataclass`` decorator defined in
  `dataclasses standard module <https://docs.python.org/3/library/dataclasses.html#module-level-decorators-classes-and-functions>`_
  and compatible with **Python 3.7+**

They are replacements and/or complements to ``collections.namedtuple``.

Here is an example using ``@dataclass``:

.. code-block:: python
  :linenos:

  from dataclasses import dataclass


  @dataclass
  class Voxel:
      """A 3D colored pixel"""
      x: int
      y: int
      z: int
      color: str = 'blue'

  broken_voxel: Voxel = Voxel(1.0, -2, 3)
  # ERROR: Argument 1 to "Voxel" has incompatible type "float"; expected "int"
  #
  # --> the first argument "x" has the wrong type: "float" instead of "int"

  voxel: Voxel = Voxel(1, -2, 3)
  # OK: all the arguments have the right type

  print(voxel)  # prints «Voxel(x=1, y=-2, z=3, color='blue')»

Type definition with forward references
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When a type hint contains a forward reference,
a reference to a type that is **not defined** yet,
the name of this type must be written as a string.

*Example:*

.. code-block:: python
  :linenos:

  from typing import Optional


  class Chain:
      """Linked values"""

      # The type "Chain" is not fully defined here,
      # references to "Chain" type should be written as a string "'Chain'"
      def __init__(self, value: int, next: Optional['Chain'] = None) -> None:
          self.value = value
          self._next = next

      @property
      def next(self) -> 'Chain':
          if self._next is None:
              raise ValueError("Last item, no next items")
          return self._next


  head: Chain = Chain(1, Chain(2, Chain(3)))
  last_value: int = head.next.next.value
  print(last_value)  # prints «3»

In **Python 4**, forward references will be supported by default
thanks to the «Postponed Evaluation of Annotations» feature introduced by the
`PEP 563 <https://www.python.org/dev/peps/pep-0563/#enabling-the-future-behavior-in-python-3-7>`_.
It will no longer be required to write type names as strings.

This feature can be used today on Python 3.7 with the following import:

``from __future__ import annotations``

*Example:*

.. code-block:: python
  :linenos:

  from __future__ import annotations

  from typing import Optional


  class Chain:
      """Linked values"""

      # "Chain" type can now be used in type annotations
      def __init__(self, value: int, next: Optional[Chain] = None) -> None:
          pass

How to add static types to Guesslang source code?
-------------------------------------------------

Now let's put all that into practice by adding type hints to Guesslang package.

Current status
^^^^^^^^^^^^^^

Guesslang core package has more than 700 lines of codes, with 29 functions.
Not counting the tools, tests and side packages.

Today **70%** of Guesslang source code is covered by unit tests.

.. code-block:: text

  Name                     Stmts   Miss  Cover   Missing
  ------------------------------------------------------
  guesslang/__init__.py        4      0   100%
  guesslang/__main__.py       70     70     0%   3-112
  guesslang/config.py         50     21    58%   38-45, 53-65, 77-79, 95-97
  guesslang/extractor.py      47      2    96%   51, 78
  guesslang/guesser.py       124      3    98%   196, 254, 256
  guesslang/utils.py          55      9    84%   77, 82-89, 121
  ------------------------------------------------------
  TOTAL                      350    105    70%

The goal
^^^^^^^^

The main goal sought in adding type hints to Guesslange
is to improve the **readability** of the source code.

Hopefully type hints may also reveal hidden typing **bugs** that
unit tests didn't detect.

On the other hand it would be good to avoid spending too much time
adding type hints to parts of code that don't really need them.

Setting the scope
~~~~~~~~~~~~~~~~~

To reach the goals defined above, type hints will be added
to the following definitions:

* **Method** definitions
* **Class** definitions
* Class **public attribute** definitions
* **Ambiguous** variable definitions

In addition to that, the added type hints should be readable and concise...
because *this is not C++* 😛

.. code-block:: c++
  :linenos:

  // C++, I love you... but thats way too long...
  static inline std::map<std::string, int> zip_and_map(std::list<std::string> keys, std::list<int> values) {
    ...
  }

The tool
^^^^^^^^

Mypy with Typeshed
~~~~~~~~~~~~~~~~~~

The checker I used is the de facto standard Python static type checker
`Mypy <http://mypy.readthedocs.io/>`_.

Mypy is a powerfull static type checker maintained by Python core developers
including
`Guido van Rossum <https://en.wikipedia.org/wiki/Guido_van_Rossum>`_,
the Python language creator.
Mypy provide detailed error message that helps quickly fix the typing issues.

To overcome the lack of type annotations in Python standard library
as well as third party packages, Mypy uses
`Typeshed package <https://github.com/python/typeshed/>`_.

Typeshed is a collection of type annotations for Python standard library,
``builtins`` and some third party packages.

You can install Mypy with the following command:

.. code-block:: shell
  :linenos:

  pip install mypy

Checking Guesslang types
^^^^^^^^^^^^^^^^^^^^^^^^

Run static type checking
~~~~~~~~~~~~~~~~~~~~~~~~

The type checker is executed with the command line bellow:

.. code-block:: shell
  :linenos:

  mypy --strict --ignore-missing-imports guesslang/

Explanation:

* ``mypy``: the static type checker command line tool

* ``--strict``: option to check everything,
  will print an **error** or a **warning** if any type issue is found.

* ``--ignore-missing-imports``:
  ignore third party dependencies that lacks type hints.
  Guesslang is based on ``numpy`` and ``tensorflow`` and they don't
  provide type information.
  In addition to that, **no type hints** is defined for these third party packages
  in `typeshed <https://github.com/python/typeshed>`_.
  Without this option the following error messages would be generated:

  .. code-block:: text
    :linenos:

    guesslang/config.py:12: error: Cannot find module named 'tensorflow'
    guesslang/config.py:12: note: (Perhaps setting MYPYPATH or using the "--ignore-missing-imports" flag would help)
    guesslang/utils.py:10: error: No library stub file for module 'numpy'
    guesslang/utils.py:10: note: (Stub files are from https://github.com/python/typeshed)
    guesslang/guesser.py:10: error: Cannot find module named 'tensorflow'

Running Mypy will list **all the typing issues** found by the checker.
If there is no typing issue Mypy won't print anything.

Fixing Guesslang type issues
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Fix types issues from Mypy error messages
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The first and most obvious way to fix static typing issues highlighted by Mypy
is to **read** Mypy error messages and warnings then apply the proposed fixes.

For example the error bellow is fixed by changing the argument type
from ``str`` to ``int``:

.. code-block:: text
  :linenos:

  error: Argument 2 to "_pop_many" has incompatible type "int"; expected "str"

In addition to that, there are several other ways to gather the information
required to fix the typing issues.

Fix types issues from Guesslang documentation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In fact most of Guesslang methods are documented.
The arguments and return types are detailed in the documentation.
I just have to reuse them as type hints.

*For example:*

.. code-block:: python
  :linenos:

  def learn(self, input_dir):
      """Learn languages features from source files.

      :raise GuesslangError: when the default model is used for learning
      :param str input_dir: source code files directory.
      :return: learning accuracy
      :rtype: float
      """
      ...

The method argument type is given in ``:param str input_dir:``
and the return type in ``:rtype: float``.
The type hints for this method are then:

.. code-block:: python
  :linenos:

  def learn(self, input_dir: str) -> float:
      """Learn languages features from source files.

      :raise GuesslangError: when the default model is used for learning
      :param input_dir: source code files directory.
      :return: learning accuracy
      """
      ...

Fix types issues from the unit tests
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

All Guesslang "public" methods are tested by unit tested.
**Literal** values (with obvious types) are sent to these methods.
The literals types can then be used to write the methods type hints.

*Example:*

.. code-block:: python
  :linenos:

  def test_split():
      text = """
          int * last(int *tab, int size)
          {
          \treturn tab + (size - 1);
          }
      """
      tokens = [
          '\n', 'int', '*', 'last', '(', 'int', '*', 'tab', ',', 'int', 'size',
          ')', '\n', '{', '\n', 'return', 'tab', '+', '(', 'size', '-', '1', ')',
          ';', '\n', '}', '\n'
      ]

      assert extractor.split(text) == tokens

From this test we can easily deduce that ``split(...)`` methods
takes a string ``str`` as argument and returns a list of strings ``List[str]``:

.. code-block:: python
  :linenos:

  def split(text: str) -> List[str]:
      ...

Handle special types
~~~~~~~~~~~~~~~~~~~~

Some type hints where less usual that the other ones.
Like:

* A method that returns a tuple with a **variable** number of ``str`` elements
  ``Tuple[str, ...]``:

  .. code-block:: python
    :linenos:

    def probable_languages(
            self,
            text: str,
            max_languages: int = 3) -> Tuple[str, ...]:
        ...

* A method that takes a file object or **STD-IN** as an argument ``typing.TextIO``:

  .. code-block:: python
    :linenos:

    def _read_file(input_file: TextIO) -> str:
        ...

* A really long type that have been replaced by an **alias**
  to avoid over-complicated type hints:

  .. code-block:: python
    :linenos:

    DataSet = Tuple[Sequence[Sequence[float]], Sequence[int]]

* A method that produces a callable object.
  The callable returns tuple of ``Any`` instead of an identifiable type
  because the tuple will only be Tensorflow. A third party package that
  **cannot be checked** by the static type checker.

  .. code-block:: python
    :linenos:

    def _to_func(vector: DataSet) -> Callable[[], Tuple[Any, Any]]:
        return lambda: (
            tf.constant(vector[0], name='const_features'),
            tf.constant(vector[1], name='const_labels'))

What to do when no suitable type is found
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A little Quiz: There is a Guesslang method that loads a **JSON string**,
what should be its return type?

*Sample code:*

.. code-block:: python
  :linenos:

  def config_dict(name):
      """Load a JSON configuration dict from Guesslang config directory.

      :param str name: the JSON file name.
      :return: configuration
      :rtype: dict
      """
      content = ...  # read file content
      return json.loads(content)

The closest definition of a ``JsonObject`` type would be:

.. code-block:: python
  :linenos:

  import json
  from typing import Dict, List, Union


  JsonObject = Union[
      None,
      int,
      bool,
      str,
      List['JsonObject'],
      Dict[str, 'JsonObject']
  ]
  # ERROR: Recursive types not fully supported yet,
  #     nested types replaced with "Any"
  #
  # --> "JsonValue" type alias cannot have a reference to itself


  value: JsonValue = json.loads('{"a": null}')

Unfortunately it is not yet possible to define recursive type aliases.

**The actual answer is**:

«*We can't define JsonObject in a very tight way* ──
`by Guido van Rossum  <https://github.com/python/typing/issues/182#issuecomment-199872724>`_»

As a workaround, the ``JsonObject`` type is defined
by ``Dict[str, Any]`` in Guesslang:

.. code-block:: python
  :linenos:

  def config_dict(name: str) -> Dict[str, Any]:
      """Load a JSON configuration dict from Guesslang config directory.

      :param name: the JSON file name.
      :return: configuration
      """
      content = ...  # read file content
      return json.loads(content)

Updating Guesslang documentation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To document the process of adding static types to Guesslang this documentation
page was written. This page is also a tour of Python static typing feature,
a feature that might be pillar of the next exciting Python features.

The documentation generated from the source code have been improved using
the package:
`sphinx-autodoc-typehints <https://github.com/agronholm/sphinx-autodoc-typehints>`_.
With this package, the type annotations are automatically added to the methods
description.

Any actual benefits?
--------------------

As expected, adding type information to Guesslang had a **positive impact**
on the project:

* The source code is **easier to read** and understand.
* The project is statically type checked now.
  The type checking is now part of the **continuous integration**.
* The code is more **consistent** now. It is easier to see where an argument
  with a wrong type is sent to a function.
  For example there where a minor mix-up between ``list`` and ``type`` values
  that have been detected and fixed thanks to the type checking.
* The documentation is **easier to write**, no need to add type information in
  the doc-string.
* The generated documentation is more **detailed**.

On the over hand:

* The new type checking **didn't uncover new bugs**, just little improvements.
  But type hints are still a great complement to actual tests.
* Few **tweaks where required** to fix all the type checking issues.
  In most cases adding types to local variables, casting types and
  using the ``Any`` type where enough to solve the most complex issues.

Finally
^^^^^^^

I would say that type hints are a **great step forward** for Python language,
it builds a solid bridge between the statically typed languages world and
the dynamically typed languages one.
Of course the bigger and more complex the project is
**the bigger the type hints benefits** will be.

Currently I'm quite happy with them and I will use them in more projects.
