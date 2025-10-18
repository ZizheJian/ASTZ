import os,csv

def check_csv_record(csv_path,rel_eb_str,compressor):
    with open(csv_path,mode='r',newline='') as f:
        reader=csv.DictReader(f)
        for row in reader:
            if row["rel_eb"]==rel_eb_str:
                if row.get(compressor+"_CR") and row.get(compressor+"_PSNR"):
                    return True
                else:
                    return False
    return False