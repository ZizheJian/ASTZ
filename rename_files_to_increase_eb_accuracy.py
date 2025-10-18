import os,re

def rename_files(directory):
    # 正则匹配：匹配像 3e-04 或 9e-05 的科学计数法部分
    pattern=re.compile(r'([1-9])e-0(\d)')

    for filename in os.listdir(directory):
        match=pattern.search(filename)
        if match:
            old_path=os.path.join(directory,filename)

            # 将匹配到的部分变为一位小数形式，例如 3e-04 -> 3.0e-04
            new_filename=pattern.sub(r'\1.0e-0\2', filename)
            new_path=os.path.join(directory,new_filename)

            # 避免覆盖已有文件
            if os.path.exists(new_path):
                print(f"⚠️ 目标文件已存在，跳过: {new_filename}")
                continue
            
            print(f"准备重命名: {filename} -> {new_filename}")
            flag=input("确认重命名？(y/n): ").strip().lower()
            if flag not in ('', 'y'):
                continue
            os.rename(old_path,new_path)
            print(f"重命名: {filename}->{new_filename}")
            print()

# 使用示例
if __name__=="__main__":
    directory="/work/hdd/bdgi/zjian1/APS_DYS/xpcs_datasets/APSU_TestData_004/blocks"
    rename_files(directory)