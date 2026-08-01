# ================================================================================================================================
# Proxy design pattern is a structural design pattern that provides a substitute or placeholder object for another object to control access to it.
#
# The proxy has the same interface as the real object, so the client can use the proxy without knowing whether it is communicating with the real object or the proxy.
#
# When to use:
# - When access control is required.
# - When creating an object is expensive (Virtual Proxy).
# - When we need lazy initialization.
# - When we need logging, caching, or security checks.
#
# Lazy Initialization is a technique where an object is created only when it is first needed, instead of during application startup. It improves startup time and saves memory by avoiding unnecessary object creation.
#
# Singleton → Delay creating the single instance until it's first needed.
# Proxy     → Delay creating the real object until it's first accessed.
#
# Eager Initialization --The object is created immediately.
#
# Example: Movie streaming service.
# Real object: Movie -> Plays the actual movie.
# Proxy: MovieProxy -> Checks subscription before allowing playback.
# ================================================================================================================================

from abc import ABC, abstractmethod

class MovieInterface(ABC):
    @abstractmethod
    def play(self):
        pass

class Movie(MovieInterface):
    def play(self):
        print("Playing movie...")

class MovieProxy(MovieInterface):
    def __init__(self,movie,is_subscribed):
        self.movie = movie
        self.is_subscribed=is_subscribed

    def play(self):
        if self.is_subscribed:
            print("Access granted")
            self.movie.play()
        else:
            print("Access denied")

if __name__=="__main__":
    movie = Movie()
    proxy = MovieProxy(movie,True)
    proxy.play()