import os,shutil

times=16
chunk_size=50*1024*1024
file_num_in_chunk=0
chunk_current_size=0
chunk_num=0

for i in range(times):
    for i0 in range(4):
        for i1 in range(4):
            for i2 in range(4):
                file_name=f"APSU_TestData_004_cut.bin_{i0}{i1}{i2}.fhde"
                file_size=os.path.getsize(file_name)
                with open(file_name,"rb") as f:
                    data=f.read()
                    if file_num_in_chunk==0 or chunk_current_size+file_size<=chunk_size:
                        with open(f"chunk_{chunk_num}","ab") as f_chunk:
                            f_chunk.write(data)
                            chunk_current_size += file_size
                            file_num_in_chunk += 1
                    else:
                        chunk_num+=1
                        with open(f"chunk_{chunk_num}","wb") as f_chunk:
                            f_chunk.write(data)
                            chunk_current_size = file_size
                            file_num_in_chunk = 1