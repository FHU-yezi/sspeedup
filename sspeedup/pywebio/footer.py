from pywebio.session import run_js


def set_footer(html: str) -> None:
    run_js(f"$('footer').html('{html}')")
