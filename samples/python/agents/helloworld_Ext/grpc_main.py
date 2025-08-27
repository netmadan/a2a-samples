import asyncio
import logging

import asyncclick as click
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
from grpc_reflection.v1alpha import reflection
from grpc_agent_executor import HelloWorldGrpcAgentExecutor  # type: ignore[import-untyped]


logging.basicConfig(level=logging.INFO)


@click.command()
@click.option('--host', 'host', default='localhost')
@click.option('--port', 'port', default=50051)
async def main(host: str, port: int) -> None:
    """Starts the HelloWorld gRPC Agent server."""
    
    # Define agent skills
    skill = AgentSkill(
        id='hello_world_grpc',
        name='Returns hello world via gRPC',
        description='Returns a hello world message using gRPC transport',
        tags=['hello world', 'grpc'],
        examples=['hi', 'hello world', 'greet me'],
    )

    extended_skill = AgentSkill(
        id='super_hello_world_grpc',
        name='Returns a SUPER Hello World via gRPC',
        description='A more enthusiastic greeting using gRPC, only for authenticated users.',
        tags=['hello world', 'super', 'extended', 'grpc'],
        examples=['super hi', 'give me a super hello via grpc'],
    )

    # Public agent card for gRPC
    public_agent_card = AgentCard(
        name='Hello World gRPC Agent',
        description='A hello world agent using gRPC transport',
        url=f'{host}:{port}',
        version='1.0.0',
        default_input_modes=['text'],
        default_output_modes=['text'],
        capabilities=AgentCapabilities(streaming=True),
        skills=[skill],
        preferred_transport=TransportProtocol.grpc,
        supports_authenticated_extended_card=True,
    )

    # Extended agent card
    extended_agent_card = public_agent_card.model_copy(
        update={
            'name': 'Hello World gRPC Agent - Extended Edition',
            'description': 'The full-featured hello world agent using gRPC for authenticated users.',
            'version': '1.0.1',
            'skills': [skill, extended_skill],
        }
    )

    # Create agent executor and request handler
    agent_executor = HelloWorldGrpcAgentExecutor()
    request_handler = DefaultRequestHandler(
        agent_executor=agent_executor,
        task_store=InMemoryTaskStore(),
    )

    # Create gRPC server
    server = grpc.aio.server()
    a2a_pb2_grpc.add_A2AServiceServicer_to_server(
        GrpcHandler(public_agent_card, request_handler),
        server,
    )

    # Enable reflection for debugging
    SERVICE_NAMES = (
        a2a_pb2.DESCRIPTOR.services_by_name['A2AService'].full_name,
        reflection.SERVICE_NAME,
    )
    reflection.enable_server_reflection(SERVICE_NAMES, server)

    # Start the server
    listen_addr = f'[::]:{port}'
    server.add_insecure_port(listen_addr)
    
    print(f'Starting HelloWorld gRPC server on {listen_addr}')
    print(f'Transport Protocol: gRPC')
    print(f'Agent Card: {public_agent_card.name}')
    print('Press Ctrl+C to stop the server')
    
    await server.start()
    
    try:
        await server.wait_for_termination()
    except KeyboardInterrupt:
        print("\nReceived interrupt signal, shutting down...")
        await server.stop(5)


if __name__ == '__main__':
    asyncio.run(main())