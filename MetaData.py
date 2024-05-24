from dataclasses import dataclass,field

@dataclass
class MetaData:
    resolution_time : float
    objective_value : float
    misc : dict[str : object] = field(default_factory= lambda : {})
