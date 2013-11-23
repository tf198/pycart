PyCart
======

A web interface for your git repositories.  Aims to be a quick drop in
replacement for Trac + Git.  Much of the design blatently borrowed from
`GitHub` until I have time to work out something better :)

Installation
============

TODO: write setup.py

Renderers
=========

The following renders are supported if the modules are installed:

* Pygments ``pip install pygments``
* Markdown ``pip install markdown``
* ReSTructured text ``pip install docutils``

Documentation
=============

With one of the markup renderers installed, you can store and view your documentation
within the interface.

e.g.

docs/README.md::

   Example documentation
   =====================
   
   Here are the sections:
   * [Introduction](introduction.md)
   * [Basic usage](usage.md)
   
docs/introduction.md::

   Introduction
   ============
   
   This is self documenting...
   

TODO
====
* Tags not currently supported
* Support PyIssues based issue tracking within the interface
* Investigate whether we could OAuth and enable writing of repos.