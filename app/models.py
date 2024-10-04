from dataclasses import dataclass
from typing import List, Optional

@dataclass
class dependency:
    namespace: str
    name: str
    version: str

@dataclass
class project:
    modelVersion: str
    groupId: str
    artifactId: str
    version: str
    dependencies: List[dependency]

@dataclass
class metadata:
    id: int
    name: str
    description: Optional[str]
    createdAt: str
    updatedAt: str
    file: dict
    dependencies: List[dependency]
