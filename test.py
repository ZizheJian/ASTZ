import subprocess

command = "ping -c 5 google.com"  # 一个有持续输出的命令
process = subprocess.Popen(command, shell=True, encoding="utf-8", stdout=subprocess.PIPE, stderr=subprocess.PIPE)

output_lines = []
for line in iter(process.stdout.readline, ''):
    print(line, end="", flush=True)  # 立即输出，不受缓冲影响
    output_lines.append(line)

output = "".join(output_lines)  # 存储完整输出