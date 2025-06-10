class WorldObject():
    def __init__(self, id: int):
        self.mesh_id: int = id
        self.pos: list[int] = [0, 0, 0]
        self.rotation: int = 0

    def move(self, newPosition: list[int]) -> None:
        self.pos = newPosition

    def rotate(self, newRotation: int) -> None:
        self.rotation = newRotation

    def to_dict(self) -> dict:
        return {
            "mesh_id": self.mesh_id,
            "pos": self.pos,
            "rotation": self.rotation
        }

    @staticmethod
    def from_dict(data: dict) -> "WorldObject":
        obj = WorldObject(data["mesh_id"])
        obj.pos = data["pos"]
        obj.rotation = data["rotation"]
        return obj

