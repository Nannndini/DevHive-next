import sys
import os
import unittest
from unittest.mock import MagicMock, AsyncMock, patch

# Add frontend to path so 'api' is recognized as a package
sys.path.append(os.path.abspath("frontend"))

from api.services.ingestion_service import IngestionService

class TestSimilarityDeduplication(unittest.IsolatedAsyncioTestCase):
    @patch("api.services.ingestion_service.SessionLocal")
    @patch("api.services.ingestion_service.chunking_service")
    @patch("api.services.ingestion_service.embedding_service")
    async def test_similarity_dedup_threshold(self, mock_embedding, mock_chunking, mock_session_local):
        # 1. Setup mock chunking and embedding
        mock_chunking.chunk_text.return_value = ["This is a test chunk."]
        mock_embedding.batch_generate_embeddings = AsyncMock(return_value=[[0.1] * 384])
        
        # 2. Setup mock DB session
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db
        
        # Case A: Chunk is unique (duplicate check returns None) -> Should call INSERT
        mock_db.execute.reset_mock()
        mock_result_unique = MagicMock()
        mock_result_unique.fetchone.return_value = None
        mock_db.execute.return_value = mock_result_unique
        
        # Create IngestionService instance
        service = IngestionService()
        
        # Run unique chunk ingestion
        await service.process_document_async("test-doc-id", "test.txt", "This is a test chunk.")
        
        # Verify SELECT duplicate check was executed
        select_calls = [call for call in mock_db.execute.call_args_list if "SELECT id FROM document_chunks" in str(call[0][0])]
        self.assertEqual(len(select_calls), 1)
        
        # Verify the similarity threshold parameter is set to < 0.05 (which corresponds to > 0.95 similarity)
        query_str = select_calls[0][0][0].text
        self.assertTrue("< 0.05" in query_str, f"Deduplication threshold is incorrect in query: {query_str}")
        
        # Verify INSERT was called
        insert_calls = [call for call in mock_db.execute.call_args_list if "INSERT INTO document_chunks" in str(call[0][0])]
        self.assertEqual(len(insert_calls), 1)
        
        # Case B: Chunk is near-duplicate (duplicate check returns a row) -> Should SKIP INSERT
        mock_db.reset_mock()
        mock_result_duplicate = MagicMock()
        mock_result_duplicate.fetchone.return_value = (1,)  # match found
        mock_db.execute.return_value = mock_result_duplicate
        
        # Run duplicate chunk ingestion
        await service.process_document_async("test-doc-id", "test.txt", "This is a test chunk.")
        
        # Verify SELECT duplicate check was executed
        select_calls = [call for call in mock_db.execute.call_args_list if "SELECT id FROM document_chunks" in str(call[0][0])]
        self.assertEqual(len(select_calls), 1)
        
        # Verify INSERT was NOT called
        insert_calls = [call for call in mock_db.execute.call_args_list if "INSERT INTO document_chunks" in str(call[0][0])]
        self.assertEqual(len(insert_calls), 0)
        print("Similarity deduplication verification test passed successfully.")

if __name__ == "__main__":
    unittest.main()
