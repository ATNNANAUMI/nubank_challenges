"""Minimal stand-in for CodeSignal's timeout_decorator so the suite runs
locally. Uses SIGALRM (Unix). On platforms without SIGALRM it becomes a no-op.
"""
import functools

try:
    import signal

    class TimeoutError(Exception):
        pass

    def timeout(seconds):
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                def _handler(signum, frame):
                    raise TimeoutError(f"Timed out after {seconds}s")
                old = signal.signal(signal.SIGALRM, _handler)
                signal.setitimer(signal.ITIMER_REAL, seconds)
                try:
                    return func(*args, **kwargs)
                finally:
                    signal.setitimer(signal.ITIMER_REAL, 0)
                    signal.signal(signal.SIGALRM, old)
            return wrapper
        return decorator
except Exception:  # pragma: no cover
    pass
