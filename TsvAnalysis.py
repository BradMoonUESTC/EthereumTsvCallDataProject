import pandas as pd
# block_id	transaction_hash	index	depth	time
# failed	fail_reason	type	sender	recipient	child_call_count
# value	value_usd	transferred	input_hex	output_hex
import networkx as nx
from tqdm import tqdm, trange
import json

#
'''
另外一种重入的判别方式
之所以要考虑这种，是因为有的重入攻击可能仅发生一次
——————————————————————————————————————————————————————————————————————————————————————————————————
第一个例子：0xe1f375a47172b5612d96496a4599247049f07c9a7d518929fbe296b0c281e04d
https://cn.etherscan.com/tx/0xe1f375a47172b5612d96496a4599247049f07c9a7d518929fbe296b0c281e04d/advanced#internal
这次攻击是 Akropolis 重入攻击，利用了ERC20的transferFrom函数恶意代币重入

查看internal call 的4、4-0-3和4-0-3-0：
4	    deposit	        受害者	Generic		恶意代币	0	TRUE	0.2996
4-0-3	transferFrom	恶意代币	Generic		受害者	0	TRUE	0.1423!!!
4-0-3-0	deposit	        受害者	Generic		恶意代币	0	TRUE	0.1405

0x73fc3038b4cd8ffd07482b92a52ea806505e5748调用了0xe2307837524db8961c4541f943598654240bd62f恶意代币的transferFrom，
然后0xe2307837524db8961c4541f943598654240bd62f又调用了0x73fc3038b4cd8ffd07482b92a52ea806505e5748
——————————————————————————————————————————————————————————————————————————————————————————————————
第二个例子：再比如uniswap的这次重入：0x9cb1d93d6859883361e8c2f9941f13d6156a1e8daa0ebe801b5d0b5a612723c1
https://explorer.bitquery.io/zh/ethereum/tx/0x9cb1d93d6859883361e8c2f9941f13d6156a1e8daa0ebe801b5d0b5a612723c1/calls
利用了ERC777的hook

0xbd2250d713bf98b7e00c26e2907370ad30f0891a攻击者在5-0-2-1被调用tokensToSend时进行了重入
5-0-2-1	        tokensToSend	    Attacker	    		imToken	        0	TRUE	0.0015
5-0-2-1-1	    tokenToEthSwapInput	imToken Pool		    Attacker	    0	TRUE	0.0013
5-0-2-1-1-0-2	transferFrom	    imToken			        imToken Pool	0	TRUE	7.53E-04
5-0-2-1-1-0-2-1	tokensToSend	    Attacker	    	    imToken     	0	TRUE	6.84E-05
——————————————————————————————————————————————————————————————————————————————————————————————————
这种重入的考虑判别方法为：
1、首先搜索完全相同（caller，calee，functionname）的两次调用，具体为:
A->B functionA
？？？
？？？
？？？
A->B functionA
2、再在这中间搜索能够凑成B->A的调用
将中间的调用生成一张有向图，找通路

###
满足以上几个条件的调用即考虑为重入
————————————————————————————————————————————————————————————————————————————————————————————————————
但是 以上的判重对于2021年7月13日的cream finance无效，原因如下：
————————————————————————————————————————————————————————————————————————————————————————————————————
第三个例子：https://bloxy.info/tx/0x221c5e3f5b06b678c8f995badb151350cb93d6c6f5500c8b62606b1d57db3974
攻击者在当时发起了多比交易进行攻击，每笔交易都存在着重入，以上面这笔交易为例，它产生了1180个内部调用，非常复杂，但是实际上关键调用不多，请看下面：
我将不同的合约名进行修改，方便看出（攻击合约为A，恶意代币为B1与B2，受害合约分别为X Y Z）
2-9-2-1-3	            55a9f495	A	B1	staticcall																																																																
																																																																				
2-9-2-1-4	            borrow	    A	X	call																																																															
2-9-2-1-4-1	            borrow	    X	Y	delegatecall																																																																
																																																																				
2-9-2-1-4-1-4	        transfer	X	B1	call	  																																																															
2-9-2-1-4-1-4-0	        7a17edf7	B1	A	call																																																																
																																																																				
2-9-2-1-4-1-4-0-0	    55a9f495	A	B2	staticcall																																																																
																																																																				
2-9-2-1-4-1-4-0-1	    borrow	    A	Z	call																																																																
2-9-2-1-4-1-4-0-1-1	    borrow	    Z	Y	delegatecall																																																																
																																																																				
2-9-2-1-4-1-4-0-1-1-4	transfer	Z	B2	call																																																																
2-9-2-1-4-1-4-0-1-1-4-0	7a17edf7	B2	A	call
这次攻击的重入路径是A->X->B1-(*重入函数点)->A->Z->B2-(*重入函数点)->A
同时，这次攻击的调用树可查，并非所有调用都是call，如果只关注call，如下：
																																																																				
2-9-2-1-4	            borrow	    A	X	call																																																															
																																																																				
2-9-2-1-4-1-4	        transfer	X	B1	call																																																																
2-9-2-1-4-1-4-0	        7a17edf7	B1	A	call																																																																
																																																																				
																																																																				
2-9-2-1-4-1-4-0-1	    borrow	    A	Z	call																																																																
																																																																				
2-9-2-1-4-1-4-0-1-1-4	transfer	Z	B2	call																																																																
2-9-2-1-4-1-4-0-1-1-4-0	7a17edf7	B2	A	call
很明显能发现上面那个方法的缺点，即这里面在A->X和A->Z的地方并没有找到对应的相同调用
所以20210921针对上面的判重修改如下：
																																																																
1、首先搜索相同（caller，functionname，call type）的两次调用，具体为:
A->X functionA
【中间调用】
A->Y functionA
2、再在中间调用搜索能够凑成X->A的调用
并在A->Y后搜索能凑成Y->A的调用（强化判断）
将中间的调用生成一张有向图，找通路

'''


