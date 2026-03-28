"""Support chatbot service with optional free local LLM and rule-based fallback."""

import logging
import os
from functools import lru_cache

logger = logging.getLogger(__name__)


RULES = [
    (
        ['order', 'track', 'status'],
        'You can track orders from Dashboard > Orders. If payment is complete and status is pending for long, contact support from the Contact page.',
    ),
    (
        ['return', 'refund'],
        'Open your order details and use the return request option for eligible items. Seller review is required before approval.',
    ),
    (
        ['delivery', 'shipping', 'ship'],
        'Delivery details are shown in each product and checkout summary. For exact timelines, use Chat with Seller on product page.',
    ),
    (
        ['payment', 'card', 'cod', 'gateway'],
        'We support secure payment gateways and cash on delivery where available. If payment fails, retry from checkout and verify your method.',
    ),
    (
        ['agent', 'seller', 'store'],
        'Tap the seller name on a product to open their storefront and browse all items from that seller.',
    ),
]


@lru_cache(maxsize=1)
def _get_llm_pipeline():
    """Load a free local Hugging Face model if enabled via env vars."""
    if os.getenv('SUPPORT_BOT_USE_LLM', '0').strip().lower() not in {'1', 'true', 'yes'}:
        return None

    model_name = os.getenv('SUPPORT_BOT_MODEL', 'google/flan-t5-small')

    try:
        from transformers import pipeline

        return pipeline('text2text-generation', model=model_name)
    except Exception as exc:
        logger.warning('Support LLM disabled due to load failure: %s', exc)
        return None


def _rule_reply(message):
    msg = (message or '').strip().lower()
    for keys, reply in RULES:
        if any(key in msg for key in keys):
            return reply
    return 'I can help with orders, returns, shipping, payments, and seller/store questions. For human support, please use the Contact page.'


def generate_support_reply(message):
    """Generate a support reply using local LLM if available, else fallback to rules."""
    text = (message or '').strip()
    if not text:
        return 'Please type your question and I will help.'

    llm = _get_llm_pipeline()
    if llm:
        prompt = (
            'You are a concise ecommerce customer-care assistant for Bhrikutimandap. '
            'Answer in 1 to 3 short sentences. If unsure, suggest using contact page support.\n'
            f'Customer question: {text}'
        )
        try:
            output = llm(prompt, max_new_tokens=96, do_sample=True, temperature=0.3)
            if output and isinstance(output, list):
                reply = (output[0].get('generated_text') or '').strip()
                if reply:
                    return reply
        except Exception as exc:
            logger.warning('Support LLM generation failed, using rule fallback: %s', exc)

    return _rule_reply(text)
