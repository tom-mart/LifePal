"""
Universal Tool Executors

Handles execution of tools based on their type (script, lambda, webhook).
"""

import subprocess
import json
import logging
import time
import httpx
from typing import Dict, Any
from django.conf import settings

logger = logging.getLogger(__name__)


class ToolExecutor:
    """
    Universal tool executor.
    Routes to appropriate execution method based on tool type.
    """
    
    @staticmethod
    def execute(tool, parameters: dict, user) -> dict:
        """
        Execute a tool based on its execution type.
        
        Args:
            tool: ToolDefinition instance
            parameters: Tool parameters
            user: User instance
            
        Returns:
            dict: Execution result
        """
        from .models import ToolExecution
        
        start_time = time.time()
        
        try:
            # Route to appropriate executor
            if tool.execution_type == 'script':
                result = ScriptExecutor.execute(tool, parameters, user)
            elif tool.execution_type == 'lambda':
                result = LambdaExecutor.execute(tool, parameters, user)
            elif tool.execution_type == 'webhook':
                result = WebhookExecutor.execute(tool, parameters, user)
            else:
                raise ValueError(f"Unknown execution type: {tool.execution_type}")
            
            execution_time = int((time.time() - start_time) * 1000)
            
            # Log successful execution
            ToolExecution.objects.create(
                tool=tool,
                user=user,
                parameters=parameters,
                result=result,
                status='success',
                execution_time_ms=execution_time
            )
            
            # Update tool statistics
            tool.update_stats(success=True, execution_time_ms=execution_time)
            
            logger.info(f"Tool {tool.name} executed successfully in {execution_time}ms")
            
            return result
            
        except Exception as e:
            execution_time = int((time.time() - start_time) * 1000)
            
            logger.error(f"Tool execution error: {tool.name}", exc_info=True)
            
            # Log failed execution
            ToolExecution.objects.create(
                tool=tool,
                user=user,
                parameters=parameters,
                status='error',
                error_message=str(e),
                execution_time_ms=execution_time
            )
            
            # Update tool statistics
            tool.update_stats(success=False, execution_time_ms=execution_time)
            
            return {
                'success': False,
                'error': str(e),
                'message': f'Tool execution failed: {str(e)}'
            }


class ScriptExecutor:
    """Execute Python scripts"""
    
    @staticmethod
    def execute(tool, parameters: dict, user) -> dict:
        """
        Execute a Python script.
        
        Script receives JSON via stdin and returns JSON via stdout.
        
        Input format:
        {
            "user_id": 123,
            "user_email": "user@example.com",
            "parameters": {...}
        }
        
        Output format:
        {
            "success": true,
            "message": "...",
            ...
        }
        """
        # Prepare input
        input_data = {
            'user_id': user.id,
            'user_email': user.email,
            'username': user.username,
            'parameters': parameters
        }
        
        try:
            # Execute script
            result = subprocess.run(
                ['python', tool.script_path],
                input=json.dumps(input_data),
                capture_output=True,
                text=True,
                timeout=tool.script_timeout
            )
            
            if result.returncode != 0:
                raise Exception(f"Script error: {result.stderr}")
            
            # Parse output
            try:
                return json.loads(result.stdout)
            except json.JSONDecodeError:
                raise Exception(f"Script output is not valid JSON: {result.stdout[:200]}")
            
        except subprocess.TimeoutExpired:
            raise Exception(f"Script timeout after {tool.script_timeout}s")
        except FileNotFoundError:
            raise Exception(f"Script not found: {tool.script_path}")


class LambdaExecutor:
    """Execute AWS Lambda functions"""
    
    @staticmethod
    def execute(tool, parameters: dict, user) -> dict:
        """Execute AWS Lambda function"""
        try:
            import boto3
        except ImportError:
            raise Exception("boto3 not installed. Install with: pip install boto3")
        
        lambda_client = boto3.client(
            'lambda',
            region_name=tool.lambda_region
        )
        
        # Prepare payload
        payload = {
            'user_id': user.id,
            'user_email': user.email,
            'username': user.username,
            'parameters': parameters
        }
        
        try:
            response = lambda_client.invoke(
                FunctionName=tool.lambda_function_arn,
                InvocationType='RequestResponse',
                Payload=json.dumps(payload)
            )
            
            # Parse response
            result = json.loads(response['Payload'].read())
            
            # Check for Lambda errors
            if 'errorMessage' in result:
                raise Exception(result['errorMessage'])
            
            return result
            
        except Exception as e:
            raise Exception(f"Lambda execution error: {str(e)}")


class WebhookExecutor:
    """Execute external webhooks"""
    
    @staticmethod
    def execute(tool, parameters: dict, user) -> dict:
        """Call external webhook (synchronous)"""
        
        # Prepare payload
        payload = {
            'user_id': user.id,
            'user_email': user.email,
            'username': user.username,
            'parameters': parameters
        }
        
        # Prepare headers
        headers = tool.webhook_headers.copy() if tool.webhook_headers else {}
        headers['Content-Type'] = 'application/json'
        
        try:
            # Use synchronous httpx client
            with httpx.Client(timeout=tool.webhook_timeout) as client:
                if tool.webhook_method == 'GET':
                    response = client.get(
                        tool.webhook_url,
                        params=parameters,
                        headers=headers
                    )
                else:
                    response = client.post(
                        tool.webhook_url,
                        json=payload,
                        headers=headers
                    )
                
                response.raise_for_status()
                
                try:
                    return response.json()
                except json.JSONDecodeError:
                    raise Exception("Webhook response is not valid JSON")
                
        except httpx.TimeoutException:
            raise Exception(f"Webhook timeout after {tool.webhook_timeout}s")
        except httpx.HTTPError as e:
            raise Exception(f"Webhook HTTP error: {str(e)}")
