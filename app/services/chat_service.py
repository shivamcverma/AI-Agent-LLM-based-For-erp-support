from app.agents.agent import ERPAgent
from app.utils.logger import save_chat_log


class ChatService:

    def __init__(self):
        self.agent = ERPAgent()

    async def process_message(
        self,
        message: str,
        school_id: int,
        conversation_history: list[dict] | None = None,
        previous_understanding: dict | None = None
    ):

        result = await self.agent.process(
            message=message,
            school_id=school_id,
            conversation_history=conversation_history or [],
            previous_understanding=previous_understanding
        )

        save_chat_log(
            user_message=message,
            bot_response=result.get("response", ""),
            intent=result.get("intent", ""),
            confidence=result.get("confidence", 0)
        )

        return result