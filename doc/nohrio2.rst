**********
Version 2
**********

Development of version 2 of *nohrio* is currently underway.
Development will proceed with minimal changes to old API, in the hopes that the old API remains usable
until the few things that use *nohrio* have been ported

Key features:

  * Python 3 oriented: While any reasonable patches to implement 2.7.x compatibility will be gladly accepted,
    Py3 is the way forward for Python and Py3 most urgently needs more software available for it -- which
    is itself dependent on how many projects have already been ported.
    
    Also, Python 3 makes I/O way more consistent and understandable, and this project's all about I/O.

  * *Unified data model*: all data types are class-based and usually derive from IOHandler. Anything that is not
    inherently a container (for example, PAL) is made up of attributes, not NumPy subfields...
    
  * *Better use of NumPy*: ... NumPy still has a heavy involvement in making things happen behind the scenes,
    especially in the use of dtypes.
    
  * *Unified and simplified I/O*:  if it does i/o, it subclasses IOHandler.. and probably defines very few,
    very short methods in order to implement I/O support. It will read from or write to a filehandle directly,
    which means that a range of input sources are supported. For example, OHRRPGCE.NEW is 230k; OHRRPGCE.NEW.gz is 6k
    (small enough to store directly in a module's source code!), and in the new framework,
    we can read from the latter just as easily as the former.
    
  * *Test coverage*: the new code has high test coverage; some modules have 100%.
    This provides a place to look for example code and to understand the behaviour of the API in detail
    (more than is feasible to go into in a written explanation.).
    It also makes it much easier to check whether you broke something :)

*********************
Current state of API
*********************

.. automodule:: nohrio.nohrio2
    :members:

.. automodule:: nohrio.dtypes.archinym
    :members:

.. automodule:: nohrio.dtypes.general
    :members:

.. automodule:: nohrio.dtypes.tag
    :members:
    TagCheck
