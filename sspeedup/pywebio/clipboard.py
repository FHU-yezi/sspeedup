from pywebio.session import run_js


def copy_to_clipboard(text: str) -> None:
    # 参见：https://juejin.cn/post/7119169721081004069
    run_js(
        """
        const copyDom = document.createElement("textarea");
        copyDom.value = "%s";
        document.body.appendChild(copyDom);
        setTimeout(() => {
            copyDom.select();
            document.execCommand("Copy");
            document.body.removeChild(copyDom);
        }, 100);
        """
        % text
    )
