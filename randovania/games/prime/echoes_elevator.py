import copy
import re
from collections import defaultdict
from typing import NamedTuple, List, Dict, TextIO, Optional

from randovania.games.prime import claris_random, binary_data
from randovania.resolver.game_patches import GamePatches

RANDOMIZER_VERSION = "3.2"


class Elevator:
    world_number: int
    area_number: int
    world_asset_id: int
    area_asset_id: int
    instance_id: int
    destination_world: int
    destination_area: int
    connected_elevator: "Elevator"

    def __init__(self, world_number, area_number, world_id, area_id, instance_id, destination_world, destination_area):
        self.world_number = world_number
        self.area_number = area_number
        self.world_asset_id = world_id
        self.area_asset_id = area_id
        self.instance_id = instance_id
        self.destination_world = destination_world
        self.destination_area = destination_area
        self.connected_elevator = None

    def connect_to(self, other: "Elevator"):
        self.destination_world = other.world_asset_id
        self.destination_area = other.area_asset_id
        other.destination_world = self.world_asset_id
        other.destination_area = self.area_asset_id
        self.connected_elevator = other
        other.connected_elevator = self
        
    @property
    def pretty_name(self):
        return "{} <> {}".format(elevator_id_to_name[self.instance_id], elevator_id_to_name[self.connected_elevator.instance_id])


echoes_elevators = [
    Elevator(1, 9, 1006255871, 2918020398, 589851, 2252328306, 2556480432),
    Elevator(1, 24, 1006255871, 1660916974, 1572998, 1119434212, 1473133138),
    Elevator(1, 30, 1006255871, 2889020216, 1966093, 1039999561, 1868895730),
    Elevator(1, 32, 1006255871, 1287880522, 2097251, 2252328306, 2399252740),
    Elevator(1, 51, 1006255871, 3455543403, 3342446, 464164546, 3528156989),
    Elevator(1, 54, 1006255871, 1345979968, 3538975, 2252328306, 408633584),
    Elevator(2, 0, 2252328306, 408633584, 152, 1006255871, 1345979968),
    Elevator(2, 6, 2252328306, 2556480432, 393260, 1006255871, 2918020398),
    Elevator(2, 8, 2252328306, 2399252740, 524321, 1006255871, 1287880522),
    Elevator(3, 0, 1119434212, 1473133138, 122, 1006255871, 1660916974),
    Elevator(3, 19, 1119434212, 2806956034, 1245307, 1039999561, 3479543630),
    Elevator(3, 45, 1119434212, 3331021649, 2949235, 464164546, 900285955),
    Elevator(4, 0, 1039999561, 1868895730, 129, 1006255871, 2889020216),
    Elevator(4, 33, 1039999561, 3479543630, 2162826, 1119434212, 2806956034),
    Elevator(4, 69, 1039999561, 3205424168, 4522032, 464164546, 3145160350),
    Elevator(5, 0, 464164546, 3528156989, 38, 1006255871, 3455543403),
    Elevator(5, 19, 464164546, 900285955, 1245332, 1119434212, 3331021649),
    Elevator(5, 25, 464164546, 3145160350, 1638535, 1039999561, 3205424168),
]


def try_randomize_elevators(randomizer: claris_random.Random) -> Optional[List[Elevator]]:
    elevator_database: List[Elevator] = copy.deepcopy(echoes_elevators)

    elevator_list = copy.copy(elevator_database)
    elevators_by_world: Dict[int, List[Elevator]] = defaultdict(list)
    for elevator in elevator_list:
        elevators_by_world[elevator.world_number].append(elevator)

    while elevator_list:
        source_elevators: List[Elevator] = max(elevators_by_world.values(), key=len)
        target_elevators: List[Elevator] = [
            elevator
            for elevator in elevator_list
            if elevator not in source_elevators
        ]
        source_elevator = source_elevators[0]
        target_elevator = target_elevators[randomizer.next_with_max(len(target_elevators) - 1)]

        source_elevator.connect_to(target_elevator)

        elevators_by_world[source_elevator.world_number].remove(source_elevator)
        elevators_by_world[target_elevator.world_number].remove(target_elevator)
        elevator_list.remove(source_elevator)
        elevator_list.remove(target_elevator)

    # TODO
    list3 = copy.copy(elevator_database)
    celevator_list3 = [list3[0]]
    while list3:
        celevator_list1 = []
        for celevator1 in celevator_list3:
            index = 0
            while index < len(list3):
                celevator2 = list3[index]
                if celevator2.world_number == celevator1.world_number or celevator2.area_asset_id == celevator1.destination_area:
                    celevator_list1.append(celevator2)
                    list3.remove(celevator2)
                else:
                    index += 1
        if celevator_list1:
            celevator_list3 = celevator_list1
        else:
            # Randomization failed
            return None

    return elevator_database


elevator_name_to_id: Dict[str, int] = {
    "Temple Grounds - Temple Transport C": 589851,
    "Temple Grounds - Transport to Agon Wastes": 1572998,
    "Temple Grounds - Transport to Torvus Bog": 1966093,
    "Temple Grounds - Temple Transport B": 2097251,
    "Temple Grounds - Transport to Sanctuary Fortress": 3342446,
    "Temple Grounds - Temple Transport A": 3538975,
    "Great Temple - Temple Transport A": 152,
    "Great Temple - Temple Transport C": 393260,
    "Great Temple - Temple Transport B": 524321,
    "Agon Wastes - Transport to Temple Grounds": 122,
    "Agon Wastes - Transport to Torvus Bog": 1245307,
    "Agon Wastes - Transport to Sanctuary Fortress": 2949235,
    "Torvus Bog - Transport to Temple Grounds": 129,
    "Torvus Bog - Transport to Agon Wastes": 2162826,
    "Torvus Bog - Transport to Sanctuary Fortress": 4522032,
    "Sanctuary Fortress - Transport to Temple Grounds": 38,
    "Sanctuary Fortress - Transport to Agon Wastes": 1245332,
    "Sanctuary Fortress - Transport to Torvus Bog": 1638535,
}

elevator_id_to_name = {
    elevator_id: name
    for name, elevator_id in elevator_name_to_id.items()
}
