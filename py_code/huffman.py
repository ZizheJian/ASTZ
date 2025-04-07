import heapq
from collections import Counter
from typing import List
from bitarray import bitarray

# 定义 Huffman 树的节点类
class HuffmanNode:
    def __init__(self,value,freq):
        self.value:int=value  # 整数值
        self.freq:int=freq    # 频率
        self.left:"HuffmanNode"=None    # 左子节点
        self.right:"HuffmanNode"=None   # 右子节点
    
    # 用于堆比较
    def __lt__(self,other):
        return self.freq<other.freq

# 构建 Huffman 树并返回根节点
def build_huffman_tree(freq_dict)->"HuffmanNode":
    heap:List["HuffmanNode"]=[]
    # 将每个整数及其频率加入最小堆
    for value,freq in freq_dict.items():
        heapq.heappush(heap,HuffmanNode(value,freq))
    
    # 合并节点直到只剩一个
    while len(heap)>1:
        left=heapq.heappop(heap)
        right=heapq.heappop(heap)
        parent=HuffmanNode(None,left.freq+right.freq)
        parent.left=left
        parent.right=right
        heapq.heappush(heap,parent)
    
    return heap[0]  # 返回根节点

# 压缩 Huffman 树到 bitarray
def compress_huffman_tree(root:"HuffmanNode",max_num:int,min_num:int)->bitarray:
    compressed=bitarray()
    def preorder15(node:"HuffmanNode"):
        if node is None:
            return
        if node.value is not None:  # 叶子节点
            compressed.append(1)  # 1 表示叶子
            value_bits = bitarray(format(node.value & 0xFFFF, '016b'))
            compressed.extend(value_bits)
        else:  # 内部节点
            compressed.append(0)  # 0 表示内部节点
            preorder15(node.left)
            preorder15(node.right)
    def preorder31(node:"HuffmanNode"):
        if node is None:
            return
        if node.value is not None:  # 叶子节点
            compressed.append(1)  # 1 表示叶子
            # 将值转为 32 位二进制（假设整数是 32 位有符号）
            value_bits = bitarray(format(node.value & 0xFFFFFFFF, '032b'))
            compressed.extend(value_bits)
        else:  # 内部节点
            compressed.append(0)  # 0 表示内部节点
            preorder31(node.left)
            preorder31(node.right)
    
    if -32768<=min_num and max_num<=32767:
        compressed.append(0)
        preorder15(root)
    elif -2147483648<=min_num and max_num<=2147483647:
        compressed.append(1)
        preorder31(root)
    else:
        raise NotImplementedError("没有写qb超过2^31的情况")
    return compressed

# 生成 Huffman 编码表
def build_huffman_codes(root:HuffmanNode,current_code="",codes=None):
    if codes is None:
        codes={}
    
    # 到达叶子节点，记录编码
    if root.value is not None:
        codes[root.value]=current_code or "0"  # 如果只有一个节点，默认给 "0"
        return
    
    # 递归遍历左子树（0）和右子树（1）
    if root.left:
        build_huffman_codes(root.left,current_code+"0",codes)
    if root.right:
        build_huffman_codes(root.right,current_code+"1",codes)
    
    return codes

# 编码函数
def huffman_encode(numbers):
    if not numbers:
        return "",{}
    max_num=max(numbers)
    min_num=min(numbers)
    # 统计频率
    freq_dict=Counter(numbers)
    # 构建 Huffman 树
    root=build_huffman_tree(freq_dict)
    # 生成编码表
    huffman_codes=build_huffman_codes(root)
    
    # 对输入序列编码
    encoded_tree=compress_huffman_tree(root,max_num,min_num)
    encoded_main=bitarray()
    for num in numbers:
        encoded_main.extend(huffman_codes[num])
    encoded_tree_bits=len(encoded_tree)
    encoded_main_bits=len(encoded_main)
    result=bitarray()
    result.extend(format(encoded_tree_bits&0xFFFFFFFF,'032b'))
    result.extend(encoded_tree)
    result.extend(format(encoded_main_bits&0xFFFFFFFF,'032b'))
    result.extend(encoded_main)
    return result

# 解码函数
def huffman_decode(encoded,root):
    if not encoded:
        return []
    
    decoded=[]
    current_node=root
    
    # 遍历二进制字符串
    for bit in encoded:
        if bit == "0" and current_node.left:
            current_node=current_node.left
        elif bit == "1" and current_node.right:
            current_node=current_node.right
        
        # 到达叶子节点
        if current_node.value is not None:
            decoded.append(current_node.value)
            current_node=root  # 重置到根节点
    
    return decoded

# 主程序测试
if __name__ == "__main__":
    # 输入整数列表
    numbers=[1,2,2,3,3,3,4,4,4,4]
    print(f"原始数据: {numbers}")
    
    # 编码
    encoded,codes,root=huffman_encode(numbers)
    print(f"Huffman 编码表: {codes}")
    print(f"编码结果: {encoded}")
    
    # 解码
    decoded=huffman_decode(encoded,root)
    print(f"解码结果: {decoded}")
    
    # 验证
    print(f"是否正确: {numbers == decoded}")