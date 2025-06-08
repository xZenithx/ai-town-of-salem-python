# LLM agent wrapper for player AI
from ollama import AsyncClient

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from game.player import Player
    from game.roles.mayor import Mayor
    from game.parser import PlayerResponse

reference_num: int = 0

class LLMAgent:
    # nemotron-mini:4b
    # gemma3:4b
    def __init__(self, player: 'Player', model_name: str = "gemma3:4b", system_prompt: str = "", ):
        self.model_name: str = model_name
        self.system_prompt: str = system_prompt
        self.player: 'Player' = player
        self.client: AsyncClient = AsyncClient()

    async def chat(self, player_prompt: str) -> 'PlayerResponse':
        global reference_num
        # save the prompt for debugging
        _reference_num: str = self.player.name + "_" + str(reference_num)
        reference_num += 1
        with open(f"prompts/debug_prompt_{_reference_num}.txt", "w", encoding="utf-8") as f:
            f.write(self.system_prompt + "\n" + player_prompt)
        
        response = await self.client.chat(
            model=self.model_name,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": player_prompt}
            ],
            options={"num_ctx": 8192}  # Set context window to 8192 tokens (adjust as needed)
        )
        from game.parser import PlayerResponse
        llm_response = PlayerResponse(response['message']['content'])

        with open(f"response/debug_response_{_reference_num}.txt", "w", encoding="utf-8") as f:
            f.write(response['message']['content'])

        return llm_response
