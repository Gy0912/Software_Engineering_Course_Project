import subprocess
import re

def get_final_first_movement(xml_path, query_path):
    command = ["verifyta", "-t1", "-f", "--strategy=shortest", xml_path, query_path]
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        output = result.stdout
        print(output)

    except subprocess.CalledProcessError as e:
        print("❌ verifyta运行出错:")
        print(e.stderr)
        return None

# 调用示例
get_final_first_movement("Check_tool.xml", "Check_tool.q")
