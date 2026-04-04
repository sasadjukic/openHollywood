
import unittest
from unittest.mock import MagicMock, patch
from app.models.types import SceneConfig, Character, Genre
from app.orchestrator.scene_orchestrator import SceneOrchestrator
from app.models.types import DialogueTurn, DirectorState
from app.core.llm_provider import ChatResponse

class TestDirectorFlow(unittest.TestCase):
    def setUp(self):
        self.character1 = Character(name="Priest", constitution="A holy man.")
        self.character2 = Character(name="Sinner", constitution="A guilty man.")
        self.config = SceneConfig(
            title="Test Scene",
            genre=Genre.DRAMA,
            characters=[self.character1, self.character2],
            scene_context="A dark confessional.",
            director_system_prompt="You are a director.",
            max_turns=2,
            min_turns=1
        )

    @patch('app.core.llm_provider.LLMClientFactory.create')
    def test_execute_scene_flow(self, mock_factory_create):
        # Mock LLM client
        mock_llm_client = MagicMock()
        mock_factory_create.return_value = mock_llm_client
        
        # 1. Briefing response
        briefing_response = ChatResponse(
            message='{"chosen_ending": "ABSOLUTION", "pacing_notes": "Start slow, end with mercy."}',
            stop_reason="end_turn",
            provider="ollama"
        )
        
        # 2. Character response
        character_response = ChatResponse(
            message="Hello my son.",
            stop_reason="end_turn",
            provider="ollama"
        )
        
        # 3. Director evaluation response
        director_eval_response = ChatResponse(
            message='{"turn_count": 1, "emotional_arc": "tension", "arc_stages_hit": ["opening"], "unresolved_threads": ["sin"], "resolved_threads": [], "closure_detected": false, "scene_end": false, "stage_direction": "Keep it tense."}',
            stop_reason="end_turn",
            provider="ollama"
        )
        
        mock_llm_client.chat.side_effect = [
            briefing_response,      # Briefing
            character_response,      # Priest turn 1
            character_response,      # Sinner turn 1
            director_eval_response,  # Director turn 1
            character_response,      # Priest turn 2
            character_response,      # Sinner turn 2
            director_eval_response   # Director turn 2
        ]

        orchestrator = SceneOrchestrator(self.config)
        
        # track turns
        turns_received = []
        def on_turn_callback(turn, director_state):
            turns_received.append((turn, director_state))

        result = orchestrator.execute_scene(on_turn_callback=on_turn_callback)

        # Verify briefing was called
        self.assertEqual(orchestrator.chosen_ending, "ABSOLUTION")
        self.assertEqual(orchestrator.pacing_notes, "Start slow, end with mercy.")
        
        # Verify orchestration calls
        # 1 briefing + 2 turns * (2 characters + 1 director) = 7 calls
        self.assertEqual(mock_llm_client.chat.call_count, 7)
        
        # Verify director state in result
        self.assertEqual(result.director_state.target_ending, "ABSOLUTION")
        self.assertEqual(result.director_state.pacing_notes, "Start slow, end with mercy.")
        
        # Verify callback was called for each character
        # char1, char2, char1, char2
        self.assertEqual(len(turns_received), 4)

if __name__ == '__main__':
    unittest.main()
