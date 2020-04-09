- What is cfg4py_auto_gen.py?
    It's generated only for code complete. It's safe to keep it in both development environment and release package.
Don't try to instantiate it (an TypeError will raise to prevent from instantiate it), you should only use it for typing
annotation.