def generateGraph(callTxs, A, B):
    callTxs = callTxs.reset_index(drop=True)  # 重置索引、

    # 根据输入的txs生成有向图
    D = nx.DiGraph()
    D.add_node(A)
    D.add_node(B)
    # 遍历并输出节点和边的图
    list_nodes = []
    for i in range(len(callTxs)):
        sender = callTxs['sender'][i]
        recipient = callTxs['recipient'][i]
        D.add_edge(sender, recipient)
    return D


def getABAB(txs, hash):
    txs = txs.reset_index(drop=True)  # 重置索引
    list_index = []
    list_senderAndRecipient = []
    list_input_hex=[]
    list_finalOutPut = []
    count = 0  # 记录重复出现path的次数
    for i in range(len(txs)):
        txStart_tmp = [txs['sender'][i], txs['recipient'][i], txs['input_hex'][i][0:8], txs['index'][i]]
        # region 如果存在A调用A，则抛弃此次调用
        if txStart_tmp[0] == txStart_tmp[1]:
            continue;
        # endregion
        for j in range(i + 1, len(txs)):
            txEnd_tmp = [txs['sender'][j], txs['recipient'][j], txs['input_hex'][j][0:8], txs['index'][j]]
            # 交易限制判断
            if (
                # sender相同
                (txStart_tmp[0] == txEnd_tmp[0])
                # 调用的函数相同
                & (txStart_tmp[2] == txEnd_tmp[2])
                # index必须是【B以A开头】，保证B调用在A的子调用下面
                # 这种做法也限制了A和B之间的所有调用必须是子调用，因为数据本身就是按照index从浅到深输出的
                & (str(txEnd_tmp[3]).startswith(str(txStart_tmp[3]))) & (j - i > 1)):

                # 记录下相关信息用于输出
                A = txStart_tmp[0]
                X = txStart_tmp[1]
                AtoX_index = txStart_tmp[3]
                AtoY_index = txEnd_tmp[3]
                AtoX_input_hex = txStart_tmp[2]
                AtoY_input_hex = txEnd_tmp[2]

                # 满足前后完全相同且相隔>1时,将中间的tx作为有向图：切片，切行，从i+1到j
                list_middle_txs = txs.iloc[i + 1:j]
                # 根据切片之后的交易生成有向图
                D = generateGraph(list_middle_txs, A, X)

                # 判断有向图是否存在X->A的通路
                if nx.has_path(D, X, A):

                    # region 聚合输出信息
                    list_senderAndRecipient.append(A)
                    list_senderAndRecipient.append(X)
                    list_index.append(AtoX_index)
                    list_index.append(AtoY_index)
                    list_input_hex.append(AtoX_input_hex)
                    list_input_hex.append(AtoY_input_hex)
                    shortest_path = nx.shortest_path(D, X, A)
                    list_finalOutPut.append(list_senderAndRecipient)
                    list_finalOutPut.append(list_index)
                    list_finalOutPut.append(list_input_hex)
                    list_finalOutPut.append(shortest_path)
                    list_finalOutPut.append(hash)
                    # endregion

                    # region 写文件
                    f = open('test.txt', 'a')  # 若是'wb'就表示写二进制文件
                    f.write(",")
                    f.write(json.dumps(list_finalOutPut))
                    f.close()
                    # endregion

                    # FLAG = True

                list_index = []
                list_senderAndRecipient = []
                list_finalOutPut=[]
                list_input_hex=[]
    # if FLAG:
    #     print("^^^^^^^^^^^^^^^^^^txhash：" + hash + "^^^^^^^^^^^^^^^^^^")


if __name__ == '__main__':
    file_path = r'C:\迅雷下载\blockchair_ethereum_calls_20210917.tsv\blockchair_ethereum_calls_20210917.tsv'
    # file_path = r'C:\Users\nerbonic\Desktop\new.tsv'
    datas = pd.read_csv(file_path, sep='\t', header=0, index_col=None)
    wp = datas.drop_duplicates(['transaction_hash'])
    list_senderAndRecipient = []
    list_paths = []
    list_blocknum = []
    flag = 0
    for i in trange(len(wp['transaction_hash'].values)):

        hash = wp['transaction_hash'].values[i]
        blockNum = wp['block_id'].values[i]
        if blockNum not in list_blocknum:
            list_blocknum.append(blockNum)
            print(blockNum)
        # region 数据清洗
        if len(hash) != 64:
            continue
        txs = datas[datas['transaction_hash'] == hash]
        # 筛选掉所有非call的行
        callTxs = txs[txs['type'] == "call"]
        # 筛选掉所有hash,sender,recipient为空的
        callTxs = callTxs.dropna(axis=0, subset=["transaction_hash", "sender", "recipient"])
        # 消除input_hex为空的情况
        callTxs = callTxs.fillna('ABCDEFGH')
        callTxs = callTxs[callTxs['input_hex'] != 'ABCDEFGH']  # 筛选掉所有index hex为空的，避免把转账的操作当成调用

        # endregion

        if (len(callTxs) > 2):  # 大于2才进行重入判断
            getABAB(callTxs, hash)
