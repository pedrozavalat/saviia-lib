from .types.get_events_types import GetEventsUseCaseInput, GetEventsUseCaseOutput

class GetEventsUseCase:
    def __init__(self, input: GetEventsUseCaseInput) -> None:
        pass
    
    async def execute(self) -> GetEventsUseCaseOutput:
        return GetEventsUseCaseOutput([])