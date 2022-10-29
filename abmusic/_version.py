from dataclasses import dataclass

__version__ = "1.0.0b1"


@dataclass
class VersionInfo:
    major: int
    minor: int
    micro: int
    releaselevel: str
    serial: int


version_info = VersionInfo(1, 0, 0, "beta", 1)
