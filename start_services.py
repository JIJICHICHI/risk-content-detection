import subprocess
import time
import os


def run_flask_app(script_path, env_name, port, cwd):
    """
    在指定的 Conda 环境中运行 Flask 应用，并指定工作目录
    """
    command = f'cmd /c "conda activate {env_name} && python {script_path}"'
    subprocess.Popen(command, shell=True, cwd=cwd)  # 设置工作目录
    print(f"已启动 {script_path} - 端口: {port}")
    time.sleep(3)  # 等待服务启动


def run_vue():
    """
    启动 Vue 前端
    """
    vue_dir = r"C:\Users\几迟\Desktop\毕业论文\risk_content_detection\frontend"
    command = 'cmd /c "npm run dev"'
    subprocess.Popen(command, shell=True, cwd=vue_dir)  # 设置 Vue 目录
    print("已启动 Vue 前端")


if __name__ == "__main__":
    # 启动 Flask API（不同的工作目录）
    run_flask_app(
        script_path=r"image_api.py",
        env_name="base",
        port=8080,
        cwd=r"C:\Users\几迟\Desktop\毕业论文\risk_content_detection\image_detection\generalImageClassification-master"
    )

    run_flask_app(
        script_path=r"textapi.py",  # 你的 Flask 应用代码文件路径
        env_name="base",
        port=5000,
        cwd=r"C:\Users\几迟\Desktop\毕业论文\risk_content_detection\text_detection\bert_classfication-master"
    )

    # start_services.py 中的配置
    run_flask_app(
        script_path=r"2.py",
        env_name="codecfake",
        port=5001,  # 正确端口
        cwd=r"C:\Users\几迟\Desktop\毕业论文\risk_content_detection\audio_detection\Codecfake-main\Codecfake-main"
    )

    # 启动 Vue 前端
    run_vue()

    print("所有服务已启动！")
