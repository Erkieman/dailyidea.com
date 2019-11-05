import logging
import os
from ..utils.mail_sender import send_mail_to_user
from jinja2 import Template
import boto3
from ..utils.json_util import loads
from datetime import datetime

client = boto3.client('dynamodb', region_name=os.environ['AWS_REGION'])

USERS_TABLE_NAME = os.environ['USERS_TABLE_NAME']
IDEAS_TABLE_NAME = os.environ['IDEAS_TABLE_NAME']
TAGS_TABLE_NAME = os.environ['TAGS_TABLE_NAME']

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_user_by_id(user_id: str) -> dict:
    resp = client.get_item(
        TableName=USERS_TABLE_NAME,
        Key={'userId': {'S': user_id}}
    )
    return resp.get('Item')


def get_idea_by_id(user_id: str, idea_id: str) -> dict:
    resp = client.get_item(
        TableName=IDEAS_TABLE_NAME,
        Key={'userId': {'S': user_id}, 'ideaId': {'S': idea_id}}
    )
    return resp.get('Item')


def get_idea_tags(idea_id: str):
    resp = client.query(
        TableName=TAGS_TABLE_NAME,
        IndexName='ideaTags',
        KeyConditionExpression="ideaId = :ideaId",
        ExpressionAttributeValues={":ideaId": {"S": idea_id}},
    )
    return map(lambda raw_tag: raw_tag['tag']['S'], resp.get('Items', []))


def endpoint(event, context):
    # logger.info(event)
    idea_id = event.get('ideaId')
    email = event.get('email')
    user_id = event.get('identity').get('username')

    sender_user = get_user_by_id(user_id)
    idea_to_send = get_idea_by_id(user_id, idea_id)
    idea_tags = get_idea_tags(idea_id)
    if idea_to_send is None:
        return {'ok': False, 'error': 'Idea Not Found'}

    SUBJECT = f"[Daily Idea] {sender_user['email']['S']} sent you Idea!"  # change to name
    BUCKET_URL_PREFIX = os.environ.get('BUCKET_URL_PREFIX')

    render_context = {
        "user": loads(sender_user),
        "tags": idea_tags,
        "BUCKET_URL_PREFIX": BUCKET_URL_PREFIX,
        "BASE_SITE_URL": f"https://{os.environ['DOMAIN_NAME']}/",
        "idea": loads(idea_to_send),
        "link_to_idea": f"https://{os.environ['DOMAIN_NAME']}/ideas/{user_id}/{idea_id}",
        "datetime": datetime,
    }

    with open('./functions/share_idea/share_idea.html') as html_template_file:
        html_template = Template(html_template_file.read())
        with open('./functions/share_idea/share_idea.txt') as txt_template_file:
            txt_template = Template(txt_template_file.read())
            html_content = html_template.render(**render_context)
            txt_content = txt_template.render(**render_context)
            send_mail_to_user(email, SUBJECT, txt_content, html_content)

    return {"ok": True}
