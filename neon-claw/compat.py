"""
Starlette / FastAPI compatibility shim for modern Starlette releases
Ensures Router and FastAPI initialize smoothly on newer Starlette versions.
"""

try:
    import starlette.routing
    _orig_router_init = starlette.routing.Router.__init__
    def _patched_router_init(self, *args, on_startup=None, on_shutdown=None, **kwargs):
        return _orig_router_init(self, *args, **kwargs)
    starlette.routing.Router.__init__ = _patched_router_init

    import fastapi
    if not hasattr(fastapi.FastAPI, "max_body_size"):
        fastapi.FastAPI.max_body_size = None
except Exception:
    pass
