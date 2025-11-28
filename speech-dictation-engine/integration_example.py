#!/usr/bin/env python3
"""
Integration Example: Connecting Person B → You → Person D

This shows how to receive from Person B (filler removal)
and send to Person D (tone stage)
"""
import requests
import sys
sys.path.insert(0, 'src')

from grammar_unified_pipeline_minilm import GrammarFormattingEngine, PipelineMessage

class GrammarStageIntegration:
    """
    Integration wrapper for Grammar Stage (Person C)
    """
    
    def __init__(self, person_d_url=None):
        """
        Initialize grammar engine and configure Person D's endpoint
        
        Args:
            person_d_url: URL of Person D's tone stage (e.g., "http://localhost:8001/process")
        """
        print("Initializing Grammar Stage...")
        self.engine = GrammarFormattingEngine()
        self.person_d_url = person_d_url
        print("✅ Grammar Stage Ready")
    
    def process_from_person_b(self, message_dict: dict) -> dict:
        """
        Process message received from Person B (filler removal stage)
        
        Args:
            message_dict: Dictionary from Person B with cleaned text
        
        Returns:
            Processed message ready for Person D
        """
        # Convert dict to PipelineMessage
        input_msg = PipelineMessage(**message_dict)
        
        print(f"\n[Person B → You] Received:")
        print(f"  ID: {input_msg.id}")
        print(f"  Chunk: {input_msg.chunk_index}")
        print(f"  Text: '{input_msg.text}'")
        print(f"  Event: {input_msg.event}")
        
        # Process through grammar engine
        output_msg = self.engine.process_message(input_msg)
        
        print(f"\n[You → Person D] Sending:")
        print(f"  ID: {output_msg.id}")
        print(f"  Chunk: {output_msg.chunk_index}")
        print(f"  Text: '{output_msg.text}'")
        print(f"  Event: {output_msg.event}")
        
        # Convert to dict for JSON
        return output_msg.model_dump()
    
    def forward_to_person_d(self, message_dict: dict):
        """
        Forward processed message to Person D (tone stage)
        
        Args:
            message_dict: Processed message from grammar stage
        """
        if not self.person_d_url:
            print("\n⚠️ Person D URL not configured. Message not forwarded.")
            return
        
        try:
            response = requests.post(
                self.person_d_url,
                json=message_dict,
                timeout=5
            )
            
            if response.status_code == 200:
                print(f"\n✅ Forwarded to Person D successfully")
                print(f"   Response: {response.json()}")
            else:
                print(f"\n❌ Person D returned error: {response.status_code}")
        
        except requests.exceptions.ConnectionError:
            print(f"\n❌ Could not connect to Person D at {self.person_d_url}")
        except Exception as e:
            print(f"\n❌ Error forwarding to Person D: {e}")
    
    def process_and_forward(self, message_dict: dict):
        """
        Complete flow: Receive from B → Process → Forward to D
        """
        # Process
        processed = self.process_from_person_b(message_dict)
        
        # Forward to Person D
        self.forward_to_person_d(processed)
        
        return processed


# ========== EXAMPLE USAGE ==========

if __name__ == "__main__":
    print("=" * 70)
    print("INTEGRATION EXAMPLE: Person B → You (Grammar) → Person D")
    print("=" * 70)
    
    # Initialize integration
    # TODO: Replace with actual Person D URL
    person_d_url = "http://localhost:8001/process"  # Person D's endpoint
    
    integration = GrammarStageIntegration(person_d_url=person_d_url)
    
    # Simulate messages from Person B
    test_messages = [
        {
            "id": "utterance_001",
            "chunk_index": 0,
            "text": "he go to the store yesterday",
            "event": "PART",
            "is_final": False,
            "end_of_speech_time": 1250.5
        },
        {
            "id": "utterance_001",
            "chunk_index": 1,
            "text": "and buy some milk",
            "event": "PART",
            "is_final": False,
            "end_of_speech_time": 2100.3
        },
        {
            "id": "utterance_001",
            "chunk_index": -1,
            "text": "",
            "event": "END_CLEAN",
            "is_final": True,
            "end_of_speech_time": 2500.0
        }
    ]
    
    print("\n" + "=" * 70)
    print("PROCESSING MESSAGES")
    print("=" * 70)
    
    for i, msg in enumerate(test_messages, 1):
        print(f"\n{'='*70}")
        print(f"MESSAGE {i}")
        print(f"{'='*70}")
        
        # Process and forward
        result = integration.process_and_forward(msg)
    
    print("\n" + "=" * 70)
    print("✅ Integration example completed!")
    print("=" * 70)
    print("\nNext steps:")
    print("1. Get Person B's actual endpoint and connect")
    print("2. Get Person D's actual endpoint and configure above")
    print("3. Deploy your service at a fixed URL")
    print("4. Share your URL with Person B: http://your-host:8000/process")
