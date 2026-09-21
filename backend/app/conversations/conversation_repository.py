from app.shared.base_repository import Repository
from app.conversations.conversation_model import Conversation


class ConversationRepository(Repository):
    model = Conversation
