from dataclasses import dataclass

@dataclass
class GetEventsUseCaseInput:    
    pass

@dataclass
class GetEventsUseCaseOutput:
    events: list[dict]
    