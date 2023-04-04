from typing import Callable

from pywebio.io_ctrl import output_register_callback as get_callback_id
from pywebio.session import run_js


def on_enter_pressed(pin_name: str, func: Callable[[], None]) -> None:
    def func_to_bind(_: None) -> None:
        func()

    callback_id = get_callback_id(func_to_bind)
    run_js(
        """
        $("input[name=\'%s\']").keyup(function(e){
            if(e.which == "13"){
                WebIO.pushData(null, callback_id)
            }
        });
        """
        % pin_name,
        pin_name=pin_name,
        callback_id=callback_id,
    )
