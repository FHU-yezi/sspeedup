from pywebio.session import run_js


def patch_better_tabs() -> None:
    run_js(
        '$("label").map(function(_, x)' '{x.style = "flex-grow:1; text-align: center"})'
    )
