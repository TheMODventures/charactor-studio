from app.shared.base_repository import Repository
from app.generations.generation_model import Generation


class GenerationRepository(Repository):
    model = Generation
