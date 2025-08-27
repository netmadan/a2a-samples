#!/usr/bin/env python3

import asyncio
import logging

try:
    import grpc
    from a2a.grpc import a2a_pb2, a2a_pb2_grpc
    from a2a.server.request_handlers import DefaultRequestHandler, GrpcHandler
    from a2a.server.tasks import InMemoryTaskStore
    from a2a.types import (
        AgentCapabilities,
        AgentCard,
        AgentSkill,
        TransportProtocol,
    )
    from grpc_agent_executor import HelloWorldGrpcAgentExecutor
    
    print("✅ All imports successful")
    
    async def test_simple_grpc():
        print("🚀 Creating agent card...")
        
        skill = AgentSkill(
            id='hello_world_grpc',
            name='Returns hello world via gRPC',
            description='Returns a hello world message using gRPC transport',
            tags=['hello world', 'grpc'],
            examples=['hi', 'hello world'],
        )

        agent_card = AgentCard(
            name='Hello World gRPC Agent',
            description='A hello world agent using gRPC transport',
            url='localhost:50051',
            version='1.0.0',
            default_input_modes=['text'],
            default_output_modes=['text'],
            capabilities=AgentCapabilities(streaming=True),
            skills=[skill],
            preferred_transport=TransportProtocol.grpc,
        )
        
        print("✅ Agent card created")
        
        # Create components
        agent_executor = HelloWorldGrpcAgentExecutor()
        request_handler = DefaultRequestHandler(
            agent_executor=agent_executor,
            task_store=InMemoryTaskStore(),
        )
        
        print("✅ Components created")
        
        # Create server
        server = grpc.aio.server()
        a2a_pb2_grpc.add_A2AServiceServicer_to_server(
            GrpcHandler(agent_card, request_handler),
            server,
        )
        
        print("✅ gRPC server configured")
        
        # Add port and start
        listen_addr = '[::]:50051'
        server.add_insecure_port(listen_addr)
        
        print(f"🚀 Starting server on {listen_addr}")
        await server.start()
        
        print("✅ Server started successfully!")
        
        # Keep running for a bit
        await asyncio.sleep(5)
        
        print("🛑 Stopping server...")
        await server.stop(5)
        print("✅ Server stopped")
    
    if __name__ == '__main__':
        asyncio.run(test_simple_grpc())
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()