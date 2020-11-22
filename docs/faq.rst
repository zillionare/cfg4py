FAQ
===
- Q. What is schema.py? ::

  A. It's generated for code completion. It's safe to keep it in both development environment and release package. Don't try to instantiate it (an TypeError will raise to prevent from instantiate it), you should only use it for typing annotation.