import os

def rename_or_delete_qoz_files(directory):
    for filename in os.listdir(directory):
        # 只匹配包含 "qoz" 但不包含 "qoz2" 的文件名
        if "qoz" in filename and "qoz2" not in filename:
            old_path = os.path.join(directory, filename)
            new_filename = filename.replace("qoz", "qoz2")
            new_path = os.path.join(directory, new_filename)

            if os.path.exists(new_path):
                # 若重名，则删除原文件
                os.remove(old_path)
                print(f"🗑️ 已删除：{filename}（因目标文件 {new_filename} 已存在）")
            else:
                os.rename(old_path, new_path)
                print(f"✅ 已重命名：{filename} → {new_filename}")

if __name__ == "__main__":
    directory = "/work/hdd/bdgi/zjian1/APS_DYS/xpcs_datasets/APSU_TestData_004/blocks"
    rename_or_delete_qoz_files(directory)