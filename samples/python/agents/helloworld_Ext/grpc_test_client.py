import asyncio
import logging
from uuid import uuid4

import grpc
from a2a.grpc import a2a_pb2, a2a_pb2_grpc


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_grpc_agent():
    """Test the HelloWorld gRPC agent."""
    
    # Connect to the gRPC server
    channel = grpc.aio.insecure_channel('localhost:50051')
    stub = a2a_pb2_grpc.A2AServiceStub(channel)
    
    try:
        # Test 1: Get Agent Card
        logger.info("Testing GetAgentCard...")
        agent_card_request = a2a_pb2.GetAgentCardRequest()
        agent_card_response = await stub.GetAgentCard(agent_card_request)
        logger.info(f"Agent Card Response: {agent_card_response}")
        
        # Test 2: Send Message
        logger.info("\nTesting SendMessage...")
        message = a2a_pb2.Message(
            role="user",
            parts=[a2a_pb2.Part(text=a2a_pb2.TextPart(text="Hello gRPC!"))],
            message_id=str(uuid4())
        )
        
        send_request = a2a_pb2.SendMessageRequest(
            id=str(uuid4()),
            params=a2a_pb2.MessageSendParams(message=message)
        )
        
        send_response = await stub.SendMessage(send_request)
        logger.info(f"Send Message Response: {send_response}")
        
        # Test 3: Send Streaming Message
        logger.info("\nTesting SendStreamingMessage...")
        stream_request = a2a_pb2.SendStreamingMessageRequest(
            id=str(uuid4()),
            params=a2a_pb2.MessageSendParams(message=message)
        )
        
        logger.info("Streaming responses:")
        async for response in stub.SendStreamingMessage(stream_request):
            logger.info(f"Stream chunk: {response}")
            
    except grpc.RpcError as e:
        logger.error(f"gRPC Error: {e.code()} - {e.details()}")
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        await channel.close()


if __name__ == '__main__':
    asyncio.run(test_grpc_agent())