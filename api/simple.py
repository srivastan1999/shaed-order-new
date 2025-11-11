"""
Minimal test endpoint to verify Vercel Python function works
"""
import json

def handler(event, context):
    """Simple handler that doesn't require any imports"""
    try:
        return {
            'statusCode': 200,
            'body': json.dumps({
                'status': 'ok',
                'message': 'Simple endpoint works!',
                'event': str(event)[:200] if event else 'No event'
            }),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            }
        }
    except Exception as e:
        import traceback
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e),
                'traceback': traceback.format_exc()
            }),
            'headers': {'Content-Type': 'application/json'}
        }

