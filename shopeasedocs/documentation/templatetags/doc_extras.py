from django import template
from django.utils.safestring import mark_safe
import markdown as md
from pygments import highlight
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.formatters import HtmlFormatter

register = template.Library()


@register.filter(name='markdown_render')
def markdown_render(value):
    """Render Markdown text to HTML with syntax highlighting."""
    if not value:
        return ''
    extensions = [
        'markdown.extensions.fenced_code',
        'markdown.extensions.codehilite',
        'markdown.extensions.tables',
        'markdown.extensions.toc',
        'markdown.extensions.nl2br',
    ]
    extension_configs = {
        'codehilite': {
            'css_class': 'highlight',
            'linenums': False,
        },
    }
    html = md.markdown(value, extensions=extensions, extension_configs=extension_configs)
    return mark_safe(html)


@register.filter(name='pygments_highlight')
def pygments_highlight(code, language='python'):
    """Highlight code using Pygments."""
    if not code:
        return ''
    try:
        lexer = get_lexer_by_name(language, stripall=True)
    except Exception:
        lexer = guess_lexer(code)
    formatter = HtmlFormatter(cssclass='highlight', linenos=True)
    return mark_safe(highlight(code, lexer, formatter))
