import os,csv

def add_csv_record(csv_path,rel_eb_str,compressor,cr,psnr):
    rows=[]
    found=False
    with open(csv_path,mode='r',newline='') as f:
        reader=csv.DictReader(f)
        fieldnames=reader.fieldnames
        for row in reader:
            if row["rel_eb"]==rel_eb_str:
                row[compressor+"_CR"]=f"{cr:.3f}"
                row[compressor+"_PSNR"]=f"{psnr:.3f}"
                found=True
            rows.append(row)

    if not found:
        rows.append({"rel_eb":rel_eb_str,compressor+"_CR":f"{cr:.3f}",compressor+"_PSNR":f"{psnr:.3f}"})

    with open(csv_path,mode='w',newline='') as f:
        writer = csv.DictWriter(f,fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)